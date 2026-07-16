import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


raiz = tk.Tk()
raiz.withdraw()

print("Selecione um arquivo de telemetria...")
caminho_arquivo = filedialog.askopenfilename(
    title="Selecione o arquivo de telemetria do Kart",
    filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*,*")]
)

if not caminho_arquivo:
    print("Nenhum arquivo selecionado. Encerrando programa.")
    exit()

print(f'Arquivo selecionado: {caminho_arquivo}')

