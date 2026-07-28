#In[1]:
import os
import io
import logging
import textwrap
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, NextPageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from functools import partial

import relatorio_janela_main

#In[2]:
'''ESCOPO GLOBAL'''
#CONFIG DO LOG
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

meses = {
    1: 'Janeiro',
    2: 'Fevereiro',
    3: 'Março',
    4: 'Abril',
    5: 'Maio',
    6: 'Junho',
    7: 'Julho',
    8: 'Agosto',
    9: 'Setembro',
    10: 'Outubro',
    11: 'Novembro',
    12: 'Dezembro'
}

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

#In[3]:
#CRIAÇÃO DO DATAFRAME
def relatorio_dataframe():
    try:
        #CAMINHO DAS PASTAS
        pasta_atual = os.getcwd()
        pasta_arq = os.path.join(pasta_atual, "Arquivos")
        os.makedirs(pasta_arq, exist_ok=True)

        #NOME DO ARQUIVO
        hoje = datetime.today().strftime("%d_%m_%y")
        arq_nome = f"consulta.csv"
        arq_cam = os.path.join(pasta_arq,arq_nome)

        #CRIANDO  DATAFRAME
        df = pd.read_csv(arq_cam, sep=';', encoding='utf-8-sig')        

        return df
        
    except Exception as e:
        logger.error(f"Erro crítico: {e}", exc_info=True)
        raise

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
def desenhar_cabecalho_rodape(pais,ano,canvas,doc):
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

    texto_relatorio = f"Relatório de Comércio Exterior: {pais} - {ano}"
    canvas.setFont('Helvetica-Bold',14)
    canvas.setFillColor(cor_texto_cabecalho)
    canvas.drawString(64, altura - 59, texto_relatorio)

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
    texto_linha02 = "Geointeligência de Dados Econômicos do Estado de Rondônia"

    #FONTE 01
    canvas.drawCentredString(centro_x, 38, texto_linha01 )    
    largura_texto1 = canvas.stringWidth(texto_linha01, 'Helvetica-Oblique', 8)
    canvas.linkURL(
        url="https://geo.sedec.ro.gov.br/?page=Com%C3%A9rcio-Exterior&views=Com%C3%A9rcio-Exterior---Munic%C3%ADpio", 
        rect=(centro_x - (largura_texto1/2), 35, centro_x + (largura_texto1/2), 46), 
        thickness=0  # Mantém o retângulo do link invisível
    )

    #FONTE 02    
    canvas.drawCentredString(centro_x, 26, texto_linha02)
    largura_texto2 = canvas.stringWidth(texto_linha02, 'Helvetica-Oblique', 8)
    canvas.linkURL(
        url="https://comexstat.mdic.gov.br/pt/home", 
        rect=(centro_x - (largura_texto2/2), 23, centro_x + (largura_texto2/2), 34), 
        thickness=0
    )
    
    #NUMERAÇÃO DA PÁGINA
    canvas.setFont("Helvetica",9)
    canvas.drawRightString(largura-54, 45, f"Página {canvas._pageNumber}")
    canvas.restoreState()

'''função de tabelas de dados totais'''

#In[]:

'''
FUNÇÃO DE CRIAÇÃO DE TABELAS DA PAGINA COM DADOS DE QUANTIDADE DE VALOR FOB
VALOR EM KG E QUANTIDADE DE PRODUTOS
'''
def montar_tabela_totais(df_fluxo, estilo_celula, estilo_header):
    total_fob = formatar_br(df_fluxo['valor_fob'].sum())
    total_kg = formatar_br(df_fluxo['valor_kg'].sum())
    total_prod = int(df_fluxo['produto'].nunique())

    return [
        [Paragraph("Métrica", estilo_header), Paragraph("Valor Total", estilo_header)],
        [Paragraph("Valor FOB (US$)", estilo_celula), Paragraph(total_fob, estilo_celula)],
        [Paragraph("Peso Líquido (KG)", estilo_celula), Paragraph(total_kg, estilo_celula)],
        [Paragraph("Quantidade de Produtos", estilo_celula), Paragraph(str(total_prod), estilo_celula)]
    ]

