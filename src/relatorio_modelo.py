#In[1]:
import os
import time
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
from reportlab.pdfbase.pdfmetrics import stringWidth

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

dataframes = relatorio_dataframe.main()
df_municipio = dataframes[0]
df_balanca = dataframes[1]

#In[3]:
'''
CONFIGURAÇÃO DOS "MODOS" DE RELATÓRIO
--------------------------------------
Cada modo representa um dos scripts originais (pais / municipio / produto / ano).
Para adicionar um novo tipo de relatório no futuro, basta acrescentar uma nova
entrada neste dicionário -- não é necessário duplicar nenhuma função abaixo.

    requer_valor       -> se o modo precisa de um valor de recorte (ex.: "China"),
                           ou se é um relatório "geral" (como o de ano, sem recorte)
    extra_breakdowns   -> lista de colunas (na ordem) que geram as páginas de
                           "Top 10 ..." dentro de construir_secao_fluxo()
    tipo_aba           -> string repassada para relatorio_dataframe.main()
    comparacao         -> se True, adiciona o bloco extra de comparação
                           2025 x 2026 ao final do relatório (hoje só o modo "ano")
'''
MODOS = {
    "pais": {
        "requer_valor": True,
        "extra_breakdowns": ["produto", "municipio"],
        "tipo_aba": "pais_ano",
        "comparacao": False,
    },
    "municipio": {
        "requer_valor": True,
        "extra_breakdowns": ["produto", "pais"],
        "tipo_aba": "municipio_ano",  # confirme se é este o valor esperado por relatorio_dataframe.py
        "comparacao": False,
    },
    "produto": {
        "requer_valor": True,
        "extra_breakdowns": ["produto", "municipio"],
        "tipo_aba": "produto_ano",
        "comparacao": False,
    },
    "ano": {
        "requer_valor": False,
        "extra_breakdowns": ["pais", "produto", "municipio"],
        "tipo_aba": "apenas_ano",
        "comparacao": True,
    },
}

#RÓTULO NO PLURAL PARA O TÍTULO DE CADA PÁGINA "TOP 10 ..."
LABELS_PLURAL = {
    "pais": "Países",
    "produto": "Produtos",
    "municipio": "Municípios",
}

#In[]:
#FORMATAR PARA NÚMERO BR
def formatar_br(numero):
    return f'{numero:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

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
def desenhar_cabecalho_rodape(valor_recorte, ano, canvas, doc, exibir_imagens=True, caminhos_imagens=None):
    """
    valor_recorte: o país / município / produto do relatório.
    Quando None (caso do relatório "apenas ano"), usa "Rondônia" no título,
    igual ao comportamento original de relatorio_modelo_ano.py.
    """
    canvas.saveState()

    titulo_local = valor_recorte if valor_recorte else "Rondônia"

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
    texto_relatorio = f"Relatório de Comércio Exterior: {titulo_local} - {ano}"
    fonte = "Helvetica-Bold"
    tamanho = 14

    # Limite esquerdo das imagens
    margem_lateral = 10
    espaco_entre_imagens = 8

    # Reserva um espaço fixo para as duas imagens (ajuste conforme necessário)
    largura_reservada_imagens = 120
    largura_disponivel = largura_faixa - largura_reservada_imagens - 20

    # Função para quebrar o texto
    def quebrar_texto(texto, fonte, tamanho, largura_max):
        palavras = texto.split()
        linhas = []
        linha = ""

        for palavra in palavras:
            teste = palavra if linha == "" else f"{linha} {palavra}"

            if stringWidth(teste, fonte, tamanho) <= largura_max:
                linha = teste
            else:
                linhas.append(linha)
                linha = palavra

        if linha:
            linhas.append(linha)

        return linhas

    linhas = quebrar_texto(
        texto_relatorio,
        fonte,
        tamanho,
        largura_disponivel
    )

    texto = canvas.beginText()
    texto.setFont(fonte, tamanho)
    texto.setFillColor(cor_texto_cabecalho)

    # Se houver duas linhas, sobe um pouco a primeira
    y_texto = altura - 59
    if len(linhas) > 1:
        y_texto += 7

    texto.setTextOrigin(64, y_texto)

    for linha in linhas[:2]:   # no máximo duas linhas
        texto.textLine(linha)

    canvas.drawText(texto)

    #IMAGENS DO CABEÇALHO (LADO DIREITO)
    if exibir_imagens and caminhos_imagens:
        margem_lateral = 10
        espaco_entre_imagens = 8
        padding_vertical = 8
        altura_maxima_imagem = altura_faixa - (padding_vertical * 2)
        y_imagem = y_faixa + padding_vertical

        # posição inicial: borda direita da faixa azul, menos a margem
        x_atual = 54 + largura_faixa - margem_lateral

        for caminho in reversed(caminhos_imagens):
            img = carregar_imagem_recortada(caminho)

            largura_original, altura_original = img.getSize()
            escala = altura_maxima_imagem / altura_original
            largura_imagem = largura_original * escala

            x_atual -= largura_imagem

            canvas.drawImage(
                img,
                x_atual,
                y_faixa + (altura_faixa - altura_maxima_imagem) / 2,
                width=largura_imagem,
                height=altura_maxima_imagem,
                preserveAspectRatio=True,
                mask="auto"
            )

            x_atual -= espaco_entre_imagens

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
    canvas.drawCentredString(centro_x, 38, texto_linha01)
    largura_texto1 = canvas.stringWidth(texto_linha01, 'Helvetica-Oblique', 8)
    canvas.linkURL(
        url=url01,
        rect=(centro_x - (largura_texto1 / 2), 35, centro_x + (largura_texto1 / 2), 46),
        thickness=0  # Mantém o retângulo do link invisível
    )

    #FONTE 02
    canvas.drawCentredString(centro_x, 26, texto_linha02)
    largura_texto2 = canvas.stringWidth(texto_linha02, 'Helvetica-Oblique', 8)
    canvas.linkURL(
        url=url02,
        rect=(centro_x - (largura_texto2 / 2), 23, centro_x + (largura_texto2 / 2), 34),
        thickness=0
    )

    #NUMERAÇÃO DA PÁGINA
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(largura - 54, 45, f"Página {canvas._pageNumber}")
    canvas.restoreState()

