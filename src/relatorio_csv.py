#In[]
'''
ESSE SCRIPT PUXA UM DATAFRAME EM .csv DO PROPRIO BANCO PARA GERAR UMA QUERY
 DE DADOS DE BUSCA PARA O MENU DROPDOWN DE JANELAS DE BUSCA 
'''
import os
import pandas as pd
import logging
import time
from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, select

#SRC
import relatorio_utils

#In[3]:
'''ESCOPO GLOBAL'''
#CONFIG DO LOG
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#LOAD DO .env ÚNICO
load_dotenv()

#In[5]:
#FUNÇÃO DE SELECT DO BD
def db_select(engine):
    try:
        #CRIAÇÃO DA TABELA
        metadata = MetaData()
        tabela_nome = os.getenv("DB_TAB")
        tabela = Table(tabela_nome, metadata, autoload_with=engine)

        # QUERY SQL DO .csv
        query = (
            select(tabela.c.pais, tabela.c.ano, tabela.c.municipio,tabela.c.produto).distinct()
        )
        
        #LEVANTAR ERRO SE NÃO ENCONTRAR A TABELA
        if not tabela_nome:
            raise ValueError("Variável 'DB_TAB' não foi encontrada no .env")

        #CONEXÃO COM O BANCO DE DADOS
        with engine.connect() as conn:
            #CRIANDO O DATAFRAME
            df = pd.read_sql_query(query, conn)
        
        logger.info(f"PASSO 1.3.1: Sucesso para a execução do Dataframe de Rôndonia - Dataframe Exportação Municipal. Total de Linhas: {len(df)}")
        return df
    
    except Exception as e:
        logger.error(f"Erro no db_select: {e}", exc_info=True)
        raise

#In[]:
def db_etl(df):
        try:
            #REMOVENDO #U+00a0
            df = df.map(lambda x: x.replace('\xa0', ' ').strip() if isinstance(x, str) else x)
            df['ano'] = df['ano'].astype(int)
            return df

        except Exception as e:
            logger.error(f"Erro no ETL: {e}", exc_info=True)
            raise

#In[6]:
#FUNÇÃO DE DF BD
def db_dataframe(df):
    try:
        #CAMINHO DAS PASTAS
        pasta_atual = os.getcwd()
        pasta_arq = os.path.join(pasta_atual, "Auxiliar")
        os.makedirs(pasta_arq, exist_ok=True)

        #NOME DO ARQUIVO
        arq_nome = f"busca_ano_pais_ro_municipal.csv"
        arq_cam = os.path.join(pasta_arq,arq_nome)

        #SALVANDO DATAFRAME
        df.to_csv(arq_cam, index=False, sep=';', encoding="utf-8-sig")

        return arq_cam

    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)
        raise


#In[7]:
#FUNÇÃO main()
def main():

    engine = None
    sucesso = False
    tempo_ini = time.perf_counter()

    try:
        logger.info("=="*32)
        logger.info("--- INÍCIO PROCESSO DE COLETA DO DATAFRAME ---")

        logger.info("PASSO 1.1: CONEXÃO COM O BANCO DE DADOS")
        engine = relatorio_utils.main()

        logger.info("PASSO 1.2: FAZENDO A QUERY DE DADOS")
        df = db_select(engine)

        logger.info("PASSO 1.3:ETL DO DATAFRAME")
        df_final = db_etl(df)

        '''
        logger.info("PASSO 1.4: SALVANDO DATAFRAME")
        db_dataframe(df_final)
        '''
       
        # PASSO 1.5: EXTRAINDO LISTAS DO DF
        paises = sorted(df_final['pais'].dropna().astype(str).str.strip().unique().tolist())
        municipios = sorted(df_final['municipio'].dropna().astype(str).str.strip().unique().tolist())
        produto = sorted(df_final['produto'].dropna().astype(str).str.strip().unique().tolist())
        
        anos_int = sorted(df_final['ano'].dropna().astype(int).unique().tolist(), reverse=True)
        anos_str = [str(a) for a in anos_int]

        sucesso = True
        return paises, municipios, anos_str, produto

    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)
        raise
    
    finally:
        if engine:
            engine.dispose()
            logger.info("PASSO 1.5: DESCONEXÃO DA ENGINE")

        tempo_fim = time.perf_counter()
        tempo_total = tempo_fim - tempo_ini

        if not sucesso:
            logger.info(f"PROCESSO CONCLUÍDO SEM ÊXITO - TEMPO TOTAL: {tempo_total:.4f}s.")
        else:        
            logger.info(f"PROCESSO CONCLUÍDO COM ÊXITO - TEMPO TOTAL: {tempo_total:.4f}s.")

        logger.info("--- FIM PROCESSO DE COLETA DO DATAFRAME ---")
        logger.info("=="*32)

#In[8]:
#EXECUTAR
if __name__ == "__main__":
    main()