def montar_tabela_mes(story, dados_totais, df_fluxo, tipo_fluxo, estilo_header, estilo_celula):
    #TABELAS DE VALOR POR MÊS
    t_totais = Table(dados_totais, colWidths=[150, 150])
    t_totais.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#2B6CB0")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_totais)
    story.append(Spacer(1, 15))

    df_mes = df_fluxo.groupby('ordem', as_index=False)[['valor_fob', 'valor_kg']].sum().sort_values('ordem')
    img_linha = gerar_grafico_linha(df_mes, f"Evolução Mensal do Valor FOB - {tipo_fluxo}")
    story.append(img_linha)
    story.append(Spacer(1, 10))

    dados_tabela = [[
        Paragraph("Mês", estilo_header),
        Paragraph("Valor FOB (US$)", estilo_header),
        Paragraph("Valor KG", estilo_header)
    ]]

    #MUDANDO NOME DO MÊS
    for _, row in df_mes.iterrows():
        num_mes = int(row['ordem'])
        nome_mes = meses.get(num_mes,num_mes)

        dados_tabela.append([
            Paragraph(str(nome_mes), estilo_celula),
            Paragraph(f"{formatar_br(row['valor_fob'])}", estilo_celula),
            Paragraph(f"{formatar_br(row['valor_kg'])}", estilo_celula)
        ])
    
    #CONFIGURAÇÕES DE TABELAS
    t_mensal = Table(dados_tabela, colWidths=[100, 180, 180])
    t_mensal.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_mensal)
    story.append(NextPageTemplate('Paisagem'))
    story.append(PageBreak())

#In[]
'''
ESSA FUNÇÃO TEM O OBJETIVO DE LER UMA IMAGEM
COM ISSO ELA LÊ UMA IMAGEM E RETORNA UM TAMANHO
PROPORCIONAL PARA O REPORT LABS
'''
def buffer_para_image(buf, largura_max, altura_max=340):
    buf.seek(0)
    largura_px, altura_px = PILImage.open(buf).size
    buf.seek(0)
    fator = largura_max / largura_px
    largura_final = largura_max
    altura_final = altura_px * fator

    # Se a altura ultrapassar a altura máxima permitida no frame, redimensiona pela altura
    if altura_final > altura_max:
        fator = altura_max / altura_px
        altura_final = altura_max
        largura_final = largura_px * fator
    return Image(buf, width=largura_final, height=altura_final)
#In[]

def gerar_grafico_linha(df, titulo):
    #GERAR GRÁFICO DE VALOR FOB POR MÊS
    df_copy = df.copy()
    
    df_media = df_copy['valor_fob'].mean()

    escalas = [
        (1_000_000_000, 1_000_000_000, "(em Bilhões de US$)"),
        (1_000_000,     1_000_000,     "(em Milhões de US$)"),
        (1_000,         1_000,         "(em Milhares de US$)"),
        (0,             1,             "(em US$)")
    ]

    for limite, divisor, sufixo in escalas:
        if df_media >= limite:
            valor_requisicao = df_copy['valor_fob'] / divisor
            titulo_escala =  sufixo
            break

    titulo_completo = f"{titulo} {titulo_escala}".replace('$',r'\$')

    fig, ax = plt.subplots(figsize=(7,2.6))
    ax.plot(df_copy['ordem'], valor_requisicao, marker='o', color='#2B6CB0', linewidth=2)
    ax.set_title(f'{titulo_completo}',fontsize=10, fontweight='bold',color='#2D3748')
    ax.set_xlabel('Mês', fontsize=8)
    ax.set_ylabel('Valor FOB (US$)',fontsize=8)
    ax.tick_params(labelsize=7)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xticks(df_copy['ordem'])
    ax.set_xticklabels([meses.get(m, m) for m in df_copy['ordem']], rotation=30, ha='right')

    #LIMITE MÁXIMO E MÍNIMO DO GRÁFICO 
    valor_maior = valor_requisicao.max()
    valor_menor = valor_requisicao.min()
    margem = (valor_maior - valor_menor) * 0.15
    ax.set_ylim(valor_menor - margem, valor_maior + margem)

    #COLOCANDO VALOR ACIMA DO MARCADOR
    for x,y in zip(df_copy['ordem'], valor_requisicao):
        ax.annotate(
            formatar_br(y),
            (x,y),
            textcoords="offset points",
            xytext=(0,4),
            ha='center',
            fontsize=6,
            fontweight='bold',
            color='#2D3748'
        )

    #SALVANDO A IMAGEM
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=200, bbox_inches='tight', pad_inches=0.25)
    plt.close(fig)
    return buffer_para_image(buf, altura_max=680,largura_max=450)

