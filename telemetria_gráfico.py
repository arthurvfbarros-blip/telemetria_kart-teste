import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, ttk, messagebox


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

try:
    df = pd.head_csv(caminho_arquivo)

    sensores_disponiveis = df[df['Sensor'].unique().tolist()]

    janela_painel = tk.Toplevel()
    janela_painel.title("Painel de telemetria")
    janela_painel.geometry("400x200")

    tk.Label(janela_painel, text="Selecione o Sensor para Análise:", font=("Arial", 12).pack(pady= 20))
    combo_sensores = ttk.Combobox(janela_painel, values=sensores_disponiveis, state="readonly", width=30)

    if sensores_disponiveis:
        combo_sensores.current(0)

    def gerar_gráfico():
        sensor_escolhido = combo_sensores.get()

        def_filtrado = df[df['Sensor']==sensor_escolhido]

        plt.figure(figsize=(10,6))
        plt.plot(def_filtrado['Hora'], def_filtrado['Valor'], color='blue', marker= 'o')
        plt.title(f'Telemetria - {sensor_escolhido}')
        plt.xlabel("Tempo")
        plt.ylabel("Valor")
        plt.xticks(rotation = 45)
        plt.grid(True, linestyle = '--', alpha = 0.7)
        plt.tight_layout()
        plt.show

    bnt_gerar = tk.Button(janela_painel, text="Gerar Gráfico", command=gerar_gráfico)
    bnt_gerar.pack(pady=20)

    janela_painel.mainloop()


except Exception as e:
    print(f'Erro ao processar o arquivo {e}')