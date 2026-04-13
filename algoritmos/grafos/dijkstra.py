import heapq
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QSpinBox, QTextEdit, QFileDialog, QInputDialog)
from PySide6.QtCore import Qt
from controladores.grafo_controller import GrafoController
from controladores.visualizador_grafo import VisualizadorGrafo
from algoritmos.funcion_mod import DialogoClave

class DijkstraWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos = volver_a_grafos
        self.volver_a_principal = volver_a_principal
        self.controller = GrafoController()
        self.setWindowTitle("Dijkstra - Camino más corto")
        self.setGeometry(100, 50, 1200, 700)
        self.setStyleSheet("background-color: #f0f8ff;")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #cce6ff; border-radius: 10px;")
        header_layout = QHBoxLayout(header)
        btn_back = QPushButton("← Volver a Grafos")
        btn_back.clicked.connect(self.volver_a_grafos)
        btn_home = QPushButton("🏠 Inicio")
        btn_home.clicked.connect(self.volver_a_principal)
        header_layout.addWidget(btn_back)
        header_layout.addWidget(btn_home)
        titulo = QLabel("DIJKSTRA")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        header_layout.addWidget(titulo, alignment=Qt.AlignCenter)
        main_layout.addWidget(header)

        # Cuerpo
        body = QHBoxLayout()
        self.visual = VisualizadorGrafo("Grafo", es_editable=True)
        self.visual.vertice_clicked.connect(self.on_vertice_clicked)
        body.addWidget(self.visual, stretch=2)

        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setAlignment(Qt.AlignTop)

        lbl_vertices = QLabel("Número de vértices:")
        self.spin_vertices = QSpinBox()
        self.spin_vertices.setRange(1, 10)
        self.spin_vertices.setValue(4)
        btn_crear = QPushButton("Crear grafo")
        btn_crear.clicked.connect(self.crear_grafo)
        panel_layout.addWidget(lbl_vertices)
        panel_layout.addWidget(self.spin_vertices)
        panel_layout.addWidget(btn_crear)

        btn_agregar_arista = QPushButton("Agregar arista")
        btn_agregar_arista.clicked.connect(self.agregar_arista)
        btn_eliminar_arista = QPushButton("Eliminar arista")
        btn_eliminar_arista.clicked.connect(self.eliminar_arista)
        panel_layout.addWidget(btn_agregar_arista)
        panel_layout.addWidget(btn_eliminar_arista)

        btn_guardar = QPushButton("Guardar grafo")
        btn_guardar.clicked.connect(self.guardar_grafo)
        btn_cargar = QPushButton("Cargar grafo")
        btn_cargar.clicked.connect(self.cargar_grafo)
        panel_layout.addWidget(btn_guardar)
        panel_layout.addWidget(btn_cargar)

        lbl_origen = QLabel("Vértice origen:")
        self.spin_origen = QSpinBox()
        lbl_destino = QLabel("Destino:")
        self.spin_destino = QSpinBox()
        btn_ejecutar = QPushButton("Calcular Dijkstra")
        btn_ejecutar.clicked.connect(self.ejecutar_dijkstra)
        self.resultado_text = QTextEdit()
        self.resultado_text.setReadOnly(True)
        panel_layout.addWidget(lbl_origen)
        panel_layout.addWidget(self.spin_origen)
        panel_layout.addWidget(lbl_destino)
        panel_layout.addWidget(self.spin_destino)
        panel_layout.addWidget(btn_ejecutar)
        panel_layout.addWidget(self.resultado_text)

        panel_layout.addStretch()
        body.addWidget(panel, stretch=1)
        main_layout.addLayout(body)

        self.crear_grafo()

    def crear_grafo(self):
        n = self.spin_vertices.value()
        self.controller.set_vertices(n)
        self.spin_origen.setRange(0, n-1)
        self.spin_destino.setRange(0, n-1)
        self.actualizar_vista()

    def actualizar_vista(self):
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(datos['vertices'], datos['aristas'],
                              datos['etiquetas'], datos['pesos'])

    def agregar_arista(self):
        n = self.controller._vertices
        u, ok = QInputDialog.getInt(self, "Arista", f"Vértice origen (0..{n-1})", 0, 0, n-1)
        if not ok: return
        v, ok = QInputDialog.getInt(self, "Arista", f"Vértice destino (0..{n-1})", 1, 0, n-1)
        if not ok: return
        peso, ok = QInputDialog.getInt(self, "Arista", "Peso", 1, 1, 100)
        if not ok: return
        if self.controller.agregar_arista(u, v, peso):
            self.actualizar_vista()
        else:
            DialogoClave(0, "Error", "mensaje", self, "Arista inválida o ya existe.").exec()

    def eliminar_arista(self):
        n = self.controller._vertices
        u, ok = QInputDialog.getInt(self, "Eliminar arista", f"Vértice origen (0..{n-1})", 0, 0, n-1)
        if not ok: return
        v, ok = QInputDialog.getInt(self, "Eliminar arista", f"Vértice destino (0..{n-1})", 1, 0, n-1)
        if not ok: return
        if self.controller.eliminar_arista(u, v):
            self.actualizar_vista()
        else:
            DialogoClave(0, "Error", "mensaje", self, "Arista no existe.").exec()

    def guardar_grafo(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar grafo", "", "JSON (*.json)")
        if ruta:
            self.controller.guardar_json(ruta)
            DialogoClave(0, "Éxito", "mensaje", self, f"Grafo guardado en {ruta}").exec()

    def cargar_grafo(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar grafo", "", "JSON (*.json)")
        if ruta:
            self.controller.cargar_json(ruta)
            self.spin_vertices.setValue(self.controller._vertices)
            self.spin_origen.setRange(0, self.controller._vertices-1)
            self.spin_destino.setRange(0, self.controller._vertices-1)
            self.actualizar_vista()
            DialogoClave(0, "Éxito", "mensaje", self, "Grafo cargado.").exec()

    def on_vertice_clicked(self, idx):
        etiqueta_actual = self.controller._etiquetas.get(idx, str(idx+1))
        nueva, ok = QInputDialog.getText(self, "Cambiar etiqueta", f"Nueva etiqueta para vértice {idx}:", text=etiqueta_actual)
        if ok and nueva:
            self.controller.cambiar_etiqueta(idx, nueva)
            self.actualizar_vista()

    def ejecutar_dijkstra(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Cree o cargue un grafo primero.").exec()
            return
        origen = self.spin_origen.value()
        destino = self.spin_destino.value()
        adj = self.controller.lista_adyacencia()
        n = self.controller._vertices
        dist = [float('inf')] * n
        prev = [-1] * n
        dist[origen] = 0
        pq = [(0, origen)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in adj[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        if dist[destino] == float('inf'):
            self.resultado_text.setText("No hay camino.")
        else:
            path = []
            cur = destino
            while cur != -1:
                path.append(cur)
                cur = prev[cur]
            path.reverse()
            self.resultado_text.setText(f"Distancia mínima: {dist[destino]}\nCamino: {' -> '.join(str(v) for v in path)}")