import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MaxNLocator
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os

df_referencia = None
df_comparacao = None
nome_arquivo_referencia = ""
nome_arquivo_comparacao = ""

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

    # Limpamos as colunas administrativas para sobrar apenas os Sensores reais
    sensores_disponiveis = df_referencia.columns.tolist()
    colunas_ignorar = ['Volta', 'Tempo_Volta', 'Tempo', 'Hora']
    for col in colunas_ignorar:
        if col in sensores_disponiveis:
            sensores_disponiveis.remove(col)

    voltas_referencia = df_referencia['Volta'].unique().tolist()

    janela_painel = tk.Toplevel()
    janela_painel.title("Painel de Telemetria - Análise por Voltas")
    janela_painel.geometry("1100x650") 

    # --- FRAME SUPERIOR (Controles de Sensores e Comparação) ---
    frame_controles = tk.Frame(janela_painel)
    frame_controles.pack(side=tk.TOP, fill=tk.X, pady=5, padx=10)

    tk.Label(frame_controles, text="Sensor:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
    combo_sensores = ttk.Combobox(frame_controles, values=sensores_disponiveis, state="readonly", width=15)
    combo_sensores.pack(side=tk.LEFT, padx=5)
    if sensores_disponiveis: combo_sensores.current(0)

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
                
                # Preenche as opções de volta para o segundo arquivo
                voltas_comparacao = df_comparacao['Volta'].unique().tolist()
                combo_volta_comp['values'] = voltas_comparacao
                combo_volta_comp.current(0)
                
                btn_comparar.config(text="Trocar Comparação", bg="#17a2b8")
                messagebox.showinfo("Sucesso", f"Arquivo carregado:\n{nome_arquivo_comparacao}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler o arquivo:\n{e}")

    btn_comparar = tk.Button(frame_controles, text="+ Adicionar Comparação", command=carregar_comparacao, bg="#6c757d", fg="white", font=("Arial", 9, "bold"))
    btn_comparar.pack(side=tk.LEFT, padx=15)

    btn_gerar = tk.Button(frame_controles, text="GERAR GRÁFICO", command=lambda: gerar_grafico(), bg="#28a745", fg="white", font=("Arial", 10, "bold"))
    btn_gerar.pack(side=tk.RIGHT, padx=10)

    # --- FRAME SECUNDÁRIO (Seletores de Volta) ---
    frame_voltas = tk.Frame(janela_painel)
    frame_voltas.pack(side=tk.TOP, fill=tk.X, pady=5, padx=10)

    tk.Label(frame_voltas, text="Volta Referência:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
    combo_volta_ref = ttk.Combobox(frame_voltas, values=voltas_referencia, state="readonly", width=10)
    combo_volta_ref.pack(side=tk.LEFT, padx=5)
    if voltas_referencia: combo_volta_ref.current(0)

    tk.Label(frame_voltas, text="Volta Comparação:", font=("Arial", 9)).pack(side=tk.LEFT, padx=20)
    combo_volta_comp = ttk.Combobox(frame_voltas, state="readonly", width=10)
    combo_volta_comp.pack(side=tk.LEFT, padx=5)

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
        volta_ref_escolhida = int(combo_volta_ref.get())

        # Filtra apenas os dados da volta selecionada
        df_ref_filtrado = df_referencia[df_referencia['Volta'] == volta_ref_escolhida]

        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)

        # Plotagem usando o Tempo_Volta como eixo X
        ax.plot(
            df_ref_filtrado['Tempo_Volta'], 
            df_ref_filtrado[sensor_escolhido], 
            color='#1f77b4', 
            linewidth=1.5, 
            linestyle='--', 
            alpha=0.6, 
            label=f"Ref: {nome_arquivo_referencia} (Volta {volta_ref_escolhida})"
        )
        
        if df_comparacao is not None and combo_volta_comp.get() != "":
            volta_comp_escolhida = int(combo_volta_comp.get())
            df_comp_filtrado = df_comparacao[df_comparacao['Volta'] == volta_comp_escolhida]

            if sensor_escolhido in df_comparacao.columns:
                ax.plot(
                    df_comp_filtrado['Tempo_Volta'], 
                    df_comp_filtrado[sensor_escolhido], 
                    color='#ff7f0e', 
                    linewidth=1.5, 
                    alpha=1.0, 
                    label=f"Comp: {nome_arquivo_comparacao} (Volta {volta_comp_escolhida})"
                )
            else:
                messagebox.showwarning("Aviso", f"O sensor não existe no arquivo de comparação.")

        ax.set_title(f"Telemetria - {sensor_escolhido}", fontsize=14, fontweight='bold', pad=10)
        ax.set_xlabel("Tempo Decorrido na Volta (Segundos)", fontsize=11)
        ax.set_ylabel("Valor", fontsize=11)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        ax.legend(loc="upper right", fontsize=9)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=15))
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