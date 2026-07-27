import os
import logging
import pandas as pd
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog

'''ESCOPO GLOBAL'''
#CONFIG DO LOG
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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