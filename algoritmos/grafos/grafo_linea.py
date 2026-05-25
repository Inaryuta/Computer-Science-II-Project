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


class GrafoLineaWindow(QMainWindow):
    def __init__(self, callback_grafos, callback_principal):
        super().__init__()
        self.callback_grafos = callback_grafos       # callback para volver a ventana de grafos
        self.callback_principal = callback_principal # callback para volver a principal

        self.grafo = GrafoController()  # grafo original

        self.setWindowTitle("Grafo Línea")
        self.setGeometry(100, 50, 1200, 700)
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
        titulo = QLabel("GRAFO LÍNEA")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        header_layout.addWidget(titulo, alignment=Qt.AlignCenter)
        main_layout.addWidget(header)

        # Panel de controles (dos columnas)
        controles_frame = QFrame()
        controles_frame.setStyleSheet("background-color: #e6f2ff; border-radius: 8px;")
        controles_layout = QHBoxLayout(controles_frame)
        controles_layout.setSpacing(20)

        # Columna izquierda: grafo original
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(8)

        lbl_original = QLabel("GRAFO ORIGINAL")
        lbl_original.setStyleSheet("font-weight: bold; color: #003366;")
        left_layout.addWidget(lbl_original, alignment=Qt.AlignCenter)

        # Vértices
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Vértices:"))
        self.spin_vertices = QSpinBox()
        self.spin_vertices.setRange(2, 10)
        self.spin_vertices.setValue(4)
        self.spin_vertices.setFixedWidth(60)
        btn_crear = QPushButton("Crear")
        btn_crear.setStyleSheet(self._button_style("#4d9de0", "white"))
        btn_crear.clicked.connect(self.crear_grafo)
        h1.addWidget(self.spin_vertices)
        h1.addWidget(btn_crear)
        left_layout.addLayout(h1)

        # Botones aristas
        h2 = QHBoxLayout()
        btn_agregar = QPushButton("+ Arista")
        btn_agregar.setStyleSheet(self._button_style("#27ae60", "white"))
        btn_agregar.clicked.connect(self.agregar_arista)
        btn_eliminar = QPushButton("- Arista")
        btn_eliminar.setStyleSheet(self._button_style("#e74c3c", "white"))
        btn_eliminar.clicked.connect(self.eliminar_arista)
        h2.addWidget(btn_agregar)
        h2.addWidget(btn_eliminar)
        left_layout.addLayout(h2)

        # Guardar/Cargar
        h3 = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setStyleSheet(self._button_style("#3498db", "white"))
        btn_guardar.clicked.connect(self.guardar_grafo)
        btn_cargar = QPushButton("Cargar")
        btn_cargar.setStyleSheet(self._button_style("#3498db", "white"))
        btn_cargar.clicked.connect(self.cargar_grafo)
        h3.addWidget(btn_guardar)
        h3.addWidget(btn_cargar)
        left_layout.addLayout(h3)

        btn_limpiar = QPushButton("Limpiar Grafo")
        btn_limpiar.setStyleSheet(self._button_style("#95a5a6", "white"))
        btn_limpiar.clicked.connect(self.limpiar_grafo)
        left_layout.addWidget(btn_limpiar)

        controles_layout.addWidget(left_widget)

        # Columna derecha: transformación
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(8)

        lbl_transform = QLabel("TRANSFORMACIÓN")
        lbl_transform.setStyleSheet("font-weight: bold; color: #003366;")
        right_layout.addWidget(lbl_transform, alignment=Qt.AlignCenter)

        btn_generar = QPushButton("🔄 Generar Grafo Línea")
        btn_generar.setStyleSheet(self._button_style("#9c724a", "white"))
        btn_generar.clicked.connect(self.generar_grafo_linea)
        right_layout.addWidget(btn_generar)

        controles_layout.addWidget(right_widget)

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
        grafos_layout.setSpacing(20)

        self.visual_original = VisualizadorGrafo("Grafo Original", es_editable=True)
        self.visual_linea = VisualizadorGrafo("Grafo Línea L(G)", es_editable=False)

        for vis in (self.visual_original, self.visual_linea):
            vis.setFixedSize(450, 450)
            vis.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 8px;")
            grafos_layout.addWidget(vis)

        container_layout.addLayout(grafos_layout)

        # Botones adicionales
        extra_layout = QHBoxLayout()
        btn_guardar_linea = QPushButton("Guardar Grafo Línea")
        btn_guardar_linea.setStyleSheet(self._button_style("#3498db", "white"))
        btn_guardar_linea.clicked.connect(self.guardar_grafo_linea)
        btn_limpiar_resultado = QPushButton("Limpiar Resultado")
        btn_limpiar_resultado.setStyleSheet(self._button_style("#95a5a6", "white"))
        btn_limpiar_resultado.clicked.connect(self.limpiar_resultado)
        btn_limpiar_todo = QPushButton("Limpiar Todo")
        btn_limpiar_todo.setStyleSheet(self._button_style("#e74c3c", "white"))
        btn_limpiar_todo.clicked.connect(self.limpiar_todo)
        extra_layout.addWidget(btn_guardar_linea)
        extra_layout.addWidget(btn_limpiar_resultado)
        extra_layout.addWidget(btn_limpiar_todo)
        container_layout.addLayout(extra_layout)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

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
        return {
            "#4d9de0": "#3b7cb0",
            "#27ae60": "#1e8449",
            "#e74c3c": "#c0392b",
            "#3498db": "#2980b9",
            "#95a5a6": "#7f8c8d",
            "#e6f2ff": "#cce6ff",
            "#9c724a": "#6C4E31",
        }.get(color, color)

    # ========== Grafo original ==========
    def crear_grafo(self):
        n = self.spin_vertices.value()
        self.grafo.set_vertices(n)
        self.actualizar_visual_original()
        DialogoClave(0, "Éxito", "mensaje", self, f"Grafo original creado con {n} vértices.").exec()

    def actualizar_visual_original(self):
        datos = self.grafo.obtener_datos()
        self.visual_original.set_grafo(datos['vertices'], datos['aristas'],
                                       datos['etiquetas'], datos['pesos'])

    def agregar_arista(self):
        n = self.grafo._vertices
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea el grafo.").exec()
            return
        etiquetas = self.grafo._etiquetas
        dlg = DialogoArista(n, self, etiquetas)
        if dlg.exec():
            u, v, peso = dlg.get_arista()
            self.grafo.agregar_arista(u, v, peso)
            self.actualizar_visual_original()
            etiq_u = etiquetas.get(u, str(u+1))
            etiq_v = etiquetas.get(v, str(v+1))
            if u == v:
                DialogoClave(0, "Arista agregada", "mensaje", self, f"Bucle en {etiq_u} agregado.").exec()
            else:
                DialogoClave(0, "Arista agregada", "mensaje", self, f"Arista ({etiq_u} ↔ {etiq_v}) agregada.").exec()

    def eliminar_arista(self):
        n = self.grafo._vertices
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea el grafo.").exec()
            return
        if not self.grafo._aristas:
            DialogoClave(0, "Error", "mensaje", self, "No hay aristas para eliminar.").exec()
            return
        etiquetas = self.grafo._etiquetas
        dlg = DialogoArista(n, self, etiquetas)
        if dlg.exec():
            u, v, _ = dlg.get_arista()
            if self.grafo.eliminar_arista(u, v):
                self.actualizar_visual_original()
                DialogoClave(0, "Arista eliminada", "mensaje", self, "Arista eliminada.").exec()
            else:
                DialogoClave(0, "Error", "mensaje", self, "Arista no encontrada.").exec()

    def guardar_grafo(self):
        if self.grafo._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay grafo para guardar.").exec()
            return
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Grafo", "", "JSON (*.json)")
        if ruta:
            self.grafo.guardar_json(ruta)
            DialogoClave(0, "Éxito", "mensaje", self, "Grafo guardado.").exec()

    def cargar_grafo(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar Grafo", "", "JSON (*.json)")
        if ruta:
            try:
                self.grafo.cargar_json(ruta)
                self.spin_vertices.setValue(self.grafo._vertices)
                self.actualizar_visual_original()
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {str(e)}").exec()

    def limpiar_grafo(self):
        self.grafo.set_vertices(0)
        self.spin_vertices.setValue(4)
        self.actualizar_visual_original()

    # ========== Grafo línea ==========
    def generar_grafo_linea(self):
        n_vertices = self.grafo._vertices
        aristas_original = self.grafo._aristas  # lista de tuplas (u,v,peso)
        if n_vertices < 2:
            DialogoClave(0, "Error", "mensaje", self, "Se necesitan al menos 2 vértices.").exec()
            return
        if len(aristas_original) < 1:
            DialogoClave(0, "Error", "mensaje", self, "El grafo debe tener al menos una arista.").exec()
            return

        m = len(aristas_original)
        # Etiquetas para los vértices del grafo línea
        etiquetas_linea = {}
        for idx, (u, v, peso) in enumerate(aristas_original):
            etiq_u = self.grafo._etiquetas.get(u, str(u+1))
            etiq_v = self.grafo._etiquetas.get(v, str(v+1))
            if peso:
                etiquetas_linea[idx] = f"{etiq_u}{etiq_v}[{peso}]"
            else:
                etiquetas_linea[idx] = f"{etiq_u}{etiq_v}"

        # Construir aristas del grafo línea
        aristas_linea = []
        for i in range(m):
            for j in range(i+1, m):
                u1, v1, _ = aristas_original[i]
                u2, v2, _ = aristas_original[j]
                # Comparten algún vértice?
                if (u1 == u2 or u1 == v2 or v1 == u2 or v1 == v2):
                    aristas_linea.append((i, j))

        # Visualizar
        self.visual_linea.set_grafo(m, aristas_linea, etiquetas_linea, {})
        DialogoClave(0, "Grafo Línea generado", "mensaje", self,
                     f"Vértices: {m} (cada arista original)\nAristas: {len(aristas_linea)}").exec()

    def guardar_grafo_linea(self):
        if self.visual_linea.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay grafo línea para guardar. Génere primero.").exec()
            return
        datos = {
            'vertices': self.visual_linea.num_vertices,
            'aristas': self.visual_linea.aristas,
            'etiquetas': self.visual_linea.etiquetas,
            'pesos': self.visual_linea.pesos
        }
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Grafo Línea", "", "JSON (*.json)")
        if ruta:
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4)
            DialogoClave(0, "Éxito", "mensaje", self, "Grafo línea guardado.").exec()

    def limpiar_resultado(self):
        self.visual_linea.set_grafo(0, [], {})

    def limpiar_todo(self):
        self.grafo.set_vertices(0)
        self.spin_vertices.setValue(4)
        self.actualizar_visual_original()
        self.limpiar_resultado()