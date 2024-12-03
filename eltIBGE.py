import os
import pandas as pd

# Diretório onde o arquivo será salvo
directory = "datasets"

# Verifica se o diretório já existe, caso contrário, cria o diretório
if not os.path.exists(directory):
    os.makedirs(directory)

url ='https://servicodados.ibge.gov.br/api/v3/agregados/8688/periodos/201102-202407/variaveis/11623?localidades=N1[all]&classificacao=11046[56726]|12355[107071,106869,106874,31399,106876,31426]'
data = pd.read_json(url)

# Normalizar o JSON para um DataFrame
df = pd.json_normalize(data['resultados'][0])

# Criar um dicionário para armazenar as séries temporais com seus respectivos nomes de coluna
series_dict = {}

# Iterar sobre as classificações e séries
for i in range(len(df['classificacoes'])):
    # Extrair o nome da coluna
    nome_coluna = list(df['classificacoes'][i][1]['categoria'].values())[0]

    # Extrair os valores da série
    serie_valores = df['series'][i][0]['serie']

    # Adicionar a série ao dicionário
    series_dict[nome_coluna] = serie_valores

# Criar um DataFrame a partir do dicionário de séries
df_series = pd.DataFrame(series_dict)

# Adicionar a coluna de Data como índice (anos-meses)
df_series.index = df['series'][0][0]['serie'].keys()

# Certificar que o índice está no formato datetime para posterior análise
df_series.index = pd.to_datetime(df_series.index, format='%Y%m')

# Renomear o índice para "Data"
df_series.index.name = "Data"

# Exibir o DataFrame criado
display (df_series)

# Salvar o DataFrame em um CSV com a formatação brasileira
df_series.to_csv('datasets/pms_vendas.csv', encoding='utf-8-sig')