from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class VentanaGrafos(QWidget):
    def __init__(self, volver_a_principal):
        super().__init__()
        self.volver_a_principal = volver_a_principal
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Algoritmos de Grafos")
        self.setGeometry(150, 150, 500, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
            }
            QLabel {
                color: #003366;
                font-size: 16px;
            }
            QPushButton {
                background-color: #e6f2ff;
                color: #003366;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #99ccff;
                border-radius: 8px;
                padding: 12px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #cce6ff;
                border: 2px solid #66a3ff;
            }
            QPushButton:pressed {
                background-color: #b3d9ff;
            }
            QPushButton#boton_volver {
                background-color: #ffdddd;
                border: 2px solid #ff9999;
            }
            QPushButton#boton_volver:hover {
                background-color: #ffcccc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("ALGORITMOS DE GRAFOS")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #003366; margin-bottom: 20px;")
        layout.addWidget(titulo)

        self.btn_inicio = QPushButton("🏠  INICIO")
        self.btn_inicio.setObjectName("boton_volver")
        self.btn_inicio.setCursor(Qt.PointingHandCursor)
        self.btn_inicio.clicked.connect(self.volver_a_principal_action)
        layout.addWidget(self.btn_inicio)

        layout.addStretch()

        # Mensaje informativo
        info = QLabel("(Próximamente más algoritmos)")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #6699cc; font-style: italic;")
        layout.addWidget(info)
        
    def volver_a_principal_action(self):
        self.close()
        self.volver_a_principal()