#In[]:
def construir_secao_fluxo(story, df_fluxo, tipo_fluxo, styles, extra_breakdowns):
    """
    extra_breakdowns: lista de colunas (ex.: ["produto", "municipio"]) que
    definem, na ordem, quais páginas de "Top 10 ..." serão geradas após a
    página de visão geral -- substitui as versões fixas que existiam em
    cada script separado.
    """
    if df_fluxo.empty:
        story.append(Paragraph(f"Sem dados disponíveis para {tipo_fluxo}", styles['TituloTopico']))
        story.append(PageBreak())
        return

    estilo_celula = ParagraphStyle('Cel', parent=styles['Normal'], fontSize=8, leading=10, alignment=TA_CENTER)
    estilo_header = ParagraphStyle('Head', parent=styles['Normal'], fontSize=9, leading=11, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)

    """ ----- PÁGINA 1: VISÃO GERAL ----- """
    story.append(Paragraph(f"Análise de {tipo_fluxo} - Visão Geral", styles['TituloTopico']))

    #TABELAS DE VALOR
    dados_totais = gfs.montar_tabela_totais(df_fluxo, estilo_celula, estilo_header)

    #TABELAS POR MÊS
    gfs.montar_tabela_mes(story, dados_totais, df_fluxo, tipo_fluxo, estilo_header, estilo_celula)

    """ ----- PÁGINAS SEGUINTES: TOP 10 POR COLUNA ----- """
    total = len(extra_breakdowns)
    for i, coluna in enumerate(extra_breakdowns):
        rotulo_plural = LABELS_PLURAL.get(coluna, coluna.capitalize())
        story.append(Paragraph(f"Análise de {tipo_fluxo} - Top 10 {rotulo_plural}", styles['TituloTopico']))

        df_top = df_fluxo.groupby(coluna, as_index=False)['valor_fob'].sum().sort_values('valor_fob', ascending=False).head(10)
        img_top = gfs.gerar_grafico_barras(df_top, coluna, 'valor_fob', f"Top 10 {rotulo_plural} por Valor FOB - {tipo_fluxo}")
        story.append(img_top)

        eh_ultima = (i == total - 1)
        if eh_ultima:
            story.append(NextPageTemplate("Retrato"))
        story.append(PageBreak())

