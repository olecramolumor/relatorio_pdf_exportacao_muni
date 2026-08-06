#In[1]:
import os
import pandas as pd
import logging
import time
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, select

#SRC
import relatorio_utils

#In[3]:
'''ESCOPO GLOBAL'''
#CONFIG DO LOG
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#LOAD DO .env ÚNICO
load_dotenv()
dados_brutos = os.getenv("DB_TAB")
dados_lista = [item.strip() for item in dados_brutos.split(",")]


#In[]
def relatorio_conn():
    try:
        logger.info("PASSO 1.1: CONEXÃO COM O BANCO DE DADOS")
        engine = relatorio_utils.main()

        return engine

    except Exception as e:
        logger.error(f"Erro na Conexão em relatorio_conn(): {e}", exc_info=True)
        raise

#In[5]:
#FUNÇÃO DE SELECT DO BD POR ANO
def relatorio_select_ano(engine,tabela, flt_ano):
    try:
        with engine.connect() as conn:
            query = (
                select(tabela)
                .where( tabela.c.ano == flt_ano)
            )
        
            resultado = conn.execute(query)

            df = pd.DataFrame(resultado.fetchall(), columns=resultado.keys())
        
        logger.info(f"PASSO 1.2.1.1: Sucesso para a execução do Dataframe de {flt_ano}.")
        logger.info(f"Total de Linhas: {len(df)}")

        return df
    
    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)
        raise

#FUNÇÃO DE SELECT DO BD POR MUNICIPIO E ANO
def relatorio_select_muni(engine,tabela, flt_ano, flt_municipio):
    try:
        with engine.connect() as conn:
            query = (
                select(tabela)
                .where(tabela.c.municipio == flt_municipio, tabela.c.ano == flt_ano)
            )
        
            resultado = conn.execute(query)

            df = pd.DataFrame(resultado.fetchall(), columns=resultado.keys())
        
        logger.info(f"PASSO 1.2.2.1: Sucesso para a execução do Dataframe de {flt_municipio} - {flt_ano}.")
        logger.info(f"Total de Linhas: {len(df)}")

        return df
    
    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)
        raise

#FUNÇÃO DE SELECT DO BD POR PAIS E ANO
def relatorio_select_pais(engine,tabela, flt_ano, flt_pais):
    try:
        with engine.connect() as conn:
            query = (
                select(tabela)
                .where(tabela.c.pais == flt_pais, tabela.c.ano == flt_ano)
            )
        
            resultado = conn.execute(query)

            df = pd.DataFrame(resultado.fetchall(), columns=resultado.keys())
        
        logger.info(f"PASSO 1.2.3.1: Sucesso para a execução do Dataframe de {flt_pais} - {flt_ano}.")
        logger.info(f"Total de Linhas: {len(df)}")

        return df
    
    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)
        raise

#FUNÇÃO DE SELECT DO BD POR PRODUTO E ANO
def relatorio_select_produto(engine,tabela, flt_ano, flt_produto):
    try:
        with engine.connect() as conn:
            query = (
                select(tabela)
                .where(tabela.c.produto == flt_produto, tabela.c.ano == flt_ano)
            )
        
            resultado = conn.execute(query)

            df = pd.DataFrame(resultado.fetchall(), columns=resultado.keys())
        
        logger.info(f"PASSO 1.2.4.1: Sucesso para a execução do Dataframe de {flt_produto} - {flt_ano}.")
        logger.info(f"Total de Linhas: {len(df)}")

        return df
    
    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)
        raise

#In[]:
def relatorio_select_balanca_comercial(engine,tabela,flt_ano):
    try:
            with engine.connect() as conn:
                ano_atual = datetime.today().year
                if ano_atual == flt_ano:
                  ano_comparacao = ano_atual - 1

                else:
                    ano_comparacao = ano_atual
                    
                query = (
                            select(tabela)
                            .where(
                                tabela.c.estado == "Rondônia",
                                tabela.c.ano.in_([flt_ano,ano_comparacao])
                            )
                        )
                resultado = conn.execute(query)
                df = pd.DataFrame(resultado.fetchall(), columns=resultado.keys())

            logger.info(f"PASSO 1.3.1.1: Sucesso para a execução do Dataframe de Balança Comercial {flt_ano} e {ano_comparacao}.")
            logger.info(f"Total de Linhas: {len(df)}")

            return df
    
    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)
        raise

