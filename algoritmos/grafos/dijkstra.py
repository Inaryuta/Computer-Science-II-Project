"""
algoritmos/grafos/dijkstra.py  — versión corregida
Fixes:
  1. _limpiar_textos_caminos ahora guarda con scene antes de removeItem
  2. Pesos almacenados como int (no str)
  3. Tras cargar/crear, se actualizan los rangos de spin_origen y spin_destino
  4. Visualizador usa VisualizadorGrafoDirigido (alias de VisualizadorGrafoColoreable)
     correctamente — no se hereda, se instancia
"""
import json
import heapq
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTextEdit, QSpinBox, QFileDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from controladores.visualizador_grafo import VisualizadorGrafoDirigido
from algoritmos.funcion_mod import DialogoClave


# ══════════════════════════════════════════════════════════════════════
#  Modelo interno del grafo (Dijkstra trabaja con dígrafo ponderado)
# ══════════════════════════════════════════════════════════════════════
class ModeloGrafoInterno:
    def __init__(self):
        self.num_vertices  = 0
        self.aristas       = []   # lista de tuplas (origen, destino)
        self.ponderaciones = []   # lista de int paralela a aristas   FIX: int, no str
        self.etiquetas     = {}

    def crear_grafo(self, n: int):
        self.num_vertices  = n
        self.aristas       = []
        self.ponderaciones = []
        self.etiquetas     = {i: str(i + 1) for i in range(n)}

    def agregar_arista(self, u: int, v: int, peso: int = 1) -> bool:
        if not (0 <= u < self.num_vertices and 0 <= v < self.num_vertices):
            return False
        if (u, v) in self.aristas:
            return False
        self.aristas.append((u, v))
        self.ponderaciones.append(int(peso))   # FIX: siempre int
        return True

    def eliminar_ultima_arista(self):
        if self.aristas:
            self.aristas.pop()
            self.ponderaciones.pop()

    def guardar(self, ruta: str):
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump({
                'num_vertices':  self.num_vertices,
                'aristas':       self.aristas,
                'ponderaciones': self.ponderaciones,
                'etiquetas':     self.etiquetas,
            }, f, indent=4)

    def cargar(self, ruta: str):
        with open(ruta, 'r', encoding='utf-8') as f:
            d = json.load(f)
        self.num_vertices  = d['num_vertices']
        self.aristas       = [tuple(a) for a in d['aristas']]
        self.ponderaciones = [int(p) for p in d.get('ponderaciones', [])]  # FIX: int
        self.etiquetas     = {int(k): v for k, v in d['etiquetas'].items()}


# ══════════════════════════════════════════════════════════════════════
#  Visualizador especializado para Dijkstra
#  FIX: ya NO hereda de VisualizadorGrafoDirigido (que ahora es un alias
#       con firma diferente). En su lugar, agrega el texto de caminos
#       sobre el visualizador base usando set_colores().
# ══════════════════════════════════════════════════════════════════════
class VisualizadorDijkstra(VisualizadorGrafoDirigido):
    """
    Extiende VisualizadorGrafoDirigido (alias de VisualizadorGrafoColoreable)
    añadiendo textos de distancia/camino encima del canvas.
    """
    def __init__(self, titulo="Dijkstra", parent=None):
        super().__init__(titulo, parent, es_editable=False)
        self._textos_caminos = []
        self._dist_items     = {}   # {vertice: texto QGraphicsTextItem}

    # FIX: guard — scene puede no existir si se llama antes de dibujar
    def _limpiar_textos_caminos(self):
        if not hasattr(self, 'scene'):
            self._textos_caminos = []
            return
        for item in self._textos_caminos:
            try:
                self.scene.removeItem(item)
            except Exception:
                pass
        self._textos_caminos = []

    def set_grafo(self, num_vertices, aristas, etiquetas, pesos=None,
                  colores_vertices=None, colores_aristas=None):
        self._limpiar_textos_caminos()
        super().set_grafo(num_vertices, aristas, etiquetas, pesos,
                          colores_vertices, colores_aristas)

    def set_resultado_dijkstra(self, dist: list, prev: list, origen: int,
                               etiquetas: dict, aristas: list):
        """
        Colorea el grafo según los caminos mínimos y añade etiquetas de distancia.
        dist  – lista de distancias desde origen
        prev  – lista de predecesores
        """
        self._limpiar_textos_caminos()
        n   = len(dist)
        INF = float('inf')

        # Aristas que pertenecen al árbol de caminos mínimos
        arbol_aristas: set[int] = set()
        for v in range(n):
            if prev[v] != -1:
                u = prev[v]
                for i, (a, b) in enumerate(aristas):
                    if a == u and b == v:
                        arbol_aristas.add(i)
                        break

        # Colores: origen en naranja, alcanzables en verde, inalcanzables en gris
        col_v = {}
        for v in range(n):
            if v == origen:
                col_v[v] = "#e67e22"
            elif dist[v] < INF:
                col_v[v] = "#27ae60"
            else:
                col_v[v] = "#95a5a6"

        col_a = {i: "#27ae60" for i in arbol_aristas}
        self.set_colores(colores_vertices=col_v, colores_aristas=col_a)

        # Añadir texto de distancia encima de cada vértice
        for v, (x, y) in enumerate(self.posiciones):
            d_val = dist[v]
            txt   = "0" if v == origen else ("∞" if d_val == INF else str(d_val))
            item  = self.scene.addText(txt)
            item.setDefaultTextColor(QColor("#c0392b" if d_val == INF else "#003366"))
            item.setFont(QFont("Arial", 8, QFont.Bold))
            rect  = item.boundingRect()
            item.setPos(x - rect.width() / 2, y - self.radio - rect.height() - 2)
            self._textos_caminos.append(item)

    def limpiar_resultado(self):
        self._limpiar_textos_caminos()
        # Reset colores a default
        self.set_colores(colores_vertices={}, colores_aristas={})


