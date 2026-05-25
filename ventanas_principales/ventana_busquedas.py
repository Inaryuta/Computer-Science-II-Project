from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMenu, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor

class VentanaBusquedas(QWidget):
    def __init__(self, volver_a_principal):
        super().__init__()
        self.volver_a_principal = volver_a_principal
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Algoritmos de Búsqueda")
        self.setGeometry(150, 150, 500, 500)  # Aumentamos altura para más botones
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
            QMenu {
                background-color: white;
                border: 1px solid #99ccff;
                border-radius: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                color: #003366;
            }
            QMenu::item:selected {
                background-color: #cce6ff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Título
        titulo = QLabel("ALGORITMOS DE BÚSQUEDA")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #003366; margin-bottom: 20px;")
        layout.addWidget(titulo)

        # Botón Inicio (volver a principal)
        self.btn_inicio = QPushButton("🏠  INICIO")
        self.btn_inicio.setObjectName("boton_volver")
        self.btn_inicio.setCursor(Qt.PointingHandCursor)
        self.btn_inicio.clicked.connect(self.volver_a_principal_action)
        layout.addWidget(self.btn_inicio)

        # Botón Búsquedas Internas con menú desplegable
        self.btn_internas = QPushButton("🔎  BÚSQUEDAS INTERNAS")
        self.btn_internas.setCursor(Qt.PointingHandCursor)
        self.btn_internas.clicked.connect(self.mostrar_menu_internas)
        layout.addWidget(self.btn_internas)

        # Crear menú para internas
        self.menu_internas = QMenu()
        self.menu_internas.setStyleSheet(self.styleSheet())

        accion_lineal = self.menu_internas.addAction("Búsqueda Lineal")
        accion_lineal.triggered.connect(self.abrir_lineal)
        accion_binaria = self.menu_internas.addAction("Búsqueda Binaria")
        accion_binaria.triggered.connect(self.abrir_binaria)
        
        # Submenú para funciones hash (internas)
        self.menu_hash = QMenu("Funciones Hash", self.menu_internas)
        self.menu_hash.setStyleSheet(self.styleSheet())
        accion_mod = self.menu_hash.addAction("Módulo")
        accion_mod.triggered.connect(self.abrir_mod)
        accion_cuadrado = self.menu_hash.addAction("Cuadrado")
        accion_cuadrado.triggered.connect(self.abrir_cuadrado)
        accion_truncamiento = self.menu_hash.addAction("Truncamiento")
        accion_truncamiento.triggered.connect(self.abrir_truncamiento)
        accion_plegamiento = self.menu_hash.addAction("Plegamiento")
        accion_plegamiento.triggered.connect(self.abrir_plegamiento)
        self.menu_internas.addMenu(self.menu_hash)

        # Submenú para árboles
        self.menu_arboles = QMenu("Árboles", self.menu_internas)
        self.menu_arboles.setStyleSheet(self.styleSheet())
        accion_digitales = self.menu_arboles.addAction("Digitales")
        accion_digitales.triggered.connect(self.abrir_arboles_digitales)
        accion_residuos = self.menu_arboles.addAction("De Residuos")
        accion_residuos.triggered.connect(self.abrir_arboles_residuos)
        accion_multiresiduos = self.menu_arboles.addAction("Múltiples Residuos")
        accion_multiresiduos.triggered.connect(self.abrir_arboles_multiresiduos)
        accion_huffman = self.menu_arboles.addAction("Huffman")
        accion_huffman.triggered.connect(self.abrir_arboles_huffman)
        self.menu_internas.addMenu(self.menu_arboles)

        # Botón Búsquedas Externas con menú desplegable
        self.btn_externas = QPushButton("🌐  BÚSQUEDAS EXTERNAS")
        self.btn_externas.setCursor(Qt.PointingHandCursor)
        self.btn_externas.clicked.connect(self.mostrar_menu_externas)
        layout.addWidget(self.btn_externas)

        # Menú para externas (se crea dinámicamente)
        self.menu_externas = QMenu()
        self.menu_externas.setStyleSheet(self.styleSheet())

        # Opciones de búsqueda externa
        accion_lineal_ext = self.menu_externas.addAction("Búsqueda Lineal Externa")
        accion_lineal_ext.triggered.connect(self.abrir_lineal_externa)
        accion_binaria_ext = self.menu_externas.addAction("Búsqueda Binaria Externa")
        accion_binaria_ext.triggered.connect(self.abrir_binaria_externa)

        # Submenú para funciones hash externas
        self.menu_hash_ext = QMenu("Funciones Hash Externas", self.menu_externas)
        self.menu_hash_ext.setStyleSheet(self.styleSheet())
        accion_mod_ext = self.menu_hash_ext.addAction("Módulo")
        accion_mod_ext.triggered.connect(self.abrir_hash_mod_externo)
        accion_trunc_ext = self.menu_hash_ext.addAction("Truncamiento")
        accion_trunc_ext.triggered.connect(self.abrir_hash_truncamiento_externo)
        accion_pleg_ext = self.menu_hash_ext.addAction("Plegamiento")
        accion_pleg_ext.triggered.connect(self.abrir_hash_plegamiento_externo)
        accion_base_ext = self.menu_hash_ext.addAction("Cambio de Base")
        accion_base_ext.triggered.connect(self.abrir_hash_cambio_base_externo)
        self.menu_externas.addMenu(self.menu_hash_ext)

        # Submenú para estructuras dinámicas externas
        self.menu_dinamicas_ext = QMenu("Estructuras Dinámicas", self.menu_externas)
        self.menu_dinamicas_ext.setStyleSheet(self.styleSheet())
        accion_exp_total = self.menu_dinamicas_ext.addAction("Expansión Total")
        accion_exp_total.triggered.connect(self.abrir_expansion_total)
        accion_red_total = self.menu_dinamicas_ext.addAction("Reducción Total")
        accion_red_total.triggered.connect(self.abrir_reduccion_total)
        accion_exp_parcial = self.menu_dinamicas_ext.addAction("Expansión Parcial")
        accion_exp_parcial.triggered.connect(self.abrir_expansion_parcial)
        accion_red_parcial = self.menu_dinamicas_ext.addAction("Reducción Parcial")
        accion_red_parcial.triggered.connect(self.abrir_reduccion_parcial)
        self.menu_externas.addMenu(self.menu_dinamicas_ext)

        # Botón Índices (placeholder)
        self.btn_indices = QPushButton("📌  ÍNDICES")
        self.btn_indices.setCursor(Qt.PointingHandCursor)
        self.btn_indices.clicked.connect(self.mostrar_mensaje_indices)
        layout.addWidget(self.btn_indices)

        layout.addStretch()

    # ---------- Menús internos ----------
    def mostrar_menu_internas(self):
        self.menu_internas.exec(QCursor.pos())

    def mostrar_menu_externas(self):
        self.menu_externas.exec(QCursor.pos())

    # ---------- Abrir ventanas internas (ya existentes) ----------
    def abrir_lineal(self):
        try:
            from algoritmos.busqueda_lineal import BusquedaLinealWindow
            self.ventana_lineal = BusquedaLinealWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana_lineal.show()
            self.hide()
        except ImportError:
            QMessageBox.information(self, "En desarrollo", "Búsqueda lineal en desarrollo")

    def abrir_binaria(self):
        try:
            from algoritmos.busqueda_binaria import BusquedaBinariaWindow
            self.ventana_binaria = BusquedaBinariaWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana_binaria.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "En desarrollo", f"Búsqueda binaria en desarrollo. Error: {e}")

    def abrir_mod(self):
        try:
            from algoritmos.funcion_mod import FuncionModWindow
            self.ventana_mod = FuncionModWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana_mod.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "En desarrollo", f"Función Módulo en desarrollo. Error: {e}")

    def abrir_cuadrado(self):
        try:
            from algoritmos.funcion_cuadrado import FuncionCuadradoWindow
            self.ventana_cuadrado = FuncionCuadradoWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana_cuadrado.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "En desarrollo", f"Función Cuadrado en desarrollo. Error: {e}")

    def abrir_truncamiento(self):
        try:
            from algoritmos.funcion_truncamiento import FuncionTruncamientoWindow
            self.ventana_truncamiento = FuncionTruncamientoWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana_truncamiento.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "En desarrollo", f"Función Truncamiento en desarrollo. Error: {e}")

    def abrir_plegamiento(self):
        try:
            from algoritmos.funcion_plegamiento import FuncionPlegamientoWindow
            self.ventana_plegamiento = FuncionPlegamientoWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana_plegamiento.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "En desarrollo", f"Función Plegamiento en desarrollo. Error: {e}")

    def abrir_arboles_digitales(self):
        try:
            from algoritmos.arboles_digitales import ArbolesDigitalesWindow
            self.ventana_arboles = ArbolesDigitalesWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana_arboles.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "En desarrollo", f"Árboles Digitales en desarrollo. Error: {e}")

    def abrir_arboles_residuos(self):
        try:
            from algoritmos.arboles_residuos import ArbolesResiduosWindow
            self.ventana_residuos = ArbolesResiduosWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana_residuos.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "En desarrollo", f"Árboles de Residuos en desarrollo. Error: {e}")

    def abrir_arboles_multiresiduos(self):
        try:
            from algoritmos.arboles_multiresiduos import ArbolesMultiResiduosWindow
            self.ventana_multiresiduos = ArbolesMultiResiduosWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana_multiresiduos.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "En desarrollo", f"Árboles de Múltiples Residuos en desarrollo. Error: {e}")

    def abrir_arboles_huffman(self):
        try:
            from algoritmos.arboles_huffman import ArbolesHuffmanWindow
            self.ventana_huffman = ArbolesHuffmanWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana_huffman.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "En desarrollo", f"Árbol de Huffman en desarrollo. Error: {e}")

    # ---------- Métodos para búsquedas externas ----------
    def abrir_lineal_externa(self):
        try:
            from algoritmos.externas.busqueda_lineal_externa import BusquedaLinealExternaWindow
            self.ventana = BusquedaLinealExternaWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "Error", f"No se pudo cargar Búsqueda Lineal Externa: {e}")

    def abrir_binaria_externa(self):
        try:
            from algoritmos.externas.busqueda_binaria_externa import BusquedaBinariaExternaWindow
            self.ventana = BusquedaBinariaExternaWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "Error", f"No se pudo cargar Búsqueda Binaria Externa: {e}")

    def abrir_hash_mod_externo(self):
        try:
            from algoritmos.externas.hash_mod_externo import HashModExternoWindow
            self.ventana = HashModExternoWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "Error", f"No se pudo cargar Hash Módulo Externo: {e}")

    def abrir_hash_truncamiento_externo(self):
        try:
            from algoritmos.externas.hash_truncamiento_externo import HashTruncamientoExternoWindow
            self.ventana = HashTruncamientoExternoWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "Error", f"No se pudo cargar Hash Truncamiento Externo: {e}")

    def abrir_hash_plegamiento_externo(self):
        try:
            from algoritmos.externas.hash_plegamiento_externo import HashPlegamientoExternoWindow
            self.ventana = HashPlegamientoExternoWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "Error", f"No se pudo cargar Hash Plegamiento Externo: {e}")

    def abrir_hash_cambio_base_externo(self):
        try:
            from algoritmos.externas.hash_cambio_base_externo import HashCambioBaseExternoWindow
            self.ventana = HashCambioBaseExternoWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "Error", f"No se pudo cargar Hash Cambio de Base Externo: {e}")

    def abrir_expansion_total(self):
        try:
            from algoritmos.externas.estructura_expansion_total import ExpansionTotalWindow
            self.ventana = ExpansionTotalWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "Error", f"No se pudo cargar Expansión Total: {e}")

    def abrir_reduccion_total(self):
        try:
            from algoritmos.externas.estructura_reduccion_total import ReduccionTotalWindow
            self.ventana = ReduccionTotalWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "Error", f"No se pudo cargar Reducción Total: {e}")

    def abrir_expansion_parcial(self):
        try:
            from algoritmos.externas.estructura_expansion_parcial import ExpansionParcialWindow
            self.ventana = ExpansionParcialWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "Error", f"No se pudo cargar Expansión Parcial: {e}")

    def abrir_reduccion_parcial(self):
        try:
            from algoritmos.externas.estructura_reduccion_parcial import ReduccionParcialWindow
            self.ventana = ReduccionParcialWindow(
                self.mostrar_ventana_busquedas,
                self.volver_a_principal
            )
            self.ventana.show()
            self.hide()
        except ImportError as e:
            QMessageBox.information(self, "Error", f"No se pudo cargar Reducción Parcial: {e}")

    # ---------- Navegación ----------
    def mostrar_ventana_busquedas(self):
        self.show()

    def mostrar_mensaje_indices(self):
        QMessageBox.information(self, "Información", "Módulo de índices en desarrollo")

    def volver_a_principal_action(self):
        self.close()
        self.volver_a_principal()