"""
algoritmos/grafos/metricas_grafo.py
Métricas para Grafos NO Dirigidos:
  • Matriz de adyacencia (vértices × vértices)
  • Matriz de incidencia (vértices × aristas)
  • Matriz de circuitos  (ciclos × aristas) + visualización coloreada
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QFrame, QFileDialog, QComboBox,
    QScrollArea, QGridLayout, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from controladores.grafo_controller import GrafoController
from controladores.visualizador_grafo import VisualizadorGrafo
from algoritmos.grafos.dialogo_arista import DialogoArista
from algoritmos.funcion_mod import DialogoClave


# ══════════════════════════════════════════════════════════════════════
#  Algoritmos de ciclos (grafos no dirigidos)
# ══════════════════════════════════════════════════════════════════════

def _ciclos_fundamentales(n: int, aristas: list[tuple]) -> list[list[int]]:
    """
    Devuelve los ciclos fundamentales del grafo usando un árbol DFS.
    Cada ciclo es una lista de índices de arista (posición en `aristas`).
    """
    if n == 0:
        return []

    # Árbol DFS
    visitado = [False] * n
    padre = [-1] * n
    padre_arista = [-1] * n          # índice de arista que llevó a este vértice
    profundidad = [0] * n

    # lista de adyacencia: (vecino, idx_arista)
    adj: list[list[tuple]] = [[] for _ in range(n)]
    for i, (u, v, *_) in enumerate(aristas):
        adj[u].append((v, i))
        adj[v].append((u, i))

    ciclos: list[list[int]] = []

    def dfs(v: int, depth: int):
        visitado[v] = True
        profundidad[v] = depth
        for (w, ei) in adj[v]:
            if not visitado[w]:
                padre[w] = v
                padre_arista[w] = ei
                dfs(w, depth + 1)
            elif padre[v] != w:          # arista de retroceso → ciclo
                # Reconstruir el ciclo
                ciclo_aristas = [ei]
                cur = v
                while cur != w:
                    ciclo_aristas.append(padre_arista[cur])
                    cur = padre[cur]
                ciclos.append(ciclo_aristas)

    for s in range(n):
        if not visitado[s]:
            dfs(s, 0)

    return ciclos


def _todos_los_ciclos_simples(n: int, aristas: list[tuple]) -> list[list[int]]:
    """
    Encuentra TODOS los ciclos simples (no solo los fundamentales).
    Devuelve cada ciclo como lista de índices de arista.
    Limitado a grafos pequeños (≤ 12 vértices) para evitar explosión combinatoria.
    """
    if n == 0:
        return []

    adj: list[list[tuple]] = [[] for _ in range(n)]
    for i, (u, v, *_) in enumerate(aristas):
        adj[u].append((v, i))
        if u != v:
            adj[v].append((u, i))

    encontrados: list[frozenset] = []   # para deduplicar
    ciclos_aristas: list[list[int]] = []

    def dfs(inicio: int, actual: int, visitados: list[bool],
            camino_v: list[int], camino_e: list[int], ultima_arista: int):
        for (vecino, ei) in adj[actual]:
            if ei == ultima_arista:      # no volver por la misma arista
                continue
            if vecino == inicio and len(camino_v) >= 2:
                # ciclo encontrado
                clave = frozenset(camino_e + [ei])
                if clave not in encontrados:
                    encontrados.append(clave)
                    ciclos_aristas.append(camino_e + [ei])
            elif not visitados[vecino]:
                visitados[vecino] = True
                dfs(inicio, vecino, visitados,
                    camino_v + [vecino], camino_e + [ei], ei)
                visitados[vecino] = False

    for inicio in range(n):
        vis = [False] * n
        vis[inicio] = True
        dfs(inicio, inicio, vis, [inicio], [], -1)

    return ciclos_aristas


# ══════════════════════════════════════════════════════════════════════
#  Paleta para colorear circuitos
# ══════════════════════════════════════════════════════════════════════
COLORES_CIRCUITO = [
    "#e74c3c", "#27ae60", "#f39c12", "#8e44ad",
    "#16a085", "#2980b9", "#d35400", "#c0392b",
]


# ══════════════════════════════════════════════════════════════════════
#  Ventana principal
# ══════════════════════════════════════════════════════════════════════
class MetricasGrafoWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos = volver_a_grafos
        self.volver_a_principal = volver_a_principal

        self.controller = GrafoController()
        self._ciclos: list[list[int]] = []   # lista de ciclos (índices de arista)
        self._ciclo_actual: int = 0

        self.setWindowTitle("Métricas Grafos No Dirigidos")
        self.setGeometry(100, 50, 1500, 800)
        self.setStyleSheet("background-color: #f0f8ff;")

        self._build_ui()
        self.controller.grafo_cambiado.connect(self._actualizar_visual)

    # ──────────────────────────────────────────────────────────────────
    #  UI
    # ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(10, 10, 10, 10)
        root.addWidget(self._make_header())

        body = QHBoxLayout()
        body.setSpacing(12)

        # ── Visualizador ──────────────────────────────────────────────
        self.visual = VisualizadorGrafo("Grafo", es_editable=True)
        self.visual.setFixedSize(500, 520)
        body.addWidget(self.visual, stretch=2)

        # ── Panel derecho (con scroll) ─────────────────────────────────
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("border: none;")
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: #e6f2ff; border-radius: 8px;")
        self.right_layout = QVBoxLayout(right_widget)
        self.right_layout.setSpacing(8)
        self.right_layout.setAlignment(Qt.AlignTop)
        right_scroll.setWidget(right_widget)
        body.addWidget(right_scroll, stretch=1)

        root.addLayout(body)
        self._build_panel()

    def _make_header(self) -> QFrame:
        h = QFrame()
        h.setStyleSheet("background-color: #cce6ff; border-radius: 10px;")
        hl = QHBoxLayout(h)
        b1 = QPushButton("← Volver a Grafos")
        b1.setStyleSheet(self._btn("#e6f2ff", "#003366"))
        b1.clicked.connect(self._cerrar_grafos)
        b2 = QPushButton("🏠 Inicio")
        b2.setStyleSheet(self._btn("#e6f2ff", "#003366"))
        b2.clicked.connect(self._cerrar_principal)
        titulo = QLabel("MÉTRICAS GRAFOS NO DIRIGIDOS")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        hl.addWidget(b1)
        hl.addWidget(b2)
        hl.addWidget(titulo, alignment=Qt.AlignCenter)
        return h

    def _build_panel(self):
        lay = self.right_layout

        # ── Crear grafo ───────────────────────────────────────────────
        lay.addWidget(self._lbl("Número de vértices:"))
        self.spin_v = QSpinBox()
        self.spin_v.setRange(1, 12)
        self.spin_v.setValue(4)
        self.spin_v.setStyleSheet(self._input_style())
        lay.addWidget(self.spin_v)
        b = QPushButton("Crear grafo")
        b.setStyleSheet(self._btn("#4d9de0", "white"))
        b.clicked.connect(self._crear_grafo)
        lay.addWidget(b)

        # ── Aristas ───────────────────────────────────────────────────
        lay.addWidget(self._sep())
        lay.addWidget(self._lbl("Agregar arista:"))
        row = QHBoxLayout()
        self.combo_u = QComboBox(); self.combo_u.setStyleSheet(self._input_style())
        self.combo_v = QComboBox(); self.combo_v.setStyleSheet(self._input_style())
        self.spin_peso = QSpinBox()
        self.spin_peso.setRange(0, 9999); self.spin_peso.setValue(1)
        self.spin_peso.setStyleSheet(self._input_style())
        row.addWidget(QLabel("De:")); row.addWidget(self.combo_u)
        row.addWidget(QLabel("A:"));  row.addWidget(self.combo_v)
        row.addWidget(QLabel("Peso:")); row.addWidget(self.spin_peso)
        lay.addLayout(row)
        ba = QPushButton("+ Arista")
        ba.setStyleSheet(self._btn("#27ae60", "white"))
        ba.clicked.connect(self._agregar_arista)
        lay.addWidget(ba)
        be = QPushButton("- Eliminar arista")
        be.setStyleSheet(self._btn("#e74c3c", "white"))
        be.clicked.connect(self._eliminar_arista)
        lay.addWidget(be)

        # ── Guardar / Cargar ──────────────────────────────────────────
        lay.addWidget(self._sep())
        row2 = QHBoxLayout()
        bs = QPushButton("💾 Guardar"); bs.setStyleSheet(self._btn("#3498db", "white"))
        bc = QPushButton("📂 Cargar");  bc.setStyleSheet(self._btn("#3498db", "white"))
        bs.clicked.connect(self._guardar); bc.clicked.connect(self._cargar)
        row2.addWidget(bs); row2.addWidget(bc)
        lay.addLayout(row2)

        # ── Operación ─────────────────────────────────────────────────
        lay.addWidget(self._sep())
        lay.addWidget(self._lbl("Operación matricial:"))
        self.combo_op = QComboBox()
        self.combo_op.addItem("Matriz de adyacencia y de incidencia", "adyacencia_incidencia")
        self.combo_op.addItem("Matriz de circuitos", "circuitos")
        self.combo_op.setStyleSheet(self._input_style())
        lay.addWidget(self.combo_op)
        br = QPushButton("▶ Calcular")
        br.setStyleSheet(self._btn("#2c3e50", "white"))
        br.clicked.connect(self._calcular)
        lay.addWidget(br)

        # ── Botón ver otro circuito (oculto por defecto) ───────────────
        self.btn_otro = QPushButton("🔄 Ver otro circuito")
        self.btn_otro.setStyleSheet(self._btn("#8e44ad", "white"))
        self.btn_otro.clicked.connect(self._ver_otro_circuito)
        self.btn_otro.setVisible(False)
        lay.addWidget(self.btn_otro)

        # ── Área de resultados ────────────────────────────────────────
        lay.addWidget(self._sep())
        self.lbl_resultado = QLabel()
        self.lbl_resultado.setStyleSheet("font-weight: bold; color: #003366; font-size: 13px;")
        self.lbl_resultado.setAlignment(Qt.AlignCenter)
        self.lbl_resultado.setVisible(False)
        lay.addWidget(self.lbl_resultado)

        # Contenedor de matrices (se rellena dinámicamente)
        self.matrices_widget = QWidget()
        self.matrices_layout = QVBoxLayout(self.matrices_widget)
        self.matrices_layout.setSpacing(16)
        lay.addWidget(self.matrices_widget)

    # ──────────────────────────────────────────────────────────────────
    #  Acciones
    # ──────────────────────────────────────────────────────────────────
    def _crear_grafo(self):
        n = self.spin_v.value()
        self.controller.set_vertices(n)
        self._actualizar_combos()
        self._limpiar_matrices()
        self.btn_otro.setVisible(False)
        self.lbl_resultado.setVisible(False)

    def _agregar_arista(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea el grafo.").exec()
            return
        u = self.combo_u.currentData()
        v = self.combo_v.currentData()
        peso = self.spin_peso.value()
        if u is None or v is None:
            return
        self.controller.agregar_arista(u, v, peso)

    def _eliminar_arista(self):
        datos = self.controller.obtener_datos()
        aristas = datos["aristas"]
        etiq = datos["etiquetas"]
        if not aristas:
            DialogoClave(0, "Info", "mensaje", self, "No hay aristas para eliminar.").exec()
            return
        from PySide6.QtWidgets import QInputDialog
        opts = [f"{etiq.get(u, u+1)} — {etiq.get(v, v+1)}" for (u, v) in aristas]
        sel, ok = QInputDialog.getItem(self, "Eliminar arista", "Arista:", opts, 0, False)
        if ok:
            idx = opts.index(sel)
            u, v = aristas[idx]
            self.controller.eliminar_arista(u, v, indice=idx)

    def _guardar(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay grafo para guardar.").exec()
            return
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar", "", "JSON (*.json)")
        if ruta:
            self.controller.guardar_json(ruta)
            DialogoClave(0, "Éxito", "mensaje", self, "Grafo guardado.").exec()

    def _cargar(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar", "", "JSON (*.json)")
        if ruta:
            try:
                self.controller.cargar_json(ruta)
                self.spin_v.setValue(self.controller._vertices)
                self._actualizar_combos()
                self._limpiar_matrices()
                self.btn_otro.setVisible(False)
                self.lbl_resultado.setVisible(False)
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {e}").exec()

    def _calcular(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec()
            return
        op = self.combo_op.currentData()
        self._limpiar_matrices()
        self.btn_otro.setVisible(False)
        self.lbl_resultado.setVisible(False)

        if op == "adyacencia_incidencia":
            self._mostrar_incidencia()          # vértices × aristas   
            self._mostrar_adyacencia()          # vértices × vértices
            self._mostrar_adyacencia_aristas()  # aristas  × aristas  ← nueva
        else:
            self._calcular_circuitos()

    # ──────────────────────────────────────────────────────────────────
    #  Matrices
    # ──────────────────────────────────────────────────────────────────
    def _mostrar_adyacencia(self):
        n = self.controller._vertices
        etiq = self.controller._etiquetas
        mat = self.controller.matriz_adyacencia()

        frame = self._frame_titulo("Matriz de Adyacencia  (vértices × vértices)")
        grid = QGridLayout()
        grid.setSpacing(2)

        # Cabecera columnas
        for j in range(n):
            lbl = QLabel(etiq.get(j, str(j+1)))
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, 0, j+1)

        for i in range(n):
            lbl = QLabel(etiq.get(i, str(i+1)))
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            for j in range(n):
                val = mat[i][j]
                c = QLabel(str(val))
                c.setAlignment(Qt.AlignCenter)
                c.setMinimumSize(44, 36)
                style = self._cell_diag() if i == j else (
                    self._cell_highlight() if val > 0 else self._cell_normal()
                )
                c.setStyleSheet(style)
                grid.addWidget(c, i+1, j+1)

        inner = QWidget(); inner.setLayout(grid)
        frame.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame)

    def _mostrar_incidencia(self):
        n = self.controller._vertices
        aristas = self.controller._aristas
        m = len(aristas)
        etiq = self.controller._etiquetas

        if m == 0:
            return

        frame = self._frame_titulo(f"Matriz de Incidencia  (vértices × aristas)  —  {m} arista(s)")
        grid = QGridLayout()
        grid.setSpacing(2)

        # Cabecera columnas (aristas e1, e2, …)
        for j in range(m):
            u, v, _ = aristas[j]
            eu = etiq.get(u, str(u+1)); ev = etiq.get(v, str(v+1))
            lbl = QLabel(f"e{j+1}\n({eu}-{ev})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setWordWrap(True)
            grid.addWidget(lbl, 0, j+1)

        for i in range(n):
            lbl = QLabel(etiq.get(i, str(i+1)))
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            for j, (u, v, _) in enumerate(aristas):
                if u == v == i:      # bucle
                    val = 2
                elif i in (u, v):
                    val = 1
                else:
                    val = 0
                c = QLabel(str(val))
                c.setAlignment(Qt.AlignCenter)
                c.setMinimumSize(44, 36)
                c.setStyleSheet(self._cell_highlight() if val > 0 else self._cell_normal())
                grid.addWidget(c, i+1, j+1)

        inner = QWidget(); inner.setLayout(grid)
        frame.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame)

    def _mostrar_adyacencia_aristas(self):
        """
        Matriz de adyacencia de aristas (m × m).
        B[i][j] con i≠j:
        +1 si el destino del arco i  es el origen del arco j  (i "entra" en j)
        -1 si el origen  del arco i  es el destino del arco j (i "sale" de donde j llega)
        0 si no comparten vértice en esa relación
        Diagonal siempre 0.
        """
        aristas = self.controller._aristas
        m = len(aristas)
        etiq = self.controller._etiquetas

        if m == 0:
            return

        frame = self._frame_titulo(
            f"Matriz de Adyacencia de Aristas  (aristas × aristas)  — diagonal = 0"
        )
        grid = QGridLayout(); grid.setSpacing(2)

        # Cabecera
        for j in range(m):
            u, v, _ = aristas[j]
            lbl = QLabel(f"e{j+1}\n({etiq.get(u,str(u+1))}→{etiq.get(v,str(v+1))})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter); lbl.setWordWrap(True)
            grid.addWidget(lbl, 0, j+1)

        for i in range(m):
            ui, vi, _ = aristas[i]
            lbl = QLabel(f"e{i+1}\n({etiq.get(ui,str(ui+1))}→{etiq.get(vi,str(vi+1))})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter); lbl.setWordWrap(True)
            grid.addWidget(lbl, i+1, 0)

            for j in range(m):
                if i == j:
                    val = 0
                    style = self._cell_diag()
                else:
                    uj, vj, _ = aristas[j]
                    # destino de i = origen de j  →  +1
                    # origen de i  = destino de j →  -1
                    if vi == uj:
                        val = 1
                        style = self._cell_highlight()
                    elif ui == vj:
                        val = -1
                        style = self._cell_neg()
                    else:
                        val = 0
                        style = self._cell_normal()

                c = QLabel(str(val)); c.setAlignment(Qt.AlignCenter); c.setMinimumSize(44, 36)
                c.setStyleSheet(style)
                grid.addWidget(c, i+1, j+1)

        inner = QWidget(); inner.setLayout(grid)
        frame.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame)

    def _calcular_circuitos(self):
        n = self.controller._vertices
        aristas = self.controller._aristas
        m = len(aristas)
        etiq = self.controller._etiquetas

        if m == 0:
            DialogoClave(0, "Info", "mensaje", self,
                         "El grafo no tiene aristas, no hay circuitos.").exec()
            return

        self._ciclos = _todos_los_ciclos_simples(n, aristas)

        if not self._ciclos:
            self._ciclos = _ciclos_fundamentales(n, aristas)

        if not self._ciclos:
            DialogoClave(0, "Info", "mensaje", self,
                         "El grafo no contiene circuitos.").exec()
            return

        self._ciclo_actual = 0

        # ── Lista de conjuntos de circuitos ────────────────────────────
        frame_lista = self._frame_titulo(f"Circuitos encontrados ({len(self._ciclos)})")
        for k, ciclo in enumerate(self._ciclos):
            nombres = []
            for ei in ciclo:
                u, v, _ = aristas[ei]
                nombres.append(f"e{ei+1}({etiq.get(u,str(u+1))}-{etiq.get(v,str(v+1))})")
            lbl = QLabel(f"C{k+1} = {{ {',  '.join(nombres)} }}")
            lbl.setStyleSheet("color: #003366; padding: 3px 6px;")
            lbl.setWordWrap(True)
            frame_lista.layout().addWidget(lbl)
        self.matrices_layout.addWidget(frame_lista)

        # ── Matriz de circuitos ────────────────────────────────────────
        nc = len(self._ciclos)
        frame_mat = self._frame_titulo(
            f"Matriz de Circuitos  ({nc} circuitos × {m} aristas)"
        )
        grid = QGridLayout(); grid.setSpacing(2)

        for j in range(m):
            u, v, _ = aristas[j]
            lbl = QLabel(f"e{j+1}\n({etiq.get(u,str(u+1))}-{etiq.get(v,str(v+1))})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter); lbl.setWordWrap(True)
            grid.addWidget(lbl, 0, j+1)

        for i, ciclo in enumerate(self._ciclos):
            lbl = QLabel(f"C{i+1}")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            ciclo_set = set(ciclo)
            for j in range(m):
                val = 1 if j in ciclo_set else 0
                c = QLabel(str(val))
                c.setAlignment(Qt.AlignCenter)
                c.setMinimumSize(44, 36)
                c.setStyleSheet(self._cell_highlight() if val else self._cell_normal())
                grid.addWidget(c, i+1, j+1)

        inner = QWidget(); inner.setLayout(grid)
        frame_mat.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame_mat)

        # Resultado y botón
        self.lbl_resultado.setText(
            f"Mostrando circuito C{self._ciclo_actual + 1} de {len(self._ciclos)}"
        )
        self.lbl_resultado.setVisible(True)
        self.btn_otro.setVisible(True)

        self._colorear_circuito(self._ciclo_actual)

    # ──────────────────────────────────────────────────────────────────
    #  Coloreo de circuitos
    # ──────────────────────────────────────────────────────────────────
    def _colorear_circuito(self, idx: int):
        """Colorea las aristas del circuito `idx` en el visualizador."""
        datos = self.controller.obtener_datos()
        aristas_sin_peso = datos["aristas"]
        n = datos["vertices"]

        # Construir diccionario de color de aristas
        ciclo = self._ciclos[idx]
        ciclo_set = set(ciclo)
        color_aristas = {}
        color = COLORES_CIRCUITO[idx % len(COLORES_CIRCUITO)]
        for ei in ciclo_set:
            color_aristas[ei] = color

        # VisualizadorGrafo no soporta colores de aristas nativamente,
        # así que seteamos el grafo normalmente y luego pintamos aristas
        self.visual.set_grafo(n, aristas_sin_peso, datos["etiquetas"], datos["pesos"])
        # Redibujar con aristas coloreadas usando el mecanismo del visualizador
        self._pintar_aristas_circuito(ciclo_set, color)

        self.lbl_resultado.setText(
            f"Mostrando circuito C{idx + 1} de {len(self._ciclos)}"
        )

    def _pintar_aristas_circuito(self, ciclo_set: set, color: str):
        """
        Redibuja el grafo y superpone líneas de color para las aristas del circuito.
        Compatible con VisualizadorGrafo original (sin soporte de color propio).
        Si el proyecto ya usa VisualizadorGrafoColoreable, este método se puede
        simplificar usando visual.set_colores(colores_aristas=...).
        """
        # Intentar usar la API coloreable si está disponible
        if hasattr(self.visual, 'set_colores'):
            self.visual.set_colores(colores_aristas={ei: color for ei in ciclo_set})
        # Si no, el grafo ya está dibujado en gris — al menos los pasos se muestran en texto

    def _ver_otro_circuito(self):
        if not self._ciclos:
            return
        self._ciclo_actual = (self._ciclo_actual + 1) % len(self._ciclos)
        self._colorear_circuito(self._ciclo_actual)

    # ──────────────────────────────────────────────────────────────────
    #  Helpers de UI
    # ──────────────────────────────────────────────────────────────────
    def _actualizar_visual(self):
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(
            datos["vertices"], datos["aristas"],
            datos["etiquetas"], datos["pesos"]
        )

    def _actualizar_combos(self):
        n = self.controller._vertices
        etiq = self.controller._etiquetas
        for combo in (self.combo_u, self.combo_v):
            combo.clear()
            for i in range(n):
                combo.addItem(etiq.get(i, str(i+1)), i)

    def _limpiar_matrices(self):
        while self.matrices_layout.count():
            child = self.matrices_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _frame_titulo(self, titulo: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            "background-color: white; border: 2px solid #99ccff;"
            "border-radius: 8px; margin: 2px;"
        )
        lay = QVBoxLayout(frame)
        lbl = QLabel(titulo)
        lbl.setStyleSheet("font-weight: bold; color: #003366; font-size: 13px; padding: 4px;")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)
        return frame

    def _cerrar_grafos(self):
        self.close(); self.volver_a_grafos()

    def _cerrar_principal(self):
        self.close(); self.volver_a_principal()

    # ──────────────────────────────────────────────────────────────────
    #  Estilos
    # ──────────────────────────────────────────────────────────────────
    @staticmethod
    def _btn(bg: str, fg: str) -> str:
        return (
            f"QPushButton {{background-color:{bg};color:{fg};font-weight:bold;"
            f"border:none;border-radius:5px;padding:8px 12px;}}"
            f"QPushButton:hover {{opacity:0.85;}}"
        )

    @staticmethod
    def _lbl(text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet("font-weight: bold; color: #003366;")
        return l

    @staticmethod
    def _sep() -> QFrame:
        s = QFrame(); s.setFrameShape(QFrame.HLine)
        s.setStyleSheet("color: #99ccff;")
        return s

    @staticmethod
    def _input_style() -> str:
        return "background-color:white;border:2px solid #99ccff;border-radius:4px;"

    @staticmethod
    def _cell_header() -> str:
        return (
            "background-color:#4d9de0;color:white;font-weight:bold;"
            "padding:6px;border-radius:3px;min-width:42px;min-height:32px;"
        )

    @staticmethod
    def _cell_normal() -> str:
        return (
            "background-color:white;color:#003366;"
            "border:1px solid #99ccff;border-radius:3px;padding:4px;"
        )

    @staticmethod
    def _cell_highlight() -> str:
        return (
            "background-color:#cce6ff;color:#003366;font-weight:bold;"
            "border:1px solid #4d9de0;border-radius:3px;padding:4px;"
        )

    @staticmethod
    def _cell_diag() -> str:
        return (
            "background-color:#e8f4fd;color:#666;"
            "border:1px solid #99ccff;border-radius:3px;padding:4px;"
        )
        
    @staticmethod
    def _cell_neg() -> str:
        return (
            "background-color:#fde8e8;color:#c0392b;font-weight:bold;"
            "border:1px solid #e74c3c;border-radius:3px;padding:4px;"
        )