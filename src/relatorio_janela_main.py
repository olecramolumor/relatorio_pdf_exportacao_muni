#In[]:
import time
import logging
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
#CLASSE DA JANELA
class AppSelecaoCSV(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.ano_selecionado = None
        self.municipio_selecionado = None
        self.pais_selecionado = None
        self.produto_selecionado = None
        self.tipo_relatorio = None
        self.checkbox_valor = True  # valor default do novo campo

        # CONFIG DA JANELA
        self.title("Filtro Comex Stat - Rondônia")
        self.geometry("460x420")
        self.resizable(False, False)

        # LEITURA DOS DADOS
        ### ARRUMAR AQUI ####
        self.paises, self.municipios, self.anos, self.produtos= relatorio_csv.main()
        

        # CRIAÇÃO DA ESTRUTURA DE ABAS
        self.tabview = ctk.CTkTabview(self, width=420, height=340)
        self.tabview.pack(padx=20, pady=10)

        # Adicionando as abas para cada parâmetro
        self.tabview.add("Apenas Ano")
        self.tabview.add("Município e Ano")
        self.tabview.add("País e Ano")
        self.tabview.add("Produto e Ano")

        # CHAMADA DAS FUNÇÕES DE CONSTRUÇÃO DE CADA WIDGET
        self.criar_aba_apenas_ano()
        self.criar_aba_municipio_ano()
        self.criar_aba_pais_ano()
        self.criar_aba_produto_ano()

        # VARIÁVEL E WIDGET DO CHECKBOX (RODAPÉ)
        self.var_checkbox = ctk.BooleanVar(value=True)
        self.checkbox_opcao = ctk.CTkCheckBox(
            self,
            text="Cabeçalho da SEDEC",
            variable=self.var_checkbox,
            onvalue=True,
            offvalue=False
        )
        self.checkbox_opcao.pack(pady=(0, 5))

        # BOTÃO CONFIRMAR GERAL (RODAPÉ)
        btn_confirmar = ctk.CTkButton(
            self, 
            text="Processar / Gerar Relatório", 
            command=self.confirmar_selecao,
            height=38,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_confirmar.pack(pady=(0, 15))
        
    #BUSCA POR ANO
    def criar_aba_apenas_ano(self):
        tab = self.tabview.tab("Apenas Ano")

        lbl_titulo = ctk.CTkLabel(tab, text="Relatório Geral Por Ano", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_titulo.pack(pady=(20, 15))

        lbl_ano = ctk.CTkLabel(tab, text="Selecione o Ano do Relatório:", font=ctk.CTkFont(size=13))
        lbl_ano.pack(anchor="w", padx=20, pady=(5, 2))

        self.combo_ano_aba1 = ctk.CTkComboBox(
            tab, 
            values=self.anos if self.anos else ["Nenhum ano encontrado"],
            width=340
        )
        self.combo_ano_aba1.pack(padx=20, pady=(0, 15))

    #BUSCA POR MUNICÍPIO
    def criar_aba_municipio_ano(self):
        tab = self.tabview.tab("Município e Ano")

        lbl_titulo = ctk.CTkLabel(tab, text="Relatório por Município e Ano", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_titulo.pack(pady=(10, 10))

        lbl_muni = ctk.CTkLabel(tab, text="Selecione o Município:", font=ctk.CTkFont(size=12))
        lbl_muni.pack(anchor='w', padx=20, pady=(2, 2))

        self.combo_muni_aba2 = ctk.CTkComboBox(
            tab,
            values=self.municipios if self.municipios else ["Nenhum Município Encontrado"],
            width=340        
        )
        self.combo_muni_aba2.pack(padx=20, pady=(0, 10))

        lbl_ano = ctk.CTkLabel(tab, text="Selecione o Ano:", font=ctk.CTkFont(size=12))
        lbl_ano.pack(anchor="w", padx=20, pady=(2, 2))

        self.combo_ano_aba2 = ctk.CTkComboBox(
            tab, 
            values=self.anos if self.anos else ["Nenhum ano encontrado"],
            width=340
        )
        self.combo_ano_aba2.pack(padx=20, pady=(0, 10))

    #BUSCA POR PAIS
    def criar_aba_pais_ano(self):
        tab = self.tabview.tab("País e Ano")
        
        lbl_titulo = ctk.CTkLabel(tab, text="Relatório por País e Ano", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_titulo.pack(pady=(10, 10))

        lbl_pais = ctk.CTkLabel(tab, text="Selecione o País:", font=ctk.CTkFont(size=12))
        lbl_pais.pack(anchor='w', padx=20, pady=(2, 2))

        self.combo_pais_aba3 = ctk.CTkComboBox(
            tab,
            values=self.paises if self.paises else ["Nenhum País Encontrado"],
            width=340        
        )
        self.combo_pais_aba3.pack(padx=20, pady=(0, 10))

        lbl_ano = ctk.CTkLabel(tab, text="Selecione o Ano:", font=ctk.CTkFont(size=12))
        lbl_ano.pack(anchor="w", padx=20, pady=(2, 2))

        self.combo_ano_aba3 = ctk.CTkComboBox(
            tab, 
            values=self.anos if self.anos else ["Nenhum ano encontrado"],
            width=340
        )
        self.combo_ano_aba3.pack(padx=20, pady=(0, 10))

    #BUSCA POR PAIS
    def criar_aba_produto_ano(self):
        tab = self.tabview.tab("Produto e Ano")
                
        lbl_titulo = ctk.CTkLabel(tab, text="Relatório por Produto e Ano", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_titulo.pack(pady=(10, 10))

        lbl_produto = ctk.CTkLabel(tab, text="Selecione o Produto:", font=ctk.CTkFont(size=12))
        lbl_produto.pack(anchor='w', padx=20, pady=(2, 2))

        self.combo_produto_aba4 = ctk.CTkComboBox(
            tab,
            values=self.produtos if self.produtos else ["Nenhum Produto Encontrado"],
            width=340        
        )
        self.combo_produto_aba4.pack(padx=20, pady=(0, 10))

        lbl_ano = ctk.CTkLabel(tab, text="Selecione o Ano:", font=ctk.CTkFont(size=12))
        lbl_ano.pack(anchor="w", padx=20, pady=(2, 2))

        self.combo_ano_aba4 = ctk.CTkComboBox(
            tab, 
            values=self.anos if self.anos else ["Nenhum ano encontrado"],
            width=340
        )
        self.combo_ano_aba4.pack(padx=20, pady=(0, 10))

    def confirmar_selecao(self):
        aba_ativa = self.tabview.get()

        # LEITURA DO VALOR DO CHECKBOX (True/False)
        self.checkbox_valor = self.var_checkbox.get()

        if aba_ativa == "Apenas Ano":
            ano = self.combo_ano_aba1.get()

            if not ano or "Nenhum" in ano:
                messagebox.showwarning("Atenção", "Selecione um Ano válido.")
                return

            self.tipo_relatorio = "apenas_ano"
            self.ano_selecionado = int(ano)

        elif aba_ativa == "Município e Ano":
            muni = self.combo_muni_aba2.get()
            ano = self.combo_ano_aba2.get()

            if not muni or "Nenhum" in muni:
                messagebox.showwarning("Atenção", "Selecione um Município válido.")
                return
            if not ano or "Nenhum" in ano:
                messagebox.showwarning("Atenção", "Selecione um Ano válido.")
                return

            self.tipo_relatorio = "municipio_ano"
            self.municipio_selecionado = muni
            self.ano_selecionado = int(ano)

        elif aba_ativa == "País e Ano":
            pais = self.combo_pais_aba3.get()
            ano = self.combo_ano_aba3.get()

            if not pais or "Nenhum" in pais:
                messagebox.showwarning("Atenção", "Selecione um País válido.")
                return
            if not ano or "Nenhum" in ano:
                messagebox.showwarning("Atenção", "Selecione um Ano válido.")
                return

            self.tipo_relatorio = "pais_ano"
            self.pais_selecionado = pais
            self.ano_selecionado = int(ano)

        elif aba_ativa == "Produto e Ano":
            produto = self.combo_produto_aba4.get()
            ano = self.combo_ano_aba4.get()

            if not produto or "Nenhum" in produto:
                messagebox.showwarning("Atenção", "Selecione um País válido.")
                return
            if not ano or "Nenhum" in ano:
                messagebox.showwarning("Atenção", "Selecione um Ano válido.")
                return

            self.tipo_relatorio = "produto_ano"
            self.produto_selecionado = produto
            self.ano_selecionado = int(ano)

        self.destroy()

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

#In[]
def main():
    tempo_ini = time.perf_counter()
    logger.info("=="*32)
    logger.info("--- INÍCIO PROCESSO DE JANELA ---")
    sucesso = False

    try:
        app = AppSelecaoCSV()
        app.mainloop()

        if app.tipo_relatorio:
            logger.info(
                f"Relatório Solicitado: {app.tipo_relatorio} | "
                f"País: {app.pais_selecionado} | Município: {app.municipio_selecionado} | "
                f"Produto: {app.produto_selecionado} | Ano: {app.ano_selecionado} | "
                f"Opção: {app.checkbox_valor}"
            )
            sucesso = True
            return (app.tipo_relatorio, app.pais_selecionado, app.municipio_selecionado,
                    app.produto_selecionado, app.ano_selecionado, app.checkbox_valor)
        else:
            cancelado = True
            return None, None, None, None, None, None

    except Exception as e:
         logger.error(f"Erro no main(): {e}", exc_info=True)

    finally:
        tempo_fim = time.perf_counter()
        tempo_total = tempo_fim - tempo_ini
        logger.info(f"TEMPO DE EXECUÇÃO: {tempo_total}")
        logger.info("--- FIM PROCESSO DE JANELAS ---")
        logger.info("=="*32)



#In[]:
if __name__ == "__main__":
    main()