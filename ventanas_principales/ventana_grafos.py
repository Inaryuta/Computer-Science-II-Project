from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel

class VentanaGrafos(QWidget):
    def __init__(self, volver_a_principal):
        super().__init__()
        self.volver_a_principal = volver_a_principal
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Algoritmos de Grafos")
        self.setGeometry(150, 150, 400, 300)
        
        layout = QVBoxLayout()
        
        label = QLabel("Seleccione un algoritmo:")
        layout.addWidget(label)
        
        btn_bfs = QPushButton("BFS (Búsqueda en Amplitud)")
        btn_bfs.setEnabled(False)
        layout.addWidget(btn_bfs)
        
        btn_dijkstra = QPushButton("Algoritmo de Dijkstra")
        btn_dijkstra.setEnabled(False)
        layout.addWidget(btn_dijkstra)
        
        btn_volver = QPushButton("← Volver")
        btn_volver.clicked.connect(self.volver_a_principal)
        layout.addWidget(btn_volver)
        
        self.setLayout(layout)
    
    def volver_a_principal(self):
        self.volver_a_principal()