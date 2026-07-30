#In[1]:
import os
import logging
import textwrap
import pandas as pd
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, NextPageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.utils import ImageReader

import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from functools import partial

from PIL import Image
from io import BytesIO

#src
import relatorio_janela_main
import relatorio_grafico as gfs
import relatorio_dataframe

#In[2]:
'''ESCOPO GLOBAL'''
#CONFIG DO LOG
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#In[]:
#FORMATAR PARA NÚMERO BR
def formatar_br(numero):
    return f'{numero:,.2f}'.replace(',','X').replace('.',',').replace('X','.')

#FORMATAR QUANTIDADE DE PRODUTOS DO COMEX
def formatar_produtos(texto, max_char=50, largura_quebra=30):
    texto = str(texto).strip()
    if len(texto) > max_char:
        texto = texto[: max_char - 3] + "..."

    return "\n".join(textwrap.wrap(texto, width=largura_quebra))

#FORMATAR IMAGEM
def carregar_imagem_recortada(caminho, margem_px=4):
    """
    Abre a imagem, remove as margens transparentes/vazias ao redor do
    conteúdo real e retorna um ImageReader pronto para uso no canvas.
    margem_px: pequena margem de respiro a manter ao redor do conteúdo.
    """
    img = Image.open(caminho).convert("RGBA")
    bbox = img.getbbox()  # bounding box do conteúdo não-transparente

    if bbox:
        esquerda, topo, direita, base = bbox
        # aplica uma margem de segurança sem estourar os limites da imagem
        esquerda = max(esquerda - margem_px, 0)
        topo = max(topo - margem_px, 0)
        direita = min(direita + margem_px, img.width)
        base = min(base + margem_px, img.height)
        img = img.crop((esquerda, topo, direita, base))

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return ImageReader(buffer)

#In[4]:
def dataframe_exportacao(df):
    try:
        return df[df['fluxo'].str.lower() == 'exportação']
    except Exception as e:
        logger.error(f"ERRO EM dataframe_exportacao(): {e}")
        return pd.DataFrame()

def dataframe_importacao(df):
    try:
        return df[df['fluxo'].str.lower() == 'importação']
    except Exception as e:
        logger.error(f"ERRO EM dataframe_importacao(): {e}")
        return pd.DataFrame()

