'''
Aqui Tem a geração dos Gráficos para o relatório
'''
#In[1]:
import os
import io
import logging
import textwrap
from datetime import datetime
 
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from svglib.svglib import svg2rlg

from reportlab.graphics.shapes import Drawing 
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, Image, NextPageTemplate

#In[2]:
'''ESCOPO GLOBAL'''
#CONFIG DO LOG
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MESES = {
    1: 'Janeiro',    2: 'Fevereiro',    3: 'Março',
    4: 'Abril',    5: 'Maio',    6: 'Junho',
    7: 'Julho',    8: 'Agosto',    9: 'Setembro',
    10: 'Outubro',    11: 'Novembro',    12: 'Dezembro'
}

ESCALAS_VALOR = [
    (1_000_000_000, 1_000_000_000, "(em Bilhões de US$)"),
    (1_000_000,     1_000_000,     "(em Milhões de US$)"),
    (1_000,         1_000,         "(em Milhares de US$)"),
    (0,             1,             "(em US$)"),
]

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
        return pd.read_csv(arq_cam, sep=';', encoding='utf-8-sig')        
        
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
        nome_mes = MESES.get(num_mes,num_mes)

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
    drawing = svg2rlg(buf)

    largura_px, altura_px = drawing.width, drawing.height
    fator = largura_max / largura_px
    largura_final = largura_max
    altura_final = altura_px * fator

    if altura_final > altura_max:
        fator = altura_max / altura_px
        altura_final = altura_max
        largura_final = largura_px * fator

    drawing.width = largura_final
    drawing.height = altura_final
    drawing.scale(fator, fator)
    return drawing
#In[]
def gerar_grafico_linha(df, titulo):
    #GERAR GRÁFICO DE VALOR FOB POR MÊS
    df_copy = df.copy()
    
    df_media = df_copy['valor_fob'].mean()


    for limite, divisor, sufixo in ESCALAS_VALOR:
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
    ax.set_xticklabels([MESES.get(m, m) for m in df_copy['ordem']], rotation=30, ha='right')

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
    fig.savefig(buf, format='svg', bbox_inches='tight', pad_inches=0.25)
    plt.close(fig)
    return buffer_para_image(buf, altura_max=680,largura_max=450)

#In[]
def gerar_grafico_barras(df_top10, x_col, y_col, titulo):
    
    df_copy = df_top10.copy()
    df_media = df_copy[y_col].mean()

    for limite, divisor, sufixo in ESCALAS_VALOR:
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
    fig.savefig(buf, format='svg', bbox_inches='tight', pad_inches=0.25)
    plt.close(fig)
    return buffer_para_image(buf, largura_max=710,altura_max=340)