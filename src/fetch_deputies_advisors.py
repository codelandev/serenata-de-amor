import csv
import datetime
import lzma
import os
from itertools import chain, islice
from lxml import html

import grequests
import requests

CAMARA_URL = (
    'http://www2.camara.leg.br/transparencia/recursos-humanos/'
    'servidores/lotacao/consulta-secretarios-parlamentares/'
    'layouts_transpar_quadroremuner_consultaSecretariosParlamentares'
)

USERAGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/46.0.2490.86 Safari/537.36'
)
FIELDNAMES = (
    'point',
    'name',
    'act_issue_at',
    'act_issued_by',
    'congressperson_name',
    'congressperson_number'
)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data')
DATE = datetime.date.today().strftime('%Y-%m-%d')
FILE_BASE_NAME = '{}-congresspeople-advisors.xz'.format(DATE)
OUTPUT = os.path.join(DATA_PATH, FILE_BASE_NAME)


def run():
    print("Fetching congresspeople data…")
    congresspeople_data = fetch_congresspeople_data()

    print("Preparing requests to fetch advisors data…")
    requests_ = (get_page(congressperson) for congressperson in congresspeople_data)
    for page_data in send_requests(requests_):
        congressperson_with_advisors = page_data["data"]
        congressperson = {
            "congressperson_name": congressperson_with_advisors["congressperson_name"],
            "congressperson_number": congressperson_with_advisors["congressperson_number"]
        }
        advisors = tuple(congressperson_with_advisors["congressperson_advisors"])
        congressperson_information = organize_congressperson_data(congressperson, advisors)
        write_to_csv(congressperson_information, OUTPUT)

    print("\nDone! The file can be found at {}".format(OUTPUT))


def send_requests(reqs):
    """
    Send all the requests in :reqs: and reads the response data to extract the
    congresspeople data.  It will check if a congressperson has more than one page of
    advisors and send new requests if True
    """
    buffer = list()

    print("Sending!")
    kwargs = dict(size=8, exception_handler=http_exception_handler)
    for response in grequests.imap(reqs, **kwargs):
        page_data = extract_data_from_page(response)

        yield page_data
        print('.', end="", flush=True)

        if page_data["has_next_page"]:
            current = page_data["current_page"]
            total = page_data["number_of_pages"]
            for page in range(current + 1, total + 1):
                buffer.append(get_page(page_data['data'], page))

    pending = len(buffer)
    print("\nFound {} more pages to fetch. Starting now…".format(pending))
    for req in grequests.imap(buffer, **kwargs):
        page_data = extract_data_from_page(req)
        yield page_data
        print('.', end="", flush=True)


def fetch_congresspeople_data():
    """
    Returns a list with all congresspeople names and its numbers after parsing the
    `<select>` element in `CAMARA_URL`
    """
    page = requests.get(CAMARA_URL)
    tree = html.fromstring(page.content)

    select = tree.xpath('//select[@id="lotacao"]/option')
    congresspeople_data = get_congresspeople_list(select)

    return islice(congresspeople_data, 1, None)  # skip first as it is "Selecione…"


def get_congresspeople_list(select):
    """ Parses the `<select>` element in `CAMARA_URL` """
    for option in select:
        yield dict(
            congressperson_name=option.xpath("./text()")[0],
            congressperson_number=option.xpath('./@value')[0]
        )


def get_page(congressperson, page=1):
    """
    Returns a POST AsyncRequest object from grequests ready to be sent to
    `CAMARA_URL` with `lotacao` field filled with `congressperson_number`. Some
    congresspeople can have more than 20 advisors, so some pages will have
    pagination. In this case it's necessary to inform the specific page you
    want to create a request to, otherwise a request to the first page will be
    created.
    :congressperson: (dict) A Dict with fields `congressperson_name` and `congressperson_number`
    :page: (int) Defaults to 1. The page number
    """
    data = {
        "lotacao": congressperson["congressperson_number"],
        "b_start:int": (page - 1) * 20  # page 1 = 0, page 2 = 20, page 3 = 40
    }
    return grequests.post(CAMARA_URL, data=data)


