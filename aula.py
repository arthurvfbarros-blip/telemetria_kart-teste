import sys
import random
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QLabel, QPushButton, QMessageBox)
from PyQt6.QtCore import QTimer, Qt
import pyqtgraph as pg
import csv
import os
from datetime import datetime

class painel_telemetria(QMainWindow):
    def __init__(self):
        super().__init__()


        self.setWindowTitle("Telemetria Kart")
        self.resize(1000,700)
        self.setStyleSheet("background-color: black; color: white;")

        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # 1. LAYOUT PRINCIPAL (Vertical)
        # Mantemos ele como a "espinha dorsal" da janela
        layout_principal = QVBoxLayout()
        widget_central.setLayout(layout_principal)

        # --- ÁREA SUPERIOR: GRÁFICO RPM ---
        self.grafico_rpm = pg.PlotWidget(title = "Rotação do motor (RPM)")
        self.grafico_rpm.showGrid(x=True, y=True, alpha = 0.3)
        self.grafico_rpm.setYRange(0, 15000) # Ajustei para 15k (3000 é muito baixo para Kart)
        self.grafico_rpm.setBackground("k")
        styles = {'color':'#b0b0b0', 'font-size':'12px'}
        self.grafico_rpm.getPlotItem().setLabel('left', 'Rotação', **styles)
        self.grafico_rpm.getPlotItem().setLabel('bottom', 'Tempo (s)', **styles)
        
        # Adiciona o gráfico ao layout principal
        layout_principal.addWidget(self.grafico_rpm, stretch=2)

        # --- ÁREA INFERIOR: PEDAIS E TEMPO ---
        layout_inferior = QHBoxLayout() # Cria o layout horizontal
        
        # CORREÇÃO 1: Adiciona o layout inferior ao principal corretamente
        layout_principal.addLayout(layout_inferior, stretch=1)

        # === ESQUERDA: PEDAIS ===
        layout_pedais = QHBoxLayout()

        
        self.bar_freio = QProgressBar()
        self.bar_freio.setOrientation(Qt.Orientation.Vertical)
        self.bar_freio.setRange(0,100)
        self.bar_freio.setStyleSheet("""
            QProgressBar { border: 2px solid #555; border-radius: 5px; background: #333; }
            QProgressBar::chunk { background-color: #ff3333; } 
        """)

        self.bar_acelerador = QProgressBar()
        self.bar_acelerador.setOrientation(Qt.Orientation.Vertical)
        self.bar_acelerador.setRange(0,100)
        self.bar_acelerador.setStyleSheet("""
            QProgressBar { border: 2px solid #555; border-radius: 5px; background: #333; }
            QProgressBar::chunk { background-color: #00ff00; } 
        """)

        lbl_freio = QLabel("FREIO")
        lbl_accel = QLabel("ACELERADOR")

        # Coluna do Freio
        col_freio = QVBoxLayout()
        col_freio.addWidget(self.bar_freio)
        col_freio.addWidget(lbl_freio, alignment=Qt.AlignmentFlag.AlignCenter)

        # Coluna do Acelerador
        col_acelerador = QVBoxLayout()
        col_acelerador.addWidget(self.bar_acelerador)
        col_acelerador.addWidget(lbl_accel, alignment=Qt.AlignmentFlag.AlignCenter)

        layout_pedais.addLayout(col_freio)
        layout_pedais.addLayout(col_acelerador)

        layout_inferior.addLayout(layout_pedais)

        # === DIREITA: TEMPO ===
        layout_tempo = QVBoxLayout()
        layout_tempo.setContentsMargins(50,0,50,0)
        font_style = "font-size: 30px; font-weight: bold; font-family: monospace;"

        self.lbl_tempo_atual = QLabel("00:00:000")
        self.lbl_tempo_atual.setStyleSheet(f"color: white; {font_style}")

        self.lbl_melhor_volta = QLabel("BEST: --:--.---")
        self.lbl_melhor_volta.setStyleSheet("color: #aaaaaa; font-size: 20px;")

        self.lbl_delta = QLabel("DELTA: +0.000")
        self.lbl_delta.setStyleSheet(f"color: white; {font_style}")

        layout_tempo.addWidget(QLabel("TEMPO ATUAL:"))
        layout_tempo.addWidget(self.lbl_tempo_atual)
        layout_tempo.addSpacing(20)
        layout_tempo.addWidget(self.lbl_melhor_volta)
        layout_tempo.addWidget(self.lbl_delta)
        layout_tempo.addStretch()

        layout_inferior.addLayout(layout_tempo)

        self.historico_completo = []
        layout_botoes = QHBoxLayout()

        self.btn_reset = QPushButton("Resetar tempos")
        self.btn_reset.setStyleSheet("background-color: black; color: white; padding:10px; font-weight: bold;")
        self.btn_reset.clicked.connect(self.reiniciar_tempos)

        self.btn_salvar = QPushButton("Salvar dados")
        self.btn_salvar.setStyleSheet("background-color: black; color: white; padding:10px; font-weight: bold;")
        self.btn_salvar.clicked.connect(self.salvar_telemetria)

        layout_botoes.addWidget(self.btn_reset)
        layout_botoes.addWidget(self.btn_salvar)

        layout_principal.addLayout(layout_botoes)

        # --- DADOS E VARIÁVEIS ---
        self.x = list(range(100))
        self.y = [0] * 100
        self.linha_rpm = self.grafico_rpm.plot(self.x, self.y, pen=pg.mkPen('#00ccff', width=2))
        
        self.inicio_volta = time.time()
        self.melhor_tempo_s = None 
        
        self.timer = QTimer()
        self.timer.setInterval(16) 
        self.timer.timeout.connect(self.atualizar_tudo)
        self.timer.start()

    def atualizar_tudo(self):
        # Simulação
        rpm = random.randint(8000, 13000)
        freio = 0
        acel = random.randint(50, 100)
        
        if random.random() < 0.05: 
            rpm = random.randint(4000, 7000)
            freio = random.randint(60, 100)
            acel = 0

        # Atualiza Gráfico
        self.y.pop(0)
        self.y.append(rpm)
        self.linha_rpm.setData(self.x, self.y)

        # Atualiza Pedais (Agora os nomes batem!)
        self.bar_freio.setValue(freio)
        self.bar_acelerador.setValue(acel)

        # Lógica de Tempo
        agora = time.time()
        tempo_decorrido = agora - self.inicio_volta
        
        mins = int(tempo_decorrido // 60)
        segs = int(tempo_decorrido % 60)
        milis = int((tempo_decorrido * 1000) % 1000)
        self.lbl_tempo_atual.setText(f"{mins:02}:{segs:02}.{milis:03}")


        if self.melhor_tempo_s:
            delta = tempo_decorrido - (self.melhor_tempo_s * (tempo_decorrido/self.melhor_tempo_s)) + random.uniform(-0.5, 0.5)
            sinal = "+" if delta > 0 else "-"
            cor = "#ff5555" if delta > 0 else "#55ff55"
            self.lbl_delta.setText(f"DELTA: {sinal}{abs(delta):.3f}")
            self.lbl_delta.setStyleSheet(f"color: {cor}; font-size: 30px; font-weight: bold; font-family: monospace;")
        
        if tempo_decorrido > 10.0:
            self.fechar_volta(tempo_decorrido)

        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        self.historico_completo.append([timestamp, rpm, acel, freio])

    def reiniciar_tempos(self, checked = None):
        self.inicio_volta = time.time()
        self.melhor_tempo_s = None
        self.lbl_melhor_volta.setText("BEST: --:--:---")
        self.lbl_melhor_volta.setStyleSheet("color: #aaaaaa; font-size: 20px;")
        self.lbl_delta.setText("Delta: +0.000")
        self.lbl_delta.setStyleSheet("color: white; font-size: 30px; font-weight: bold; font-family: monospace;")
    
    def salvar_telemetria(self, checked = None):
        if not self.historico_completo:
            QMessageBox.warning(self, "aviso, nenhum arquivo dado pra salvar ainda!")
            return
        
        pasta_destino = "dados_telemetria"
        os.makedirs(pasta_destino, exist_ok=True)
        nome_arquivo = f'Telemetria_{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}.csv'
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)

        try:
            with open(caminho_completo, mode="w", newline='') as arquivo:
                escritor= csv.writer(arquivo)
                escritor.writerow(["Tempo", "RPM", "Acelerador", "Freio"])
                escritor.writerows(self.historico_completo)

            QMessageBox.information(self, "Sucesso", f"dados salvos em:\n{caminho_completo}")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"erro ao salvar o arquivo {e}")

    def fechar_volta(self, tempo_final):
        if self.melhor_tempo_s is None or tempo_final < self.melhor_tempo_s:
            self.melhor_tempo_s = tempo_final
            mins = int(tempo_final // 60)
            segs = int(tempo_final % 60)
            milis = int((tempo_final * 1000) % 1000)
            self.lbl_melhor_volta.setText(f"BEST: {mins:02}:{segs:02}.{milis:03}")
            self.lbl_melhor_volta.setStyleSheet("color: #55ff55; font-size: 20px; font-weight: bold;") 
        
        self.inicio_volta = time.time()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = painel_telemetria()
    janela.show()
    sys.exit(app.exec())