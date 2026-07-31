#In[1]:
#PYTHON
import logging
import time

#src
import relatorio_janela_main #2
import relatorio_modelo_ano #4
import relatorio_modelo_pais #4

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
    tipo_aba,pais, municipio,produto, ano,logo = relatorio_janela_main.main()

    #FAZER A BUSCA DE DADOS
    #CRIAR O MODELO EM .pdf
    #SALVAR O ARQUIVO
    if tipo_aba == "apenas_ano":
        '''PRECISA FAZER O MODELO'''
        logger.info(f"PASSO 1.2: Gerando Relatório Comercial Rondônia - {ano}")
        arq_name = f"Relatório Exportação - Rondônia - {ano}"
        relatorio_modelo_ano.main(tipo_aba,arq_name, ano,logo)

    elif tipo_aba == "municipio_ano":
        '''PRECISA FAZER O MODELO'''
        logger.info(f"PASSO 1.2: Gerando Relatório Comercial {municipio} - {ano}")
        arq_name = f"Relatório Exportação - {municipio} - {ano}"
        #relatorio_modelo_muni.main(tipo_aba,arq_name, ano,municipio,logo)
        
    elif tipo_aba == "pais_ano":
        logger.info(f"PASSO 1.2: Gerando Relatório Comercial {pais} - {ano}")
        arq_name = f"Relatório Exportação - {pais} - {ano}"
        relatorio_modelo_pais.main(tipo_aba,arq_name, ano,pais,logo)

    elif tipo_aba == "produto_ano":
        '''PRECISA FAZER O MODELO'''
        logger.info(f"PASSO 1.2: Gerando Relatório Comercial {produto} - {ano}")
        arq_name = f"Relatório Exportação - {produto} - {ano}"
        relatorio_modelo_pais.main(tipo_aba,arq_name, ano,produto,logo)
        
    tempo_fim = time.perf_counter()
    tempo_total = tempo_fim - tempo_ini
    logger.info(f"TEMPO DE EXECUÇÃO: {tempo_total:.4}s")

#In[]:
if __name__ == "__main__":
    main()