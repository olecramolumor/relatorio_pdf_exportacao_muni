'''
SCRIPT RESPONSÁVEL PELA CONEXÃO COM O BANCO DE DADOS (GISDB)
PARA LIMPAR O CÓDIGO E NÃO FICAR REPETINDO OS MESMOS SCRIPTS MIL VEZES.
ESTRUTURA:
    CONFIG
    CONNECT
'''
#In[1]:
import os
import logging
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine

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
        env_var = (
            'DB_DRIVER',
            'DB_HOST',
            'DB_NAME',
            'DB_USER',
            'DB_PASSWORD',
            'DB_PORT',
            'DB_TAB'
        )
        

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
#In[]:
def main():
    engine = None
    sucesso = False
    tempo_ini = time.perf_counter()

    try:
        logger.info("=="*32)
        logger.info("--- INÍCIO PROCESSO DE COLETA DO DATAFRAME ---")

        logger.info("PASSO 1.1: CONFIGURAÇÃO DA ENGINE")
        config = db_config()

        logger.info("PASSO 1.2: CONEXÃO COM O BANCO DE DADOS")
        engine = db_conecta(config)

        sucesso = True
        logger.info("PASSO 1.3: CONEXÃO BEM SUCEDIDA")

        return engine

    except Exception as e:
        logger.info(f"Erro de execução no main(): {e}")
        raise

    finally:
        if engine and not sucesso:
            engine.dispose()
            logger.error("DESCONEXÃO FEITA DEVIDO A ERRO")

        tempo_fim = time.perf_counter()
        tempo_total = tempo_fim - tempo_ini
        logger.info(f"TEMPO DE EXECUÇÃO: {tempo_total:.4}s")

#In[]:
if __name__ == "__main__":
    main()