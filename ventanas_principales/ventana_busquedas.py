from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel

class VentanaBusquedas(QWidget):
    def __init__(self, volver_a_principal):
        super().__init__()
        self.volver_a_principal = volver_a_principal
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Algoritmos de Búsqueda")
        self.setGeometry(150, 150, 400, 300)
        
        layout = QVBoxLayout()
        
        label = QLabel("Seleccione un algoritmo:")
        layout.addWidget(label)
        
        btn_lineal = QPushButton("Búsqueda Lineal")
        btn_lineal.clicked.connect(self.abrir_lineal)
        layout.addWidget(btn_lineal)
        
        btn_binaria = QPushButton("Búsqueda Binaria")
        btn_binaria.setEnabled(False)
        layout.addWidget(btn_binaria)
        
        btn_volver = QPushButton("← Volver")
        btn_volver.clicked.connect(self.volver_a_principal)
        layout.addWidget(btn_volver)
        
        self.setLayout(layout)
    
    def abrir_lineal(self):
        try:
            from algoritmos.busqueda_lineal import BusquedaLinealWindow
            self.ventana_lineal = BusquedaLinealWindow(self.mostrar_ventana_busquedas)
            self.ventana_lineal.show()
            self.hide()
        except ImportError:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "En desarrollo", "Búsqueda lineal en desarrollo")
    
    def mostrar_ventana_busquedas(self):
        self.show()
    
    def volver_a_principal(self):
        self.volver_a_principal()