#In[]:
def montar_bloco_comparacao(story, styles,df, flt_ano):
    try:
        estilo_celula = ParagraphStyle('Cel', parent=styles['Normal'], fontSize=8, leading=10, alignment=TA_CENTER)
        estilo_header = ParagraphStyle('Head', parent=styles['Normal'], fontSize=9, leading=11, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)

        ano_atual = datetime.today().year
        if ano_atual == flt_ano:
            ano_comparacao = ano_atual - 1
        else:
            ano_comparacao = flt_ano

        story.append(Paragraph(f"Comparação Valores Gerais de Exportação e Importação {ano_comparacao} X {ano_atual}", styles['TituloTopico']))
        gfs.montar_tabela_comparar_ano(story,df)

    except Exception as e:
            logger.info(f"ERRO NA GERAÇÃO DA COMPARAÇÃO: {e}", exc_info=True)
    

#In[5]:
def gerar_relatorio(nome_arquivo, df_exp, df_imp, modo, valor_recorte, ano, logo):
    try:
        config = MODOS[modo]

        caminho_arquivo = relatorio_janela_main.janela_salvar(nome_arquivo)

        if not caminho_arquivo:
            logger.info("Geração de PDF cancelada pelo usuário.")
            return

        margem_esq, margem_dir = 54, 54
        margem_topo, margem_base = 98, 80

        tam_retrato = A4
        tam_paisagem = landscape(A4)

        frame_retrato = Frame(
            margem_esq, margem_base,
            tam_retrato[0] - margem_esq - margem_dir,
            tam_retrato[1] - margem_topo - margem_base,
            id='frame_retrato'
        )

        frame_paisagem = Frame(
            margem_esq, margem_base,
            tam_paisagem[0] - margem_esq - margem_dir,
            tam_paisagem[1] - margem_topo - margem_base,
            id='frame_paisagem'
        )

        #CRIANDO CAMINHO PARA IMAGENS
        pasta_atual = os.getcwd()
        pasta_aux = os.path.join(pasta_atual, "Auxiliar")
        arq_cam = []
        imagens = [
            "05.png",
            "04.png",
        ]

        for img in imagens:
            arq_name = os.path.join(pasta_aux, img)
            arq_cam.append(arq_name)
        cabecalho_e_rodape_dados = partial(desenhar_cabecalho_rodape, valor_recorte, ano, exibir_imagens=logo, caminhos_imagens=arq_cam)

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
        styles.add(ParagraphStyle(
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
        styles.add(ParagraphStyle(
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
        story.append(Paragraph("Visão Geral dos dados de Comércio Exterior Municipal - Comex Stat Municipal", styles['TituloTopico']))
        story.append(Paragraph(
            "O Comex Stat Municipal é a ferramenta oficial do Governo Federal para a consulta de dados detalhados do comércio exterior brasileiro em nível municipal."
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
            "Trata-se de uma fonte pública, gratuita e atualizada mensalmente, essencial para a inteligência de mercado, atração de investimentos e planejamento de políticas"
            " públicas locais. O foco deste relatório concentra-se nas exportações do Estado de Rondônia e seus municípios.",
            styles['TextoCorpo']
        ))

        story.append(PageBreak())

        '''INTRODUÇÃO EXPORTAÇÃO'''
        story.append(Paragraph("Paronama Geral de Exportação - Rondônia", styles['TituloTopico']))
        story.append(Paragraph(
            "Rondônia destaca-se como um dos principais motores do comércio exterior da Região Norte do Brasil."
            " Com uma economia baseada no agronegócio de alta eficiência e no aproveitamento sustentável de seus recursos,"
            " o estado mantém uma balança comercial fortemente superavitária,"
            " figurando como um fornecedor estratégico de alimentos e matérias-primas para o mercado global.",
            styles['TextoCorpo']
        ))

        story.append(Paragraph("Principais Mercados de Rondônia", styles['TituloTopico']))
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
        construir_secao_fluxo(story, df_exp, "Exportação", styles, config["extra_breakdowns"])

        '''INTRODUÇÃO IMPORTAÇÃO'''
        story.append(Paragraph("Paronama Geral de Importação - Rondônia", styles['TituloTopico']))
        story.append(Paragraph(
            "Enquanto as exportações de Rondônia são impulsionadas pelo agronegócio,"
            " o perfil das importações reflete diretamente a necessidade de suprir a cadeia produtiva local."
            " O estado importa prioritariamente insumos agrícolas, máquinas, equipamentos e combustíveis,"
            " essenciais para sustentar o crescimento da produção do agro, a infraestrutura e o setor industrial rondoniense.",
            styles['TextoCorpo']
        ))

        story.append(Paragraph("Principais Mercados de Rondônia", styles['TituloTopico']))
        itens_lista03 = [
            "<b>Adubos e Fertilizantes:</b> rincipal item da pauta de importação (compostos nitrogenados, fosfatados e potássicos), cruciais para a nutrição do solo e o alto rendimento das safras de soja e milho.",
            "<b>Máquinas e Equipamentos Agrícolas:</b> Tratores, colheitadeiras e peças de reposição para modernização do parque fabril e do campo.",
            "<b>Combustíveis e Óleos Minerais:</b> Insumos para abastecimento da frota logística e operações de transporte regional.",
            "<b>Produtos Químicos e Defensivos:</b> Defensivos agrícolas e insumos para a indústria de transformação.",
            "<b>Bens de Consumo e Eletroeletrônicos:</b> Itens diversos para abastecimento do comércio varejista local."
        ]

        for item in itens_lista03:
            story.append(Paragraph(f"<bullet>&bull;</bullet>{item}", styles['TextoBullet']))

        story.append(PageBreak())

        '''SEÇÃO DE IMPORTAÇÃO'''
        construir_secao_fluxo(story, df_imp, "Importação", styles, config["extra_breakdowns"])

        '''BLOCO EXTRA (SOMENTE MODO "ano")'''
        if config.get("comparacao"):
            montar_bloco_comparacao(story, styles)

        montar_bloco_comparacao(story, styles,df_balanca, ano)

        if story and isinstance(story[-1], PageBreak):
            story.pop()

        '''COMPILAÇÃO'''
        doc.build(story)
        logger.info(f"Relatório gerado com sucesso em: {caminho_arquivo}")

    except Exception as e:
        logger.info(f"ERRO NA GERAÇÃO DO .pdf: {e}", exc_info=True)

#In[]:
def main(modo, nome_arquivo, ano, valor_recorte=None, logo=True):
    """
    modo: uma das chaves de MODOS -> "pais", "municipio", "produto" ou "ano"
    valor_recorte: obrigatório para os modos "pais"/"municipio"/"produto"
                   (ex.: "China", "Porto Velho", "Soja"); ignorado/None no modo "ano"
    """
    if modo not in MODOS:
        raise ValueError(f"Modo de relatório desconhecido: '{modo}'. Opções válidas: {list(MODOS)}")

    config = MODOS[modo]

    if config["requer_valor"] and not valor_recorte:
        raise ValueError(f"O modo '{modo}' exige um valor de recorte (ex.: país, município ou produto).")

    tempo_ini = time.perf_counter()
    sucesso = False
    try:
        tipo_aba = config["tipo_aba"]    
        df_exp = dataframe_exportacao(df_municipio)
        df_imp = dataframe_importacao(df_municipio)

        gerar_relatorio(nome_arquivo, df_exp, df_imp, modo, valor_recorte, ano, logo)
        sucesso = True

    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        raise

    finally:
        if sucesso:
            logger.info("RELATÓRIO GERADO COM ÊXITO")

        tempo_fim = time.perf_counter()
        tempo_total = tempo_fim - tempo_ini
        logger.info(f"TEMPO DE EXECUÇÃO: {tempo_total:.4}s")

#In[6]:
if __name__ == "__main__":
    logos = True, False

    # ---- Exemplo: relatório por país ----
    ano = 2025
    pais = "Bonaire, Saint Eustatius e Saba"
    nome_arquivo = f"Teste XX - {pais} - {logos[1]}"
    main("pais", nome_arquivo, ano, valor_recorte=pais, logo=logos[1])

    # ---- Exemplo: relatório por município ----
    # muni = "Porto Velho"
    # nome_arquivo = f"Teste XX - {muni} - {logos[1]}"
    # main("municipio", nome_arquivo, ano, valor_recorte=muni, logo=logos[1])

    # ---- Exemplo: relatório por produto ----
    # produto = "Soja"
    # nome_arquivo = f"Teste XX - {produto} - {logos[1]}"
    # main("produto", nome_arquivo, ano, valor_recorte=produto, logo=logos[1])

    # ---- Exemplo: relatório apenas por ano (sem recorte) ----
    # nome_arquivo = f"Teste XX - ano - {logos[1]}"
    # main("ano", nome_arquivo, ano, logo=logos[1])