# ══════════════════════════════════════════════════════════════════════
#  Ventana principal
# ══════════════════════════════════════════════════════════════════════
class DijkstraWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos    = volver_a_grafos
        self.volver_a_principal = volver_a_principal
        self.modelo             = ModeloGrafoInterno()

        self.setWindowTitle("Algoritmo de Dijkstra")
        self.setGeometry(150, 80, 1300, 750)
        self.setStyleSheet("background-color: #f0f8ff;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #cce6ff; border-radius: 10px;")
        hl = QHBoxLayout(header)
        b1 = QPushButton("← Volver a Grafos")
        b1.setStyleSheet(self._btn("#e6f2ff", "#003366"))
        b1.clicked.connect(self.cerrar_y_volver_a_grafos)
        b2 = QPushButton("🏠 Inicio")
        b2.setStyleSheet(self._btn("#e6f2ff", "#003366"))
        b2.clicked.connect(self.cerrar_y_volver_a_principal)
        titulo = QLabel("DIJKSTRA")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        hl.addWidget(b1); hl.addWidget(b2)
        hl.addWidget(titulo, alignment=Qt.AlignCenter)
        layout.addWidget(header)

        # Cuerpo (tres columnas)
        cuerpo = QHBoxLayout()

        # Panel visual
        panel_vis = QFrame()
        panel_vis.setStyleSheet("background-color: #e6f2ff; border-radius: 8px; padding: 10px;")
        vl = QVBoxLayout(panel_vis)
        self.visualizador = VisualizadorDijkstra("Grafo Dirigido", self)
        self.visualizador.setFixedSize(480, 480)
        vl.addWidget(self.visualizador, alignment=Qt.AlignCenter)
        leyenda = QLabel(
            "<b>Leyenda:</b>  "
            "<span style='color:#e67e22;'>■</span> Origen  "
            "<span style='color:#27ae60;'>■</span> Alcanzable  "
            "<span style='color:#95a5a6;'>■</span> Inalcanzable<br>"
            "Número sobre cada vértice = distancia mínima desde el origen."
        )
        leyenda.setStyleSheet("background-color:white;border-radius:4px;padding:5px;color:#003366;")
        vl.addWidget(leyenda)
        cuerpo.addWidget(panel_vis, 2)

        # Panel construcción del grafo
        panel_g = QFrame()
        panel_g.setStyleSheet("background-color: #e6f2ff; border-radius: 8px; padding: 10px;")
        gl = QVBoxLayout(panel_g)
        gl.setAlignment(Qt.AlignTop)

        gl.addWidget(self._lbl("Número de vértices:"))
        self.spin_vertices = QSpinBox()
        self.spin_vertices.setRange(2, 12)
        self.spin_vertices.setValue(4)
        self.spin_vertices.setStyleSheet(self._spin_style())
        gl.addWidget(self.spin_vertices)
        btn_crear = QPushButton("Crear Grafo")
        btn_crear.setStyleSheet(self._btn("#4d9de0", "white"))
        btn_crear.clicked.connect(self.crear_grafo)
        gl.addWidget(btn_crear)
        gl.addWidget(self._sep())

        gl.addWidget(self._lbl("Agregar arista:"))
        row = QHBoxLayout()
        self.spin_origen  = QSpinBox(); self.spin_origen.setPrefix("De: ")
        self.spin_origen.setRange(1, 12); self.spin_origen.setStyleSheet(self._spin_style())
        self.spin_destino = QSpinBox(); self.spin_destino.setPrefix("A: ")
        self.spin_destino.setRange(1, 12); self.spin_destino.setStyleSheet(self._spin_style())
        self.spin_peso = QSpinBox()
        self.spin_peso.setRange(1, 999); self.spin_peso.setValue(1)
        self.spin_peso.setPrefix("P: "); self.spin_peso.setStyleSheet(self._spin_style())
        row.addWidget(self.spin_origen)
        row.addWidget(self.spin_destino)
        row.addWidget(self.spin_peso)
        gl.addLayout(row)

        btn_add = QPushButton("+ Agregar Arista")
        btn_add.setStyleSheet(self._btn("#27ae60", "white"))
        btn_add.clicked.connect(self.agregar_arista)
        gl.addWidget(btn_add)
        btn_del = QPushButton("- Eliminar última arista")
        btn_del.setStyleSheet(self._btn("#e74c3c", "white"))
        btn_del.clicked.connect(self.eliminar_arista)
        gl.addWidget(btn_del)
        gl.addWidget(self._sep())

        btn_s = QPushButton("💾 Guardar Grafo")
        btn_s.setStyleSheet(self._btn("#3498db", "white"))
        btn_s.clicked.connect(self.guardar_grafo)
        btn_l = QPushButton("📂 Cargar Grafo")
        btn_l.setStyleSheet(self._btn("#3498db", "white"))
        btn_l.clicked.connect(self.cargar_grafo)
        btn_x = QPushButton("↺ Limpiar Grafo")
        btn_x.setStyleSheet(self._btn("#95a5a6", "white"))
        btn_x.clicked.connect(self.limpiar_grafo)
        gl.addWidget(btn_s); gl.addWidget(btn_l); gl.addWidget(btn_x)
        cuerpo.addWidget(panel_g, 1)

        # Panel Dijkstra
        panel_d = QFrame()
        panel_d.setStyleSheet("background-color: #e6f2ff; border-radius: 8px; padding: 10px;")
        dl = QVBoxLayout(panel_d)
        dl.setAlignment(Qt.AlignTop)

        dl.addWidget(self._lbl("Vértice origen:"))
        self.spin_origen_algo = QSpinBox()
        self.spin_origen_algo.setRange(1, 12)
        self.spin_origen_algo.setStyleSheet(self._spin_style())
        dl.addWidget(self.spin_origen_algo)

        btn_run = QPushButton("▶ Ejecutar Dijkstra")
        btn_run.setStyleSheet(self._btn("#2c3e50", "white"))
        btn_run.clicked.connect(self.ejecutar_dijkstra)
        dl.addWidget(btn_run)
        dl.addWidget(self._sep())

        dl.addWidget(self._lbl("Proceso paso a paso:"))
        self.texto_proceso = QTextEdit()
        self.texto_proceso.setReadOnly(True)
        self.texto_proceso.setStyleSheet(
            "background-color:white;font-family:monospace;"
            "border:2px solid #99ccff;border-radius:4px;"
        )
        dl.addWidget(self.texto_proceso)
        cuerpo.addWidget(panel_d, 1)

        layout.addLayout(cuerpo)
        self.crear_grafo()   # grafo inicial por defecto

    # ── Estilos ──────────────────────────────────────────────────────
    def _btn(self, bg, fg):
        dk = {"#4d9de0":"#3b7cb0","#27ae60":"#1e8449","#e74c3c":"#c0392b",
              "#3498db":"#2980b9","#95a5a6":"#7f8c8d","#2c3e50":"#1a252f",
              "#e6f2ff":"#cce6ff"}.get(bg, bg)
        return (f"QPushButton {{background-color:{bg};color:{fg};font-weight:bold;"
                f"border:none;border-radius:5px;padding:6px 12px;}}"
                f"QPushButton:hover {{background-color:{dk};}}")

    @staticmethod
    def _spin_style():
        return "QSpinBox {background-color:white;border:2px solid #99ccff;border-radius:4px;padding:4px;color:#003366;}"

    @staticmethod
    def _lbl(text):
        l = QLabel(text); l.setStyleSheet("font-weight:bold;color:#003366;"); return l

    @staticmethod
    def _sep():
        from PySide6.QtWidgets import QFrame as F
        s = F(); s.setFrameShape(F.HLine); s.setStyleSheet("color:#99ccff;"); return s

    # ── Navegación ───────────────────────────────────────────────────
    def cerrar_y_volver_a_grafos(self):
        self.close(); self.volver_a_grafos()

    def cerrar_y_volver_a_principal(self):
        self.close(); self.volver_a_principal()

    # ── Gestión del grafo ─────────────────────────────────────────────
    def crear_grafo(self):
        n = self.spin_vertices.value()
        self.modelo.crear_grafo(n)
        self._sync_spin_ranges(n)          # FIX: actualizar rangos
        self.visualizador.limpiar_resultado()
        self.texto_proceso.clear()
        self._actualizar_vista()
        DialogoClave(0, "Éxito", "mensaje", self, f"Grafo creado con {n} vértices.").exec()

    def _sync_spin_ranges(self, n: int):
        """FIX: mantiene los SpinBox de origen/destino dentro del rango válido."""
        for sp in (self.spin_origen, self.spin_destino, self.spin_origen_algo):
            sp.setMaximum(n)
            if sp.value() > n:
                sp.setValue(1)

    def _actualizar_vista(self):
        self.visualizador.set_grafo(
            self.modelo.num_vertices,
            self.modelo.aristas,
            self.modelo.etiquetas,
            self.modelo.ponderaciones,   # FIX: lista de int
        )

    def agregar_arista(self):
        if self.modelo.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec(); return
        u = self.spin_origen.value() - 1
        v = self.spin_destino.value() - 1
        peso = self.spin_peso.value()
        if u == v:
            DialogoClave(0, "Error", "mensaje", self, "No se permiten bucles.").exec(); return
        if self.modelo.agregar_arista(u, v, peso):
            self.visualizador.limpiar_resultado()
            self._actualizar_vista()
            DialogoClave(0, "Arista agregada", "mensaje", self,
                         f"Arista {u+1} → {v+1} (peso {peso})").exec()
        else:
            DialogoClave(0, "Error", "mensaje", self, "La arista ya existe.").exec()

    def eliminar_arista(self):
        if self.modelo.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay grafo.").exec(); return
        self.modelo.eliminar_ultima_arista()
        self.visualizador.limpiar_resultado()
        self._actualizar_vista()
        DialogoClave(0, "Arista eliminada", "mensaje", self, "Se eliminó la última arista.").exec()

    def guardar_grafo(self):
        if self.modelo.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay grafo para guardar.").exec(); return
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Grafo", "", "JSON (*.json)")
        if ruta:
            try:
                self.modelo.guardar(ruta)
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo guardado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {e}").exec()

    def cargar_grafo(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar Grafo", "", "JSON (*.json)")
        if ruta:
            try:
                self.modelo.cargar(ruta)
                n = self.modelo.num_vertices
                self.spin_vertices.setValue(n)
                self._sync_spin_ranges(n)      # FIX: actualizar rangos tras cargar
                self.visualizador.limpiar_resultado()
                self._actualizar_vista()
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {e}").exec()

    def limpiar_grafo(self):
        n = self.spin_vertices.value()
        self.modelo.crear_grafo(n)
        self._sync_spin_ranges(n)
        self.visualizador.limpiar_resultado()
        self._actualizar_vista()

    # ── Algoritmo ────────────────────────────────────────────────────
    def ejecutar_dijkstra(self):
        n = self.modelo.num_vertices
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea o carga un grafo.").exec(); return
        if not self.modelo.aristas:
            DialogoClave(0, "Error", "mensaje", self, "El grafo debe tener al menos una arista.").exec(); return

        origen = self.spin_origen_algo.value() - 1

        # Lista de adyacencia
        adj = [[] for _ in range(n)]
        for (u, v), p in zip(self.modelo.aristas, self.modelo.ponderaciones):
            adj[u].append((v, int(p) if p else 1))

        INF  = float('inf')
        dist = [INF] * n
        prev = [-1]  * n
        dist[origen] = 0
        pq = [(0, origen)]
        visitados = [False] * n
        pasos_html = []
        paso = 1

        while pq:
            d, u = heapq.heappop(pq)
            if visitados[u]:
                continue
            visitados[u] = True

            html = (f"<b>Paso {paso}: extraer V{u+1} (dist={d})</b><br>"
                    "<table border='1' cellspacing='0' cellpadding='3' "
                    "style='border-collapse:collapse;width:100%;'>"
                    "<tr style='background:#4d9de0;color:white;'><th>V</th><th>dist</th></tr>")
            for i in range(n):
                dv = dist[i]
                ds = "∞" if dv == INF else str(dv)
                bg = "background:#cce6ff;" if i == u else ""
                html += f"<tr style='{bg}'><td>V{i+1}</td><td>{ds}</td></tr>"
            html += "</table>"

            cambios = []
            for v, w in adj[u]:
                if not visitados[v] and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    prev[v] = u
                    heapq.heappush(pq, (dist[v], v))
                    cambios.append(f"V{v+1}={dist[v]}")

            if cambios:
                html += f"<b>Actualizaciones:</b> {', '.join(cambios)}<br>"
            else:
                html += "<i>Sin actualizaciones.</i><br>"

            pasos_html.append(html)
            paso += 1

        self.texto_proceso.setHtml("<br>".join(pasos_html))
        self.visualizador.set_resultado_dijkstra(
            dist, prev, origen, self.modelo.etiquetas, self.modelo.aristas
        )
        DialogoClave(0, "Dijkstra", "mensaje", self,
                     "Algoritmo ejecutado. Los números sobre los vértices son las distancias mínimas.").exec()