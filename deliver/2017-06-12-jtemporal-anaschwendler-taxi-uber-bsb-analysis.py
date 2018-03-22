
# coding: utf-8

# # Taxi and Uber expenses in Brasília analysis

# In[1]:

import pandas as pd
import numpy as np

from serenata_toolbox.datasets import fetch


# In[2]:

fetch('2017-05-25-reimbursements.xz', '../data')
fetch('2017-05-21-companies-no-geolocation.xz', '../data') # we won't need geolocation for this analysis


# In[3]:

reimbursements = pd.read_csv('../data/2017-05-25-reimbursements.xz',
                             dtype={'applicant_id': np.str,
                                    'cnpj_cpf': np.str,
                                    'congressperson_id': np.str,
                                    'subquota_number': np.str},
                             low_memory=False)


# In[4]:

companies = pd.read_csv('../data/2017-05-21-companies-no-geolocation.xz', low_memory=False)
companies['cnpj'] = companies['cnpj'].str.replace(r'\D', '')


# For this analysis Tony wanted the `Taxi, toll and parking` reimbursements from June 2014 to the present day. Let's filter that.

# In[5]:

reimbursements = reimbursements[reimbursements['subquota_description'] == 'Taxi, toll and parking']
reimbursements2014 = reimbursements[reimbursements['year'] == 2014]
reimbursements2014 = reimbursements2014[reimbursements2014['month'] >= 6]
reimbursementsall = reimbursements[reimbursements['year'] >= 2015]
reimbursements = reimbursements2014.append(reimbursementsall)
reimbursements.head()


# In[6]:

reimbursements.shape


# From June 2014, how much was spent in this category?

# In[7]:

sum(reimbursements['total_net_value'])


# CNPJs that correspond to sanctioned taxi-like apps in Brazil
# 1. APPS
#    1. 99 TAXIS LLC - CNPJ: 18533324000150
#    1. 99 TAXIS DESENVOLVIMENTO DE SOFTWARES LTDA. - CNPJ: 18033552000161
#    1. EASY TAXI SERVICOS LTDA. - CNPJ: 16809351000188
#    1. UBER DO BRASIL TECNOLOGIA LTDA. - CNPJ: 17895646000187
#    
# How many of the total amount of the reimbursements from June 2014 to the present day

# In[8]:

apps_cnpjs = ['18533324000150', '18033552000161', '16809351000188', '17895646000187']
reimbursements[reimbursements['cnpj_cpf'].isin(apps_cnpjs)].shape


# We want to find the top 500 companies we have most expenses for

# In[9]:

aggregation = reimbursements.groupby('cnpj_cpf')['total_net_value'].agg(np.sum).rename('sum').reset_index()
top500 = aggregation.sort_values('sum', ascending=False).head(500)
top500 = top500.reset_index(drop=True)
top500.head()


# In[10]:

dataset = pd.merge(top500, companies, how='left', left_on='cnpj_cpf', right_on='cnpj')
dataset = dataset.drop('cnpj', axis=1)
dataset.head()


# In[11]:

dataset.shape


# ## Further investigation
# 
# With that table we selected a few companies and apps for further investigation:
# 
# 1. Companies
#    1. CGMP CENTRO DE GESTAO DE MEIOS DE PAGAMENTO LTDA - CNPJ: 04088208000165
#    1. SINDICATO DOS PERMISSIONARIOS DE TAXIS E MOTORISTAS AUXILIARES DO DISTRITO FEDERAL - CNPJ: 00031708000100
#    1. SINDICATO DOS TAXISTAS DO DISTRITO FEDERAL- SINTAXI - CNPJ: 07424109000103
#    1. RADIO TAXI ALVORADA LTDA - ME - CNPJ: 37990298000134
#    1. ALLPARK EMPREENDIMENTOS, PARTICIPACOES E SERVICOS S.A. - CNPJ: 60537263089981 
# 1. APPS
#    1. 99 TAXIS LLC - CNPJ: 18533324000150
#    1. 99 TAXIS DESENVOLVIMENTO DE SOFTWARES LTDA. - CNPJ: 18033552000161
#    1. EASY TAXI SERVICOS LTDA. - CNPJ: 16809351000188
#    1. UBER DO BRASIL TECNOLOGIA LTDA. - CNPJ: 17895646000187
#    
#    
# We want to know the top 5 lower house representatives with most expenses in those CNPJs and how many expenses where there.

# In[12]:

cnpjs = ['04088208000165', '00031708000100', '07424109000103', '37990298000134', '60537263089981',
         '18533324000150', '18033552000161', '16809351000188', '17895646000187']
reimbursements = reimbursements[reimbursements['cnpj_cpf'].isin(cnpjs)]
reimbursements.head()


# In[13]:

keys = ['congressperson_name', 'cnpj_cpf']

reimbursements_agg = reimbursements.groupby(keys)['total_net_value']                                    .agg([np.sum, len]).rename(columns={'len':'expenses'})
reimbursements_agg.head(20)


# In[14]:

reimbursements_agg = reimbursements_agg.reset_index()
reimbursements_agg.head()


# In[15]:

reimbursements_agg.shape


# In[16]:

companies = companies[['name', 'cnpj']]
companies.head(20)


# In[17]:

dataset = pd.merge(reimbursements_agg, companies, right_on='cnpj', left_on='cnpj_cpf')
dataset = dataset.drop('cnpj', axis=1)
dataset.head(20)


# In[18]:

dataset.shape


# In[19]:

dataset = dataset.sort_values(['sum', 'expenses'], ascending=[False, False]).reset_index(drop=True)
dataset.head()


# In[20]:

# writer = pd.ExcelWriter('2017-06-20-taxi-analysis.xlsx') # requires openpyxl
# dataset.to_excel(writer,'Sheet1')
# writer.save()

