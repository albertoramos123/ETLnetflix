import requests
import json
import pandas as pd
import sqlite3
import os

# Diretório onde o arquivo será salvo
directory = "datasets"

# Verifica se o diretório já existe, caso contrário, cria o diretório
if not os.path.exists(directory):
    os.makedirs(directory)

class etlBcb:
    def __init__(self, api_link):
        self.api_link = api_link
        self.dados = None
        self.df = None

    def requisicao_api(self):
        """
        Método GET para a API e armazenar a resposta.
        """
        try:
            resposta = requests.get(self.api_link)
            if resposta.status_code == 200:
                self.dados = resposta.json()
                print('Status Code:', resposta.status_code)
            else:
                print('Erro na requisição. Status Code:', resposta.status_code)
        except Exception as e:
            print('Erro ao fazer a requisição:', e)

    def transformar_dados(self, chave_json):
        """
        Método para transformar os dados JSON em um DataFrame pandas.
        """
        if self.dados:
            try:
                data = self.dados[chave_json]
                self.df = pd.json_normalize(data)

                # Verificar se a coluna 'trimestre' está presente e converter
                if 'trimestre' in self.df.columns:
                    print('Coluna "trimestre" encontrada, convertendo para datas...')
                    self.df['trimestre'] = self.df['trimestre'].astype(str)
                    self.df['data'] = self.df['trimestre'].apply(self.trimestre_para_data)
                    self.df['data'] = self.df['data'].dt.date  # Converte para o formato de data sem hora
                if 'AnoMes' in self.df.columns:
                    print('Coluna "AnoMes" encontrada, convertendo para datas...')
                    self.df['AnoMes'] = self.df['AnoMes'].astype(str)
                    self.df['data'] = self.df['AnoMes'].apply(self.anoMes_para_data)
                    self.df['data'] = self.df['data'].dt.date  # Converte para o formato de data sem hora
                if 'Data' in self.df.columns:
                    print('Coluna "Data" encontrada, convertendo para datas...')
                    self.df['Data'] = self.df['Data'].astype(str)
                    self.df['Data'] = pd.to_datetime(self.df['Data']).dt.date
                else:
                    print('Coluna "trimestre" não encontrada nos dados.')
                print('Transformação concluída.')
            except KeyError:
                print(f'Chave "{chave_json}" não encontrada nos dados JSON.')
            except Exception as e:
                print('Erro ao transformar os dados:', e)
        else:
            print('Nenhum dado para transformar.')

    @staticmethod
    def trimestre_para_data(trimestre):
        """
        Função para converter o formato de trimestre para data.
        """
        try:
            ano = int(str(trimestre)[:4])
            trimestre_num = int(str(trimestre)[-1])
            mes = (trimestre_num - 1) * 3 + 1
            return pd.to_datetime(f"{ano}-{mes:02d}-01")
        except ValueError:
            print(f"Erro ao converter o trimestre: {trimestre}")
            return pd.NaT  # Retorna data nula se houver erro

    @staticmethod
    def anoMes_para_data(AnoMes):
        """
        Função para converter o formato de AnoMes (ex: 202202) para data.
        """
        try:
            ano = int(str(AnoMes)[:4])  # Ano nos primeiros 4 caracteres
            mes = int(str(AnoMes)[4:6])  # Mês nos últimos 2 caracteres
            return pd.to_datetime(f"{ano}-{mes:02d}-01")  # Formata como 'YYYY-MM-01'
        except ValueError:
            print(f"Erro ao converter o mês/ano: {AnoMes}")
            return pd.NaT  # Retorna data nula se houver erro

    def salvar_sqlite(self, nome_tabela):
        """
        Método para salvar o DataFrame transformado em um banco de dados SQLite.
        """
        nome_banco = 'Fecomdb.db'
        if self.df is not None:
            try:
                conexao = sqlite3.connect(nome_banco)
                self.df.to_sql(nome_tabela, conexao, if_exists='replace', index=False)
                conexao.close()
                print(f'Dados salvos na tabela "{nome_tabela}" do banco de dados "{nome_banco}".')
            except Exception as e:
                print('Erro ao salvar os dados no banco de dados SQLite:', e)
        else:
            print('Nenhum dado para salvar no banco de dados.')

    def salvar_csv(self, nome_arquivo):
        """
        Método para salvar o CSV.
        """
        if self.df is not None:
            try:
                self.df.to_csv(f'datasets/{nome_arquivo}', sep=';', decimal=',', encoding='utf-8-sig')
                print(f'Dados salvos no arquivo CSV "{nome_arquivo}".')
            except Exception as e:
                print('Erro ao salvar o CSV:', e)
        else:
            print('Nenhum dado no CSV.')

    def executar_etl(self, chave_json, nome_tabela, nome_arquivo):
        """
        Método para executar todo o processo de ETL.
        """
        # Executar extração
        self.requisicao_api()

        # Transformar os dados
        self.transformar_dados(chave_json)

        # Salvar no banco SQLite
        self.salvar_sqlite(nome_tabela)

        # Salvar em CSV
        self.salvar_csv(nome_arquivo)