#In[5]
def desenhar_cabecalho_rodape(ano,canvas,doc, exibir_imagens=True, caminhos_imagens=None):
    canvas.saveState()

    #Tamanho da Página
    largura, altura = canvas._pagesize

    '''CABEÇALHO'''
    #CORES
    cor_fundo_cabecalho = colors.HexColor("#0c3470")  # Azul escuro para o background
    cor_texto_cabecalho = colors.HexColor("#FFFFFF")  # Texto em Branco para contrastar

    #DESENHAR RETÃNGULO - TAMANHO
    altura_faixa = 40
    y_faixa = altura - 75
    largura_faixa = largura - 108

    #DESENHAR RETÃNGULO - CORES E RETANGULO
    canvas.setFillColor(cor_fundo_cabecalho)
    canvas.rect(54, y_faixa, largura_faixa, altura_faixa, stroke=0, fill=1)

    #TÍTULO DO RELATÓRIO:
    texto_relatorio = f"Relatório de Comércio Exterior: {ano}"
    canvas.setFont('Helvetica-Bold',14)
    canvas.setFillColor(cor_texto_cabecalho)
    canvas.drawString(64, altura - 59, texto_relatorio)

    #IMAGENS DO CABEÇALHO (LADO DIREITO)
    if exibir_imagens and caminhos_imagens:
        margem_lateral = 10
        espaco_entre_imagens = 8
        padding_vertical = 8
        altura_maxima_imagem = altura_faixa - (padding_vertical * 2)
        y_imagem = y_faixa + padding_vertical

        # posição inicial: borda direita da faixa azul, menos a margem
        x_atual = 54 + largura_faixa - margem_lateral
        # espaço reservado para o título (evita sobreposição)
        largura_reservada_titulo = canvas.stringWidth(texto_relatorio, 'Helvetica-Bold', 14) + 20

        x_atual = 54 + largura_faixa - margem_lateral
        limite_esquerdo = 64 + largura_reservada_titulo

        for caminho in reversed(caminhos_imagens):
            try:
                img = gfs.carregar_imagem_recortada(caminho)
                largura_original, altura_original = img.getSize()
                escala = altura_maxima_imagem / altura_original
                largura_imagem = largura_original * escala

                # se não couber, reduz a imagem para caber no espaço restante
                if x_atual - largura_imagem < limite_esquerdo:
                    largura_imagem = max(x_atual - limite_esquerdo, 0)
                    if largura_imagem <= 0:
                        continue  # sem espaço, pula a imagem
                    altura_desenho = largura_imagem * (altura_original / largura_original)
                else:
                    altura_desenho = altura_maxima_imagem

                x_atual -= largura_imagem
                canvas.drawImage(
                    img,
                    x_atual,
                    y_faixa + (altura_faixa - altura_desenho) / 2,  # centraliza verticalmente
                    width=largura_imagem,
                    height=altura_desenho,
                    mask='auto',
                    preserveAspectRatio=True
                )
                x_atual -= espaco_entre_imagens
            except Exception as e:
                print(f"Aviso: não foi possível carregar a imagem '{caminho}': {e}")

    '''RODAPÉ'''
    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.setLineWidth(1)
    canvas.line(54, 65, largura - 54, 65)
   
    centro_x = largura / 2
    
    #FONTE
    canvas.setFont('Helvetica-Oblique', 8)
    canvas.setFillColor(colors.HexColor("#1A365D"))
    canvas.drawCentredString(centro_x, 50, "Fonte dos dados:")

    #TEXTO DA FONTE    
    texto_linha01 = "Comex Stat"
    url01 = "https://comexstat.mdic.gov.br/pt/home"

    texto_linha02 = "Geointeligência de Dados Econômicos do Estado de Rondônia"
    url02 = "https://geo.sedec.ro.gov.br/?page=Com%C3%A9rcio-Exterior&views=Com%C3%A9rcio-Exterior---Munic%C3%ADpio"

    #FONTE 01
    canvas.drawCentredString(centro_x, 38, texto_linha01 )    
    largura_texto1 = canvas.stringWidth(texto_linha01, 'Helvetica-Oblique', 8)
    canvas.linkURL(
        url=url01, 
        rect=(centro_x - (largura_texto1/2), 35, centro_x + (largura_texto1/2), 46), 
        thickness=0  # Mantém o retângulo do link invisível
    )

    #FONTE 02    
    canvas.drawCentredString(centro_x, 26, texto_linha02)
    largura_texto2 = canvas.stringWidth(texto_linha02, 'Helvetica-Oblique', 8)
    canvas.linkURL(
        url=url02, 
        rect=(centro_x - (largura_texto2/2), 23, centro_x + (largura_texto2/2), 34), 
        thickness=0
    )
    
    #NUMERAÇÃO DA PÁGINA
    canvas.setFont("Helvetica",9)
    canvas.drawRightString(largura-54, 45, f"Página {canvas._pageNumber}")
    canvas.restoreState()
    
#In[]:
def construir_secao_fluxo(story, df_fluxo, tipo_fluxo, styles):
    if df_fluxo.empty:
        story.append(Paragraph(f"Sem dados disponíveis para {tipo_fluxo}", styles['TituloTopico']))
        story.append(PageBreak())
        return
    
    estilo_celula = ParagraphStyle('Cel', parent=styles['Normal'], fontSize=8, leading=10, alignment=TA_CENTER)
    estilo_header = ParagraphStyle('Head', parent=styles['Normal'], fontSize=9, leading=11, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)

    """ ----- PÁGINA 1 ----- """
    story.append(Paragraph(f"Análise de {tipo_fluxo} - Visão Geral",styles['TituloTopico']))

    #TABELAS DE VALOR
    dados_totais = gfs.montar_tabela_totais(df_fluxo, estilo_celula,estilo_header)
    
    #TABELAS POR MÊS
    gfs.montar_tabela_mes(story, dados_totais, df_fluxo, tipo_fluxo, estilo_header, estilo_celula)

    """ ----- PÁGINA 2 ----- """
    story.append(Paragraph(f"Análise de {tipo_fluxo} - Top 10 Países", styles['TituloTopico']))
    df_prod = df_fluxo.groupby('pais', as_index=False)['valor_fob'].sum().sort_values('valor_fob', ascending=False).head(10)
    img_prod = gfs.gerar_grafico_barras(df_prod, 'pais', 'valor_fob', f"Top 10 Países por Valor FOB - {tipo_fluxo}")
    story.append(img_prod)
    story.append(PageBreak())
    
    """ ----- PÁGINA 3 ----- """
    story.append(Paragraph(f"Análise de {tipo_fluxo} - Top 10 Produtos", styles['TituloTopico']))
    df_prod = df_fluxo.groupby('produto', as_index=False)['valor_fob'].sum().sort_values('valor_fob', ascending=False).head(10)
    img_prod = gfs.gerar_grafico_barras(df_prod, 'produto', 'valor_fob', f"Top 10 Produtos por Valor FOB - {tipo_fluxo}")
    story.append(img_prod)
    story.append(PageBreak())

    """ ----- PÁGINA 4 ----- """
    story.append(Paragraph(f"Análise de {tipo_fluxo} - Top 10 Municípios", styles['TituloTopico']))
    df_mun = df_fluxo.groupby('municipio', as_index=False)['valor_fob'].sum().sort_values('valor_fob', ascending=False).head(10)
    img_mun = gfs.gerar_grafico_barras(df_mun, 'municipio', 'valor_fob', f"Top 10 Municípios por Valor FOB - {tipo_fluxo}")
    story.append(img_mun)
    story.append(NextPageTemplate("Retrato"))
    story.append(PageBreak())

