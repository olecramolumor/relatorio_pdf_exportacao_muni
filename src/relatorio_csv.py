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
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import Session

#In[3]:
'''ESCOPO GLOBAL'''
#CONFIG DO LOG
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#LOAD DO .env ÚNICO
load_dotenv()

#In[3]:
#FUNÇÃO DE CONFIG DO BD
def db_config():
    try:
        env_var = {
            'DB_DRIVER',
            'DB_HOST',
            'DB_NAME',
            'DB_USER',
            'DB_PASSWORD',
            'DB_PORT',
            'DB_TAB'
        }

        #LISTA DE DADOS VAZIO
        config = {}

        #LOOP DE VERIFICAÇÃO DE DADOS:
        for var in env_var:
            #SETANDO var DO .env EM dados
            dado = os.getenv(var)

            #VERIFICA SE O DADO EXISTE
            if dado:
                config[var] = dado

            #MENSAGEM DE ERRO PARA DADO VAZIO
            else:
                raise ValueError(f"{var}: Variável Inexistente ou Valor Nulo no .env")

        return config

    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)
        raise

#In[4]:
#FUNÇÃO DE CONEXÃO DO BD
def db_conecta(config):
    try:
        #URL DE ACESSO DA ENGINE
        DB_URL = f"{config['DB_DRIVER']}://{config['DB_USER']}:{config['DB_PASSWORD']}@{config['DB_HOST']}:{config['DB_PORT']}/{config['DB_NAME']}"

        #CRIAÇÃO DA ENGINE
        #engine= create_engine(DB_URL, echo=True) #LOGS GIGANTES
        engine= create_engine(DB_URL, echo=False)

        return engine

    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)
        raise

#In[5]:
#FUNÇÃO DE SELECT DO BD
def db_select(engine):
    try:
        metadata = MetaData()
        tabela = Table(os.getenv('DB_TAB'), metadata, autoload_with=engine)

        with engine.connect() as conn:
            query = (
                select(tabela.c.pais, tabela.c.ano).distinct()
            )
        
            resultado = conn.execute(query)

            df = pd.DataFrame(resultado.fetchall(), columns=resultado.keys())
        
        logger.info(f"PASSO 1.3.1: Sucesso para a execução do Dataframe de Rôndonia - Dataframe Exportação Municipal. Total de Linhas: {len(df)}")

        return df
    
    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)
        raise

#In[]:
def db_etl(df):
        #REMOVENDO #U+00a0
        df = df.map(lambda x: x.replace('\xa0', ' ').strip() if isinstance(x, str) else x)
        return df

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
    try:
        engine = None
        sucesso = False
        tempo_ini = time.perf_counter()

        logger.info("=="*32)
        logger.info("--- INÍCIO PROCESSO DE COLETA DO DATAFRAME ---")

        logger.info("PASSO 1.1: CONFIGURAÇÃO DA ENGINE")
        config = db_config()

        logger.info("PASSO 1.2: CONEXÃO COM O BANCO DE DADOS")
        engine = db_conecta(config)

        logger.info("PASSO 1.3: FAZENDO A QUERY DE DADOS")

        df = db_select(engine)

        logger.info("PASSO 1.4:ETL DO DATAFRAME")
        df_final = db_etl(df)

        logger.info("PASSO 1.5: SALVANDO DATAFRAME")
        arq_cam= db_dataframe(df_final)

        logger.info("PASSO 1.6: DESCONEXÃO DA ENGInE")
        engine.dispose()

        sucesso = True
        return arq_cam

    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)
        
        try:
            engine.dispose()
            logger.info("--- DEVIDO A ERRO CONEXÃO COM O BANCO DE DADOS ENCERRADA! ---")
        except:
            pass
        raise
    
    finally:
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
    '''MUDAR AQUI'''
   
    '''MUDAR AQUI'''
    main()
