
# coding: utf-8

# # Showcasing `serenata-ocr`
# 
# As outlined in [a previous notebook](https://github.com/datasciencebr/serenata-de-amor/blob/master/research/develop/2016-12-30-fgrehm-ocr-receipts-with-google-cloud-vision.ipynb), we have an interest in analysing the contents of a receipt. Given the receipts are mostly scanned documents saved as PDFs with no textual information that can be parsed by a computer, we need to rely on OCR tools to get the job done.
# 
# [serenata-ocr](https://github.com/fgrehm/serenata-ocr) is an API that takes in Chamber of Deputies reimbursement information and returns the text contained in its receipt. While the project is still in its early days, it provides some improvements over the process that was done to OCR the initial set of 200K receipts documented [here](https://github.com/datasciencebr/serenata-de-amor/blob/master/docs/receipts-ocr.md), namely support for deskewing receipts images (making them straight), giving google a hint that the text is in portuguese and usage of the new [document text detection](https://cloud.google.com/vision/docs/detecting-fulltext) feature provided by Google Cloud Vision.
# 
# Picking the same set of 10 receipts used in the previous notebook ([available in the `2017-02-15-receipts-texts.xz` dataset](https://github.com/datasciencebr/serenata-de-amor/blob/master/docs/receipts-ocr.md#available-datasets)) as examples, the idea here is to compare the text returned by `serenata-ocr` with the information obtained by the initial approach used for OCRing receipts:
# 
# * http://www.camara.gov.br/cota-parlamentar/documentos/publ/1789/2015/5631309.pdf
# * http://www.camara.gov.br/cota-parlamentar/documentos/publ/1789/2015/5631380.pdf
# * http://www.camara.gov.br/cota-parlamentar/documentos/publ/1564/2016/5928875.pdf
# * http://www.camara.gov.br/cota-parlamentar/documentos/publ/80/2015/5768932.pdf
# * http://www.camara.gov.br/cota-parlamentar/documentos/publ/3052/2016/5962849.pdf
# * http://www.camara.gov.br/cota-parlamentar/documentos/publ/3052/2016/5962903.pdf
# * http://www.camara.gov.br/cota-parlamentar/documentos/publ/2238/2015/5855221.pdf
# * http://www.camara.gov.br/cota-parlamentar/documentos/publ/2238/2015/5856784.pdf
# * http://www.camara.gov.br/cota-parlamentar/documentos/publ/2871/2016/5921187.pdf
# * http://www.camara.gov.br/cota-parlamentar/documentos/publ/2935/2016/6069360.pd

# ## Processing PDFs

# In[1]:


SERENATA_OCR_URL = "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/latest/chamber-of-deputies/receipt"


# In[2]:


reimbursements = [
    { "applicant_id": 1789, "year": 2015, "document_id": 5631380, "args": ""},
    { "applicant_id": 1564, "year": 2016, "document_id": 5928875, "args": ""},
    { "applicant_id": 3052, "year": 2016, "document_id": 5962849, "args": ""},
    { "applicant_id": 3052, "year": 2016, "document_id": 5962903, "args": ""},
    { "applicant_id": 2238, "year": 2015, "document_id": 5855221, "args": ""},
    { "applicant_id": 2238, "year": 2015, "document_id": 5856784, "args": ""},
    { "applicant_id": 2871, "year": 2016, "document_id": 5921187, "args": ""},
    { "applicant_id": 2935, "year": 2016, "document_id": 6069360, "args": ""},
    # These 2 reimbursements require a smaller density, otherwise the API times out
    { "applicant_id": 80,   "year": 2015, "document_id": 5768932, "args": "density=100" },
    { "applicant_id": 1789, "year": 2015, "document_id": 5631309, "args": "density=175" },
]


# In[3]:


import os
import urllib.request
import json

new_texts = {}
for r in reimbursements:
    document_id = r["document_id"]

    print("OCRing", r)
    response = urllib.request.urlopen("{0}/{1}/{2}/{3}?{4}".format(
        SERENATA_OCR_URL, 
        r["applicant_id"], 
        r["year"], 
        r["document_id"],
        r["args"]
    ))
    raw_data = response.read()
    encoding = response.info().get_content_charset('utf8')
    data = json.loads(raw_data.decode(encoding))
    text = data['ocrResponse']['textAnnotations'][0]['description']
    new_texts[document_id] = text

print("DONE")


# ## Comparing results
# 
# The previous batch of OCRed documents is available on the `2017-02-15-receipts-texts` dataset, so we'll load it up and compare the texts.

# In[4]:


import pandas as pd
import numpy as np

from serenata_toolbox.datasets import fetch

# fetch("2017-02-15-receipts-texts.xz", "data")
df = pd.read_csv('data/2017-02-15-receipts-texts.xz', low_memory=False)
df = df[df.document_id.isin(new_texts.keys())]


# ## Compare each document individually

# In[5]:


df['new_text'] = ""


# In[6]:


txt_series = pd.Series(new_texts)
df = df.set_index('document_id')
df['new_text'] = txt_series
df = df.reset_index()


# In[7]:


df['text'] = df.text.str.replace('\n', ' ')
df['new_text'] = df.new_text.str.replace('\n', ' ')


# In[8]:


# From http://code.activestate.com/recipes/302380-formatting-plain-text-into-columns/
import re