#In[5]:
def gerar_relatorio(nome_arquivo, df_exp, df_imp, ano,logo):
    try:
        caminho_arquivo = relatorio_janela_main.janela_salvar(nome_arquivo)

        if not caminho_arquivo:
            logger.info("Geração de PDF cancelada pelo usuário.")
            return

        margem_esq, margem_dir = 54,54
        margem_topo, margem_base = 98,80

        tam_retrato = A4
        tam_paisagem = landscape(A4)

        frame_retrato = Frame (
            margem_esq, margem_base,
            tam_retrato[0] - margem_esq - margem_dir,
            tam_retrato[1] - margem_topo - margem_base,
            id='frame_retrato'
        )

        frame_paisagem = Frame (
            margem_esq, margem_base,
            tam_paisagem[0] - margem_esq - margem_dir,
            tam_paisagem[1] - margem_topo - margem_base,
            id='frame_paisagem'
        )

        #CRIANDO CAMINHO PARA IMAGENS   
        pasta_atual = os.getcwd()
        pasta_aux = os.path.join(pasta_atual,"Auxiliar")
        arq_cam = []
        imagens = [
            "05.png",
            "04.png",
        ]

        for img in imagens:
            arq_name = os.path.join(pasta_aux,img)
            arq_cam.append(arq_name)
        cabecalho_e_rodape_dados = partial(desenhar_cabecalho_rodape, ano, exibir_imagens=logo, caminhos_imagens=arq_cam)

        doc = BaseDocTemplate(
            caminho_arquivo,
            pagesize=tam_retrato,
        )

        doc.addPageTemplates([
            PageTemplate(id='Retrato', frames=[frame_retrato], pagesize=tam_retrato, onPage=cabecalho_e_rodape_dados),
            PageTemplate(id='Paisagem', frames=[frame_paisagem], pagesize=tam_paisagem, onPage=cabecalho_e_rodape_dados),
        ])

        styles = getSampleStyleSheet()     

        '''CUSTOMIZAÇÃO DE ESTILO PARA O CORPO'''
        #TITULO
        styles.add (ParagraphStyle(
            'TituloTopico',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#2B6CB0"),
            spaceAfter=12,
            alignment=TA_CENTER,
            keepWithNext=True
        ))

        #TEXTO DO CORPO
        styles.add (ParagraphStyle(
            'TextoCorpo',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=20,
            textColor=colors.HexColor("#000000"),
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            keepWithNext=True
        ))

        styles.add(ParagraphStyle(
        'TextoBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#000000"),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leftIndent=20,
        firstLineIndent=-10,
        bulletIndent=10,
        keepWithNext=False
        ))

        '''APRESENTAÇÃO DO TEXTO'''
        story = []
        story.append(Paragraph(f"Visão Geral dos dados de Comércio Exterior Municipal - Comex Stat Municipal", styles['TituloTopico']))
        story.append(Paragraph(
            "O Comex Stat Municipal é a ferramenta oficial do Governo Federal para a consulta de dados detalhados do comércio exterior brasileiro em nível municipal." \
            "A plataforma permite analisar com precisão o desempenho de exportações e importações de cada cidade, destacando:",
            styles['TextoCorpo']
            ))
        
        itens_lista01 = [
            "<b>Balança Comercial Local:</b> Saldo e volume de trocas comerciais da cidade;",
            "<b>Principais Produtos:</b> Os itens mais exportados e importados pelo município;", 
            "<b>Parceiros Internacionais:</b> Os países de destino e origem das mercadorias."
        ]

        for item in itens_lista01:
            story.append(Paragraph(f"<bullet>&bull;</bullet>{item}", styles['TextoBullet']))

        story.append(Paragraph(
            "Trata-se de uma fonte pública, gratuita e atualizada mensalmente, essencial para a inteligência de mercado, atração de investimentos e planejamento de políticas" \
            " públicas locais. O foco deste relatório concentra-se nas exportações do Estado de Rondônia e seus municípios.",
            styles['TextoCorpo']
        ))

        story.append(PageBreak())

        '''INTRODUÇÃO EXPORTAÇÃO'''
        story.append(Paragraph(f"Paronama Geral de Exportação - Rondônia", styles['TituloTopico']))
        story.append(Paragraph(
                    "Rondônia destaca-se como um dos principais motores do comércio exterior da Região Norte do Brasil." \
                    " Com uma economia baseada no agronegócio de alta eficiência e no aproveitamento sustentável de seus recursos," \
                    " o estado mantém uma balança comercial fortemente superavitária," \
                    " figurando como um fornecedor estratégico de alimentos e matérias-primas para o mercado global.",
                    styles['TextoCorpo']
                    ))

        story.append(Paragraph(f"Principais Mercados de Rondônia", styles['TituloTopico']))
        itens_lista02 = [
            "<b>Complexo Soja:</b> Principal item da pauta (grãos e farelo), impulsionado pela alta produtividade das lavouras do cone sul do estado.",
            "<b>Carne Bovina:</b> Destaque para os cortes congelados e desossados, sustentados pelo status sanitário do estado como área livre de febre aftosa sem vacinação.",
            "<b>Madeira e Derivados:</b> Produtos de alto valor agregado originários de manejo florestal sustentável e concessionárias locais.",
            "<b>Café (Coffea canephora/Robusta/ Robusta Amazônico):</b> Crescente inserção global dos cafés finos e sustentáveis da Amazônia.",
            "<b>Outros Destaques:</b> Cacau, peixes de água doce (como o tambaqui) e milho."
        ]

        for item in itens_lista02:
                    story.append(Paragraph(f"<bullet>&bull;</bullet>{item}", styles['TextoBullet']))

        story.append(PageBreak())

        '''SEÇÃO DE EXPORTAÇÃO'''        
        construir_secao_fluxo(story, df_exp, "Exportação", styles)

        '''INTRODUÇÃO IMPORTAÇÃO'''
        story.append(Paragraph(f"Paronama Geral de Importação - Rondônia", styles['TituloTopico']))
        story.append(Paragraph(
                    "Enquanto as exportações de Rondônia são impulsionadas pelo agronegócio," \
                    " o perfil das importações reflete diretamente a necessidade de suprir a cadeia produtiva local." \
                    " O estado importa prioritariamente insumos agrícolas, máquinas, equipamentos e combustíveis," \
                    " essenciais para sustentar o crescimento da produção do agro, a infraestrutura e o setor industrial rondoniense.",
                    styles['TextoCorpo']
                    ))

        story.append(Paragraph(f"Principais Mercados de Rondônia", styles['TituloTopico']))
        itens_lista02 = [
            "<b>Adubos e Fertilizantes:</b> rincipal item da pauta de importação (compostos nitrogenados, fosfatados e potássicos), cruciais para a nutrição do solo e o alto rendimento das safras de soja e milho.",
            "<b>Máquinas e Equipamentos Agrícolas:</b> Tratores, colheitadeiras e peças de reposição para modernização do parque fabril e do campo.",
            "<b>Combustíveis e Óleos Minerais:</b> Insumos para abastecimento da frota logística e operações de transporte regional.",
            "<b>Produtos Químicos e Defensivos:</b> Defensivos agrícolas e insumos para a indústria de transformação.",
            "<b>Bens de Consumo e Eletroeletrônicos:</b> Itens diversos para abastecimento do comércio varejista local."
        ]

        for item in itens_lista02:
                    story.append(Paragraph(f"<bullet>&bull;</bullet>{item}", styles['TextoBullet']))

        story.append(PageBreak())

        '''SEÇÃO DE IMPORTAÇÃO'''
        construir_secao_fluxo(story, df_imp, "Importação", styles)

        if story and isinstance(story[-1], PageBreak):
            story.pop()

        '''COMPILAÇÃO'''
        doc.build(story)
        logger.info(f"Relatório gerado com sucesso em: {caminho_arquivo}")
    
    except Exception as e:
        logger.info(f"ERRO NA GERAÇÃO DO .pdf: {e}",exc_info=True)
        

#In[]:
def main(tipo_aba,nome_arquivo, ano,logo):
    try:
        pais=None
        df=relatorio_dataframe.main(tipo_aba,ano,pais)
        df_exp = dataframe_exportacao(df)
        df_imp = dataframe_importacao(df)
        gerar_relatorio(nome_arquivo, df_exp, df_imp, ano,logo)

    except Exception as e:
         logger.error(f"Erro: {e}",exc_info=True)
         raise

#In[6]:
if __name__ == "__main__":
    logos = True,False
    for logo in logos:
        ano = 2025
        nome_arquivo = f"Teste XX - ano - {logo}"
        tipo_aba = "apenas_ano"
        main(tipo_aba,nome_arquivo, ano,logo)