#In[]:
def relatorio_df_etl(df):
        #REMOVENDO #U+00a0 (LINE BREAK)
        df = df.map(lambda x: x.replace('\xa0', ' ').strip() if isinstance(x, str) else x)

        return df

#In[6]:
#FUNÇÃO DE DF BD
def relatorio_salva_dataframe(tipo_aba,df,nome_arq):
    try:
        #CAMINHO DAS PASTAS
        pasta_atual = os.getcwd()
        pasta_arq = os.path.join(pasta_atual, "Arquivos")
        os.makedirs(pasta_arq, exist_ok=True)

        #NOME DO ARQUIVO
       
        arq_cam = os.path.join(pasta_arq,nome_arq)

        #SALVANDO DATAFRAME
        df.to_csv(arq_cam, index=False, sep=';', encoding="utf-8-sig")

    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)
        raise

#In[7]:
#FUNÇÃO main()
def main(tipo_aba, flt_ano, flt_sec):
    try:
        engine = None
        sucesso = False
        tempo_ini = time.perf_counter()

        logger.info("=="*32)
        logger.info("--- INÍCIO PROCESSO DE COLETA DO DATAFRAME ---")

        logger.info("PASSO 1.1: CONEXÃO COM O BANCO DE DADOS")
        engine= relatorio_conn()
        
        metadata = MetaData()
        tabela1 = Table(dados_lista[0], metadata, autoload_with=engine)
        tabela2 = Table(dados_lista[1], metadata, autoload_with=engine)

        logger.info("PASSO 1.2 - INICIANDO COLETA DE DADOS DO DATAFRAME PADRÃO")
        if tipo_aba == "apenas_ano":
            logger.info("PASSO 1.2.1: FAZENDO A QUERY DE DADOS")
            df = relatorio_select_ano(engine,tabela1, flt_ano)

        elif tipo_aba == "municipio_ano":
            logger.info("PASSO 1.2.2: FAZENDO A QUERY DE DADOS")
            df = relatorio_select_muni(engine,tabela1, flt_ano, flt_sec)

        elif tipo_aba == "pais_ano":
            logger.info("PASSO 1.2.3: FAZENDO A QUERY DE DADOS")
            df = relatorio_select_pais(engine,tabela1, flt_ano, flt_sec)

        elif tipo_aba == "produto_ano":
            logger.info("PASSO 1.2.4: FAZENDO A QUERY DE DADOS")
            df = relatorio_select_produto(engine,tabela1, flt_ano, flt_sec)        

        logger.info("PASSO 1.3 - INICIANDO COLETA DE DADOS DO DATAFRAME BALANÇA COMERCIAL")
        logger.info("PASSO 1.3.1: FAZENDO A QUERY DE DADOS")
        df_balanca = relatorio_select_balanca_comercial(engine,tabela2,flt_ano)

        logger.info("PASSO 1.4: ALTERANDO DATAFRAME")
        df_municipio = relatorio_df_etl(df)
        df_balanca = relatorio_df_etl(df_balanca)

        logger.info("PASSO 1.5: SALVANDO DATAFRAME")
        relatorio_salva_dataframe(tipo_aba,df_municipio,"teste01.csv")
        relatorio_salva_dataframe(tipo_aba,df_balanca,"teste02.csv")
        sucesso = True

        return {
            "df_municipio":df_municipio, 
            "df_balanca":df_balanca
        }

    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)      
        raise
    
    finally:
        if engine:
            logger.info("PASSO 1.6: DESCONEXÃO DA ENGINE")
            engine.dispose()

        tempo_fim = time.perf_counter()
        tempo_total = tempo_fim - tempo_ini

        if not sucesso:
            logger.info(f"PROCESSO CONCLUÍDO SEM ÊXITO - TEMPO TOTAL: {tempo_total:.4f}s.")
        
        else:        
            logger.info(f"PROCESSO CONCLUÍDO COM ÊXITO - TEMPO TOTAL: {tempo_total:.4f}s.")

        logger.info("--- FIM PROCESSO DE COLETA DO DATAFRAME ---")
        logger.info("=="*32)

#In[8]:
#EXECUTAR TESTES
if __name__ == "__main__":
#ano
    '''MUDAR AQUI'''
    #FILTRO
    tipo_aba= "apenas_ano"
    flt_ano= 2025
    flt_sec= None
    '''MUDAR AQUI'''
    main(tipo_aba, flt_ano, flt_sec)