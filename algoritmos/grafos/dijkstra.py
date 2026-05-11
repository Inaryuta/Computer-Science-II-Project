# algoritmos/grafos/dijkstra.py
import json
import heapq
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTextEdit, QSpinBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from controladores.visualizador_grafo_dirigido import VisualizadorGrafoDirigido
from algoritmos.funcion_mod import DialogoClave


# ========================= MODELO INTERNO DEL GRAFO =========================
class ModeloGrafoInterno:
    def __init__(self):
        self.num_vertices = 0
        self.aristas = []               # lista de tuplas (origen, destino)
        self.etiquetas = {}             # {índice: etiqueta} (se usarán números 1..n)
        self.ponderaciones = []         # lista paralela a aristas (pesos)

    def crear_grafo(self, num_vertices):
        self.num_vertices = num_vertices
        self.aristas = []
        self.etiquetas = {i: str(i+1) for i in range(num_vertices)}
        self.ponderaciones = []

    def agregar_arista(self, origen, destino):
        if origen < 0 or origen >= self.num_vertices or destino < 0 or destino >= self.num_vertices:
            return False
        arista = (origen, destino)
        if arista not in self.aristas:
            self.aristas.append(arista)
            self.ponderaciones.append("")
            return True
        return False

    def eliminar_ultima_arista(self):
        if self.aristas:
            self.aristas.pop()
            self.ponderaciones.pop()

    def obtener_aristas(self):
        return self.aristas.copy()

    def obtener_ponderaciones(self):
        return self.ponderaciones.copy()

    def obtener_etiquetas(self):
        return self.etiquetas.copy()

    def obtener_num_vertices(self):
        return self.num_vertices

    def guardar_grafo(self, ruta):
        datos = {
            'num_vertices': self.num_vertices,
            'aristas': self.aristas,
            'etiquetas': self.etiquetas,
            'ponderaciones': self.ponderaciones
        }
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4)

    def cargar_grafo(self, ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        self.num_vertices = datos['num_vertices']
        self.aristas = [tuple(a) for a in datos['aristas']]
        self.etiquetas = {int(k): v for k, v in datos['etiquetas'].items()}
        self.ponderaciones = datos.get('ponderaciones', [])


# =================== VISUALIZADOR ESPECIAL PARA DIJKSTRA ===================
class VisualizadorDijkstra(VisualizadorGrafoDirigido):
    def __init__(self, titulo="Dijkstra", parent=None):
        super().__init__(titulo, parent, es_editable=False)
        self.distancias_minimas = {}
        self.todos_caminos = {}
        self.vertice_origen = None
        self.textos_caminos = []  # para guardar los items de texto y poder eliminarlos

    def set_resultado_dijkstra(self, distancias, todos_caminos, origen):
        self.distancias_minimas = distancias
        self.todos_caminos = todos_caminos
        self.vertice_origen = origen
        self._actualizar_textos_caminos()

    def limpiar_resultados(self):
        self.distancias_minimas = {}
        self.todos_caminos = {}
        self.vertice_origen = None
        self._limpiar_textos_caminos()

    def set_grafo(self, num_vertices, aristas, etiquetas, pesos=None):
        super().set_grafo(num_vertices, aristas, etiquetas, pesos)
        self._limpiar_textos_caminos()
        self.distancias_minimas = {}
        self.todos_caminos = {}
        self.vertice_origen = None

    def _limpiar_textos_caminos(self):
        for item in self.textos_caminos:
            self.scene.removeItem(item)
        self.textos_caminos.clear()

    def _actualizar_textos_caminos(self):
        self._limpiar_textos_caminos()
        if not self.todos_caminos or not self.posiciones:
            return

        for i, (x, y) in enumerate(self.posiciones):
            if i == self.vertice_origen:
                continue
            if i not in self.todos_caminos or not self.todos_caminos[i]:
                continue
            # Tomar el mejor camino (distancia mínima)
            mejor = min(self.todos_caminos[i], key=lambda x: x[0])
            distancia, camino = mejor
            if distancia == float('inf'):
                continue
            # Formatear texto
            dist_str = str(int(distancia)) if distancia % 1 == 0 else str(distancia)
            if len(camino) >= 2:
                prev = camino[-2]
                info = f"[{dist_str}, {prev+1}]"
            else:
                info = f"[0, {i+1}]"
            camino_str = '→'.join(str(v+1) for v in camino)
            texto = f"{info} {camino_str} ✓"
            # Crear elemento de texto
            text_item = self.scene.addText(texto)
            text_item.setDefaultTextColor(QColor("#2ecc71"))
            font = QFont("Arial", 9, QFont.Bold)
            text_item.setFont(font)
            # Posicionar a la derecha del vértice
            rect = text_item.boundingRect()
            text_item.setPos(x + 25, y - rect.height()/2)
            self.textos_caminos.append(text_item)


# ========================= VENTANA PRINCIPAL =========================
class DijkstraWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos = volver_a_grafos
        self.volver_a_principal = volver_a_principal

        self.modelo = ModeloGrafoInterno()

        self.setWindowTitle("Algoritmo de Dijkstra")
        self.setGeometry(150, 80, 1300, 750)
        self.setStyleSheet("background-color: #f0f8ff;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # ----- Header -----
        header = QFrame()
        header.setStyleSheet("background-color: #cce6ff; border-radius: 10px;")
        header_layout = QHBoxLayout(header)

        btn_back = QPushButton("← Volver a Grafos")
        btn_back.setStyleSheet(self._button_style("#e6f2ff", "#003366"))
        btn_back.clicked.connect(self.cerrar_y_volver_a_grafos)

        btn_home = QPushButton("🏠 Inicio")
        btn_home.setStyleSheet(self._button_style("#e6f2ff", "#003366"))
        btn_home.clicked.connect(self.cerrar_y_volver_a_principal)

        titulo = QLabel("DIJKSTRA")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        header_layout.addWidget(btn_back)
        header_layout.addWidget(btn_home)
        header_layout.addWidget(titulo, alignment=Qt.AlignCenter)

        layout.addWidget(header)

        # ----- Cuerpo (tres columnas) -----
        cuerpo = QHBoxLayout()

        # Panel izquierdo: visualización del grafo
        panel_visual = QFrame()
        panel_visual.setStyleSheet("background-color: #e6f2ff; border-radius: 8px; padding: 10px;")
        visual_layout = QVBoxLayout(panel_visual)
        self.visualizador = VisualizadorDijkstra("Grafo Dirigido", self)
        visual_layout.addWidget(self.visualizador, alignment=Qt.AlignCenter)
        leyenda = QLabel(
            "<b>Leyenda:</b><br>"
            "<span style='color: #2ecc71;'>[peso] camino ✓</span> = Camino más corto<br>"
            "<i>Los vértices no son editables; las etiquetas son numéricas.</i>"
        )
        leyenda.setStyleSheet("background-color: white; border-radius: 4px; padding: 5px; color: #003366;")
        visual_layout.addWidget(leyenda)
        cuerpo.addWidget(panel_visual, 2)

        # Panel central: construcción del grafo
        panel_grafo = QFrame()
        panel_grafo.setStyleSheet("background-color: #e6f2ff; border-radius: 8px; padding: 10px;")
        grafo_layout = QVBoxLayout(panel_grafo)

        lbl_vertices = QLabel("Número de vértices:")
        lbl_vertices.setStyleSheet("font-weight: bold; color: #003366;")
        self.spin_vertices = QSpinBox()
        self.spin_vertices.setRange(2, 10)
        self.spin_vertices.setValue(4)
        btn_crear = QPushButton("Crear Grafo")
        btn_crear.setStyleSheet(self._button_style("#4d9de0", "white"))
        btn_crear.clicked.connect(self.crear_grafo)
        grafo_layout.addWidget(lbl_vertices)
        grafo_layout.addWidget(self.spin_vertices)
        grafo_layout.addWidget(btn_crear)
        grafo_layout.addSpacing(15)

        # Agregar arista
        lbl_arista = QLabel("Agregar Arista")
        lbl_arista.setStyleSheet("font-weight: bold; color: #003366;")
        grafo_layout.addWidget(lbl_arista)

        arista_layout = QHBoxLayout()
        self.spin_origen = QSpinBox()
        self.spin_origen.setPrefix("Origen: ")
        self.spin_origen.setRange(1, 10)
        self.spin_destino = QSpinBox()
        self.spin_destino.setPrefix("Destino: ")
        self.spin_destino.setRange(1, 10)
        self.spin_peso = QSpinBox()
        self.spin_peso.setRange(1, 100)
        self.spin_peso.setValue(1)
        arista_layout.addWidget(self.spin_origen)
        arista_layout.addWidget(self.spin_destino)
        arista_layout.addWidget(self.spin_peso)
        grafo_layout.addLayout(arista_layout)

        btn_agregar = QPushButton("+ Agregar Arista")
        btn_agregar.setStyleSheet(self._button_style("#27ae60", "white"))
        btn_agregar.clicked.connect(self.agregar_arista)
        grafo_layout.addWidget(btn_agregar)

        btn_eliminar = QPushButton("- Eliminar última arista")
        btn_eliminar.setStyleSheet(self._button_style("#e74c3c", "white"))
        btn_eliminar.clicked.connect(self.eliminar_arista)
        grafo_layout.addWidget(btn_eliminar)

        grafo_layout.addSpacing(15)
        grafo_layout.addWidget(QLabel("─" * 20))

        # Botones de archivo
        btn_guardar = QPushButton("Guardar Grafo")
        btn_guardar.setStyleSheet(self._button_style("#3498db", "white"))
        btn_guardar.clicked.connect(self.guardar_grafo)
        btn_cargar = QPushButton("Cargar Grafo")
        btn_cargar.setStyleSheet(self._button_style("#3498db", "white"))
        btn_cargar.clicked.connect(self.cargar_grafo)
        btn_limpiar = QPushButton("Limpiar Grafo")
        btn_limpiar.setStyleSheet(self._button_style("#95a5a6", "white"))
        btn_limpiar.clicked.connect(self.limpiar_grafo)
        grafo_layout.addWidget(btn_guardar)
        grafo_layout.addWidget(btn_cargar)
        grafo_layout.addWidget(btn_limpiar)
        grafo_layout.addStretch()
        cuerpo.addWidget(panel_grafo, 1)

        # Panel derecho: ejecución y resultados
        panel_dijkstra = QFrame()
        panel_dijkstra.setStyleSheet("background-color: #e6f2ff; border-radius: 8px; padding: 10px;")
        dijkstra_layout = QVBoxLayout(panel_dijkstra)

        lbl_origen = QLabel("Vértice origen:")
        lbl_origen.setStyleSheet("font-weight: bold; color: #003366;")
        self.spin_origen_algo = QSpinBox()
        self.spin_origen_algo.setRange(1, 10)
        self.spin_origen_algo.setValue(1)

        btn_ejecutar = QPushButton("▶ Ejecutar Dijkstra")
        btn_ejecutar.setStyleSheet(self._button_style("#2c3e50", "white"))
        btn_ejecutar.clicked.connect(self.ejecutar_dijkstra)

        self.texto_proceso = QTextEdit()
        self.texto_proceso.setReadOnly(True)
        self.texto_proceso.setStyleSheet("background-color: white; font-family: monospace; border: 2px solid #99ccff; border-radius: 4px;")

        dijkstra_layout.addWidget(lbl_origen)
        dijkstra_layout.addWidget(self.spin_origen_algo)
        dijkstra_layout.addWidget(btn_ejecutar)
        dijkstra_layout.addWidget(QLabel("Proceso paso a paso:"))
        dijkstra_layout.addWidget(self.texto_proceso)

        cuerpo.addWidget(panel_dijkstra, 1)

        layout.addLayout(cuerpo)

        # Crear grafo inicial por defecto
        self.crear_grafo()

    # ----- Estilos -----
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

    # ----- Navegación -----
    def cerrar_y_volver_a_grafos(self):
        self.close()
        self.volver_a_grafos()

    def cerrar_y_volver_a_principal(self):
        self.close()
        self.volver_a_principal()

    # ----- Gestión del grafo -----
    def crear_grafo(self):
        n = self.spin_vertices.value()
        self.modelo.crear_grafo(n)
        self.spin_origen.setMaximum(n)
        self.spin_destino.setMaximum(n)
        self.spin_origen_algo.setMaximum(n)
        self.visualizador.limpiar_resultados()
        self.texto_proceso.clear()
        self._actualizar_vista()
        DialogoClave(0, "Éxito", "mensaje", self, f"Grafo creado con {n} vértices.").exec()

    def _actualizar_vista(self):
        self.visualizador.set_grafo(
            self.modelo.obtener_num_vertices(),
            self.modelo.obtener_aristas(),
            self.modelo.obtener_etiquetas(),
            self.modelo.obtener_ponderaciones()
        )

    def agregar_arista(self):
        if self.modelo.obtener_num_vertices() == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec()
            return
        u = self.spin_origen.value() - 1
        v = self.spin_destino.value() - 1
        peso = self.spin_peso.value()
        if u == v:
            DialogoClave(0, "Error", "mensaje", self, "No se permiten bucles.").exec()
            return
        if self.modelo.agregar_arista(u, v):
            idx = len(self.modelo.aristas) - 1
            self.modelo.ponderaciones[idx] = str(peso)
            self.visualizador.limpiar_resultados()
            self._actualizar_vista()
            DialogoClave(0, "Arista agregada", "mensaje", self,
                         f"Arista {u+1} → {v+1} (peso {peso})").exec()
        else:
            DialogoClave(0, "Error", "mensaje", self, "La arista ya existe.").exec()

    def eliminar_arista(self):
        if self.modelo.obtener_num_vertices() == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay grafo.").exec()
            return
        self.modelo.eliminar_ultima_arista()
        self.visualizador.limpiar_resultados()
        self._actualizar_vista()
        DialogoClave(0, "Arista eliminada", "mensaje", self, "Se eliminó la última arista.").exec()

    def guardar_grafo(self):
        if self.modelo.obtener_num_vertices() == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay grafo para guardar.").exec()
            return
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Grafo", "", "JSON (*.json)")
        if ruta:
            try:
                self.modelo.guardar_grafo(ruta)
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo guardado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error al guardar: {str(e)}").exec()

    def cargar_grafo(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar Grafo", "", "JSON (*.json)")
        if ruta:
            try:
                self.modelo.cargar_grafo(ruta)
                self.spin_vertices.setValue(self.modelo.obtener_num_vertices())
                self.visualizador.limpiar_resultados()
                self._actualizar_vista()
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error al cargar: {str(e)}").exec()

    def limpiar_grafo(self):
        self.modelo.crear_grafo(0)
        self.visualizador.limpiar_resultados()
        self._actualizar_vista()
        self.spin_vertices.setValue(4)
        DialogoClave(0, "Limpieza", "mensaje", self, "Grafo limpiado.").exec()

    # ----- Algoritmo de Dijkstra -----
    def ejecutar_dijkstra(self):
        n = self.modelo.obtener_num_vertices()
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea o carga un grafo.").exec()
            return
        if len(self.modelo.aristas) == 0:
            DialogoClave(0, "Error", "mensaje", self, "El grafo debe tener al menos una arista.").exec()
            return

        origen = self.spin_origen_algo.value() - 1

        # Lista de adyacencia con pesos
        adj = [[] for _ in range(n)]
        for (u, v), p in zip(self.modelo.aristas, self.modelo.ponderaciones):
            peso = float(p) if p else 1.0
            adj[u].append((v, peso))

        INF = float('inf')
        dist = [INF] * n
        prev = [-1] * n
        dist[origen] = 0
        pq = [(0, origen)]
        visitados = [False] * n

        # Almacenar pasos en HTML
        pasos_html = []
        paso_num = 1

        # Almacenar todos los caminos (para el visualizador)
        todos_caminos = {i: [] for i in range(n)}
        todos_caminos[origen].append((0, [origen]))

        while pq:
            d, u = heapq.heappop(pq)
            if visitados[u]:
                continue
            visitados[u] = True

            # Crear tabla de distancias actuales
            html = f"<b>Paso {paso_num}: Se extrae el vértice {self.modelo.etiquetas.get(u, str(u+1))} (distancia {d})</b><br>"
            html += "<table border='1' cellspacing='0' cellpadding='4' style='border-collapse: collapse; width: 100%;'>"
            html += "<tr style='background-color: #4d9de0; color: white;'><th>Vértice</th><th>Distancia actual</th></tr>"
            for i in range(n):
                dist_val = dist[i] if dist[i] != INF else "∞"
                row_style = "background-color: #cce6ff;" if i == u else ""
                html += f"<tr style='{row_style}'><td>V{i+1}</td><td>{dist_val}</td></tr>"
            html += "<tr><br>"

            # Actualizaciones
            cambios = []
            for v, w in adj[u]:
                if not visitados[v] and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    prev[v] = u
                    heapq.heappush(pq, (dist[v], v))
                    cambios.append((v, dist[v]))
                    # Guardar camino completo
                    camino = todos_caminos[u][-1][1] + [v]
                    todos_caminos[v].append((dist[v], camino))
            if cambios:
                html += "<b>Actualizaciones:</b><br>"
                for v, new_dist in cambios:
                    html += f"→ V{v+1} : {new_dist}<br>"
            else:
                html += "<i>No hubo actualizaciones en este paso.</i><br>"
            pasos_html.append(html)
            paso_num += 1

        # Limpiar caminos duplicados (dejar solo los de distancia mínima)
        for i in range(n):
            if todos_caminos[i]:
                todos_caminos[i].sort(key=lambda x: x[0])
                min_d = todos_caminos[i][0][0]
                todos_caminos[i] = [item for item in todos_caminos[i] if item[0] == min_d]

        # Mostrar proceso
        self.texto_proceso.setHtml("<br><br>".join(pasos_html))

        # Actualizar visualizador con los caminos
        self.visualizador.set_resultado_dijkstra(dist, todos_caminos, origen)

        DialogoClave(0, "Dijkstra", "mensaje", self, "Algoritmo ejecutado. Revise los resultados.").exec()