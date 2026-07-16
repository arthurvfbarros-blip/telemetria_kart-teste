import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, ttk

# Configuração da janela oculta
raiz = tk.Tk()
raiz.withdraw()

print("Selecione um arquivo de telemetria...")
caminho_arquivo = filedialog.askopenfilename(
    title="Selecione o arquivo de telemetria do Kart",
    filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
)

if not caminho_arquivo:
    print("Nenhum arquivo selecionado. Encerrando programa.")
    exit()

print(f'Arquivo selecionado: {caminho_arquivo}')

try:
    df = pd.read_csv(caminho_arquivo)

    # CORREÇÃO 1: Pegamos direto os nomes das colunas do seu CSV
    sensores_disponiveis = df.columns.tolist()

    # Removemos o 'Tempo' da lista de opções, pois ele sempre será o eixo X
    if 'Tempo' in sensores_disponiveis:
        sensores_disponiveis.remove('Tempo')

    # Configuração da Janela do Painel
    janela_painel = tk.Toplevel()
    janela_painel.title("Painel de telemetria")
    janela_painel.geometry("1100x650")

    frame_controles = tk.Frame(janela_painel)
    frame_controles.pack(side=tk.TOP, fill=tk.X, padx=15, pady=15)

    # CORREÇÃO 2: Parênteses ajustados corretamente no Label
    tk.Label(janela_painel, text="Selecione o Sensor para Análise:", font=("Arial", 12)).pack(pady=20)
    
    combo_sensores = ttk.Combobox(janela_painel, values=sensores_disponiveis, state="readonly", width=30)
    combo_sensores.pack(pady=10)

    if sensores_disponiveis:
        combo_sensores.current(0)

    frame_grafico_container = tk.Frame(janela_painel, bd=2, relief=tk.SUNKEN)
    frame_grafico_container.pack(side = tk.BOTTOM, fill=tk.BOTH, expand=True, padx=15, pady=15)

    canvas_rolagem = tk.Canvas(frame_grafico_container, highlightthickness=0)

    barra_rolagem_x = ttk.Scrollbar(frame_grafico_container, orient=tk.HORIZONTAL, command=canvas_rolagem.xview)
    canvas_rolagem.configure(xscrollcommand=barra_rolagem_x.set)
    
    barra_rolagem_x.pack(side=tk.BOTTOM, fill=tk.X)
    canvas_rolagem.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    frame_plot_interno = tk.Frame(canvas_rolagem)
    canvas_rolagem.create_window((0,0), window=frame_plot_interno, anchor="nw")

    def gerar_grafico():
        sensor_escolhido = combo_sensores.get()

        plt.figure(figsize=(10,6))
        
        # CORREÇÃO 3: Plotamos o Tempo vs a coluna do sensor escolhido diretamente
        plt.plot(df['Tempo'], df[sensor_escolhido], color='blue', marker='o')
        
        plt.title(f'Telemetria - {sensor_escolhido}')
        plt.xlabel("Tempo")
        plt.ylabel("Valor")
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # CORREÇÃO 4: Parênteses adicionados para chamar a função show()
        plt.show()

    bnt_gerar = tk.Button(janela_painel, text="Gerar Gráfico", command=gerar_grafico)
    bnt_gerar.pack(pady=20)

    janela_painel.mainloop()

except Exception as e:
    print(f'Erro ao processar o arquivo: {e}')