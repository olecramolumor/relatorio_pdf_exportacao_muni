#In[1]:
#PYTHON
import logging
import time

#src
#import relatorio_csv #1
import relatorio_janela_main #2
import relatorio_dataframe #3
import relatorio_modelo #4
#import relatorio_janela_salvar #5

#In[2]:
'''ESCOPO GLOBAL'''
#CONFIG DO LOG
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#In[]:
def main():
    tempo_ini = time.perf_counter()

    #CRIAR >csv DE CONSULTA
    #FEITO NO CÓDIGO DO relatorio_Janela_Main()

    #ABRIR JANELA DE BUSCA
    
    pais, ano = relatorio_janela_main.main()

    #FAZER A BUSCA DE DADOS
    relatorio_dataframe.main(pais,ano)

    #CRIAR O MODELO EM .pdf
    #SALVAR O ARQUIVO
    arq_name = f"Relatório Exportação - {pais} - {ano}"
    relatorio_modelo.main(arq_name, pais,ano)

    tempo_fim = time.perf_counter()
    tempo_total = tempo_fim - tempo_ini
    logger.info(f"TEMPO DE EXECUÇÃO: {tempo_total:.4}s")


#In[]:
if __name__ == "__main__":
    main()