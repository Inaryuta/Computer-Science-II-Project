"""
algoritmos/grafos/metricas_grafo_dirigido.py
Métricas para Grafos DIRIGIDOS:
  • Matriz de adyacencia (vértices × vértices)
  • Matriz de incidencia (vértices × aristas)  con -1 / +1
  • Matriz de circuitos  (ciclos dirigidos × aristas)
  • Circuitos fundamentales (basados en árbol de expansión)
  • Cortes fundamentales (basados en árbol de expansión)
  • Conjuntos de corte (cortes fundamentales)
  • Conjuntos independientes (sobre el grafo subyacente)
"""
from collections import deque
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QFrame, QFileDialog, QComboBox,
    QScrollArea, QGridLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from controladores.grafo_controller import GrafoController
from algoritmos.grafos.dialogo_arista import DialogoArista
from algoritmos.funcion_mod import DialogoClave


# ══════════════════════════════════════════════════════════════════════
#  Algoritmos de ciclos dirigidos (DFS con pila)
# ══════════════════════════════════════════════════════════════════════

def _ciclos_dirigidos(n: int, aristas: list[tuple]) -> list[list[int]]:
    """Todos los ciclos simples en un digrafo (solo para grafos pequeños)."""
    if n == 0:
        return []
    adj: list[list[tuple]] = [[] for _ in range(n)]
    for i, (u, v, *_) in enumerate(aristas):
        adj[u].append((v, i))
    encontrados: list[frozenset] = []
    ciclos: list[list[int]] = []

    def dfs(inicio: int, actual: int, en_pila: list[bool], camino_e: list[int]):
        for (vecino, ei) in adj[actual]:
            if vecino == inicio and len(camino_e) >= 1:
                clave = frozenset(camino_e + [ei])
                if clave not in encontrados:
                    encontrados.append(clave)
                    ciclos.append(camino_e + [ei])
            elif not en_pila[vecino]:
                en_pila[vecino] = True
                dfs(inicio, vecino, en_pila, camino_e + [ei])
                en_pila[vecino] = False

    for inicio in range(n):
        pila = [False] * n
        pila[inicio] = True
        dfs(inicio, inicio, pila, [])
    return ciclos


def _spanning_tree_dfs(n: int, aristas: list) -> tuple[list[int], list[int]]:
    """Construye un árbol de expansión usando DFS (ignorando dirección para la conexidad)."""
    adj = [[] for _ in range(n)]
    for i, (u, v, _) in enumerate(aristas):
        adj[u].append((v, i))
        adj[v].append((u, i))   # para el árbol no dirigido
    visited = [False] * n
    tree_edges = []
    chord_edges = []

    def dfs(u: int):
        visited[u] = True
        for v, ei in adj[u]:
            if not visited[v]:
                tree_edges.append(ei)
                dfs(v)
            elif ei not in tree_edges and ei not in chord_edges:
                chord_edges.append(ei)

    for i in range(n):
        if not visited[i]:
            dfs(i)
    return tree_edges, chord_edges


def _fundamental_circuits_dirigidos(n: int, aristas: list, tree_edges: list[int], chord_edges: list[int]) -> list[list[int]]:
    """Circuitos fundamentales: cada cuerda + camino en el árbol entre sus extremos (considerando orientación)."""
    adj_tree = [[] for _ in range(n)]
    for ei in tree_edges:
        u, v, _ = aristas[ei]
        adj_tree[u].append((v, ei))
        adj_tree[v].append((u, ei))
    circuits = []
    for ci in chord_edges:
        u, v, _ = aristas[ci]
        parent = [-1] * n
        parent_edge = [-1] * n
        visited = [False] * n
        q = deque([u])
        visited[u] = True
        while q:
            cur = q.popleft()
            if cur == v:
                break
            for nxt, ei in adj_tree[cur]:
                if not visited[nxt]:
                    visited[nxt] = True
                    parent[nxt] = cur
                    parent_edge[nxt] = ei
                    q.append(nxt)
        path_edges = []
        cur = v
        while cur != u:
            path_edges.append(parent_edge[cur])
            cur = parent[cur]
        circuits.append(path_edges + [ci])
    return circuits


def _fundamental_cuts_dirigidos(n: int, aristas: list, tree_edges: list[int]) -> list[list[int]]:
    """Cortes fundamentales: para cada arista del árbol, el corte contiene los arcos que van de la componente del origen a la del destino."""
    adj_tree = [[] for _ in range(n)]
    for ei in tree_edges:
        u, v, _ = aristas[ei]
        adj_tree[u].append((v, ei))
        adj_tree[v].append((u, ei))
    cuts = []
    for ei in tree_edges:
        u, v, _ = aristas[ei]
        visited = [False] * n
        q = deque([u])
        visited[u] = True
        while q:
            cur = q.popleft()
            for nxt, nxt_ei in adj_tree[cur]:
                if nxt_ei == ei:
                    continue
                if not visited[nxt]:
                    visited[nxt] = True
                    q.append(nxt)
        comp_u = {i for i in range(n) if visited[i]}
        comp_v = set(range(n)) - comp_u
        cut = [ei]
        for j, (a, b, _) in enumerate(aristas):
            if j == ei:
                continue
            if a in comp_u and b in comp_v:
                cut.append(j)
        cuts.append(cut)
    return cuts


