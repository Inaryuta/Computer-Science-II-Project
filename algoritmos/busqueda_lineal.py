from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout
from PySide6.QtCore import Qt
import random

class BusquedaLinealWindow(QMainWindow):
    def __init__(self, volver_a_busquedas):
        super().__init__()
        self.volver_a_busquedas = volver_a_busquedas
        self.datos = []
        self.initUI()
        self.generar_datos()
    
    def initUI(self):
        self.setWindowTitle("Búsqueda Lineal")
        self.setGeometry(200, 200, 700, 500)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # Barra superior
        top_layout = QHBoxLayout()
        btn_volver = QPushButton("← Volver")
        btn_volver.clicked.connect(self.volver_a_busquedas)
        top_layout.addWidget(btn_volver)
        
        titulo = QLabel("BÚSQUEDA LINEAL")
        titulo.setStyleSheet("font-weight: bold; font-size: 18px;")
        top_layout.addWidget(titulo)
        
        layout.addLayout(top_layout)
        
        # Controles
        ctrl_layout = QHBoxLayout()
        self.btn_generar = QPushButton("Generar datos")
        self.btn_generar.clicked.connect(self.generar_datos)
        
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Valor a buscar")
        
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self.buscar_valor)
        
        ctrl_layout.addWidget(self.btn_generar)
        ctrl_layout.addWidget(self.input_buscar)
        ctrl_layout.addWidget(self.btn_buscar)
        
        layout.addLayout(ctrl_layout)
        
        # Visualización
        self.cont_datos = QWidget()
        self.layout_datos = QHBoxLayout(self.cont_datos)
        layout.addWidget(self.cont_datos)
        
        # Resultado
        self.lbl_resultado = QLabel("Genera datos y busca un valor")
        self.lbl_resultado.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_resultado)
    
    def generar_datos(self):
        # Limpiar visualización
        while self.layout_datos.count():
            item = self.layout_datos.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Generar 10 números aleatorios
        self.datos = [random.randint(1, 100) for _ in range(10)]
        
        # Mostrar
        for i, valor in enumerate(self.datos):
            frame = QLabel(f"[{i}] = {valor}")
            frame.setMinimumSize(60, 60)
            frame.setStyleSheet("""
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            """)
            frame.setAlignment(Qt.AlignCenter)
            self.layout_datos.addWidget(frame)
            frame.indice = i
            frame.valor = valor
    
    def buscar_valor(self):
        if not self.input_buscar.text().isdigit():
            self.lbl_resultado.setText("Ingresa un número válido")
            return
        
        valor = int(self.input_buscar.text())
        
        # Buscar linealmente
        encontrado = False
        posicion = -1
        
        for i in range(self.layout_datos.count()):
            widget = self.layout_datos.itemAt(i).widget()
            if widget and hasattr(widget, 'valor'):
                if widget.valor == valor:
                    widget.setStyleSheet("""
                        border: 3px solid #2ecc71;
                        background-color: #2ecc71;
                        color: white;
                        border-radius: 5px;
                        padding: 5px;
                        margin: 2px;
                        font-weight: bold;
                    """)
                    encontrado = True
                    posicion = i
                    break
                else:
                    widget.setStyleSheet("""
                        border: 2px solid #e74c3c;
                        background-color: #e74c3c;
                        color: white;
                        border-radius: 5px;
                        padding: 5px;
                        margin: 2px;
                    """)
        
        if encontrado:
            self.lbl_resultado.setText(f"✅ Valor {valor} encontrado en posición {posicion}")
        else:
            self.lbl_resultado.setText(f"❌ Valor {valor} no encontrado")
    
    def volver_a_busquedas(self):
        self.close()
        self.volver_a_busquedas()