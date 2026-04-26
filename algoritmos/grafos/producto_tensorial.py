import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSpinBox, QFileDialog, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from controladores.grafo_controller import GrafoController
from controladores.visualizador_grafo import VisualizadorGrafo
from algoritmos.grafos.dialogo_arista import DialogoArista
from algoritmos.funcion_mod import DialogoClave


class ProductoTensorialWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos = volver_a_grafos
        self.volver_a_principal = volver_a_principal

        self.grafo1 = GrafoController()
        self.grafo2 = GrafoController()

        self.setWindowTitle("Producto Tensorial de Grafos")
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
        btn_back.clicked.connect(self.volver_a_grafos)
        btn_home = QPushButton("🏠 Inicio")
        btn_home.setStyleSheet(self._button_style("#e6f2ff", "#003366"))
        btn_home.clicked.connect(self.volver_a_principal)
        header_layout.addWidget(btn_back)
        header_layout.addWidget(btn_home)
        titulo = QLabel("PRODUCTO TENSORIAL")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        header_layout.addWidget(titulo, alignment=Qt.AlignCenter)
        main_layout.addWidget(header)

        # Panel de controles (tres columnas)
        controles_frame = QFrame()
        controles_frame.setStyleSheet("background-color: #e6f2ff; border-radius: 8px;")
        controles_layout = QHBoxLayout(controles_frame)
        controles_layout.setSpacing(15)

        # Columna 1: Grafo 1 (G₁)
        g1_widget = QWidget()
        g1_layout = QVBoxLayout(g1_widget)
        g1_layout.setSpacing(8)
        lbl_g1 = QLabel("GRAFO G₁")
        lbl_g1.setStyleSheet("font-weight: bold; color: #003366;")
        g1_layout.addWidget(lbl_g1, alignment=Qt.AlignCenter)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Vértices:"))
        self.spin_v1 = QSpinBox()
        self.spin_v1.setRange(2, 6)
        self.spin_v1.setValue(3)
        self.spin_v1.setFixedWidth(60)
        btn_crear1 = QPushButton("Crear")
        btn_crear1.setStyleSheet(self._button_style("#4d9de0", "white"))
        btn_crear1.clicked.connect(lambda: self.crear_grafo(1))
        h1.addWidget(self.spin_v1)
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

        # Columna 2: Grafo 2 (G₂)
        g2_widget = QWidget()
        g2_layout = QVBoxLayout(g2_widget)
        g2_layout.setSpacing(8)
        lbl_g2 = QLabel("GRAFO G₂")
        lbl_g2.setStyleSheet("font-weight: bold; color: #003366;")
        g2_layout.addWidget(lbl_g2, alignment=Qt.AlignCenter)

        h1b = QHBoxLayout()
        h1b.addWidget(QLabel("Vértices:"))
        self.spin_v2 = QSpinBox()
        self.spin_v2.setRange(2, 6)
        self.spin_v2.setValue(3)
        self.spin_v2.setFixedWidth(60)
        btn_crear2 = QPushButton("Crear")
        btn_crear2.setStyleSheet(self._button_style("#4d9de0", "white"))
        btn_crear2.clicked.connect(lambda: self.crear_grafo(2))
        h1b.addWidget(self.spin_v2)
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

        # Columna 3: Botón de cálculo
        action_widget = QWidget()
        action_layout = QVBoxLayout(action_widget)
        action_layout.setAlignment(Qt.AlignCenter)
        self.btn_calcular = QPushButton("⊗  CALCULAR\nG₁ ⊗ G₂")
        self.btn_calcular.setFixedSize(150, 80)
        self.btn_calcular.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1a252f;
            }
        """)
        self.btn_calcular.clicked.connect(self.calcular_producto)
        action_layout.addWidget(self.btn_calcular)
        controles_layout.addWidget(action_widget)

        main_layout.addWidget(controles_frame)

        # Área de visualización (scroll)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setAlignment(Qt.AlignCenter)

        grafos_layout = QHBoxLayout()
        grafos_layout.setSpacing(15)

        self.visual_g1 = VisualizadorGrafo("Grafo G₁", es_editable=True)
        self.visual_g2 = VisualizadorGrafo("Grafo G₂", es_editable=True)
        self.visual_producto = VisualizadorGrafo("Producto Tensorial G₁ ⊗ G₂", es_editable=False)

        for vis in (self.visual_g1, self.visual_g2, self.visual_producto):
            vis.setFixedSize(380, 400)
            vis.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 8px;")
            grafos_layout.addWidget(vis)

        container_layout.addLayout(grafos_layout)

        # Botones adicionales
        extra_layout = QHBoxLayout()
        btn_guardar_prod = QPushButton("Guardar Producto")
        btn_guardar_prod.setStyleSheet(self._button_style("#3498db", "white"))
        btn_guardar_prod.clicked.connect(self.guardar_producto)
        btn_limpiar_prod = QPushButton("Limpiar Producto")
        btn_limpiar_prod.setStyleSheet(self._button_style("#95a5a6", "white"))
        btn_limpiar_prod.clicked.connect(self.limpiar_producto)
        btn_limpiar_todo = QPushButton("Limpiar Todo")
        btn_limpiar_todo.setStyleSheet(self._button_style("#e74c3c", "white"))
        btn_limpiar_todo.clicked.connect(self.limpiar_todo)
        extra_layout.addWidget(btn_guardar_prod)
        extra_layout.addWidget(btn_limpiar_prod)
        extra_layout.addWidget(btn_limpiar_todo)
        container_layout.addLayout(extra_layout)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Inicializar grafos vacíos
        self.actualizar_visual(1)
        self.actualizar_visual(2)

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
        return {
            "#4d9de0": "#3b7cb0",
            "#27ae60": "#1e8449",
            "#e74c3c": "#c0392b",
            "#3498db": "#2980b9",
            "#95a5a6": "#7f8c8d",
            "#e6f2ff": "#cce6ff",
            "#2c3e50": "#1a252f",
        }.get(color, color)

    # ========== Grafo original ==========
    def crear_grafo(self, num):
        if num == 1:
            n = self.spin_v1.value()
            self.grafo1.set_vertices(n)
            for i in range(n):
                self.grafo1._etiquetas[i] = chr(65 + i)  # A, B, C...
            self.actualizar_visual(1)
            DialogoClave(0, "Éxito", "mensaje", self, f"Grafo G₁ creado con {n} vértices.").exec()
        else:
            n = self.spin_v2.value()
            self.grafo2.set_vertices(n)
            for i in range(n):
                self.grafo2._etiquetas[i] = str(i+1)
            self.actualizar_visual(2)
            DialogoClave(0, "Éxito", "mensaje", self, f"Grafo G₂ creado con {n} vértices.").exec()

    def actualizar_visual(self, num):
        datos = self.grafo1.obtener_datos() if num == 1 else self.grafo2.obtener_datos()
        vis = self.visual_g1 if num == 1 else self.visual_g2
        vis.set_grafo(datos['vertices'], datos['aristas'], datos['etiquetas'], datos['pesos'])

    def agregar_arista(self, num):
        n = self.grafo1._vertices if num == 1 else self.grafo2._vertices
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, f"Primero crea el grafo G{num}.").exec()
            return
        etiquetas = self.grafo1._etiquetas if num == 1 else self.grafo2._etiquetas
        dlg = DialogoArista(n, self, etiquetas)
        if dlg.exec():
            u, v, peso = dlg.get_arista()
            if num == 1:
                self.grafo1.agregar_arista(u, v, peso)
                self.actualizar_visual(1)
            else:
                self.grafo2.agregar_arista(u, v, peso)
                self.actualizar_visual(2)
            DialogoClave(0, "Arista agregada", "mensaje", self, "Arista agregada.").exec()

    def eliminar_arista(self, num):
        n = self.grafo1._vertices if num == 1 else self.grafo2._vertices
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, f"Primero crea el grafo G{num}.").exec()
            return
        if not (self.grafo1._aristas if num == 1 else self.grafo2._aristas):
            DialogoClave(0, "Error", "mensaje", self, "No hay aristas para eliminar.").exec()
            return
        etiquetas = self.grafo1._etiquetas if num == 1 else self.grafo2._etiquetas
        dlg = DialogoArista(n, self, etiquetas)
        if dlg.exec():
            u, v, _ = dlg.get_arista()
            if num == 1:
                if self.grafo1.eliminar_arista(u, v):
                    self.actualizar_visual(1)
                    DialogoClave(0, "Arista eliminada", "mensaje", self, "Arista eliminada.").exec()
                else:
                    DialogoClave(0, "Error", "mensaje", self, "Arista no encontrada.").exec()
            else:
                if self.grafo2.eliminar_arista(u, v):
                    self.actualizar_visual(2)
                    DialogoClave(0, "Arista eliminada", "mensaje", self, "Arista eliminada.").exec()
                else:
                    DialogoClave(0, "Error", "mensaje", self, "Arista no encontrada.").exec()

    def guardar_grafo(self, num):
        if num == 1:
            if self.grafo1._vertices == 0:
                DialogoClave(0, "Error", "mensaje", self, "No hay grafo G₁ para guardar.").exec()
                return
            ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Grafo G₁", "", "JSON (*.json)")
            if ruta:
                self.grafo1.guardar_json(ruta)
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo G₁ guardado.").exec()
        else:
            if self.grafo2._vertices == 0:
                DialogoClave(0, "Error", "mensaje", self, "No hay grafo G₂ para guardar.").exec()
                return
            ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Grafo G₂", "", "JSON (*.json)")
            if ruta:
                self.grafo2.guardar_json(ruta)
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo G₂ guardado.").exec()

    def cargar_grafo(self, num):
        ruta, _ = QFileDialog.getOpenFileName(self, f"Cargar Grafo G{num}", "", "JSON (*.json)")
        if ruta:
            try:
                if num == 1:
                    self.grafo1.cargar_json(ruta)
                    self.spin_v1.setValue(self.grafo1._vertices)
                    self.actualizar_visual(1)
                else:
                    self.grafo2.cargar_json(ruta)
                    self.spin_v2.setValue(self.grafo2._vertices)
                    self.actualizar_visual(2)
                DialogoClave(0, "Éxito", "mensaje", self, f"Grafo G{num} cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {str(e)}").exec()

    def limpiar_grafo(self, num):
        if num == 1:
            self.grafo1.set_vertices(0)
            self.spin_v1.setValue(3)
            self.actualizar_visual(1)
        else:
            self.grafo2.set_vertices(0)
            self.spin_v2.setValue(3)
            self.actualizar_visual(2)

    # ========== Producto Tensorial ==========
    def calcular_producto(self):
        n1 = self.grafo1._vertices
        n2 = self.grafo2._vertices
        if n1 < 2 or n2 < 2:
            DialogoClave(0, "Error", "mensaje", self, "Ambos grafos deben tener al menos 2 vértices.").exec()
            return

        # Mapeo (i, j) -> índice en el producto
        mapping = {}
        idx = 0
        etiquetas_producto = {}
        for i in range(n1):
            etiq1 = self.grafo1._etiquetas.get(i, chr(65+i))
            for j in range(n2):
                etiq2 = self.grafo2._etiquetas.get(j, str(j+1))
                mapping[(i, j)] = idx
                etiquetas_producto[idx] = f"({etiq1},{etiq2})"
                idx += 1

        vertices_prod = n1 * n2
        # Conjunto de aristas existentes en G₁ y G₂ (normalizadas)
        aristas_g1 = set()
        for (u, v, _) in self.grafo1._aristas:
            if u != v:
                aristas_g1.add(tuple(sorted((u, v))))
        aristas_g2 = set()
        for (u, v, _) in self.grafo2._aristas:
            if u != v:
                aristas_g2.add(tuple(sorted((u, v))))

        # Generar aristas del producto tensorial
        aristas_prod = set()
        for (i1, j1), idx1 in mapping.items():
            for (i2, j2), idx2 in mapping.items():
                if idx1 >= idx2:
                    continue
                # Condición: arista en G₁ entre i1,i2 Y arista en G₂ entre j1,j2
                arista_g1 = tuple(sorted((i1, i2)))
                arista_g2 = tuple(sorted((j1, j2)))
                if arista_g1 in aristas_g1 and arista_g2 in aristas_g2:
                    aristas_prod.add(tuple(sorted((idx1, idx2))))

        # Visualizar
        self.visual_producto.set_grafo(vertices_prod, list(aristas_prod), etiquetas_producto, {})
        msg = (f"G₁: {n1} vértices, {len(aristas_g1)} aristas\n"
               f"G₂: {n2} vértices, {len(aristas_g2)} aristas\n\n"
               f"Producto Tensorial: {vertices_prod} vértices, {len(aristas_prod)} aristas")
        DialogoClave(0, "Producto Tensorial", "mensaje", self, msg).exec()

    def guardar_producto(self):
        if self.visual_producto.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay producto para guardar. Calcule primero.").exec()
            return
        datos = {
            'vertices': self.visual_producto.num_vertices,
            'aristas': self.visual_producto.aristas,
            'etiquetas': self.visual_producto.etiquetas,
            'pesos': self.visual_producto.pesos
        }
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Producto Tensorial", "", "JSON (*.json)")
        if ruta:
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4)
            DialogoClave(0, "Éxito", "mensaje", self, "Producto guardado.").exec()

    def limpiar_producto(self):
        self.visual_producto.set_grafo(0, [], {})

    def limpiar_todo(self):
        self.grafo1.set_vertices(0)
        self.grafo2.set_vertices(0)
        self.spin_v1.setValue(3)
        self.spin_v2.setValue(3)
        self.actualizar_visual(1)
        self.actualizar_visual(2)
        self.limpiar_producto()