# ══════════════════════════════════════════════════════════════════════
#  Algoritmos de conjuntos independientes (sobre grafo subyacente)
# ══════════════════════════════════════════════════════════════════════
def _todos_independientes_maximales_undir(n: int, aristas: list) -> list[set[int]]:
    """Genera todos los conjuntos independientes maximales sobre el grafo subyacente (ignorando dirección)."""
    if n == 0:
        return []
    adj = [[] for _ in range(n)]
    for u, v, _ in aristas:
        if u != v:
            adj[u].append(v)
            adj[v].append(u)
    vecinos = [set(adj[i]) for i in range(n)]
    resultados = []

    def backtrack(inicio: int, actual: set[int]):
        for v in range(inicio, n):
            if actual.isdisjoint(vecinos[v]):
                actual.add(v)
                backtrack(v + 1, actual)
                actual.remove(v)
        resultados.append(actual.copy())
    backtrack(0, set())
    # Eliminar duplicados
    unicos = []
    for s in resultados:
        if s not in unicos:
            unicos.append(s)
    return unicos


# ══════════════════════════════════════════════════════════════════════
#  Paleta de colores para circuitos
# ══════════════════════════════════════════════════════════════════════
COLORES_CIRCUITO = [
    "#e74c3c", "#27ae60", "#f39c12", "#8e44ad",
    "#16a085", "#2980b9", "#d35400", "#c0392b",
]


