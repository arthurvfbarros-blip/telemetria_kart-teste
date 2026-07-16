import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import filedialog, ttk

# 1. Configuração da janela oculta para seleção de arquivo
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

    # Pegamos os nomes das colunas e removemos o 'Tempo' (eixo X constante)
    sensores_disponiveis = df.columns.tolist()
    if 'Tempo' in sensores_disponiveis:
        sensores_disponiveis.remove('Tempo')

    # 2. Configuração da Janela Principal do Painel (Mais larga para acomodar o visualizador)
    janela_painel = tk.Toplevel()
    janela_painel.title("Painel de Telemetria do Kart")
    janela_painel.geometry("1100x650") 

    # --- FRAME SUPERIOR (Controles) ---
    frame_controles = tk.Frame(janela_painel)
    frame_controles.pack(side=tk.TOP, fill=tk.X, pady=15, padx=15)

    tk.Label(frame_controles, text="Selecione o Sensor para Análise:", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
    
    combo_sensores = ttk.Combobox(frame_controles, values=sensores_disponiveis, state="readonly", width=25)
    combo_sensores.pack(side=tk.LEFT, padx=10)

    if sensores_disponiveis:
        combo_sensores.current(0)

    # --- FRAME INFERIOR (Área de Visualização Rolável) ---
    frame_grafico_container = tk.Frame(janela_painel, bd=2, relief=tk.SUNKEN)
    frame_grafico_container.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=15, pady=15)

    # Canvas do Tkinter que permite rolagem de elementos internos
    canvas_rolagem = tk.Canvas(frame_grafico_container, highlightthickness=0)
    
    # Barra de rolagem horizontal vinculada ao movimento horizontal do canvas
    barra_rolagem_x = ttk.Scrollbar(frame_grafico_container, orient=tk.HORIZONTAL, command=canvas_rolagem.xview)
    canvas_rolagem.configure(xscrollcommand=barra_rolagem_x.set)

    # Posicionamento dos elementos de rolagem
    barra_rolagem_x.pack(side=tk.BOTTOM, fill=tk.X)
    canvas_rolagem.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Frame que ficará "dentro" do Canvas de rolagem (é aqui que o gráfico será inserido)
    frame_plot_interno = tk.Frame(canvas_rolagem)
    canvas_rolagem.create_window((0, 0), window=frame_plot_interno, anchor="nw")

    # Função que atualiza o tamanho da área de rolagem sempre que o gráfico interno mudar de tamanho
    def ajustar_regiao_rolagem(event):
        canvas_rolagem.configure(scrollregion=canvas_rolagem.bbox("all"))

    frame_plot_interno.bind("<Configure>", ajustar_regiao_rolagem)

    # Guardamos a referência do widget do gráfico ativo para podermos limpá-lo antes de desenhar outro
    # Variáveis globais para guardar o gráfico e a toolbar atual
    canvas_matplotlib_atual = None
    toolbar_atual = None

    def gerar_grafico():
        global canvas_matplotlib_atual, toolbar_atual

        # Limpa o gráfico E a barra de ferramentas anterior, se existirem
        if canvas_matplotlib_atual is not None:
            canvas_matplotlib_atual.get_tk_widget().destroy()
        if toolbar_atual is not None:
            toolbar_atual.destroy()

        sensor_escolhido = combo_sensores.get()

        # Voltamos para um tamanho de figura que caiba na tela confortavelmente
        fig = Figure(figsize=(12, 5), dpi=100)
        ax = fig.add_subplot(111)

        # PLOTAGEM LIMPA: Sem marker='o' e com linha mais fina
        ax.plot(df['Tempo'], df[sensor_escolhido], color='#1f77b4', linewidth=1)
        
        ax.set_title(f"Histórico de Telemetria - {sensor_escolhido}", fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel("Tempo", fontsize=11)
        ax.set_ylabel("Valor Registrado", fontsize=11)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # A MÁGICA DO EIXO X: Força o Matplotlib a mostrar no máximo 15 rótulos de tempo
        ax.xaxis.set_major_locator(MaxNLocator(nbins=15))
        fig.autofmt_xdate(rotation=45)

        # Conecta a figura ao Tkinter
        canvas_matplotlib_atual = FigureCanvasTkAgg(fig, master=frame_plot_interno)
        widget_grafico = canvas_matplotlib_atual.get_tk_widget()
        widget_grafico.pack(fill=tk.BOTH, expand=True)
        
        # ADICIONA A BARRA DE FERRAMENTAS (Zoom, Pan, Salvar)
        toolbar_atual = NavigationToolbar2Tk(canvas_matplotlib_atual, frame_plot_interno)
        toolbar_atual.update()
        
        canvas_matplotlib_atual.draw()

    # Botão para gerar o gráfico posicionado no frame de controles superior
    btn_gerar = tk.Button(frame_controles, text="Gerar Análise", command=gerar_grafico, bg="#28a745", fg="white", font=("Arial", 10, "bold"), padx=10)
    btn_gerar.pack(side=tk.LEFT, padx=15)

    janela_painel.mainloop()

except Exception as e:
    print(f'Erro ao processar o arquivo: {e}')