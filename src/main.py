#In[1]:
#PYTHON
import os
import logging
import time
from datetime import datetime

#src
import relatorio_modelo
import relatorio_janela_main #2
import modelo_antingo.relatorio_modelo_ano as relatorio_modelo_ano #4
import modelo_antingo.relatorio_modelo_municipio as relatorio_modelo_municipio #4
import modelo_antingo.relatorio_modelo_pais as relatorio_modelo_pais #4

#In[]:
logger = logging.getLogger(__name__)

#In[]:
def setup_master_logging(nome_sistema):
    #DATA DE EXECUÇÃO DO SCRIPT
    data_exec = datetime.today()
    data_format = data_exec.strftime('%d_%m_%Y') 

    #PASTA DE LOG
    pasta_atual = os.getcwd() 
    pasta_log = os.path.join(pasta_atual,'Logs')
    os.makedirs(pasta_log, exist_ok=True)

    #ARQUIVO DE LOG    
    arq_log = os.path.join(pasta_log,f"{data_format}_{nome_sistema}_processo_completo.log")

    #FORMATO LOG
    log_format = '%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format= log_format,
        handlers= [
            logging.FileHandler(arq_log, mode = 'a', encoding='utf-8'),
            logging.StreamHandler()
            ],
        force=True
    )

    return arq_log

#In[]:
def main():
    try:
        sucesso = False
        tempo_ini = time.perf_counter()
        nome_sistema = "relatorio_comex_stat"
        setup_master_logging(nome_sistema)

        #CRIAR >csv DE CONSULTA
        #FEITO NO CÓDIGO DO relatorio_Janela_Main()
        #ABRIR JANELA DE BUSCA COOLETAR OS DADOS
        req = relatorio_janela_main.main()
        logger.info(type(req))
        logger.info(req)

        #CASO NÃO TENHA DADOS
        if req is None:
            logger.info("OPERAÇÃO CANCELADA")
            return
        
        #FAZER A BUSCA DE DADOS
        #CRIAR O MODELO EM .pdf
        #SALVAR O ARQUIVO
        relatorio_modelo.main(**req.parametros())
        sucesso = True

    except Exception as e:
        logger.exception(f"Erro durante a execução {e}.",exc_info=True)
        raise

    finally:
        if sucesso:
            logger.info("Programa Executado Com Sucesso!")

        else:
            logger.info("Programa encerrado devido a Erro de Execução")
            
        tempo_fim = time.perf_counter()
        tempo_total = tempo_fim - tempo_ini
        logger.info(f"TEMPO DE EXECUÇÃO: {tempo_total:.4}s")

#In[]:
if __name__ == "__main__":
    main()