def extract_data_from_page(page):
    """
    Extracts all relevant data from a page and returns it as Dict. Each
    information is inside a key in the dict as following:
    - congressperson name, number and advisors inside the key `data` as `congressperson_name`,
      `congressperson_number` and `congressperson_advisors` respectively.
    - Number of pages of advisors; as `number_of_pages`
    - The current page number as `current_page`
    - If it has more pages of advisors as `has_next_page`
    """
    html_tree = html.fromstring(page.content)
    number_of_pages = extract_number_of_pages(html_tree)
    current_page = extract_current_page(html_tree)

    tbody = html_tree.xpath('//table[@class="tabela-padrao-bootstrap"]/tbody/tr')
    congressperson_advisors = tuple(extract_adivisors(tbody))

    select = html_tree.xpath('//select[@id="lotacao"]/option[@selected]')[0]
    congressperson_data = {
        "congressperson_name": select.xpath('./text()')[0],
        "congressperson_number": select.xpath("./@value")[0],
        "congressperson_advisors": congressperson_advisors
    }

    # Some "Data de Publicação do Ato" are empty in `CAMARA_URL` and xpath are
    # not adding an 'empty string' inside the returned array, so we are adding
    # it manualy below
    for advisor_info in congressperson_advisors:
        if len(advisor_info) == 3:
            advisor_info.append("Empty")

    return {
        'data': congressperson_data,
        'number_of_pages': number_of_pages,
        'current_page': current_page,
        'has_next_page': False if current_page == number_of_pages else True
    }


def extract_current_page(tree):
    """
    Helper function to extract the current page number of the page of advisors
    from a HTMLElement (lxml)
    """
    selector = '//ul[@class="pagination"]/li[@class="current"]/span/text()'
    result = tree.xpath(selector)
    return 1 if len(result) == 0 else int(result[0])


def extract_number_of_pages(tree):
    """
    Helper function to extract the number of pages of the page of advisors from
    a HTMLElement (lxml)
    """
    selector = (
        'count(//ul'
        '[@class="pagination"]/li[not(contains(@class,"next"))]'
        '[not(contains(@class,"previous"))])'
    )
    result = tree.xpath(selector)
    return 1 if result == 0 else int(result)


def organize_congressperson_data(congressperson, advisors):
    """
    Organizes all the congresspeople information in a list. Use this function to
    prepare data to be written to CSV format.
    :congressperson: (dict) A dict with keys `congressperson_name` and `congressperson_number`
    :advisors: (tuple) lists with advisors data.
    """
    name, number = congressperson["congressperson_name"], congressperson["congressperson_number"]
    if not advisors:
        values = ('', '', '', '', name, number)
        yield dict(zip(FIELDNAMES, values))
    else:
        for advisor in advisors:
            values = chain(advisor, (name, number))
            cleaned = map(lambda x: '' if x == '-' else x, values)
            yield dict(zip(FIELDNAMES, cleaned))


def extract_adivisors(tbody):
    """Extracts advisors name from a HTML table"""
    for element in tbody:
        yield element.xpath('./td/text() | ./td/span/text()')


def write_to_csv(data, output):
    """
    Writes `data` to `output`
    :data: (list) list with organized congressperson information ready to be written
    :output: (string) the full path to a file where :data: should be written
    """
    with lzma.open(output, "at") as fh:
        kwargs = dict(fieldnames=FIELDNAMES, quoting=csv.QUOTE_ALL)
        writer = csv.DictWriter(fh, **kwargs)
        writer.writeheader()
        for advisor in data:
            print(advisor)
            writer.writerow(advisor)


def http_exception_handler(request, exception):
    """Callback to be executed by grequests when a request fails"""
    print('\n', exception)


if __name__ == '__main__':
    run()
