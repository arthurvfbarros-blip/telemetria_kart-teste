import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.ticker as ticker
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os

# Variáveis globais
df_referencia = None
df_comparacao = None
nome_arquivo_referencia = ""
nome_arquivo_comparacao = ""

# --- MOTOR MATEMÁTICO DE NORMALIZAÇÃO ---
def preparar_eixo_voltas(df):
    """
    Transforma a contagem de voltas em um eixo contínuo (ex: Volta 1.5 é o meio da volta 1).
    """
    # Conta quantas amostras existem dentro de cada volta específica
    tamanhos_voltas = df.groupby('Volta')['Volta'].transform('count')
    # Conta a posição da amostra atual (0, 1, 2...)
    amostra_atual = df.groupby('Volta').cumcount()
    # Calcula a fração e soma ao número da volta
    df['Eixo_Voltas'] = df['Volta'] + (amostra_atual / tamanhos_voltas)
    return df

# 1. Seleção do primeiro arquivo
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
    nome_arquivo_referencia = os.path.basename(caminho_arquivo)
    
    # Aplica a normalização matemática
    df_referencia = preparar_eixo_voltas(df_referencia)

    # Limpa as colunas administrativas do menu
    sensores_disponiveis = df_referencia.columns.tolist()
    colunas_ignorar = ['Volta', 'Tempo_Volta', 'Tempo', 'Hora', 'Eixo_Voltas']
    for col in colunas_ignorar:
        if col in sensores_disponiveis:
            sensores_disponiveis.remove(col)

    # 2. Configuração da Janela Principal
    janela_painel = tk.Toplevel()
    janela_painel.title("Painel de Telemetria - Análise Contínua por Voltas")
    janela_painel.geometry("1100x600") 

    # --- FRAME SUPERIOR (Controles) ---
    frame_controles = tk.Frame(janela_painel)
    frame_controles.pack(side=tk.TOP, fill=tk.X, pady=10, padx=10)

    tk.Label(frame_controles, text="Analisar Sensor:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
    
    combo_sensores = ttk.Combobox(frame_controles, values=sensores_disponiveis, state="readonly", width=20)
    combo_sensores.pack(side=tk.LEFT, padx=5)
    if sensores_disponiveis: combo_sensores.current(0)

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
                
                # Aplica a mesma normalização matemática no segundo kart
                df_comparacao = preparar_eixo_voltas(df_comparacao)
                
                btn_comparar.config(text="Trocar Comparação", bg="#17a2b8")
                messagebox.showinfo("Sucesso", f"Arquivo de comparação carregado:\n{nome_arquivo_comparacao}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler o arquivo:\n{e}")

    # Botões
    btn_gerar = tk.Button(frame_controles, text="Gerar Análise", command=lambda: gerar_grafico(), bg="#28a745", fg="white", font=("Arial", 10, "bold"))
    btn_gerar.pack(side=tk.LEFT, padx=15)

    btn_comparar = tk.Button(frame_controles, text="+ Adicionar Comparação", command=carregar_comparacao, bg="#6c757d", fg="white", font=("Arial", 10, "bold"))
    btn_comparar.pack(side=tk.LEFT, padx=5)

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

        # Plotagem usando as Voltas Contínuas no Eixo X
        ax.plot(
            df_referencia['Eixo_Voltas'], 
            df_referencia[sensor_escolhido], 
            color='#1f77b4', 
            linewidth=1.5, 
            linestyle='--', 
            alpha=0.6, 
            label=f"Referência: {nome_arquivo_referencia}"
        )
        
        if df_comparacao is not None:
            if sensor_escolhido in df_comparacao.columns:
                ax.plot(
                    df_comparacao['Eixo_Voltas'], 
                    df_comparacao[sensor_escolhido], 
                    color='#ff7f0e', 
                    linewidth=1.5, 
                    alpha=1.0, 
                    label=f"Comparação: {nome_arquivo_comparacao}"
                )
            else:
                messagebox.showwarning("Aviso", f"O sensor não existe no arquivo de comparação.")

        ax.set_title(f"Telemetria Sincronizada por Voltas - {sensor_escolhido}", fontsize=14, fontweight='bold', pad=10)
        ax.set_ylabel("Valor Registrado", fontsize=11)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # O SEGREDINHO VISUAL: Força o eixo X a exibir apenas números inteiros (1, 2, 3...)
        # e adiciona a palavra "Volta " na frente do número para ficar bonito.
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('Volta %d'))
        
        # Como removemos o texto longo, não precisamos mais inclinar as letras em 45 graus
        ax.legend(loc="upper right", fontsize=9)
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