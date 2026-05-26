"""
algoritmos/grafos/metricas_grafo.py
Métricas para Grafos NO Dirigidos:
  • Matriz de adyacencia (vértices × vértices)
  • Matriz de incidencia (vértices × aristas)
  • Matriz de circuitos (ciclos × aristas) + visualización coloreada
  • Conjuntos de corte (cortes × aristas) + visualización coloreada
  • Circuitos fundamentales (basados en árbol de expansión)
  • Cortes fundamentales (basados en árbol de expansión)
  • Conjuntos independientes maximales + visualización coloreada
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
from controladores.visualizador_grafo import VisualizadorGrafo
from algoritmos.grafos.dialogo_arista import DialogoArista
from algoritmos.funcion_mod import DialogoClave


# ══════════════════════════════════════════════════════════════════════
#  Algoritmos de ciclos (grafos no dirigidos)
# ══════════════════════════════════════════════════════════════════════

def _ciclos_fundamentales(n: int, aristas: list[tuple]) -> list[list[int]]:
    """Ciclos fundamentales usando un árbol DFS."""
    if n == 0:
        return []
    adj: list[list[tuple]] = [[] for _ in range(n)]
    for i, (u, v, *_) in enumerate(aristas):
        adj[u].append((v, i))
        adj[v].append((u, i))
    visitado = [False] * n
    padre = [-1] * n
    padre_arista = [-1] * n
    profundidad = [0] * n
    ciclos = []

    def dfs(v: int, depth: int):
        visitado[v] = True
        profundidad[v] = depth
        for w, ei in adj[v]:
            if not visitado[w]:
                padre[w] = v
                padre_arista[w] = ei
                dfs(w, depth + 1)
            elif padre[v] != w:
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
    """Todos los ciclos simples (solo para grafos pequeños)."""
    if n == 0:
        return []
    adj = [[] for _ in range(n)]
    for i, (u, v, *_) in enumerate(aristas):
        adj[u].append((v, i))
        if u != v:
            adj[v].append((u, i))
    encontrados = []
    ciclos_aristas = []

    def dfs(inicio: int, actual: int, visitados: list[bool],
            camino_v: list[int], camino_e: list[int], ultima_arista: int):
        for vecino, ei in adj[actual]:
            if ei == ultima_arista:
                continue
            if vecino == inicio and len(camino_v) >= 2:
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
#  Algoritmos de conjuntos de corte
# ══════════════════════════════════════════════════════════════════════
def _conjuntos_corte(n: int, aristas: list) -> list[list[int]]:
    """
    Conjuntos de corte fundamentales basados en un árbol DFS.
    Para cada arista del árbol, se calcula el corte (aristas con un extremo
    en cada componente al eliminar dicha arista del árbol).
    """
    if n == 0 or not aristas:
        return []
    # Construir árbol DFS
    adj = [[] for _ in range(n)]
    for i, (u, v, _) in enumerate(aristas):
        adj[u].append((v, i))
        adj[v].append((u, i))
    visitado = [False] * n
    arbol = []          # índices de aristas del árbol

    def dfs(v: int):
        visitado[v] = True
        for w, ei in adj[v]:
            if not visitado[w]:
                arbol.append(ei)
                dfs(w)

    dfs(0)

    conjuntos = []
    visto = []

    for ei in arbol:
        u, v, _ = aristas[ei]
        # Árbol sin la arista ei
        adj_t = [[] for _ in range(n)]
        for ea in arbol:
            if ea == ei:
                continue
            a, b, _ = aristas[ea]
            adj_t[a].append(b)
            adj_t[b].append(a)
        # Componente de u en el árbol reducido
        comp_u = set()
        q = deque([u])
        while q:
            cur = q.popleft()
            if cur in comp_u:
                continue
            comp_u.add(cur)
            for nb in adj_t[cur]:
                if nb not in comp_u:
                    q.append(nb)
        comp_v = set(range(n)) - comp_u
        # Aristas originales que cruzan el corte
        corte = [
            j for j, (a, b, _) in enumerate(aristas)
            if (a in comp_u and b in comp_v) or (a in comp_v and b in comp_u)
        ]
        clave = frozenset(corte)
        if corte and clave not in visto:
            visto.append(clave)
            conjuntos.append(corte)
    return conjuntos


# ══════════════════════════════════════════════════════════════════════
#  Algoritmos de circuitos y cortes fundamentales (basados en árbol)
# ══════════════════════════════════════════════════════════════════════

def _spanning_tree_dfs(n: int, aristas: list) -> tuple[list[int], list[int]]:
    """Construye un árbol de expansión usando DFS. Devuelve (tree_edges, chord_edges)."""
    adj = [[] for _ in range(n)]
    for i, (u, v, _) in enumerate(aristas):
        adj[u].append((v, i))
        adj[v].append((u, i))
    visited = [False] * n
    tree_edges = []
    chord_edges = []
    parent = [-1] * n
    parent_edge = [-1] * n

    def dfs(u: int):
        visited[u] = True
        for v, ei in adj[u]:
            if not visited[v]:
                parent[v] = u
                parent_edge[v] = ei
                tree_edges.append(ei)
                dfs(v)
            elif v != parent[u] and ei not in tree_edges and ei not in chord_edges:
                chord_edges.append(ei)
    for i in range(n):
        if not visited[i]:
            dfs(i)
    return tree_edges, chord_edges


def _fundamental_circuits(n: int, aristas: list, tree_edges: list[int], chord_edges: list[int]) -> list[list[int]]:
    """Circuitos fundamentales: cada cuerda + camino en el árbol entre sus extremos."""
    # Construir árbol
    adj_tree = [[] for _ in range(n)]
    for ei in tree_edges:
        u, v, _ = aristas[ei]
        adj_tree[u].append((v, ei))
        adj_tree[v].append((u, ei))
    circuits = []
    for ci in chord_edges:
        u, v, _ = aristas[ci]
        # BFS para camino en el árbol
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
        # Reconstruir camino de v a u
        path_edges = []
        cur = v
        while cur != u:
            path_edges.append(parent_edge[cur])
            cur = parent[cur]
        circuits.append(path_edges + [ci])
    return circuits


def _fundamental_cuts(n: int, aristas: list, tree_edges: list[int]) -> list[list[int]]:
    """Cortes fundamentales: para cada arista del árbol, el corte contiene esa arista y las cuerdas que conectan las dos componentes."""
    adj_tree = [[] for _ in range(n)]
    for ei in tree_edges:
        u, v, _ = aristas[ei]
        adj_tree[u].append((v, ei))
        adj_tree[v].append((u, ei))
    cuts = []
    for ei in tree_edges:
        u, v, _ = aristas[ei]
        # Componente de u sin la arista ei
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
            if (a in comp_u and b in comp_v) or (a in comp_v and b in comp_u):
                cut.append(j)
        cuts.append(cut)
    return cuts


# ══════════════════════════════════════════════════════════════════════
#  Algoritmos de conjuntos independientes maximales
# ══════════════════════════════════════════════════════════════════════
def _todos_independientes_maximales(n: int, aristas: list) -> list[set[int]]:
    """Genera todos los conjuntos independientes maximales mediante backtracking."""
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
#  Paletas de colores
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
        self._ciclos: list[list[int]] = []
        self._ciclo_actual: int = 0
        self._cortes: list[list[int]] = []
        self._corte_actual: int = 0
        self._fund_circuits: list[list[int]] = []
        self._fund_circuit_actual: int = 0
        self._fund_cuts: list[list[int]] = []
        self._fund_cut_actual: int = 0
        self._independientes: list[set[int]] = []
        self._independiente_actual: int = 0

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

        # Visualizador
        self.visual = VisualizadorGrafo("Grafo", es_editable=True)
        self.visual.setFixedSize(500, 520)
        body.addWidget(self.visual, stretch=2)

        # Panel derecho con scroll
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

        # Crear grafo
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

        # Aristas
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

        # Guardar / Cargar
        lay.addWidget(self._sep())
        row2 = QHBoxLayout()
        bs = QPushButton("💾 Guardar"); bs.setStyleSheet(self._btn("#3498db", "white"))
        bc = QPushButton("📂 Cargar");  bc.setStyleSheet(self._btn("#3498db", "white"))
        bs.clicked.connect(self._guardar); bc.clicked.connect(self._cargar)
        row2.addWidget(bs); row2.addWidget(bc)
        lay.addLayout(row2)

        # Operación
        lay.addWidget(self._sep())
        lay.addWidget(self._lbl("Operación:"))
        self.combo_op = QComboBox()
        self.combo_op.addItem("Matriz de adyacencia y de incidencia", "adyacencia_incidencia")
        self.combo_op.addItem("Matriz de circuitos", "circuitos")
        self.combo_op.addItem("Conjuntos de corte", "cortes")
        self.combo_op.addItem("Circuitos fundamentales", "fund_circuits")
        self.combo_op.addItem("Cortes fundamentales", "fund_cuts")
        self.combo_op.addItem("Conjuntos independientes", "independientes")
        self.combo_op.setStyleSheet(self._input_style())
        lay.addWidget(self.combo_op)
        br = QPushButton("▶ Calcular")
        br.setStyleSheet(self._btn("#2c3e50", "white"))
        br.clicked.connect(self._calcular)
        lay.addWidget(br)

        # Botones para navegar entre resultados
        self.btn_otro_circuito = QPushButton("Ver otro circuito")
        self.btn_otro_circuito.setStyleSheet(self._btn("#8e44ad", "white"))
        self.btn_otro_circuito.clicked.connect(self._ver_otro_circuito)
        self.btn_otro_circuito.setVisible(False)
        lay.addWidget(self.btn_otro_circuito)

        self.btn_otro_corte = QPushButton("Ver otro corte")
        self.btn_otro_corte.setStyleSheet(self._btn("#e67e22", "white"))
        self.btn_otro_corte.clicked.connect(self._ver_otro_corte)
        self.btn_otro_corte.setVisible(False)
        lay.addWidget(self.btn_otro_corte)

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

        self.btn_otro_indep = QPushButton("Ver otro conjunto independiente")
        self.btn_otro_indep.setStyleSheet(self._btn("#16a085", "white"))
        self.btn_otro_indep.clicked.connect(self._ver_otro_independiente)
        self.btn_otro_indep.setVisible(False)
        lay.addWidget(self.btn_otro_indep)

        # Área de resultados
        lay.addWidget(self._sep())
        self.lbl_resultado = QLabel()
        self.lbl_resultado.setStyleSheet("font-weight: bold; color: #003366; font-size: 13px;")
        self.lbl_resultado.setAlignment(Qt.AlignCenter)
        self.lbl_resultado.setVisible(False)
        lay.addWidget(self.lbl_resultado)

        # Contenedor de matrices
        self.matrices_widget = QWidget()
        self.matrices_layout = QVBoxLayout(self.matrices_widget)
        self.matrices_layout.setSpacing(16)
        lay.addWidget(self.matrices_widget)

    # ──────────────────────────────────────────────────────────────────
    #  Acciones básicas
    # ──────────────────────────────────────────────────────────────────
    def _crear_grafo(self):
        n = self.spin_v.value()
        self.controller.set_vertices(n)
        self._actualizar_combos()
        self._limpiar_matrices()
        self._reset_botones()

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
                self._reset_botones()
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {e}").exec()

    def _calcular(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec()
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
        elif op == "cortes":
            self._calcular_cortes()
        elif op == "fund_circuits":
            self._calcular_circuitos_fundamentales()
        elif op == "fund_cuts":
            self._calcular_cortes_fundamentales()
        elif op == "independientes":
            self._calcular_independientes()

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
                style = self._cell_diag() if i == j else (self._cell_highlight() if val > 0 else self._cell_normal())
                c.setStyleSheet(style)
                grid.addWidget(c, i+1, j+1)
        inner = QWidget()
        inner.setLayout(grid)
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
        for j in range(m):
            u, v, _ = aristas[j]
            eu = etiq.get(u, str(u+1))
            ev = etiq.get(v, str(v+1))
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
                if u == v == i:
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
        inner = QWidget()
        inner.setLayout(grid)
        frame.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame)

    def _mostrar_adyacencia_aristas(self):
        aristas = self.controller._aristas
        m = len(aristas)
        etiq = self.controller._etiquetas
        if m == 0:
            return
        frame = self._frame_titulo("Matriz de Adyacencia de Aristas  (aristas × aristas)")
        grid = QGridLayout()
        grid.setSpacing(2)
        for j in range(m):
            u, v, _ = aristas[j]
            lbl = QLabel(f"e{j+1}\n({etiq.get(u,str(u+1))}→{etiq.get(v,str(v+1))})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setWordWrap(True)
            grid.addWidget(lbl, 0, j+1)
        for i in range(m):
            ui, vi, _ = aristas[i]
            lbl = QLabel(f"e{i+1}\n({etiq.get(ui,str(ui+1))}→{etiq.get(vi,str(vi+1))})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setWordWrap(True)
            grid.addWidget(lbl, i+1, 0)
            for j in range(m):
                if i == j:
                    val = 0
                    style = self._cell_diag()
                else:
                    uj, vj, _ = aristas[j]
                    if vi == uj or ui == vj:
                        val = 1
                        style = self._cell_highlight()
                    else:
                        val = 0
                        style = self._cell_normal()
                c = QLabel(str(val))
                c.setAlignment(Qt.AlignCenter)
                c.setMinimumSize(44, 36)
                c.setStyleSheet(style)
                grid.addWidget(c, i+1, j+1)
        inner = QWidget()
        inner.setLayout(grid)
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
            DialogoClave(0, "Info", "mensaje", self, "El grafo no tiene aristas, no hay circuitos.").exec()
            return
        self._ciclos = _todos_los_ciclos_simples(n, aristas)
        if not self._ciclos:
            self._ciclos = _ciclos_fundamentales(n, aristas)
        if not self._ciclos:
            DialogoClave(0, "Info", "mensaje", self, "El grafo no contiene circuitos.").exec()
            return
        self._ciclo_actual = 0
        # Lista de circuitos
        frame_lista = self._frame_titulo(f"Circuitos encontrados ({len(self._ciclos)})")
        for k, ciclo in enumerate(self._ciclos):
            nombres = [f"e{ei+1}({etiq.get(u,str(u+1))}-{etiq.get(v,str(v+1))})"
                       for ei in ciclo for (u, v, _) in [aristas[ei]]]
            lbl = QLabel(f"C{k+1} = {{ {',  '.join(nombres)} }}")
            lbl.setStyleSheet("color: #003366; padding: 3px 6px;")
            lbl.setWordWrap(True)
            frame_lista.layout().addWidget(lbl)
        self.matrices_layout.addWidget(frame_lista)
        # Matriz de circuitos
        nc = len(self._ciclos)
        frame_mat = self._frame_titulo(f"Matriz de Circuitos  ({nc} circuitos × {m} aristas)")
        grid = QGridLayout()
        grid.setSpacing(2)
        for j in range(m):
            u, v, _ = aristas[j]
            lbl = QLabel(f"e{j+1}\n({etiq.get(u,str(u+1))}-{etiq.get(v,str(v+1))})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setWordWrap(True)
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
        inner = QWidget()
        inner.setLayout(grid)
        frame_mat.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame_mat)

        self.lbl_resultado.setText(f"Mostrando circuito C{self._ciclo_actual+1} de {len(self._ciclos)}")
        self.lbl_resultado.setVisible(True)
        self.btn_otro_circuito.setVisible(len(self._ciclos) > 1)
        self._colorear_circuito(self._ciclo_actual)

    def _colorear_circuito(self, idx: int):
        ciclo = self._ciclos[idx]
        color = COLORES_CIRCUITO[idx % len(COLORES_CIRCUITO)]
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(datos["vertices"], datos["aristas"], datos["etiquetas"], datos["pesos"])
        if hasattr(self.visual, "set_colores"):
            self.visual.set_colores(colores_aristas={ei: color for ei in ciclo})

    def _ver_otro_circuito(self):
        if not self._ciclos:
            return
        self._ciclo_actual = (self._ciclo_actual + 1) % len(self._ciclos)
        self._colorear_circuito(self._ciclo_actual)
        self.lbl_resultado.setText(f"Mostrando circuito C{self._ciclo_actual+1} de {len(self._ciclos)}")

    # ──────────────────────────────────────────────────────────────────
    #  Cortes (todos)
    # ──────────────────────────────────────────────────────────────────
    def _calcular_cortes(self):
        n = self.controller._vertices
        aristas = self.controller._aristas
        m = len(aristas)
        etiq = self.controller._etiquetas
        if m == 0:
            DialogoClave(0, "Info", "mensaje", self, "El grafo no tiene aristas.").exec()
            return
        self._cortes = _conjuntos_corte(n, aristas)
        if not self._cortes:
            DialogoClave(0, "Info", "mensaje", self, "No se encontraron conjuntos de corte (¿el grafo es conexo?).").exec()
            return
        self._corte_actual = 0
        # Lista de cortes
        frame_lista = self._frame_titulo(f"Conjuntos de corte ({len(self._cortes)})")
        for k, corte in enumerate(self._cortes):
            nombres = [f"e{ei+1}({etiq.get(u,str(u+1))}-{etiq.get(v,str(v+1))})"
                       for ei in corte for (u, v, _) in [aristas[ei]]]
            lbl = QLabel(f"K{k+1} = {{ {',  '.join(nombres)} }}")
            lbl.setStyleSheet("color: #003366; padding: 3px 6px;")
            lbl.setWordWrap(True)
            frame_lista.layout().addWidget(lbl)
        self.matrices_layout.addWidget(frame_lista)
        # Matriz de cortes
        nc = len(self._cortes)
        frame_mat = self._frame_titulo(f"Matriz de Cortes  ({nc} cortes × {m} aristas)")
        grid = QGridLayout()
        grid.setSpacing(2)
        for j in range(m):
            u, v, _ = aristas[j]
            lbl = QLabel(f"e{j+1}\n({etiq.get(u,str(u+1))}-{etiq.get(v,str(v+1))})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setWordWrap(True)
            grid.addWidget(lbl, 0, j+1)
        for i, corte in enumerate(self._cortes):
            lbl = QLabel(f"K{i+1}")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            corte_set = set(corte)
            for j in range(m):
                val = 1 if j in corte_set else 0
                c = QLabel(str(val))
                c.setAlignment(Qt.AlignCenter)
                c.setMinimumSize(44, 36)
                c.setStyleSheet(self._cell_highlight() if val else self._cell_normal())
                grid.addWidget(c, i+1, j+1)
        inner = QWidget()
        inner.setLayout(grid)
        frame_mat.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame_mat)

        self.lbl_resultado.setText(f"Mostrando corte K{self._corte_actual+1} de {len(self._cortes)}")
        self.lbl_resultado.setVisible(True)
        self.btn_otro_corte.setVisible(len(self._cortes) > 1)
        self._colorear_corte(self._corte_actual)

    def _colorear_corte(self, idx: int):
        corte_set = set(self._cortes[idx])
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(datos["vertices"], datos["aristas"], datos["etiquetas"], datos["pesos"])
        if hasattr(self.visual, "set_colores"):
            self.visual.set_colores(colores_aristas={ei: "#e74c3c" for ei in corte_set})

    def _ver_otro_corte(self):
        if not self._cortes:
            return
        self._corte_actual = (self._corte_actual + 1) % len(self._cortes)
        self._colorear_corte(self._corte_actual)
        self.lbl_resultado.setText(f"Mostrando corte K{self._corte_actual+1} de {len(self._cortes)}")

    # ──────────────────────────────────────────────────────────────────
    #  Circuitos fundamentales
    # ──────────────────────────────────────────────────────────────────
    def _calcular_circuitos_fundamentales(self):
        n = self.controller._vertices
        aristas = self.controller._aristas
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec()
            return
        tree_edges, chord_edges = _spanning_tree_dfs(n, aristas)
        if len(tree_edges) != n - 1:
            DialogoClave(0, "Info", "mensaje", self, "El grafo no es conexo, no se puede obtener un árbol de expansión completo.").exec()
            return
        self._fund_circuits = _fundamental_circuits(n, aristas, tree_edges, chord_edges)
        if not self._fund_circuits:
            DialogoClave(0, "Info", "mensaje", self, "No hay circuitos fundamentales (grafo es un árbol).").exec()
            return
        self._fund_circuit_actual = 0
        self._mostrar_circuitos_fundamentales()

    def _mostrar_circuitos_fundamentales(self):
        etiq = self.controller._etiquetas
        aristas = self.controller._aristas
        m = len(aristas)
        nc = len(self._fund_circuits)
        self._limpiar_matrices()
        # Lista de circuitos fundamentales
        frame_lista = self._frame_titulo(f"Circuitos fundamentales ({nc})")
        for k, circuito in enumerate(self._fund_circuits):
            nombres = [f"e{ei+1}({etiq.get(u,str(u+1))}-{etiq.get(v,str(v+1))})"
                       for ei in circuito for (u, v, _) in [aristas[ei]]]
            lbl = QLabel(f"CF{k+1} = {{ {',  '.join(nombres)} }}")
            lbl.setStyleSheet("color: #003366; padding: 3px 6px;")
            lbl.setWordWrap(True)
            frame_lista.layout().addWidget(lbl)
        self.matrices_layout.addWidget(frame_lista)
        # Matriz de circuitos fundamentales
        frame_mat = self._frame_titulo(f"Matriz de Circuitos Fundamentales  ({nc} circuitos × {m} aristas)")
        grid = QGridLayout()
        grid.setSpacing(2)
        for j in range(m):
            u, v, _ = aristas[j]
            lbl = QLabel(f"e{j+1}\n({etiq.get(u,str(u+1))}-{etiq.get(v,str(v+1))})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setWordWrap(True)
            grid.addWidget(lbl, 0, j+1)
        for i, circuito in enumerate(self._fund_circuits):
            lbl = QLabel(f"CF{i+1}")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            circuito_set = set(circuito)
            for j in range(m):
                val = 1 if j in circuito_set else 0
                c = QLabel(str(val))
                c.setAlignment(Qt.AlignCenter)
                c.setMinimumSize(44, 36)
                c.setStyleSheet(self._cell_highlight() if val else self._cell_normal())
                grid.addWidget(c, i+1, j+1)
        inner = QWidget()
        inner.setLayout(grid)
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
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec()
            return
        tree_edges, _ = _spanning_tree_dfs(n, aristas)
        if len(tree_edges) != n - 1:
            DialogoClave(0, "Info", "mensaje", self, "El grafo no es conexo, no se puede obtener un árbol de expansión completo.").exec()
            return
        self._fund_cuts = _fundamental_cuts(n, aristas, tree_edges)
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
        # Lista de cortes fundamentales
        frame_lista = self._frame_titulo(f"Cortes fundamentales ({nc})")
        for k, corte in enumerate(self._fund_cuts):
            nombres = [f"e{ei+1}({etiq.get(u,str(u+1))}-{etiq.get(v,str(v+1))})"
                       for ei in corte for (u, v, _) in [aristas[ei]]]
            lbl = QLabel(f"KF{k+1} = {{ {',  '.join(nombres)} }}")
            lbl.setStyleSheet("color: #003366; padding: 3px 6px;")
            lbl.setWordWrap(True)
            frame_lista.layout().addWidget(lbl)
        self.matrices_layout.addWidget(frame_lista)
        # Matriz de cortes fundamentales
        frame_mat = self._frame_titulo(f"Matriz de Cortes Fundamentales  ({nc} cortes × {m} aristas)")
        grid = QGridLayout()
        grid.setSpacing(2)
        for j in range(m):
            u, v, _ = aristas[j]
            lbl = QLabel(f"e{j+1}\n({etiq.get(u,str(u+1))}-{etiq.get(v,str(v+1))})")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setWordWrap(True)
            grid.addWidget(lbl, 0, j+1)
        for i, corte in enumerate(self._fund_cuts):
            lbl = QLabel(f"KF{i+1}")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            corte_set = set(corte)
            for j in range(m):
                val = 1 if j in corte_set else 0
                c = QLabel(str(val))
                c.setAlignment(Qt.AlignCenter)
                c.setMinimumSize(44, 36)
                c.setStyleSheet(self._cell_highlight() if val else self._cell_normal())
                grid.addWidget(c, i+1, j+1)
        inner = QWidget()
        inner.setLayout(grid)
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
    #  Conjuntos independientes
    # ──────────────────────────────────────────────────────────────────
    def _calcular_independientes(self):
        n = self.controller._vertices
        aristas = self.controller._aristas
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec()
            return
        self._independientes = _todos_independientes_maximales(n, aristas)
        if not self._independientes:
            DialogoClave(0, "Info", "mensaje", self, "No se encontraron conjuntos independientes.").exec()
            return
        self._independiente_actual = 0
        self._mostrar_independientes()

    def _mostrar_independientes(self):
        etiq = self.controller._etiquetas
        aristas = self.controller._aristas
        m = self.controller._vertices
        nc = len(self._independientes)
        self._limpiar_matrices()
        # Lista de conjuntos independientes
        frame_lista = self._frame_titulo(f"Conjuntos independientes maximales ({nc})")
        for k, conjunto in enumerate(self._independientes):
            nom = ", ".join(etiq.get(v, str(v+1)) for v in sorted(conjunto)) or "∅"
            lbl = QLabel(f"I{k+1} = {{ {nom} }}  |D|={len(conjunto)}")
            lbl.setStyleSheet("color: #003366; padding: 3px 6px;")
            lbl.setWordWrap(True)
            frame_lista.layout().addWidget(lbl)
        self.matrices_layout.addWidget(frame_lista)
        # Matriz de independencia
        frame_mat = self._frame_titulo(f"Matriz de Independencia  ({nc} conjuntos × {m} vértices)")
        grid = QGridLayout()
        grid.setSpacing(2)
        for j in range(m):
            lbl = QLabel(etiq.get(j, str(j+1)))
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, 0, j+1)
        for i, conjunto in enumerate(self._independientes):
            lbl = QLabel(f"I{i+1}")
            lbl.setStyleSheet(self._cell_header())
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, i+1, 0)
            for j in range(m):
                val = 1 if j in conjunto else 0
                c = QLabel(str(val))
                c.setAlignment(Qt.AlignCenter)
                c.setMinimumSize(44, 36)
                c.setStyleSheet(self._cell_highlight() if val else self._cell_normal())
                grid.addWidget(c, i+1, j+1)
        inner = QWidget()
        inner.setLayout(grid)
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
        frame.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 8px; margin: 2px;")
        lay = QVBoxLayout(frame)
        lbl = QLabel(titulo)
        lbl.setStyleSheet("font-weight: bold; color: #003366; font-size: 13px; padding: 4px;")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)
        return frame

    def _reset_botones(self):
        self.btn_otro_circuito.setVisible(False)
        self.btn_otro_corte.setVisible(False)
        self.btn_otro_fund_circ.setVisible(False)
        self.btn_otro_fund_cut.setVisible(False)
        self.btn_otro_indep.setVisible(False)
        self.lbl_resultado.setVisible(False)

    def _cerrar_grafos(self):
        self.close()
        self.volver_a_grafos()

    def _cerrar_principal(self):
        self.close()
        self.volver_a_principal()

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
        l = QLabel(text)
        l.setStyleSheet("font-weight: bold; color: #003366;")
        return l

    @staticmethod
    def _sep() -> QFrame:
        s = QFrame()
        s.setFrameShape(QFrame.HLine)
        s.setStyleSheet("color: #99ccff;")
        return s

    @staticmethod
    def _input_style() -> str:
        return "background-color:white;border:2px solid #99ccff;border-radius:4px;"

    @staticmethod
    def _cell_header() -> str:
        return ("background-color:#4d9de0;color:white;font-weight:bold;"
                "padding:6px;border-radius:3px;min-width:42px;min-height:32px;")

    @staticmethod
    def _cell_normal() -> str:
        return ("background-color:white;color:#003366;"
                "border:1px solid #99ccff;border-radius:3px;padding:4px;")

    @staticmethod
    def _cell_highlight() -> str:
        return ("background-color:#cce6ff;color:#003366;font-weight:bold;"
                "border:1px solid #4d9de0;border-radius:3px;padding:4px;")

    @staticmethod
    def _cell_diag() -> str:
        return ("background-color:#e8f4fd;color:#666;"
                "border:1px solid #99ccff;border-radius:3px;padding:4px;")

    @staticmethod
    def _cell_neg() -> str:
        return ("background-color:#fde8e8;color:#c0392b;font-weight:bold;"
                "border:1px solid #e74c3c;border-radius:3px;padding:4px;")