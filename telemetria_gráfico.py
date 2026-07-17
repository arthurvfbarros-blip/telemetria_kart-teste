import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MaxNLocator
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os

# Variáveis globais para armazenar os dados
df_referencia = None
df_comparacao = None
nome_arquivo_referencia = ""
nome_arquivo_comparacao = ""

# 1. Configuração da janela oculta para seleção do primeiro arquivo
raiz = tk.Tk()
raiz.withdraw()

print("Selecione o arquivo de telemetria de referência...")
caminho_arquivo = filedialog.askopenfilename(
    title="Selecione o arquivo de telemetria (Referência)",
    filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
)

if not caminho_arquivo:
    print("Nenhum arquivo selecionado. Encerrando programa.")
    exit()

try:
    df_referencia = pd.read_csv(caminho_arquivo)
    nome_arquivo_referencia = os.path.basename(caminho_arquivo) # Pega só o nome do arquivo, sem o caminho gigante

    sensores_disponiveis = df_referencia.columns.tolist()
    if 'Tempo' in sensores_disponiveis:
        sensores_disponiveis.remove('Tempo')

    # 2. Configuração da Janela Principal
    janela_painel = tk.Toplevel()
    janela_painel.title("Painel de Telemetria do Kart - Análise e Comparação")
    janela_painel.geometry("1000x600") 

    # --- FRAME SUPERIOR (Controles) ---
    frame_controles = tk.Frame(janela_painel)
    frame_controles.pack(side=tk.TOP, fill=tk.X, pady=10, padx=10)

    tk.Label(frame_controles, text="Sensor:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
    
    combo_sensores = ttk.Combobox(frame_controles, values=sensores_disponiveis, state="readonly", width=20)
    combo_sensores.pack(side=tk.LEFT, padx=5)

    if sensores_disponiveis:
        combo_sensores.current(0)

    # --- FUNÇÃO PARA CARREGAR O SEGUNDO ARQUIVO ---
    def carregar_comparacao():
        global df_comparacao, nome_arquivo_comparacao
        caminho_comp = filedialog.askopenfilename(
            title="Selecione o arquivo de telemetria para Comparação",
            filetypes=[("Arquivos CSV", "*.csv")]
        )
        if caminho_comp:
            try:
                df_comparacao = pd.read_csv(caminho_comp)
                nome_arquivo_comparacao = os.path.basename(caminho_comp)
                messagebox.showinfo("Sucesso", f"Arquivo de comparação carregado:\n{nome_arquivo_comparacao}\n\nClique em 'Gerar Análise' para ver a sobreposição.")
                btn_comparar.config(text="Trocar Comparação", bg="#17a2b8") # Muda o visual do botão para indicar que já tem arquivo
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler o arquivo de comparação:\n{e}")

    # Botões de Controle
    btn_gerar = tk.Button(frame_controles, text="Gerar Análise", command=lambda: gerar_grafico(), bg="#28a745", fg="white", font=("Arial", 10, "bold"))
    btn_gerar.pack(side=tk.LEFT, padx=10)

    btn_comparar = tk.Button(frame_controles, text="+ Adicionar Comparação", command=carregar_comparacao, bg="#6c757d", fg="white", font=("Arial", 10, "bold"))
    btn_comparar.pack(side=tk.LEFT, padx=10)

    # --- FRAME INFERIOR (Gráfico) ---
    frame_grafico = tk.Frame(janela_painel, bd=2, relief=tk.SUNKEN)
    frame_grafico.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

    canvas_matplotlib_atual = None
    toolbar_atual = None

    def gerar_grafico():
        global canvas_matplotlib_atual, toolbar_atual

        if canvas_matplotlib_atual is not None:
            canvas_matplotlib_atual.get_tk_widget().destroy()
        if toolbar_atual is not None:
            toolbar_atual.destroy()

        sensor_escolhido = combo_sensores.get()

        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)

        # Plotagem do arquivo 1 (Referência - Azul)
        ax.plot(
            df_referencia.index, 
            df_referencia[sensor_escolhido], 
            color='#1f77b4', 
            linewidth=1.5, 
            linestyle='--', 
            alpha=0.4, 
            label=f"Referência: {nome_arquivo_referencia}"
        )
        
        # 2. Plotagem da Comparação (Usando df_comparacao.index no Eixo X)
        if df_comparacao is not None:
            if sensor_escolhido in df_comparacao.columns:
                ax.plot(
                    df_comparacao.index, 
                    df_comparacao[sensor_escolhido], 
                    color='#ff7f0e', 
                    linewidth=1.5, 
                    alpha=1.0, 
                    label=f"Comparação: {nome_arquivo_comparacao}"
                )
            else:
                messagebox.showwarning("Aviso", f"O sensor '{sensor_escolhido}' não existe.")

        ax.set_title(f"Comparativo de Telemetria - {sensor_escolhido}", fontsize=14, fontweight='bold', pad=10)
        
        # Atualize também o nome do eixo X para refletir a mudança
        ax.set_xlabel("Número da Amostra (Tempo Relativo)", fontsize=11)
        ax.set_ylabel("Valor Registrado", fontsize=11)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # Ativa a legenda para mostrar qual cor é qual arquivo
        ax.legend(loc="upper right", fontsize=9)

        ax.xaxis.set_major_locator(MaxNLocator(nbins=15))
        fig.autofmt_xdate(rotation=45)
        fig.tight_layout()

        canvas_matplotlib_atual = FigureCanvasTkAgg(fig, master=frame_grafico)
        widget_grafico = canvas_matplotlib_atual.get_tk_widget()
        widget_grafico.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        toolbar_atual = NavigationToolbar2Tk(canvas_matplotlib_atual, frame_grafico)
        toolbar_atual.update()
        
        canvas_matplotlib_atual.draw()

    janela_painel.mainloop()

except Exception as e:
    print(f'Erro fatal ao iniciar o programa: {e}')