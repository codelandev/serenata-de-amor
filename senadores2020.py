#!/usr/bin/env python
# coding: utf-8

# https://www12.senado.leg.br/dados-abertos/conjuntos?grupo=senadores&portal=administrativo

import pandas as pd
print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
print('\n')
print('#####################################################################')
print('n')
df = pd.read_csv('senadores-despesas-2020.csv', sep=';', encoding='latin1', decimal=',')
print('\n')
print('#####################################################################')
print('Cotas para Exercício da Atividade Parlamentar dos Senadores (CEAPS)')
print('######################################################################')
print('\n')
print('Assuntos: Reembolso de Senadores')
print('\n')
print(df.head(10))
print('\n')
print('#####################################################################')
print('Valores reembolsados')
print('#####################################################################')
print('\n')
df.info()
print('\n')
# Total de reembolso 2020
thousands_separator = "."
fractional_separator = ","
soma = df['VALOR_REEMBOLSADO'].sum()
currency = "R${:,.2f}".format(soma)
if thousands_separator == ".":
    main_currency, fractional_currency = currency.split(".")[0], currency.split(".")[1]
new_main_currency = main_currency.replace(",", ".")
currency = new_main_currency + fractional_separator + fractional_currency
print('#####################################################################')
print('Destaque para o valor recebido pelo Senador Humberto Costa')
print('#####################################################################')
print(currency)
print('\n')
print('#####################################################################')
print('O valor de mais de R$ 2 MI se distancia e muito dos demais valores')
print('#####################################################################')
print(df.describe().apply(lambda s: s.apply('{0:.2f}'.format)))
print('\n')
print('#####################################################################')
print(df[df['VALOR_REEMBOLSADO'] == 2141702])
print('#####################################################################')
print('\n')
print('#####################################################################')
print('Lista dos 4 maiores valores reembolsados em 2020, agrupado por senaodres')
print('#####################################################################')
print(df.groupby('SENADOR')['VALOR_REEMBOLSADO'].sum().nlargest())
print('\n')
print('#####################################################################')
print('Lista de senadores e seus respectivos valores reembolsados em 2020')
print('#####################################################################')
print('\n')
print(df.groupby('SENADOR')['VALOR_REEMBOLSADO'].sum().nlargest(40))
print(df.groupby('SENADOR')['VALOR_REEMBOLSADO'].sum().nsmallest(41).sort_values(ascending=False))
print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
