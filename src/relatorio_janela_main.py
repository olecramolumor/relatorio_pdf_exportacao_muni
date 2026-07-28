#In[]:
import os
import logging
import pandas as pd
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog

###src###
import relatorio_csv

#In[2]:
'''ESCOPO GLOBAL'''
#CONFIG DO LOG
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#In[]:

#Janela de dialogos para seleção do país:
def dados_csv(arq_cam):
    try:
        if not os.path.exists(arq_cam):
            messagebox.showerror("Erro", f"Arquivo CSV não encontrado em:\n{arq_cam}")
            return [], []

        df = pd.read_csv(arq_cam, sep=';', encoding='utf-8-sig')

        #DADOS DE PAIS
        paises = sorted(df['pais'].dropna().astype(str).str.strip().unique().tolist())

        #DADOS DE ANO
        anos = sorted(df['ano'].dropna().astype(int).unique().tolist(), reverse=True)
        anos_str = [str(a) for a in anos]

        return paises, anos_str,df

    except Exception as e:
        logger.error(f"Erro na função janela_selecao(): {e}")
        raise

#In[]:
#Janela de dialogos para salvar
def janela_salvar(nome_padrao):
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost",True)
        caminho_escolhido = filedialog.asksaveasfilename(
            title="Salvar Relatório PDF como...",
            initialfile=nome_padrao,
            defaultextension=".pdf",
            filetypes=[
                ("Arquivos PDF","*.pdf"), 
                ("Todos os Arquivos","*.*")
            ]
        )
        root.destroy()

        return caminho_escolhido

    except Exception as e:
        logger.error(f"Erro na função janela_salvar(): {e}")
        raise

#In[]:
#CLASSE DA JANELA
class AppSelecaoCSV(ctk.CTk):
    def __init__(self, arq_cam):
        super().__init__()
        self.pais_selecionado = None
        self.ano_selecionado = None

        self.caminho_csv = arq_cam

        # CONFIG DA JANELA
        self.title("Filtro de Relatório Comex Stat Rondônia - Municipal")
        self.geometry("420x350")
        self.resizable(False, False)

        self.paises, self.anos, self.df = dados_csv(self.caminho_csv)

        # LAYOUT DE INTERFACE
        self.criar_widget()

    def criar_widget(self):
        # TÍTULO / CABEÇALHO
        lbl_titulo = ctk.CTkLabel(
            self, 
            text="Seleção de Parâmetros", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_titulo.pack(pady=(25, 20))

        # PAÍS (Correção no nome da classe: CTkLabel)
        lbl_pais = ctk.CTkLabel(self, text="Selecione o País:", font=ctk.CTkFont(size=13))
        lbl_pais.pack(anchor='w', padx=40, pady=(5, 2))

        self.combo_pais = ctk.CTkComboBox(
            self,
            values=self.paises if self.paises else ["Nenhum País Encontrado"],
            width=340        
        )
        self.combo_pais.pack(padx=40, pady=(0, 15))

        # ANO
        lbl_ano = ctk.CTkLabel(self, text="Selecione o Ano:", font=ctk.CTkFont(size=13))
        lbl_ano.pack(anchor="w", padx=40, pady=(5, 2))

        self.combo_ano = ctk.CTkComboBox(
            self, 
            values=self.anos if self.anos else ["Nenhum ano encontrado"],
            width=340
        )
        self.combo_ano.pack(padx=40, pady=(0, 25))

        # BOTÃO CONFIRMAR
        btn_confirmar = ctk.CTkButton(
            self, 
            text="Processar / Gerar Relatório", 
            command=self.confirmar_selecao,
            height=38,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_confirmar.pack(padx=40, pady=10)

    def confirmar_selecao(self):
        pais = self.combo_pais.get()
        ano = self.combo_ano.get()

        if not pais or pais == "Nenhum País Encontrado":
            messagebox.showwarning("Atenção", "Por favor, selecione um país válido.")
            return

        if not ano or ano == "Nenhum ano encontrado":
            messagebox.showwarning("Atenção", "Por favor, selecione um ano válido.")
            return

        messagebox.showinfo(
            "Seleção Confirmada", 
            f"País: {pais}\nAno: {ano}"
        )

        #COLETANDO DADOS
        self.pais_selecionado = pais
        self.ano_selecionado = int(ano)

        #QUEBRA A JANELA
        self.destroy()

#In[]
def main():
    #DADOS DO CSV
    arq_cam = relatorio_csv.main()

    #ABRIR INSTANCIA E JANELA
    app = AppSelecaoCSV(arq_cam)
    app.mainloop()

    #variavel de pais e ano
    pais = app.pais_selecionado
    ano = app.ano_selecionado

    if pais and ano:
        logger.info(f"Parâmetros selecionados com sucesso -> País: {pais} | Ano: {ano}")

    else:
        logger.info("Seleção Cancelada Pelo Usuário")    

    return pais, ano

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Erro no main(): {e}")