LEFT = '<'
RIGHT = '>'
CENTER = '^'

class FormatColumns:
    '''Format some columns of text with constraints on the widths of the
    columns and the alignment of the text inside the columns.
    '''
    def __init__(self, columns, contents, spacer=' | ', retain_newlines=True):
        assert len(columns) == len(contents),             'columns and contents must be same length'
        self.columns = columns
        self.num_columns = len(columns)
        self.contents = contents
        self.spacer = spacer
        self.retain_newlines = retain_newlines
        self.positions = [0]*self.num_columns

    def format_line(self, wsre=re.compile(r'\s+')):
        l = []
        data = False
        for i, (width, alignment) in enumerate(self.columns):
            content = self.contents[i]
            col = ''
            while self.positions[i] < len(content):
                word = content[self.positions[i]]
                # if we hit a newline, honor it
                if '\n' in word:
                    # chomp
                    self.positions[i] += 1
                    if self.retain_newlines:
                        break
                    word = word.strip()

                # make sure this word fits
                if col and len(word) + len(col) > width:
                    break

                # no whitespace at start-of-line
                if wsre.match(word) and not col:
                    # chomp
                    self.positions[i] += 1
                    continue

                col += word
                # chomp
                self.positions[i] += 1
            if col:
                data = True
            col = '{:<{}}'.format(col.lstrip(), width)
            l.append(col)

        if data:
            return self.spacer.join(l).rstrip()
        # don't return a blank line
        return ''

    def format(self, splitre=re.compile(r'(\n|\r\n|\r|[ \t]|\S+)')):
        # split the text into words, spaces/tabs and newlines
        for i, content in enumerate(self.contents):
            self.contents[i] = splitre.findall(content)

        # now process line by line
        l = []
        line = self.format_line()
        while line:
            l.append(line)
            line = self.format_line()
        return '\n'.join(l)

    def __str__(self):
        return self.format()
    
def display_comparisson(document_id):
    reimbursement = df[df.document_id == document_id].iloc[0]
    print(FormatColumns(((50, LEFT), (50, LEFT)), [reimbursement.text, reimbursement.new_text]))


# ## Document [5631309](http://www.camara.gov.br/cota-parlamentar/documentos/publ/1789/2015/5631309.pdf)
# 
# Not only we were able to OCR the _whole_ document (previously it failed on a couple pages) but the extracted text makes more a bit more sense.

# In[9]:


display_comparisson(5631309)


# ## Document [5928875](https://jarbas.datasciencebr.com/#/document_id/5928875) 
# 
# Same as before, the API is obviously not that magical and it can't parse handwritten stuff BUT it got really close to parsing the value of the reimbursement (`R$175,00` OCRed as `R$ 27S-OO`)

# In[10]:


display_comparisson(5928875)


# ## Document [5768932](https://jarbas.datasciencebr.com/#/document_id/5768932) 
# 
# A six page reimbursement document, once again we have more text extracted, at first sight, the quality is almost the same:

# In[11]:


display_comparisson(5768932)


# ## Document [5962849](https://jarbas.datasciencebr.com/#/document_id/5962849) 
# 
# Similar quality of text in terms of what we are interested in (timestamps, values and receipt items)

# In[12]:


display_comparisson(5962849)


# ## Document [5962903](https://jarbas.datasciencebr.com/#/document_id/5962903) 
# 
# More text again, similar quality

# In[13]:


display_comparisson(5962903)


# ## Document [5856784](https://jarbas.datasciencebr.com/#/document_id/5856784) 
# 
# Here we have both the card receipt and the invoice but this time the API can get some timestamps and a bit more of the receipt items

# In[14]:


display_comparisson(5856784)


# ## Document [5855221](https://jarbas.datasciencebr.com/#/document_id/5855221) 
# 
# Here we have both the card receipt and the invoice, the quality of the PDF / images sucks and the API can't do much magic, at least with the changes introduced by `serenata-ocr` we can parse some timestamps

# In[15]:


display_comparisson(5855221)


# ## Document [5921187](https://jarbas.datasciencebr.com/#/document_id/5921187) 
# 
# OCR makes a lot more sense here, deskewing the image seems to help quite a lot.

# In[16]:


display_comparisson(5921187)


# ## Document [6069360](https://jarbas.datasciencebr.com/#/document_id/6069360) 
# 
# All messed up, even with `serenata-ocr`, still _very_ useful.

# In[17]:


display_comparisson(6069360)


# ## Document [5631380](https://jarbas.datasciencebr.com/#/document_id/5631380)
# 
# There are 3 timestamps on the receipt and `serenata-ocr` almost got them all right (compared to only 2 in the past). The receipt items info (description and price) were better extracted in the first OCR work

# In[18]:


display_comparisson(5631380)


# ## Conclusion and next steps
# 
# - In general, it seems like the changes introduced by `serenata-ocr` seem to have paid off.
# - Can't really tell if the results improvements were more influenced due to deskewing images or the more expensive `DOCUMENT_TEXT_DETECTION` functionality from Google Cloud Vision.
# - Given this is never going to be a perfect process, we should consider leveraging multiple versions of the text of a receipt, doing things like tweaking pre processing and using different OCR providers.
# - I'll do a bit more experiments so we can have the best results before moving on with the next batch of OCR for recent data.
