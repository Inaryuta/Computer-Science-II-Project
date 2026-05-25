# algoritmos/grafos/interseccion_grafos.py
import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QScrollArea, QFrame, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from controladores.grafo_controller import GrafoController
from controladores.visualizador_grafo import VisualizadorGrafo
from algoritmos.grafos.dialogo_arista import DialogoArista
from algoritmos.funcion_mod import DialogoClave

class InterseccionGrafosWindow(QMainWindow):
    def __init__(self, callback_grafos, callback_principal):
        super().__init__()
        self.callback_grafos = callback_grafos       
        self.callback_principal = callback_principal 

        self.grafo1 = GrafoController()
        self.grafo2 = GrafoController()

        self.setWindowTitle("Intersección de Grafos")
        self.setGeometry(100, 50, 1400, 800)
        self.setStyleSheet("background-color: #f0f8ff;")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #cce6ff; border-radius: 10px;")
        header_layout = QHBoxLayout(header)
        btn_back = QPushButton("← Volver a Grafos")
        btn_back.setStyleSheet(self._button_style("#e6f2ff", "#003366"))
        btn_back.clicked.connect(self.volver_a_grafos)   # conecta al método
        btn_home = QPushButton("🏠 Inicio")
        btn_home.setStyleSheet(self._button_style("#e6f2ff", "#003366"))
        btn_home.clicked.connect(self.volver_a_principal) # conecta al método
        header_layout.addWidget(btn_back)
        header_layout.addWidget(btn_home)
        titulo = QLabel("INTERSECCIÓN DE GRAFOS")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        header_layout.addWidget(titulo, alignment=Qt.AlignCenter)
        main_layout.addWidget(header)

        # Panel de controles
        controles_frame = QFrame()
        controles_frame.setStyleSheet("background-color: #e6f2ff; border-radius: 8px;")
        controles_layout = QHBoxLayout(controles_frame)

        # Grafo 1
        g1_widget = QWidget()
        g1_layout = QVBoxLayout(g1_widget)
        lbl_g1 = QLabel("GRAFO 1")
        lbl_g1.setStyleSheet("font-weight: bold; color: #003366;")
        g1_layout.addWidget(lbl_g1, alignment=Qt.AlignCenter)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Vértices:"))
        self.spin_v1 = QSpinBox()
        self.spin_v1.setRange(1, 10)
        self.spin_v1.setValue(4)
        h1.addWidget(self.spin_v1)
        btn_crear1 = QPushButton("Crear")
        btn_crear1.setStyleSheet(self._button_style("#4d9de0", "white"))
        btn_crear1.clicked.connect(lambda: self.crear_grafo(1))
        h1.addWidget(btn_crear1)
        g1_layout.addLayout(h1)

        h2 = QHBoxLayout()
        btn_agregar1 = QPushButton("+ Arista")
        btn_agregar1.setStyleSheet(self._button_style("#27ae60", "white"))
        btn_agregar1.clicked.connect(lambda: self.agregar_arista(1))
        btn_eliminar1 = QPushButton("- Arista")
        btn_eliminar1.setStyleSheet(self._button_style("#e74c3c", "white"))
        btn_eliminar1.clicked.connect(lambda: self.eliminar_arista(1))
        h2.addWidget(btn_agregar1)
        h2.addWidget(btn_eliminar1)
        g1_layout.addLayout(h2)

        h3 = QHBoxLayout()
        btn_guardar1 = QPushButton("Guardar")
        btn_guardar1.setStyleSheet(self._button_style("#3498db", "white"))
        btn_guardar1.clicked.connect(lambda: self.guardar_grafo(1))
        btn_cargar1 = QPushButton("Cargar")
        btn_cargar1.setStyleSheet(self._button_style("#3498db", "white"))
        btn_cargar1.clicked.connect(lambda: self.cargar_grafo(1))
        h3.addWidget(btn_guardar1)
        h3.addWidget(btn_cargar1)
        g1_layout.addLayout(h3)

        btn_limpiar1 = QPushButton("Limpiar Grafo")
        btn_limpiar1.setStyleSheet(self._button_style("#95a5a6", "white"))
        btn_limpiar1.clicked.connect(lambda: self.limpiar_grafo(1))
        g1_layout.addWidget(btn_limpiar1)

        controles_layout.addWidget(g1_widget)

        # Botón calcular
        self.btn_calcular = QPushButton("CALCULAR INTERSECCIÓN")
        self.btn_calcular.setFixedHeight(80)
        self.btn_calcular.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1a252f;
            }
        """)
        self.btn_calcular.clicked.connect(self.calcular_interseccion)
        controles_layout.addWidget(self.btn_calcular)

        # Grafo 2
        g2_widget = QWidget()
        g2_layout = QVBoxLayout(g2_widget)
        lbl_g2 = QLabel("GRAFO 2")
        lbl_g2.setStyleSheet("font-weight: bold; color: #003366;")
        g2_layout.addWidget(lbl_g2, alignment=Qt.AlignCenter)

        h1b = QHBoxLayout()
        h1b.addWidget(QLabel("Vértices:"))
        self.spin_v2 = QSpinBox()
        self.spin_v2.setRange(1, 10)
        self.spin_v2.setValue(4)
        h1b.addWidget(self.spin_v2)
        btn_crear2 = QPushButton("Crear")
        btn_crear2.setStyleSheet(self._button_style("#4d9de0", "white"))
        btn_crear2.clicked.connect(lambda: self.crear_grafo(2))
        h1b.addWidget(btn_crear2)
        g2_layout.addLayout(h1b)

        h2b = QHBoxLayout()
        btn_agregar2 = QPushButton("+ Arista")
        btn_agregar2.setStyleSheet(self._button_style("#27ae60", "white"))
        btn_agregar2.clicked.connect(lambda: self.agregar_arista(2))
        btn_eliminar2 = QPushButton("- Arista")
        btn_eliminar2.setStyleSheet(self._button_style("#e74c3c", "white"))
        btn_eliminar2.clicked.connect(lambda: self.eliminar_arista(2))
        h2b.addWidget(btn_agregar2)
        h2b.addWidget(btn_eliminar2)
        g2_layout.addLayout(h2b)

        h3b = QHBoxLayout()
        btn_guardar2 = QPushButton("Guardar")
        btn_guardar2.setStyleSheet(self._button_style("#3498db", "white"))
        btn_guardar2.clicked.connect(lambda: self.guardar_grafo(2))
        btn_cargar2 = QPushButton("Cargar")
        btn_cargar2.setStyleSheet(self._button_style("#3498db", "white"))
        btn_cargar2.clicked.connect(lambda: self.cargar_grafo(2))
        h3b.addWidget(btn_guardar2)
        h3b.addWidget(btn_cargar2)
        g2_layout.addLayout(h3b)

        btn_limpiar2 = QPushButton("Limpiar Grafo")
        btn_limpiar2.setStyleSheet(self._button_style("#95a5a6", "white"))
        btn_limpiar2.clicked.connect(lambda: self.limpiar_grafo(2))
        g2_layout.addWidget(btn_limpiar2)

        controles_layout.addWidget(g2_widget)
        main_layout.addWidget(controles_frame)

        # Área de visualización con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setAlignment(Qt.AlignCenter)

        grafos_layout = QHBoxLayout()
        grafos_layout.setSpacing(20)

        self.visual1 = VisualizadorGrafo("Grafo 1", es_editable=True)
        self.visual2 = VisualizadorGrafo("Grafo 2", es_editable=True)
        self.visual_interseccion = VisualizadorGrafo("Intersección", es_editable=False)

        for vis in (self.visual1, self.visual2, self.visual_interseccion):
            vis.setFixedSize(400, 450)
            vis.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 8px;")
            grafos_layout.addWidget(vis)

        container_layout.addLayout(grafos_layout)

        # Botones adicionales
        extra_layout = QHBoxLayout()
        btn_guardar_inter = QPushButton("Guardar Intersección")
        btn_guardar_inter.setStyleSheet(self._button_style("#3498db", "white"))
        btn_guardar_inter.clicked.connect(self.guardar_interseccion)
        btn_limpiar_inter = QPushButton("Limpiar Intersección")
        btn_limpiar_inter.setStyleSheet(self._button_style("#95a5a6", "white"))
        btn_limpiar_inter.clicked.connect(self.limpiar_interseccion)
        btn_limpiar_todo = QPushButton("Limpiar Todo")
        btn_limpiar_todo.setStyleSheet(self._button_style("#e74c3c", "white"))
        btn_limpiar_todo.clicked.connect(self.limpiar_todo)
        extra_layout.addWidget(btn_guardar_inter)
        extra_layout.addWidget(btn_limpiar_inter)
        extra_layout.addWidget(btn_limpiar_todo)
        container_layout.addLayout(extra_layout)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # No crear grafos automáticamente al inicio

    # ========== Navegación (métodos de instancia) ==========
    def volver_a_grafos(self):
        self.close()
        self.callback_grafos()

    def volver_a_principal(self):
        self.close()
        self.callback_principal()

    # ========== Estilos ==========
    def _button_style(self, bg_color, text_color):
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(bg_color)};
            }}
        """

    def _darken_color(self, color):
        if color == "#4d9de0":
            return "#3b7cb0"
        elif color == "#27ae60":
            return "#1e8449"
        elif color == "#e74c3c":
            return "#c0392b"
        elif color == "#3498db":
            return "#2980b9"
        elif color == "#95a5a6":
            return "#7f8c8d"
        elif color == "#e6f2ff":
            return "#cce6ff"
        return color

    # ========== Funciones del grafo ==========
    def crear_grafo(self, num):
        if num == 1:
            n = self.spin_v1.value()
            self.grafo1.set_vertices(n)
            self.actualizar_visual(1)
        else:
            n = self.spin_v2.value()
            self.grafo2.set_vertices(n)
            self.actualizar_visual(2)

    def actualizar_visual(self, num):
        datos = self.grafo1.obtener_datos() if num == 1 else self.grafo2.obtener_datos()
        vis = self.visual1 if num == 1 else self.visual2
        vis.set_grafo(datos['vertices'], datos['aristas'], datos['etiquetas'], datos['pesos'])

    def agregar_arista(self, num):
        n = self.grafo1._vertices if num == 1 else self.grafo2._vertices
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea el grafo.").exec()
            return
        etiquetas = self.grafo1._etiquetas if num == 1 else self.grafo2._etiquetas
        dlg = DialogoArista(n, self, etiquetas)
        if dlg.exec():
            u, v, peso = dlg.get_arista()
            etiq_u = etiquetas.get(u, str(u+1))
            etiq_v = etiquetas.get(v, str(v+1))
            if num == 1:
                ok = self.grafo1.agregar_arista(u, v, peso)
            else:
                ok = self.grafo2.agregar_arista(u, v, peso)
            if ok:
                self.actualizar_visual(num)
                DialogoClave(0, "Arista agregada", "mensaje", self,
                             f"Arista ({etiq_u} ↔ {etiq_v}) agregada.").exec()
            else:
                DialogoClave(0, "Error", "mensaje", self, "La arista ya existe.").exec()

    def eliminar_arista(self, num):
        n = self.grafo1._vertices if num == 1 else self.grafo2._vertices
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea el grafo.").exec()
            return
        etiquetas = self.grafo1._etiquetas if num == 1 else self.grafo2._etiquetas
        dlg = DialogoArista(n, self, etiquetas)
        if dlg.exec():
            u, v, _ = dlg.get_arista()
            etiq_u = etiquetas.get(u, str(u+1))
            etiq_v = etiquetas.get(v, str(v+1))
            if num == 1:
                ok = self.grafo1.eliminar_arista(u, v)
            else:
                ok = self.grafo2.eliminar_arista(u, v)
            if ok:
                self.actualizar_visual(num)
                DialogoClave(0, "Arista eliminada", "mensaje", self,
                             f"Arista ({etiq_u} ↔ {etiq_v}) eliminada.").exec()
            else:
                DialogoClave(0, "Error", "mensaje", self, "La arista no existe.").exec()

    def guardar_grafo(self, num):
        ruta, _ = QFileDialog.getSaveFileName(self, f"Guardar Grafo {num}", "", "JSON (*.json)")
        if ruta:
            if num == 1:
                self.grafo1.guardar_json(ruta)
            else:
                self.grafo2.guardar_json(ruta)
            DialogoClave(0, "Éxito", "mensaje", self, f"Grafo {num} guardado.").exec()

    def cargar_grafo(self, num):
        ruta, _ = QFileDialog.getOpenFileName(self, f"Cargar Grafo {num}", "", "JSON (*.json)")
        if ruta:
            try:
                if num == 1:
                    self.grafo1.cargar_json(ruta)
                    self.spin_v1.setValue(self.grafo1._vertices)
                else:
                    self.grafo2.cargar_json(ruta)
                    self.spin_v2.setValue(self.grafo2._vertices)
                self.actualizar_visual(num)
                DialogoClave(0, "Éxito", "mensaje", self, f"Grafo {num} cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {str(e)}").exec()

    def limpiar_grafo(self, num):
        if num == 1:
            self.grafo1.set_vertices(0)
            self.spin_v1.setValue(4)
        else:
            self.grafo2.set_vertices(0)
            self.spin_v2.setValue(4)
        self.actualizar_visual(num)

    def calcular_interseccion(self):
        if self.grafo1._vertices == 0 or self.grafo2._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Ambos grafos deben tener al menos un vértice.").exec()
            return

        etiq1 = set(self.grafo1._etiquetas.values())
        etiq2 = set(self.grafo2._etiquetas.values())
        comunes = etiq1.intersection(etiq2)
        if not comunes:
            self.visual_interseccion.set_grafo(0, [], {})
            DialogoClave(0, "Intersección vacía", "mensaje", self, "No hay vértices con etiquetas comunes.").exec()
            return

        idx1 = {v: k for k, v in self.grafo1._etiquetas.items()}
        idx2 = {v: k for k, v in self.grafo2._etiquetas.items()}
        nuevo_idx = {}
        nuevas_etiquetas = {}
        for i, etiq in enumerate(sorted(comunes)):
            nuevo_idx[etiq] = i
            nuevas_etiquetas[i] = etiq

        pesos_int = {}
        for u1, v1, peso in self.grafo1._aristas:
            etiq_u = self.grafo1._etiquetas.get(u1)
            etiq_v = self.grafo1._etiquetas.get(v1)
            if etiq_u in comunes and etiq_v in comunes:
                u2 = idx2.get(etiq_u)
                v2 = idx2.get(etiq_v)
                if u2 is not None and v2 is not None:
                    existe_en_g2 = any((x == u2 and y == v2) or (x == v2 and y == u2) for (x, y, _) in self.grafo2._aristas)
                    if existe_en_g2:
                        nu = nuevo_idx[etiq_u]
                        nv = nuevo_idx[etiq_v]
                        if nu > nv:
                            nu, nv = nv, nu
                        arista = (nu, nv)
                        if arista not in pesos_int:
                            pesos_int[arista] = peso

        aristas_finales = list(pesos_int.keys())
        pesos_finales = [pesos_int[a] for a in aristas_finales]

        self.visual_interseccion.set_grafo(len(comunes), aristas_finales, nuevas_etiquetas, pesos_finales)
        DialogoClave(0, "Intersección calculada", "mensaje", self,
                     f"Vértices comunes: {len(comunes)}\nAristas comunes: {len(aristas_finales)}").exec()

    def guardar_interseccion(self):
        if self.visual_interseccion.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay intersección para guardar.").exec()
            return
        datos = {
            'vertices': self.visual_interseccion.num_vertices,
            'aristas': self.visual_interseccion.aristas,
            'etiquetas': self.visual_interseccion.etiquetas,
            'pesos': {str(a): p for a, p in zip(self.visual_interseccion.aristas, self.visual_interseccion.pesos)}
        }
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Intersección", "", "JSON (*.json)")
        if ruta:
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4)
            DialogoClave(0, "Éxito", "mensaje", self, "Intersección guardada.").exec()

    def limpiar_interseccion(self):
        self.visual_interseccion.set_grafo(0, [], {})

    def limpiar_todo(self):
        self.grafo1.set_vertices(0)
        self.grafo2.set_vertices(0)
        self.spin_v1.setValue(4)
        self.spin_v2.setValue(4)
        self.actualizar_visual(1)
        self.actualizar_visual(2)
        self.limpiar_interseccion()