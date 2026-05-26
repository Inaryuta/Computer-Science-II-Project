# ventanas_principales/ventana_grafos.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMenu, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor

class VentanaGrafos(QWidget):
    def __init__(self, volver_a_principal):
        super().__init__()
        self.volver_a_principal = volver_a_principal
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Algoritmos de Grafos")
        self.setGeometry(150, 150, 550, 500)
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
        titulo = QLabel("ALGORITMOS DE GRAFOS")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #003366; margin-bottom: 20px;")
        layout.addWidget(titulo)

        # Botón Inicio
        self.btn_inicio = QPushButton("🏠  INICIO")
        self.btn_inicio.setObjectName("boton_volver")
        self.btn_inicio.setCursor(Qt.PointingHandCursor)
        self.btn_inicio.clicked.connect(self.volver_a_principal_action)
        layout.addWidget(self.btn_inicio)

        # Botón Operaciones entre grafos
        self.btn_operaciones = QPushButton("📊  OPERACIONES ENTRE GRAFOS")
        self.btn_operaciones.setCursor(Qt.PointingHandCursor)
        self.btn_operaciones.clicked.connect(self.mostrar_menu_operaciones)
        layout.addWidget(self.btn_operaciones)

        # Botón Grafos como árboles
        self.btn_arboles = QPushButton("🌳  GRAFOS COMO ÁRBOLES")
        self.btn_arboles.setCursor(Qt.PointingHandCursor)
        self.btn_arboles.clicked.connect(self.mostrar_menu_arboles)
        layout.addWidget(self.btn_arboles)

        # Botón Algoritmos
        self.btn_algoritmos = QPushButton("⚙️  ALGORITMOS")
        self.btn_algoritmos.setCursor(Qt.PointingHandCursor)
        self.btn_algoritmos.clicked.connect(self.mostrar_menu_algoritmos)
        layout.addWidget(self.btn_algoritmos)

        layout.addStretch()

        # Crear menús
        self.menu_operaciones = QMenu()
        self.menu_operaciones.setStyleSheet(self.styleSheet())
        self.menu_arboles = QMenu()
        self.menu_arboles.setStyleSheet(self.styleSheet())
        self.menu_algoritmos = QMenu()
        self.menu_algoritmos.setStyleSheet(self.styleSheet())

        # Llenar menú de operaciones
        operaciones = [
            "Intersección", "Unión", "Suma de anillo", "Suma",
            "Fusión de vértice", "Contracción de arista", "Grafo línea",
            "Grafo complementario", "Producto cartesiano",
            "Producto tensorial", "Composición de grafos"
        ]
        for op in operaciones:
            accion = self.menu_operaciones.addAction(op)
            accion.triggered.connect(lambda checked, nombre=op: self.abrir_operacion(nombre))

        # Llenar menú de árboles
        arboles = [
            "Árboles de Grafos",          # ← unifica mínima, máxima, distancia, Dijkstra
            "Distancia entre dos árboles", # ← ya está dentro de Árboles de Grafos, pero si quieres acceso directo
        ]
        for ar in arboles:
            accion = self.menu_arboles.addAction(ar)
            accion.triggered.connect(lambda checked, nombre=ar: self.abrir_operacion(nombre))

        # Llenar menú de algoritmos
        algoritmos = [
            "Función Ordinal",
            "Bellman-Ford",
            "Dijkstra",
            "Floyd-Warshall",
            "Coloreo de Grafos",
            "Métricas Grafos No Dirigidos",
            "Métricas Grafos Dirigidos",
            "Pareamiento Grafos",
            "Conjuntos Dominantes",
        ]
        for alg in algoritmos:
            accion = self.menu_algoritmos.addAction(alg)
            accion.triggered.connect(lambda checked, nombre=alg: self.abrir_operacion(nombre))

    def mostrar_menu_operaciones(self):
        self.menu_operaciones.exec(QCursor.pos())

    def mostrar_menu_arboles(self):
        self.menu_arboles.exec(QCursor.pos())

    def mostrar_menu_algoritmos(self):
        self.menu_algoritmos.exec(QCursor.pos())

    def abrir_operacion(self, nombre):
        if nombre == "Intersección":
            from algoritmos.grafos.interseccion_grafos import InterseccionGrafosWindow
            self.ventana_interseccion = InterseccionGrafosWindow(
                self.mostrar_ventana_grafos,
                self.volver_a_principal
            )
            self.ventana_interseccion.show()
            self.hide()
        
        elif nombre == "Unión":
            from algoritmos.grafos.union_grafos import UnionGrafosWindow
            self.ventana_operacion = UnionGrafosWindow(self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show()
            self.hide()
            
        elif nombre == "Suma de anillo":
            from algoritmos.grafos.suma_anillo import SumaAnilloGrafosWindow
            self.ventana_operacion = SumaAnilloGrafosWindow(self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show()
            self.hide()
        
        elif nombre == "Suma":
            from algoritmos.grafos.suma_grafos import SumaGrafosWindow
            self.ventana_operacion = SumaGrafosWindow(self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show()
            self.hide()
        
        elif nombre == "Fusión de vértice":
            from algoritmos.grafos.fusion_vertice import FusionVerticeWindow
            self.ventana_operacion = FusionVerticeWindow(self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show()
            self.hide()
        
        elif nombre == "Contracción de arista":
            from algoritmos.grafos.contraccion_arista import ContraccionAristaWindow
            self.ventana_operacion = ContraccionAristaWindow(self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show()
            self.hide()
        
        elif nombre == "Grafo línea":
            from algoritmos.grafos.grafo_linea import GrafoLineaWindow
            self.ventana_operacion = GrafoLineaWindow(self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show()
            self.hide()
        
        elif nombre == "Grafo complementario":
            from algoritmos.grafos.grafo_complementario import GrafoComplementarioWindow
            self.ventana_operacion = GrafoComplementarioWindow(self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show()
            self.hide()
        
        elif nombre == "Producto cartesiano":
            from algoritmos.grafos.producto_cartesiano import ProductoCartesianoWindow
            self.ventana_operacion = ProductoCartesianoWindow(self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show()
            self.hide()
            
        elif nombre == "Producto tensorial":
            from algoritmos.grafos.producto_tensorial import ProductoTensorialWindow
            self.ventana_operacion = ProductoTensorialWindow(self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show()
            self.hide()
            
        elif nombre == "Composición de grafos":
            from algoritmos.grafos.composicion_grafos import ComposicionGrafosWindow
            self.ventana_operacion = ComposicionGrafosWindow(self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show()
            self.hide()
        
        elif nombre == "Bellman-Ford":
            from algoritmos.grafos.bellman_ford import BellmanFordWindow
            self.ventana_operacion = BellmanFordWindow(self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show()
            self.hide()
        
        elif nombre == "Dijkstra":
            from algoritmos.grafos.dijkstra import DijkstraWindow
            self.ventana_dijkstra = DijkstraWindow(
                self.mostrar_ventana_grafos,
                self.volver_a_principal
            )
            self.ventana_dijkstra.show()
            self.hide()
        
        elif nombre == "Floyd-Warshall":
            from algoritmos.grafos.floyd import FloydWindow
            self.ventana_operacion = FloydWindow(self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show()
            self.hide()
        
        elif nombre == "Coloreo de Grafos":
            from algoritmos.grafos.coloreo_window import ColoreoWindow
            self.ventana_operacion = ColoreoWindow(self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show()
            self.hide()
        
        elif nombre == "Métricas Grafos No Dirigidos":
            from algoritmos.grafos.metricas_grafo import MetricasGrafoWindow
            self.ventana_operacion = MetricasGrafoWindow(
                self.mostrar_ventana_grafos,
                self.volver_a_principal
            )
            self.ventana_operacion.show()
            self.hide()
 
        elif nombre == "Métricas Grafos Dirigidos":
            from algoritmos.grafos.metricas_grafo_dirigido import MetricasGrafoDirigidoWindow
            self.ventana_operacion = MetricasGrafoDirigidoWindow(
                self.mostrar_ventana_grafos,
                self.volver_a_principal
            )
            self.ventana_operacion.show()
            self.hide()
        
        elif nombre == "Paremiento Grafos":
            from algoritmos.grafos.pareamiento_grafo import PareamientoGrafoWindow
            self.ventana_operacion = PareamientoGrafoWindow(
                self.mostrar_ventana_grafos,
                self.volver_a_principal
            )
            self.ventana_operacion.show()
            self.hide()
            
        elif nombre == "Conjuntos Dominantes":
            from algoritmos.grafos.conjuntos_dominantes import ConjuntosDominantesWindow
            self.ventana_operacion = ConjuntosDominantesWindow(
                self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show(); self.hide()
            
        elif nombre in ("Árbol expansión mínima", "Árbol expansión máxima",
                        "Árboles de Grafos", "Distancia entre dos árboles"):
            from algoritmos.grafos.grafos_arboles import GrafosArbolesWindow
            self.ventana_operacion = GrafosArbolesWindow(
                self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show(); self.hide()
        
        elif nombre == "Función Ordinal":
            from algoritmos.grafos.funcion_ordinal import FuncionOrdinalWindow
            self.ventana_operacion = FuncionOrdinalWindow(
                self.mostrar_ventana_grafos, self.volver_a_principal)
            self.ventana_operacion.show(); self.hide()
                        
        else:
            QMessageBox.information(self, "En desarrollo", f"La operación '{nombre}' estará disponible próximamente.")
        
    def mostrar_ventana_grafos(self):
        self.show()

    def volver_a_principal_action(self):
        self.close()
        self.volver_a_principal()