# ══════════════════════════════════════════════════════════════════════
#  Ventana principal
# ══════════════════════════════════════════════════════════════════════
class MetricasGrafoDirigidoWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos = volver_a_grafos
        self.volver_a_principal = volver_a_principal

        self.controller = GrafoController()
        self._ciclos: list[list[int]] = []               # todos los ciclos
        self._ciclo_actual: int = 0
        self._fund_circuits: list[list[int]] = []        # circuitos fundamentales
        self._fund_circuit_actual: int = 0
        self._fund_cuts: list[list[int]] = []            # cortes fundamentales
        self._fund_cut_actual: int = 0
        self._cortes: list[list[int]] = []               # conjuntos de corte (igual a fundamentales)
        self._corte_actual: int = 0
        self._independientes: list[set[int]] = []        # conjuntos independientes maximales
        self._independiente_actual: int = 0

        self.setWindowTitle("Métricas Grafos Dirigidos")
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

        from controladores.visualizador_grafo import VisualizadorGrafoColoreable
        self.visual = VisualizadorGrafoColoreable("Dígrafo", es_editable=True, dirigido=True)
        self.visual.setFixedSize(500, 520)
        body.addWidget(self.visual, stretch=2)

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
        h.setStyleSheet("background-color: #ffe0cc; border-radius: 10px;")
        hl = QHBoxLayout(h)
        b1 = QPushButton("← Volver a Grafos")
        b1.setStyleSheet(self._btn("#fff3e0", "#7d3c00"))
        b1.clicked.connect(self._cerrar_grafos)
        b2 = QPushButton("🏠 Inicio")
        b2.setStyleSheet(self._btn("#fff3e0", "#7d3c00"))
        b2.clicked.connect(self._cerrar_principal)
        titulo = QLabel("MÉTRICAS GRAFOS DIRIGIDOS")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setStyleSheet("color: #7d3c00;")
        hl.addWidget(b1)
        hl.addWidget(b2)
        hl.addWidget(titulo, alignment=Qt.AlignCenter)
        return h

    def _build_panel(self):
        lay = self.right_layout

        lay.addWidget(self._lbl("Número de vértices:"))
        self.spin_v = QSpinBox()
        self.spin_v.setRange(1, 12); self.spin_v.setValue(4)
        self.spin_v.setStyleSheet(self._input_style())
        lay.addWidget(self.spin_v)
        b = QPushButton("Crear dígrafo")
        b.setStyleSheet(self._btn("#e67e22", "white"))
        b.clicked.connect(self._crear_grafo)
        lay.addWidget(b)

        # Aristas dirigidas
        lay.addWidget(self._sep())
        lay.addWidget(self._lbl("Agregar arista dirigida  (origen → destino):"))
        row = QHBoxLayout()
        self.combo_u = QComboBox(); self.combo_u.setStyleSheet(self._input_style())
        self.combo_v = QComboBox(); self.combo_v.setStyleSheet(self._input_style())
        self.spin_peso = QSpinBox()
        self.spin_peso.setRange(0, 9999); self.spin_peso.setValue(1)
        self.spin_peso.setStyleSheet(self._input_style())
        row.addWidget(QLabel("De:")); row.addWidget(self.combo_u)
        row.addWidget(QLabel("→"));   row.addWidget(self.combo_v)
        row.addWidget(QLabel("Peso:")); row.addWidget(self.spin_peso)
        lay.addLayout(row)
        ba = QPushButton("+ Arista →")
        ba.setStyleSheet(self._btn("#27ae60", "white"))
        ba.clicked.connect(self._agregar_arista)
        lay.addWidget(ba)
        be = QPushButton("- Eliminar arista")
        be.setStyleSheet(self._btn("#e74c3c", "white"))
        be.clicked.connect(self._eliminar_arista)
        lay.addWidget(be)

        lay.addWidget(self._sep())
        row2 = QHBoxLayout()
        bs = QPushButton("💾 Guardar"); bs.setStyleSheet(self._btn("#3498db", "white"))
        bc = QPushButton("📂 Cargar");  bc.setStyleSheet(self._btn("#3498db", "white"))
        bs.clicked.connect(self._guardar); bc.clicked.connect(self._cargar)
        row2.addWidget(bs); row2.addWidget(bc)
        lay.addLayout(row2)

        lay.addWidget(self._sep())
        lay.addWidget(self._lbl("Operación:"))
        self.combo_op = QComboBox()
        self.combo_op.addItem("Matriz de adyacencia y de incidencia", "adyacencia_incidencia")
        self.combo_op.addItem("Matriz de circuitos", "circuitos")
        self.combo_op.addItem("Matriz de Circuitos fundamentales", "fund_circuits")
        self.combo_op.addItem("Matriz de Conjuntos de corte", "cortes")
        self.combo_op.addItem("Matriz de Conjuntos de corte fundamentales", "fund_cuts")
        self.combo_op.addItem("Matriz de Conjuntos independientes", "independientes")
        self.combo_op.setStyleSheet(self._input_style())
        lay.addWidget(self.combo_op)
        br = QPushButton("▶ Calcular")
        br.setStyleSheet(self._btn("#2c3e50", "white"))
        br.clicked.connect(self._calcular)
        lay.addWidget(br)

        # Botones de navegación
        self.btn_otro_circuito = QPushButton("Ver otro circuito")
        self.btn_otro_circuito.setStyleSheet(self._btn("#8e44ad", "white"))
        self.btn_otro_circuito.clicked.connect(self._ver_otro_circuito)
        self.btn_otro_circuito.setVisible(False)
        lay.addWidget(self.btn_otro_circuito)

        self.btn_otro_fund_circ = QPushButton("Ver otro circuito fundamental")
        self.btn_otro_fund_circ.setStyleSheet(self._btn("#8e44ad", "white"))
        self.btn_otro_fund_circ.clicked.connect(self._ver_otro_fund_circuito)
        self.btn_otro_fund_circ.setVisible(False)
        lay.addWidget(self.btn_otro_fund_circ)

        self.btn_otro_fund_cut = QPushButton("Ver otro corte fundamental")
        self.btn_otro_fund_cut.setStyleSheet(self._btn("#e67e22", "white"))
        self.btn_otro_fund_cut.clicked.connect(self._ver_otro_fund_corte)
        self.btn_otro_fund_cut.setVisible(False)
        lay.addWidget(self.btn_otro_fund_cut)

        self.btn_otro_corte = QPushButton("Ver otro conjunto de corte")
        self.btn_otro_corte.setStyleSheet(self._btn("#e67e22", "white"))
        self.btn_otro_corte.clicked.connect(self._ver_otro_corte)
        self.btn_otro_corte.setVisible(False)
        lay.addWidget(self.btn_otro_corte)

        self.btn_otro_indep = QPushButton("Ver otro conjunto independiente")
        self.btn_otro_indep.setStyleSheet(self._btn("#16a085", "white"))
        self.btn_otro_indep.clicked.connect(self._ver_otro_independiente)
        self.btn_otro_indep.setVisible(False)
        lay.addWidget(self.btn_otro_indep)

        lay.addWidget(self._sep())
        self.lbl_resultado = QLabel()
        self.lbl_resultado.setStyleSheet("font-weight:bold;color:#7d3c00;font-size:13px;")
        self.lbl_resultado.setAlignment(Qt.AlignCenter)
        self.lbl_resultado.setVisible(False)
        lay.addWidget(self.lbl_resultado)

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
        self._reset_botones()

    def _agregar_arista(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea el dígrafo.").exec()
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
            DialogoClave(0, "Info", "mensaje", self, "No hay aristas.").exec()
            return
        from PySide6.QtWidgets import QInputDialog
        opts = [f"{etiq.get(u, u+1)} → {etiq.get(v, v+1)}" for (u, v) in aristas]
        sel, ok = QInputDialog.getItem(self, "Eliminar arista", "Arista:", opts, 0, False)
        if ok:
            idx = opts.index(sel)
            u, v = aristas[idx]
            self.controller.eliminar_arista(u, v, indice=idx)

    def _guardar(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay dígrafo para guardar.").exec()
            return
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar", "", "JSON (*.json)")
        if ruta:
            self.controller.guardar_json(ruta)
            DialogoClave(0, "Éxito", "mensaje", self, "Dígrafo guardado.").exec()

    def _cargar(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar", "", "JSON (*.json)")
        if ruta:
            try:
                self.controller.cargar_json(ruta)
                self.spin_v.setValue(self.controller._vertices)
                self._actualizar_combos()
                self._limpiar_matrices()
                self._reset_botones()
                DialogoClave(0, "Éxito", "mensaje", self, "Dígrafo cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {e}").exec()

    def _calcular(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un dígrafo.").exec()
            return
        op = self.combo_op.currentData()
        self._limpiar_matrices()
        self._reset_botones()

        if op == "adyacencia_incidencia":
            self._mostrar_incidencia()
            self._mostrar_adyacencia()
            self._mostrar_adyacencia_aristas()
        elif op == "circuitos":
            self._calcular_circuitos()
        elif op == "fund_circuits":
            self._calcular_circuitos_fundamentales()
        elif op == "fund_cuts":
            self._calcular_cortes_fundamentales()
        elif op == "cortes":
            self._calcular_cortes()
        elif op == "independientes":
            self._calcular_independientes()

    # ──────────────────────────────────────────────────────────────────
    #  Matrices
    # ──────────────────────────────────────────────────────────────────
    def _mostrar_adyacencia(self):
        n = self.controller._vertices
        etiq = self.controller._etiquetas
        aristas = self.controller._aristas
        mat = [[0] * n for _ in range(n)]
        for (u, v, _) in aristas:
            mat[u][v] += 1
        frame = self._frame_titulo("Matriz de Adyacencia")
        grid = QGridLayout(); grid.setSpacing(2)
        for j in range(n):
            lbl = QLabel(etiq.get(j, str(j+1)))
            lbl.setStyleSheet(self._cell_header()); lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, 0, j+1)
        for i in range(n):
            lbl = QLabel(etiq.get(i, str(i+1)))
            lbl.setStyleSheet(self._cell_header()); lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            for j in range(n):
                val = mat[i][j]
                c = QLabel(str(val)); c.setAlignment(Qt.AlignCenter); c.setMinimumSize(44, 36)
                style = (self._cell_diag() if i == j
                         else self._cell_highlight() if val > 0
                         else self._cell_normal())
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
        frame = self._frame_titulo(f"Matriz de Incidencia Dirigida  (−1=origen, +1=destino)  —  {m} arco(s)")
        grid = QGridLayout(); grid.setSpacing(2)
        for j in range(m):
            u, v, _ = aristas[j]
            eu = etiq.get(u, str(u+1)); ev = etiq.get(v, str(v+1))
            lbl = QLabel(f"e{j+1}\n({eu}→{ev})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter); lbl.setWordWrap(True)
            grid.addWidget(lbl, 0, j+1)
        for i in range(n):
            lbl = QLabel(etiq.get(i, str(i+1)))
            lbl.setStyleSheet(self._cell_header()); lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            for j, (u, v, _) in enumerate(aristas):
                if u == v:
                    val = 1 if i == u else 0
                elif i == u:
                    val = -1
                elif i == v:
                    val = 1
                else:
                    val = 0
                c = QLabel(str(val)); c.setAlignment(Qt.AlignCenter); c.setMinimumSize(44, 36)
                if val == -1:
                    c.setStyleSheet(self._cell_neg())
                elif val == 1:
                    c.setStyleSheet(self._cell_highlight())
                else:
                    c.setStyleSheet(self._cell_normal())
                grid.addWidget(c, i+1, j+1)
        inner = QWidget(); inner.setLayout(grid)
        frame.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame)

    def _mostrar_adyacencia_aristas(self):
        aristas = self.controller._aristas
        m = len(aristas)
        etiq = self.controller._etiquetas
        if m == 0:
            return
        frame = self._frame_titulo("Matriz de Adyacencia de Aristas")
        grid = QGridLayout(); grid.setSpacing(2)
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

    # ──────────────────────────────────────────────────────────────────
    #  Circuitos (todos)
    # ──────────────────────────────────────────────────────────────────
    def _calcular_circuitos(self):
        n = self.controller._vertices
        aristas = self.controller._aristas
        m = len(aristas)
        etiq = self.controller._etiquetas
        if m == 0:
            DialogoClave(0, "Info", "mensaje", self, "No hay arcos.").exec()
            return
        self._ciclos = _ciclos_dirigidos(n, aristas)
        if not self._ciclos:
            DialogoClave(0, "Info", "mensaje", self, "No hay circuitos dirigidos.").exec()
            return
        self._ciclo_actual = 0
        # Lista de circuitos
        frame_lista = self._frame_titulo(f"Circuitos dirigidos encontrados ({len(self._ciclos)})")
        for k, ciclo in enumerate(self._ciclos):
            nombres = [f"e{ei+1}({etiq.get(u,str(u+1))}→{etiq.get(v,str(v+1))})"
                       for ei in ciclo for (u, v, _) in [aristas[ei]]]
            lbl = QLabel(f"C{k+1} = {{ {',  '.join(nombres)} }}")
            lbl.setStyleSheet("color: #7d3c00; padding: 3px 6px;")
            lbl.setWordWrap(True)
            frame_lista.layout().addWidget(lbl)
        self.matrices_layout.addWidget(frame_lista)
        # Matriz de circuitos
        nc = len(self._ciclos)
        frame_mat = self._frame_titulo(f"Matriz de Circuitos  ({nc} circuitos × {m} arcos)")
        grid = QGridLayout(); grid.setSpacing(2)
        for j in range(m):
            u, v, _ = aristas[j]
            lbl = QLabel(f"e{j+1}\n({etiq.get(u,str(u+1))}→{etiq.get(v,str(v+1))})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter); lbl.setWordWrap(True)
            grid.addWidget(lbl, 0, j+1)
        for i, ciclo in enumerate(self._ciclos):
            lbl = QLabel(f"C{i+1}")
            lbl.setStyleSheet(self._cell_header()); lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            ciclo_set = set(ciclo)
            for j in range(m):
                val = 1 if j in ciclo_set else 0
                c = QLabel(str(val)); c.setAlignment(Qt.AlignCenter); c.setMinimumSize(44, 36)
                c.setStyleSheet(self._cell_highlight() if val else self._cell_normal())
                grid.addWidget(c, i+1, j+1)
        inner = QWidget(); inner.setLayout(grid)
        frame_mat.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame_mat)
        self.lbl_resultado.setText(f"Mostrando circuito C{self._ciclo_actual+1} de {len(self._ciclos)}")
        self.lbl_resultado.setVisible(True)
        self.btn_otro_circuito.setVisible(len(self._ciclos) > 1)
        self._colorear_circuito(self._ciclo_actual)

    def _colorear_circuito(self, idx: int):
        datos = self.controller.obtener_datos()
        ciclo_set = set(self._ciclos[idx])
        color = COLORES_CIRCUITO[idx % len(COLORES_CIRCUITO)]
        self.visual.set_grafo(datos["vertices"], datos["aristas"], datos["etiquetas"], datos["pesos"])
        if hasattr(self.visual, "set_colores"):
            self.visual.set_colores(colores_aristas={ei: color for ei in ciclo_set})

    def _ver_otro_circuito(self):
        if not self._ciclos:
            return
        self._ciclo_actual = (self._ciclo_actual + 1) % len(self._ciclos)
        self._colorear_circuito(self._ciclo_actual)
        self.lbl_resultado.setText(f"Mostrando circuito C{self._ciclo_actual+1} de {len(self._ciclos)}")

    # ──────────────────────────────────────────────────────────────────
    #  Circuitos fundamentales
    # ──────────────────────────────────────────────────────────────────
    def _calcular_circuitos_fundamentales(self):
        n = self.controller._vertices
        aristas = self.controller._aristas
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un dígrafo.").exec()
            return
        tree_edges, chord_edges = _spanning_tree_dfs(n, aristas)
        if len(tree_edges) != n - 1:
            DialogoClave(0, "Info", "mensaje", self, "El dígrafo no es conexo (como grafo no dirigido).").exec()
            return
        self._fund_circuits = _fundamental_circuits_dirigidos(n, aristas, tree_edges, chord_edges)
        if not self._fund_circuits:
            DialogoClave(0, "Info", "mensaje", self, "No hay circuitos fundamentales.").exec()
            return
        self._fund_circuit_actual = 0
        self._mostrar_circuitos_fundamentales()

    def _mostrar_circuitos_fundamentales(self):
        etiq = self.controller._etiquetas
        aristas = self.controller._aristas
        m = len(aristas)
        nc = len(self._fund_circuits)
        self._limpiar_matrices()
        frame_lista = self._frame_titulo(f"Circuitos fundamentales ({nc})")
        for k, circuito in enumerate(self._fund_circuits):
            nombres = [f"e{ei+1}({etiq.get(u,str(u+1))}→{etiq.get(v,str(v+1))})"
                       for ei in circuito for (u, v, _) in [aristas[ei]]]
            lbl = QLabel(f"CF{k+1} = {{ {',  '.join(nombres)} }}")
            lbl.setStyleSheet("color: #7d3c00; padding: 3px 6px;")
            lbl.setWordWrap(True)
            frame_lista.layout().addWidget(lbl)
        self.matrices_layout.addWidget(frame_lista)
        frame_mat = self._frame_titulo(f"Matriz de Circuitos Fundamentales  ({nc} circuitos × {m} aristas)")
        grid = QGridLayout(); grid.setSpacing(2)
        for j in range(m):
            u, v, _ = aristas[j]
            lbl = QLabel(f"e{j+1}\n({etiq.get(u,str(u+1))}→{etiq.get(v,str(v+1))})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter); lbl.setWordWrap(True)
            grid.addWidget(lbl, 0, j+1)
        for i, circuito in enumerate(self._fund_circuits):
            lbl = QLabel(f"CF{i+1}")
            lbl.setStyleSheet(self._cell_header()); lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            circuito_set = set(circuito)
            for j in range(m):
                val = 1 if j in circuito_set else 0
                c = QLabel(str(val)); c.setAlignment(Qt.AlignCenter); c.setMinimumSize(44, 36)
                c.setStyleSheet(self._cell_highlight() if val else self._cell_normal())
                grid.addWidget(c, i+1, j+1)
        inner = QWidget(); inner.setLayout(grid)
        frame_mat.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame_mat)
        self.lbl_resultado.setText(f"Mostrando circuito fundamental CF{self._fund_circuit_actual+1} de {nc}")
        self.lbl_resultado.setVisible(True)
        self.btn_otro_fund_circ.setVisible(nc > 1)
        self._colorear_circuito_fundamental(self._fund_circuit_actual)

    def _colorear_circuito_fundamental(self, idx: int):
        circuito = self._fund_circuits[idx]
        color = COLORES_CIRCUITO[idx % len(COLORES_CIRCUITO)]
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(datos["vertices"], datos["aristas"], datos["etiquetas"], datos["pesos"])
        if hasattr(self.visual, "set_colores"):
            self.visual.set_colores(colores_aristas={ei: color for ei in circuito})

    def _ver_otro_fund_circuito(self):
        if not self._fund_circuits:
            return
        self._fund_circuit_actual = (self._fund_circuit_actual + 1) % len(self._fund_circuits)
        self._colorear_circuito_fundamental(self._fund_circuit_actual)
        self.lbl_resultado.setText(f"Mostrando circuito fundamental CF{self._fund_circuit_actual+1} de {len(self._fund_circuits)}")

    # ──────────────────────────────────────────────────────────────────
    #  Cortes fundamentales
    # ──────────────────────────────────────────────────────────────────
    def _calcular_cortes_fundamentales(self):
        n = self.controller._vertices
        aristas = self.controller._aristas
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un dígrafo.").exec()
            return
        tree_edges, _ = _spanning_tree_dfs(n, aristas)
        if len(tree_edges) != n - 1:
            DialogoClave(0, "Info", "mensaje", self, "El dígrafo no es conexo (como grafo no dirigido).").exec()
            return
        self._fund_cuts = _fundamental_cuts_dirigidos(n, aristas, tree_edges)
        if not self._fund_cuts:
            DialogoClave(0, "Info", "mensaje", self, "No hay cortes fundamentales.").exec()
            return
        self._fund_cut_actual = 0
        self._mostrar_cortes_fundamentales()

    def _mostrar_cortes_fundamentales(self):
        etiq = self.controller._etiquetas
        aristas = self.controller._aristas
        m = len(aristas)
        nc = len(self._fund_cuts)
        self._limpiar_matrices()
        frame_lista = self._frame_titulo(f"Cortes fundamentales ({nc})")
        for k, corte in enumerate(self._fund_cuts):
            nombres = [f"e{ei+1}({etiq.get(u,str(u+1))}→{etiq.get(v,str(v+1))})"
                       for ei in corte for (u, v, _) in [aristas[ei]]]
            lbl = QLabel(f"KF{k+1} = {{ {',  '.join(nombres)} }}")
            lbl.setStyleSheet("color: #7d3c00; padding: 3px 6px;")
            lbl.setWordWrap(True)
            frame_lista.layout().addWidget(lbl)
        self.matrices_layout.addWidget(frame_lista)
        frame_mat = self._frame_titulo(f"Matriz de Cortes Fundamentales  ({nc} cortes × {m} aristas)")
        grid = QGridLayout(); grid.setSpacing(2)
        for j in range(m):
            u, v, _ = aristas[j]
            lbl = QLabel(f"e{j+1}\n({etiq.get(u,str(u+1))}→{etiq.get(v,str(v+1))})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter); lbl.setWordWrap(True)
            grid.addWidget(lbl, 0, j+1)
        for i, corte in enumerate(self._fund_cuts):
            lbl = QLabel(f"KF{i+1}")
            lbl.setStyleSheet(self._cell_header()); lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            corte_set = set(corte)
            for j in range(m):
                val = 1 if j in corte_set else 0
                c = QLabel(str(val)); c.setAlignment(Qt.AlignCenter); c.setMinimumSize(44, 36)
                c.setStyleSheet(self._cell_highlight() if val else self._cell_normal())
                grid.addWidget(c, i+1, j+1)
        inner = QWidget(); inner.setLayout(grid)
        frame_mat.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame_mat)
        self.lbl_resultado.setText(f"Mostrando corte fundamental KF{self._fund_cut_actual+1} de {nc}")
        self.lbl_resultado.setVisible(True)
        self.btn_otro_fund_cut.setVisible(nc > 1)
        self._colorear_corte_fundamental(self._fund_cut_actual)

    def _colorear_corte_fundamental(self, idx: int):
        corte = self._fund_cuts[idx]
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(datos["vertices"], datos["aristas"], datos["etiquetas"], datos["pesos"])
        if hasattr(self.visual, "set_colores"):
            self.visual.set_colores(colores_aristas={ei: "#e74c3c" for ei in corte})

    def _ver_otro_fund_corte(self):
        if not self._fund_cuts:
            return
        self._fund_cut_actual = (self._fund_cut_actual + 1) % len(self._fund_cuts)
        self._colorear_corte_fundamental(self._fund_cut_actual)
        self.lbl_resultado.setText(f"Mostrando corte fundamental KF{self._fund_cut_actual+1} de {len(self._fund_cuts)}")

    # ──────────────────────────────────────────────────────────────────
    #  Conjuntos de corte (fundamentales)
    # ──────────────────────────────────────────────────────────────────
    def _calcular_cortes(self):
        n = self.controller._vertices
        aristas = self.controller._aristas
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un dígrafo.").exec()
            return
        # Reutilizamos cortes fundamentales
        tree_edges, _ = _spanning_tree_dfs(n, aristas)
        self._cortes = _fundamental_cuts_dirigidos(n, aristas, tree_edges)
        if not self._cortes:
            DialogoClave(0, "Info", "mensaje", self, "No se encontraron conjuntos de corte.").exec()
            return
        self._corte_actual = 0
        self._mostrar_cortes()

    def _mostrar_cortes(self):
        etiq = self.controller._etiquetas
        aristas = self.controller._aristas
        m = len(aristas)
        nc = len(self._cortes)
        self._limpiar_matrices()
        frame_lista = self._frame_titulo(f"Conjuntos de corte ({nc})")
        for k, corte in enumerate(self._cortes):
            nombres = [f"e{ei+1}({etiq.get(u,str(u+1))}→{etiq.get(v,str(v+1))})"
                       for ei in corte for (u, v, _) in [aristas[ei]]]
            lbl = QLabel(f"K{k+1} = {{ {',  '.join(nombres)} }}")
            lbl.setStyleSheet("color: #7d3c00; padding: 3px 6px;")
            lbl.setWordWrap(True)
            frame_lista.layout().addWidget(lbl)
        self.matrices_layout.addWidget(frame_lista)
        frame_mat = self._frame_titulo(f"Matriz de Cortes  ({nc} cortes × {m} aristas)")
        grid = QGridLayout(); grid.setSpacing(2)
        for j in range(m):
            u, v, _ = aristas[j]
            lbl = QLabel(f"e{j+1}\n({etiq.get(u,str(u+1))}→{etiq.get(v,str(v+1))})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter); lbl.setWordWrap(True)
            grid.addWidget(lbl, 0, j+1)
        for i, corte in enumerate(self._cortes):
            lbl = QLabel(f"K{i+1}")
            lbl.setStyleSheet(self._cell_header()); lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            corte_set = set(corte)
            for j in range(m):
                val = 1 if j in corte_set else 0
                c = QLabel(str(val)); c.setAlignment(Qt.AlignCenter); c.setMinimumSize(44, 36)
                c.setStyleSheet(self._cell_highlight() if val else self._cell_normal())
                grid.addWidget(c, i+1, j+1)
        inner = QWidget(); inner.setLayout(grid)
        frame_mat.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame_mat)
        self.lbl_resultado.setText(f"Mostrando corte K{self._corte_actual+1} de {nc}")
        self.lbl_resultado.setVisible(True)
        self.btn_otro_corte.setVisible(nc > 1)
        self._colorear_corte(self._corte_actual)

    def _colorear_corte(self, idx: int):
        corte = self._cortes[idx]
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(datos["vertices"], datos["aristas"], datos["etiquetas"], datos["pesos"])
        if hasattr(self.visual, "set_colores"):
            self.visual.set_colores(colores_aristas={ei: "#e74c3c" for ei in corte})

    def _ver_otro_corte(self):
        if not self._cortes:
            return
        self._corte_actual = (self._corte_actual + 1) % len(self._cortes)
        self._colorear_corte(self._corte_actual)
        self.lbl_resultado.setText(f"Mostrando corte K{self._corte_actual+1} de {len(self._cortes)}")

    # ──────────────────────────────────────────────────────────────────
    #  Conjuntos independientes
    # ──────────────────────────────────────────────────────────────────
    def _calcular_independientes(self):
        n = self.controller._vertices
        aristas = self.controller._aristas
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un dígrafo.").exec()
            return
        self._independientes = _todos_independientes_maximales_undir(n, aristas)
        if not self._independientes:
            DialogoClave(0, "Info", "mensaje", self, "No se encontraron conjuntos independientes.").exec()
            return
        self._independiente_actual = 0
        self._mostrar_independientes()

    def _mostrar_independientes(self):
        etiq = self.controller._etiquetas
        n = self.controller._vertices
        nc = len(self._independientes)
        self._limpiar_matrices()
        # Lista de conjuntos independientes
        frame_lista = self._frame_titulo(f"Conjuntos independientes maximales ({nc})")
        for k, conjunto in enumerate(self._independientes):
            nom = ", ".join(etiq.get(v, str(v+1)) for v in sorted(conjunto)) or "∅"
            lbl = QLabel(f"I{k+1} = {{ {nom} }}  |D|={len(conjunto)}")
            lbl.setStyleSheet("color: #7d3c00; padding: 3px 6px;")
            lbl.setWordWrap(True)
            frame_lista.layout().addWidget(lbl)
        self.matrices_layout.addWidget(frame_lista)
        # Matriz de independencia (conjuntos × vértices)
        frame_mat = self._frame_titulo(f"Matriz de Independencia  ({nc} conjuntos × {n} vértices)")
        grid = QGridLayout(); grid.setSpacing(2)
        for j in range(n):
            lbl = QLabel(etiq.get(j, str(j+1)))
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, 0, j+1)
        for i, conjunto in enumerate(self._independientes):
            lbl = QLabel(f"I{i+1}")
            lbl.setStyleSheet(self._cell_header()); lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            for j in range(n):
                val = 1 if j in conjunto else 0
                c = QLabel(str(val)); c.setAlignment(Qt.AlignCenter); c.setMinimumSize(44, 36)
                c.setStyleSheet(self._cell_highlight() if val else self._cell_normal())
                grid.addWidget(c, i+1, j+1)
        inner = QWidget(); inner.setLayout(grid)
        frame_mat.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame_mat)
        self.lbl_resultado.setText(f"Mostrando conjunto independiente I{self._independiente_actual+1} de {nc}")
        self.lbl_resultado.setVisible(True)
        self.btn_otro_indep.setVisible(nc > 1)
        self._colorear_independiente(self._independiente_actual)

    def _colorear_independiente(self, idx: int):
        conjunto = self._independientes[idx]
        datos = self.controller.obtener_datos()
        n = datos["vertices"]
        colores_v = {v: "#2ecc71" if v in conjunto else "#4d9de0" for v in range(n)}
        self.visual.set_grafo(datos["vertices"], datos["aristas"], datos["etiquetas"], datos["pesos"])
        if hasattr(self.visual, "set_colores"):
            self.visual.set_colores(colores_vertices=colores_v)

    def _ver_otro_independiente(self):
        if not self._independientes:
            return
        self._independiente_actual = (self._independiente_actual + 1) % len(self._independientes)
        self._colorear_independiente(self._independiente_actual)
        self.lbl_resultado.setText(f"Mostrando conjunto independiente I{self._independiente_actual+1} de {len(self._independientes)}")

    # ──────────────────────────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────────────────────────
    def _actualizar_visual(self):
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(datos["vertices"], datos["aristas"], datos["etiquetas"], datos["pesos"])

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
        frame.setStyleSheet("background-color: white; border: 2px solid #f0c080; border-radius: 8px; margin: 2px;")
        lay = QVBoxLayout(frame)
        lbl = QLabel(titulo)
        lbl.setStyleSheet("font-weight:bold;color:#7d3c00;font-size:13px;padding:4px;")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)
        return frame

    def _reset_botones(self):
        self.btn_otro_circuito.setVisible(False)
        self.btn_otro_fund_circ.setVisible(False)
        self.btn_otro_fund_cut.setVisible(False)
        self.btn_otro_corte.setVisible(False)
        self.btn_otro_indep.setVisible(False)
        self.lbl_resultado.setVisible(False)

    def _cerrar_grafos(self):
        self.close(); self.volver_a_grafos()

    def _cerrar_principal(self):
        self.close(); self.volver_a_principal()

    # ──────────────────────────────────────────────────────────────────
    #  Estilos
    # ──────────────────────────────────────────────────────────────────
    @staticmethod
    def _btn(bg: str, fg: str) -> str:
        return (f"QPushButton {{background-color:{bg};color:{fg};font-weight:bold;"
                f"border:none;border-radius:5px;padding:8px 12px;}}"
                f"QPushButton:hover {{opacity:0.85;}}")

    @staticmethod
    def _lbl(text: str) -> QLabel:
        l = QLabel(text); l.setStyleSheet("font-weight:bold;color:#7d3c00;"); return l

    @staticmethod
    def _sep() -> QFrame:
        s = QFrame(); s.setFrameShape(QFrame.HLine); s.setStyleSheet("color: #f0c080;"); return s

    @staticmethod
    def _input_style() -> str:
        return "background-color:white;border:2px solid #f0c080;border-radius:4px;"

    @staticmethod
    def _cell_header() -> str:
        return ("background-color:#e67e22;color:white;font-weight:bold;"
                "padding:6px;border-radius:3px;min-width:42px;min-height:32px;")

    @staticmethod
    def _cell_normal() -> str:
        return ("background-color:white;color:#003366;"
                "border:1px solid #f0c080;border-radius:3px;padding:4px;")

    @staticmethod
    def _cell_highlight() -> str:
        return ("background-color:#fdebd0;color:#7d3c00;font-weight:bold;"
                "border:1px solid #e67e22;border-radius:3px;padding:4px;")

    @staticmethod
    def _cell_neg() -> str:
        return ("background-color:#fde8e8;color:#c0392b;font-weight:bold;"
                "border:1px solid #e74c3c;border-radius:3px;padding:4px;")

    @staticmethod
    def _cell_diag() -> str:
        return ("background-color:#fef9f0;color:#aaa;"
                "border:1px solid #f0c080;border-radius:3px;padding:4px;")