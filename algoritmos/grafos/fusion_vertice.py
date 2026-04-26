import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSpinBox, QFileDialog, QScrollArea, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from controladores.grafo_controller import GrafoController
from controladores.visualizador_grafo import VisualizadorGrafo
from algoritmos.grafos.dialogo_arista import DialogoArista
from algoritmos.funcion_mod import DialogoClave


class FusionVerticeWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos = volver_a_grafos
        self.volver_a_principal = volver_a_principal

        self.grafo = GrafoController()

        self.setWindowTitle("Fusión de Vértices")
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
        titulo = QLabel("FUSIÓN DE VÉRTICES")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        header_layout.addWidget(titulo, alignment=Qt.AlignCenter)
        main_layout.addWidget(header)

        # Panel de controles
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

        # Archivo
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

        # Columna derecha: fusión
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(8)

        lbl_fusion = QLabel("FUSIÓN")
        lbl_fusion.setStyleSheet("font-weight: bold; color: #003366;")
        right_layout.addWidget(lbl_fusion, alignment=Qt.AlignCenter)

        # Combo para vértice 1
        sel1 = QHBoxLayout()
        sel1.addWidget(QLabel("Vértice 1:"))
        self.combo_v1 = QComboBox()
        self.combo_v1.setFixedWidth(100)
        sel1.addWidget(self.combo_v1)
        right_layout.addLayout(sel1)

        # Combo para vértice 2
        sel2 = QHBoxLayout()
        sel2.addWidget(QLabel("Vértice 2:"))
        self.combo_v2 = QComboBox()
        self.combo_v2.setFixedWidth(100)
        sel2.addWidget(self.combo_v2)
        right_layout.addLayout(sel2)

        btn_fusionar = QPushButton("🔗 Fusionar")
        btn_fusionar.setStyleSheet(self._button_style("#9c724a", "white"))
        btn_fusionar.clicked.connect(self.fusionar_vertices)
        right_layout.addWidget(btn_fusionar)

        controles_layout.addWidget(right_widget)

        main_layout.addWidget(controles_frame)

        # Área de visualización
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
        self.visual_fusion = VisualizadorGrafo("Grafo Fusionado", es_editable=False)

        for vis in (self.visual_original, self.visual_fusion):
            vis.setFixedSize(450, 450)
            vis.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 8px;")
            grafos_layout.addWidget(vis)

        container_layout.addLayout(grafos_layout)

        # Botones extras
        extra_layout = QHBoxLayout()
        btn_guardar_fusion = QPushButton("Guardar Fusión")
        btn_guardar_fusion.setStyleSheet(self._button_style("#3498db", "white"))
        btn_guardar_fusion.clicked.connect(self.guardar_fusion)
        btn_limpiar_fusion = QPushButton("Limpiar Fusión")
        btn_limpiar_fusion.setStyleSheet(self._button_style("#95a5a6", "white"))
        btn_limpiar_fusion.clicked.connect(self.limpiar_fusion)
        btn_limpiar_todo = QPushButton("Limpiar Todo")
        btn_limpiar_todo.setStyleSheet(self._button_style("#e74c3c", "white"))
        btn_limpiar_todo.clicked.connect(self.limpiar_todo)
        extra_layout.addWidget(btn_guardar_fusion)
        extra_layout.addWidget(btn_limpiar_fusion)
        extra_layout.addWidget(btn_limpiar_todo)
        container_layout.addLayout(extra_layout)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        self.actualizar_combos()  # Inicializar combos vacíos

    # Estilos
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
        if color == "#4d9de0": return "#3b7cb0"
        if color == "#27ae60": return "#1e8449"
        if color == "#e74c3c": return "#c0392b"
        if color == "#3498db": return "#2980b9"
        if color == "#95a5a6": return "#7f8c8d"
        if color == "#e6f2ff": return "#cce6ff"
        return color

    # --- Grafo original ---
    def crear_grafo(self):
        n = self.spin_vertices.value()
        self.grafo.set_vertices(n)
        self.actualizar_visual()
        self.actualizar_combos()
        DialogoClave(0, "Éxito", "mensaje", self, f"Grafo creado con {n} vértices.").exec()

    def actualizar_visual(self):
        datos = self.grafo.obtener_datos()
        self.visual_original.set_grafo(datos['vertices'], datos['aristas'], datos['etiquetas'], datos['pesos'])

    def agregar_arista(self):
        n = self.grafo._vertices
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea el grafo.").exec()
            return
        etiquetas = self.grafo._etiquetas
        dlg = DialogoArista(n, self, etiquetas)
        if dlg.exec():
            u, v, peso = dlg.get_arista()
            ok = self.grafo.agregar_arista(u, v, peso)
            if ok:
                self.actualizar_visual()
                etiq_u = etiquetas.get(u, str(u+1))
                etiq_v = etiquetas.get(v, str(v+1))
                if u == v:
                    DialogoClave(0, "Arista agregada", "mensaje", self, f"Bucle en {etiq_u} agregado.").exec()
                else:
                    DialogoClave(0, "Arista agregada", "mensaje", self, f"Arista ({etiq_u} ↔ {etiq_v}) agregada.").exec()
            else:
                DialogoClave(0, "Error", "mensaje", self, "No se pudo agregar la arista.").exec()

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
            # Elimina la primera coincidencia
            ok = self.grafo.eliminar_arista(u, v)
            if ok:
                self.actualizar_visual()
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
                self.actualizar_visual()
                self.actualizar_combos()
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {str(e)}").exec()

    def limpiar_grafo(self):
        self.grafo.set_vertices(0)
        self.spin_vertices.setValue(4)
        self.actualizar_visual()
        self.actualizar_combos()

    # --- Fusión ---
    def actualizar_combos(self):
        n = self.grafo._vertices
        self.combo_v1.clear()
        self.combo_v2.clear()
        for i in range(n):
            etiq = self.grafo._etiquetas.get(i, str(i+1))
            self.combo_v1.addItem(f"{i+1}: {etiq}", i)
            self.combo_v2.addItem(f"{i+1}: {etiq}", i)

    def fusionar_vertices(self):
        n = self.grafo._vertices
        if n < 2:
            DialogoClave(0, "Error", "mensaje", self, "Se necesitan al menos 2 vértices para fusionar.").exec()
            return
        idx1 = self.combo_v1.currentData()
        idx2 = self.combo_v2.currentData()
        if idx1 == idx2:
            DialogoClave(0, "Error", "mensaje", self, "Los vértices deben ser diferentes.").exec()
            return
        # Ordenar para que idx1 < idx2 (consistencia)
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
        etiq1 = self.grafo._etiquetas.get(idx1, str(idx1+1))
        etiq2 = self.grafo._etiquetas.get(idx2, str(idx2+1))
        nueva_etiq = f"{etiq1},{etiq2}"

        # Mapeo de índices antiguos a nuevos
        mapeo = {}
        nuevo_idx = 0
        for i in range(n):
            if i == idx1:
                mapeo[i] = nuevo_idx
                nuevo_idx += 1
            elif i == idx2:
                mapeo[i] = mapeo[idx1]  # mismo nuevo índice
            else:
                mapeo[i] = nuevo_idx
                nuevo_idx += 1
        vertices_fusion = n - 1

        # Etiquetas del nuevo grafo
        etiquetas_fusion = {}
        for old, new in mapeo.items():
            if old != idx2:  # solo añadir una vez por cada vértice original (excepto idx2)
                if old == idx1:
                    etiquetas_fusion[new] = nueva_etiq
                else:
                    etiquetas_fusion[new] = self.grafo._etiquetas.get(old, str(old+1))

        # Recolectar aristas, excluyendo la arista directa entre idx1 y idx2
        aristas_fusion = []
        pesos_fusion = []
        for (u, v, p) in self.grafo._aristas:
            nu = mapeo[u]
            nv = mapeo[v]
            # Saltar la arista que conecta directamente los dos vértices fusionados
            if (u == idx1 and v == idx2) or (u == idx2 and v == idx1):
                continue
            aristas_fusion.append((nu, nv))
            pesos_fusion.append(p)

        self.visual_fusion.set_grafo(vertices_fusion, aristas_fusion, etiquetas_fusion, pesos_fusion)
        DialogoClave(0, "Fusión completada", "mensaje", self,
                     f"Vértices '{etiq1}' y '{etiq2}' fusionados en '{nueva_etiq}'.\n"
                     f"Vértices resultantes: {vertices_fusion}\nAristas: {len(aristas_fusion)}").exec()

    def guardar_fusion(self):
        if self.visual_fusion.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay fusión para guardar.").exec()
            return
        datos = {
            'vertices': self.visual_fusion.num_vertices,
            'aristas': self.visual_fusion.aristas,
            'etiquetas': self.visual_fusion.etiquetas,
            'pesos': self.visual_fusion.pesos
        }
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Fusión", "", "JSON (*.json)")
        if ruta:
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4)
            DialogoClave(0, "Éxito", "mensaje", self, "Fusión guardada.").exec()

    def limpiar_fusion(self):
        self.visual_fusion.set_grafo(0, [], {})

    def limpiar_todo(self):
        self.grafo.set_vertices(0)
        self.spin_vertices.setValue(4)
        self.actualizar_visual()
        self.actualizar_combos()
        self.limpiar_fusion()