#In[]
def gerar_grafico_barras(df_top10, x_col, y_col, titulo):
    
    df_copy = df_top10.copy()
    
    df_media = df_copy[y_col].mean()

    escalas = [
        (1_000_000_000, 1_000_000_000, "(em Bilhões de US$)"),
        (1_000_000,     1_000_000,     "(em Milhões de US$)"),
        (1_000,         1_000,         "(em Milhares de US$)"),
        (0,             1,             "(em US$)")
    ]

    for limite, divisor, sufixo in escalas:
        if df_media >= limite:
            df_copy[y_col] = df_copy[y_col] / divisor
            titulo_escala =  sufixo
            break
    
    titulo_completo = f"{titulo}{titulo_escala}".replace('$',r'\$')

    df_sorted = df_copy.sort_values(by=y_col, ascending=True)
    
    fig, ax = plt.subplots(figsize=(9,4.2))
    #MUDAR OS ROTULOS PARA PULAR LINHA
    #rotulos = df_sorted[x_col].astype(str).apply(lambda x: '\n'.join(textwrap.wrap(x, width=15)))
    #rotulos = df_sorted[x_col].astype(str).apply(lambda x: '\n'.join(textwrap.wrap(x)))
    rotulos = df_sorted[x_col].apply(formatar_produtos)
    
    #GÁFICO HORIZONTAL
    barras = ax.barh(rotulos, df_sorted[y_col], color='#3182CE', edgecolor='#2B6CB0')
    ax.set_title(titulo_completo, fontsize=10, fontweight='bold', color='#2D3748')
    #ROTULO
    ax.set_xlabel('Valor FOB (US$)', fontsize=8)
    ax.tick_params(axis='x', labelsize=7)
    ax.tick_params(axis='y', labelsize=7)
    ax.grid(True, axis='x', linestyle='--',alpha=0.4, zorder=0)
    ax.set_axisbelow(True)

    #VALORES NA BARRA
    valor_fomatado = [formatar_br(v) for v in df_sorted[y_col]]
    ax.bar_label(barras, labels=valor_fomatado, padding=4, fontsize=7, color='#2D3748')
    ax.set_xlim(0, df_sorted[y_col].max() * 1.15)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=200, bbox_inches='tight', pad_inches=0.3)
    plt.close(fig)
    return buffer_para_image(buf, largura_max=710,altura_max=340)
    
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
    dados_totais = montar_tabela_totais(df_fluxo, estilo_celula,estilo_header)
    
    #TABELAS POR MÊS
    montar_tabela_mes(story, dados_totais, df_fluxo, tipo_fluxo, estilo_header, estilo_celula)
    
    """ ----- PÁGINA 2 ----- """
    story.append(Paragraph(f"Análise de {tipo_fluxo} - Top 10 Produtos", styles['TituloTopico']))
    df_prod = df_fluxo.groupby('produto', as_index=False)['valor_fob'].sum().sort_values('valor_fob', ascending=False).head(10)
    img_prod = gerar_grafico_barras(df_prod, 'produto', 'valor_fob', f"Top 10 Produtos por Valor FOB - {tipo_fluxo}")
    story.append(img_prod)
    story.append(PageBreak())

    """ ----- PÁGINA 3 ----- """
    story.append(Paragraph(f"Análise de {tipo_fluxo} - Top 10 Municípios", styles['TituloTopico']))
    df_mun = df_fluxo.groupby('municipio', as_index=False)['valor_fob'].sum().sort_values('valor_fob', ascending=False).head(10)
    img_mun = gerar_grafico_barras(df_mun, 'municipio', 'valor_fob', f"Top 10 Municípios por Valor FOB - {tipo_fluxo}")
    story.append(img_mun)
    story.append(NextPageTemplate("Retrato"))
    story.append(PageBreak())

#In[5]:
def gerar_relatorio(nome_arquivo, df_exp, df_imp, pais, ano):
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

        cabecalho_e_rodape_dados = partial(desenhar_cabecalho_rodape, pais, ano)

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
def main(nome_arquivo, pais, ano):
    df = relatorio_dataframe()
    df_exp = dataframe_exportacao(df)
    df_imp = dataframe_importacao(df)
    gerar_relatorio(nome_arquivo, df_exp, df_imp, pais, ano)

#In[6]:
if __name__ == "__main__":
    pais= "China"
    ano = 2025
    nome_arquivo = "Teste"
    main(nome_arquivo, pais, ano)