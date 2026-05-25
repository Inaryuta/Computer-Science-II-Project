from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Ciencias De la Computación II")
        self.setGeometry(100, 100, 800, 600)

        # Fondo blanco con tono azul muy suave
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f8ff;  /* AliceBlue */
            }
            QLabel {
                color: #003366;  /* Azul oscuro para texto */
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(25)
        layout.setContentsMargins(50, 50, 50, 50)

        # Título
        titulo = QLabel("CIENCIAS DE LA COMPUTACIÓN II")
        titulo.setFont(QFont("Arial", 28, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #003366; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # Subtítulo
        subtitulo = QLabel("Seleccione una categoría para explorar")
        subtitulo.setFont(QFont("Arial", 16))
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("color: #336699; margin-bottom: 30px;")
        layout.addWidget(subtitulo)

        layout.addStretch()

        # Botón de Búsquedas
        self.btn_busquedas = QPushButton("ALGORITMOS DE BÚSQUEDA")
        self.btn_busquedas.setMinimumHeight(70)
        self.btn_busquedas.setCursor(Qt.PointingHandCursor)
        self.btn_busquedas.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #6db3f2, stop:1 #4d9de0);
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 12px;
                border: 2px solid #1e6bb8;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #7ec1ff, stop:1 #5ca9f0);
                border: 2px solid #0d4b8c;
            }
            QPushButton:pressed {
                background-color: #4d9de0;
            }
        """)
        layout.addWidget(self.btn_busquedas)

        # Botón de Grafos
        self.btn_grafos = QPushButton("ALGORITMOS DE GRAFOS")
        self.btn_grafos.setMinimumHeight(70)
        self.btn_grafos.setCursor(Qt.PointingHandCursor)
        self.btn_grafos.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #5cb85c, stop:1 #4cae4c);
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 12px;
                border: 2px solid #357935;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #6ec06e, stop:1 #5cb85c);
                border: 2px solid #2e6b2e;
            }
            QPushButton:pressed {
                background-color: #4cae4c;
            }
        """)
        layout.addWidget(self.btn_grafos)

        # Botón Salir
        self.btn_salir = QPushButton("SALIR")
        self.btn_salir.setMinimumHeight(70)
        self.btn_salir.setCursor(Qt.PointingHandCursor)
        self.btn_salir.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #d9534f, stop:1 #c9302c);
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 12px;
                border: 2px solid #ac2925;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #e0645f, stop:1 #d43f3a);
                border: 2px solid #8b211e;
            }
            QPushButton:pressed {
                background-color: #c9302c;
            }
        """)
        layout.addWidget(self.btn_salir)

        layout.addStretch()

        # Créditos
        creditos = QLabel("Universidad Distrital Francisco José de Caldas")
        creditos.setFont(QFont("Arial", 10))
        creditos.setAlignment(Qt.AlignCenter)
        creditos.setStyleSheet("color: #6699cc; margin-top: 20px;")
        layout.addWidget(creditos)

        # Conexiones
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