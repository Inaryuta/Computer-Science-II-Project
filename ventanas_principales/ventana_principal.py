from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QPushButton, QFrame
)
from PySide6.QtCore import Qt

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Algoritmos de Búsqueda y Grafos")
        self.setGeometry(100, 100, 800, 600)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("ALGORITMOS Y ESTRUCTURAS DE DATOS")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel("Seleccione una categoría para explorar")
        subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitulo)
        
        # Botones
        self.btn_busquedas = QPushButton("🔍 ALGORITMOS DE BÚSQUEDA")
        self.btn_busquedas.setMinimumHeight(60)
        
        self.btn_grafos = QPushButton("📊 ALGORITMOS DE GRAFOS")
        self.btn_grafos.setMinimumHeight(60)
        
        self.btn_salir = QPushButton("🚪 SALIR")
        self.btn_salir.setMinimumHeight(60)
        
        # Estilos simples
        for btn in [self.btn_busquedas, self.btn_grafos, self.btn_salir]:
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
        
        self.btn_busquedas.setStyleSheet(self.btn_busquedas.styleSheet() + "background-color: #3498db; color: white;")
        self.btn_grafos.setStyleSheet(self.btn_grafos.styleSheet() + "background-color: #2ecc71; color: white;")
        self.btn_salir.setStyleSheet(self.btn_salir.styleSheet() + "background-color: #e74c3c; color: white;")
        
        layout.addWidget(self.btn_busquedas)
        layout.addWidget(self.btn_grafos)
        layout.addWidget(self.btn_salir)
        
        # Conectar eventos
        self.btn_busquedas.clicked.connect(self.abrir_busquedas)
        self.btn_grafos.clicked.connect(self.abrir_grafos)
        self.btn_salir.clicked.connect(self.close)
    
    def abrir_busquedas(self):
        try:
            from ventanas_principales.ventana_busquedas import VentanaBusquedas
            self.ventana_busquedas = VentanaBusquedas(self.mostrar_ventana_principal)
            self.ventana_busquedas.show()
            self.hide()
        except ImportError:
            # Crear ventana temporal si no existe
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "En desarrollo", "Ventana de búsquedas en desarrollo")
    
    def abrir_grafos(self):
        try:
            from ventanas_principales.ventana_grafos import VentanaGrafos
            self.ventana_grafos = VentanaGrafos(self.mostrar_ventana_principal)
            self.ventana_grafos.show()
            self.hide()
        except ImportError:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "En desarrollo", "Ventana de grafos en desarrollo")
    
    def mostrar_ventana_principal(self):
        self.show()