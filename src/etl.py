import pandas as pd
import requests


url = 'https://drive.google.com/uc?id=1bJpHEb_axSoTiX0lSZb5yQr5EDTtzd5o&export=download'
response = requests.get(url)

# Assuming it's a CSV
with open('temp_file.csv', 'wb') as file:
    file.write(response.content)

df = pd.read_csv('temp_file.csv')

#criar cópia do df1
df1 = df.copy()

# manipulação das datas
datas = pd.to_datetime(df1['date_added'], format='mixed')
df1['date_added'] = datas

# Valores faltantes serão substituídos por nao_informado
df1 = df1.fillna("nao_informado")

# Seleciona as linhas onde 'duration' é igual a 'nao_informado'
mask = df1['duration'] == 'nao_informado'

# Cria uma cópia dos valores de 'rating' e 'duration' apenas para essas linhas
temp = df1.loc[mask, 'rating'].copy()
df1.loc[mask, 'rating'] = df1.loc[mask, 'duration']
df1.loc[mask, 'duration'] = temp

# Função para tratar o atributo duration
def substituir_valores(duration):
  if "min" in duration:
    return int(duration.split(' ')[0])
  if "Season" in duration:
    return int(duration.split(' ')[0])
  else:
    return "nao_informado"

#Aplicando a função
df1['duracao'] = df1['duration'].apply(substituir_valores)

df1['rating'] = df1['rating'].replace(['TV-Y','TV-Y7','G','TV-G','PG','TV-PG','TV-Y7-FV'],'Kids')
df1['rating'] = df1['rating'].replace(['PG-13','TV-14'],'Teens')
df1['rating'] = df1['rating'].replace(['R','TV-MA','NC-17'],'Adults')
df1['rating'] = df1['rating'].replace(['NR','UR'],'nao_informado')


df1.to_csv('netflix.csv', sep=';', decimal=',')



