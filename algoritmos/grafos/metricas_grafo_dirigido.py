"""
algoritmos/grafos/metricas_grafo_dirigido.py
Métricas para Grafos DIRIGIDOS:
  • Matriz de adyacencia (vértices × vértices)
  • Matriz de incidencia (vértices × aristas)  con -1 / +1
  • Matriz de circuitos  (ciclos dirigidos × aristas)
"""
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
    """
    Encuentra todos los ciclos simples en un digrafo usando DFS.
    Devuelve cada ciclo como lista de índices de arista.
    Limitado a grafos pequeños (≤ 12 vértices).
    """
    if n == 0:
        return []

    # lista de adyacencia dirigida: (destino, idx_arista)
    adj: list[list[tuple]] = [[] for _ in range(n)]
    for i, (u, v, *_) in enumerate(aristas):
        adj[u].append((v, i))

    encontrados: list[frozenset] = []
    ciclos: list[list[int]] = []

    def dfs(inicio: int, actual: int, en_pila: list[bool],
            camino_e: list[int]):
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

def _conjuntos_corte_dirigidos(n: int, aristas: list) -> list[list[int]]:
    """
    Conjuntos de corte fundamentales para dígrafos.
    Para cada arco del árbol DFS, el corte contiene todos los arcos del dígrafo
    que van de la componente del origen a la componente del destino.
    """
    if n == 0 or not aristas:
        return []

    from collections import deque

    adj = [[] for _ in range(n)]
    for i, (u, v, _) in enumerate(aristas):
        adj[u].append((v, i))        # solo dirección u→v

    visitado = [False] * n
    arbol: list[int] = []

    def dfs(v: int):
        visitado[v] = True
        for w, ei in adj[v]:
            if not visitado[w]:
                arbol.append(ei)
                dfs(w)

    dfs(0)

    conjuntos: list[list[int]] = []
    visto: list[frozenset] = []

    for ei in arbol:
        u, v, _ = aristas[ei]

        adj_t = [[] for _ in range(n)]
        for ea in arbol:
            if ea == ei:
                continue
            a, b, _ = aristas[ea]
            adj_t[a].append(b)        # árbol sin dirección para BFS de componentes

        comp_u: set[int] = set()
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

        # Solo arcos que van de comp_u → comp_v  (dirección del corte)
        corte = [
            j for j, (a, b, _) in enumerate(aristas)
            if a in comp_u and b in comp_v
        ]

        clave = frozenset(corte)
        if corte and clave not in visto:
            visto.append(clave)
            conjuntos.append(corte)

    return conjuntos

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
        self._ciclos: list[list[int]] = []
        self._ciclo_actual: int = 0
        self._cortes: list[list[int]] = []
        self._corte_actual: int = 0

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
        self.visual = VisualizadorGrafoColoreable("Grafo", es_editable=True, dirigido=True)
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
        lay.addWidget(self._lbl("Operación matricial:"))
        self.combo_op = QComboBox()
        self.combo_op.addItem("Matriz de adyacencia y de incidencia", "adyacencia_incidencia")
        self.combo_op.addItem("Matriz de circuitos", "circuitos")
        self.combo_op.addItem("Conjuntos de corte", "cortes")
        self.combo_op.setStyleSheet(self._input_style())
        lay.addWidget(self.combo_op)
        br = QPushButton("▶ Calcular")
        br.setStyleSheet(self._btn("#2c3e50", "white"))
        br.clicked.connect(self._calcular)
        lay.addWidget(br)

        self.btn_otro = QPushButton("🔄 Ver otro circuito")
        self.btn_otro.setStyleSheet(self._btn("#8e44ad", "white"))
        self.btn_otro.clicked.connect(self._ver_otro_circuito)
        self.btn_otro.setVisible(False)
        lay.addWidget(self.btn_otro)
        
        self.btn_otro_corte = QPushButton("🔄 Ver otro corte")
        self.btn_otro_corte.setStyleSheet(self._btn("#e67e22", "white"))
        self.btn_otro_corte.clicked.connect(self._ver_otro_corte)
        self.btn_otro_corte.setVisible(False)
        lay.addWidget(self.btn_otro_corte)

        lay.addWidget(self._sep())
        self.lbl_resultado = QLabel()
        self.lbl_resultado.setStyleSheet(
            "font-weight:bold;color:#7d3c00;font-size:13px;"
        )
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
        self.btn_otro.setVisible(False)
        self.lbl_resultado.setVisible(False)

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
        # Para dígrafo mostramos dirección con →
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
                self.btn_otro.setVisible(False)
                self.lbl_resultado.setVisible(False)
                DialogoClave(0, "Éxito", "mensaje", self, "Dígrafo cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {e}").exec()

    def _calcular(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un dígrafo.").exec()
            return
        op = self.combo_op.currentData()
        self._limpiar_matrices()
        self.btn_otro.setVisible(False)
        self.btn_otro_corte.setVisible(False)
        self.lbl_resultado.setVisible(False)

        if op == "adyacencia_incidencia":
            self._mostrar_incidencia()
            self._mostrar_adyacencia()
            self._mostrar_adyacencia_aristas()
        elif op == "circuitos":
            self._calcular_circuitos()
        elif op == "cortes":   
            self._calcular_cortes()

    # ──────────────────────────────────────────────────────────────────
    #  Matrices
    # ──────────────────────────────────────────────────────────────────
    def _mostrar_adyacencia(self):
        """Matriz de adyacencia: """
        n = self.controller._vertices
        etiq = self.controller._etiquetas
        aristas = self.controller._aristas

        mat = [[0] * n for _ in range(n)]
        for (u, v, _) in aristas:
            mat[u][v] += 1           # solo dirección u→v (no v→u)

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
        """
        Matriz de incidencia dirigida:
          M[v][e] = -1  si v es el origen del arco e
          M[v][e] = +1  si v es el destino del arco e
          M[v][e] =  0  en otro caso
        Bucles: +1 en la celda del vértice (convención).
        """
        n = self.controller._vertices
        aristas = self.controller._aristas
        m = len(aristas)
        etiq = self.controller._etiquetas

        if m == 0:
            return

        frame = self._frame_titulo(
            f"Matriz de Incidencia Dirigida  "
            f"(−1=origen, +1=destino)  —  {m} arco(s)"
        )
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
                if u == v:           # bucle
                    val = 1 if i == u else 0
                elif i == u:
                    val = -1         # origen
                elif i == v:
                    val = 1          # destino
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
            f"Matriz de Adyacencia de Aristas"
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
                         "El grafo no tiene arcos, no hay circuitos.").exec()
            return

        self._ciclos = _ciclos_dirigidos(n, aristas)

        if not self._ciclos:
            DialogoClave(0, "Info", "mensaje", self,
                         "El grafo no contiene circuitos dirigidos.").exec()
            return

        self._ciclo_actual = 0

        # Lista de circuitos
        frame_lista = self._frame_titulo(f"Circuitos dirigidos encontrados ({len(self._ciclos)})")
        for k, ciclo in enumerate(self._ciclos):
            nombres = []
            for ei in ciclo:
                u, v, _ = aristas[ei]
                nombres.append(f"e{ei+1}({etiq.get(u,str(u+1))}→{etiq.get(v,str(v+1))})")
            lbl = QLabel(f"C{k+1} = {{ {',  '.join(nombres)} }}")
            lbl.setStyleSheet("color: #7d3c00; padding: 3px 6px;")
            lbl.setWordWrap(True)
            frame_lista.layout().addWidget(lbl)
        self.matrices_layout.addWidget(frame_lista)

        # Matriz de circuitos
        nc = len(self._ciclos)
        frame_mat = self._frame_titulo(
            f"Matriz de Circuitos  ({nc} circuitos × {m} arcos)"
        )
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
        datos = self.controller.obtener_datos()
        ciclo_set = set(self._ciclos[idx])
        color = COLORES_CIRCUITO[idx % len(COLORES_CIRCUITO)]

        self.visual.set_grafo(
            datos["vertices"], datos["aristas"],
            datos["etiquetas"], datos["pesos"]
        )

        if hasattr(self.visual, 'set_colores'):
            self.visual.set_colores(colores_aristas={ei: color for ei in ciclo_set})

        self.lbl_resultado.setText(
            f"Mostrando circuito C{idx + 1} de {len(self._ciclos)}"
        )

    def _ver_otro_circuito(self):
        if not self._ciclos:
            return
        self._ciclo_actual = (self._ciclo_actual + 1) % len(self._ciclos)
        self._colorear_circuito(self._ciclo_actual)

    # ──────────────────────────────────────────────────────────────────
    #  Helpers UI
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
            "background-color: white; border: 2px solid #f0c080;"
            "border-radius: 8px; margin: 2px;"
        )
        lay = QVBoxLayout(frame)
        lbl = QLabel(titulo)
        lbl.setStyleSheet(
            "font-weight:bold;color:#7d3c00;font-size:13px;padding:4px;"
        )
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)
        return frame

    def _calcular_cortes(self):
        n       = self.controller._vertices
        aristas = self.controller._aristas
        etiq    = self.controller._etiquetas
        m       = len(aristas)

        if m == 0:
            DialogoClave(0, "Info", "mensaje", self, "El grafo no tiene aristas.").exec()
            return

        self._cortes = _conjuntos_corte_dirigidos(n, aristas)

        if not self._cortes:
            DialogoClave(0, "Info", "mensaje", self,
                        "No se encontraron conjuntos de corte (¿el grafo es conexo?).").exec()
            return

        self._corte_actual = 0

        # ── Lista de conjuntos de corte ───────────────────────────────────
        frame_lista = self._frame_titulo(f"Conjuntos de corte ({len(self._cortes)})")
        for k, corte in enumerate(self._cortes):
            nombres = []
            for ei in corte:
                u, v, _ = aristas[ei]
                nombres.append(
                    f"e{ei+1}({etiq.get(u, str(u+1))}-{etiq.get(v, str(v+1))})"
                )
            lbl = QLabel(f"K{k+1} = {{ {',  '.join(nombres)} }}")
            lbl.setStyleSheet("color: #7d3c00; padding: 3px 6px;")
            lbl.setWordWrap(True)
            frame_lista.layout().addWidget(lbl)
        self.matrices_layout.addWidget(frame_lista)

        # ── Matriz de cortes  (cortes × aristas) ─────────────────────────
        nc = len(self._cortes)
        frame_mat = self._frame_titulo(
            f"Matriz de Cortes  ({nc} cortes × {m} aristas)"
        )
        from PySide6.QtWidgets import QGridLayout
        grid = QGridLayout(); grid.setSpacing(2)

        for j in range(m):
            u, v, _ = aristas[j]
            lbl = QLabel(
                f"e{j+1}\n({etiq.get(u,str(u+1))}-{etiq.get(v,str(v+1))})"
            )
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
                c   = QLabel(str(val)); c.setAlignment(Qt.AlignCenter)
                c.setMinimumSize(44, 36)
                c.setStyleSheet(
                    self._cell_highlight() if val else self._cell_normal()
                )
                grid.addWidget(c, i+1, j+1)

        inner = QWidget(); inner.setLayout(grid)
        frame_mat.layout().addWidget(inner)
        self.matrices_layout.addWidget(frame_mat)

        # Resultado y botón
        self.lbl_resultado.setText(
            f"Mostrando corte K{self._corte_actual + 1} de {len(self._cortes)}"
        )
        self.lbl_resultado.setVisible(True)
        self.btn_otro_corte.setVisible(True)
        self._colorear_corte(self._corte_actual)


    def _colorear_corte(self, idx: int):
        """
        Colorea las aristas del corte en rojo y las dos componentes
        de vértices en colores distintos.
        """
        from collections import deque
        aristas = self.controller._aristas
        n       = self.controller._vertices
        datos   = self.controller.obtener_datos()

        corte_set = set(self._cortes[idx])

        # BFS ignorando las aristas del corte → dos componentes
        adj = [[] for _ in range(n)]
        for i, (u, v, _) in enumerate(aristas):
            if i not in corte_set and u != v:
                adj[u].append(v); adj[v].append(u)

        comp = [-1] * n
        c_id = 0
        for s in range(n):
            if comp[s] == -1:
                q = deque([s])
                while q:
                    cur = q.popleft()
                    if comp[cur] != -1:
                        continue
                    comp[cur] = c_id
                    for nb in adj[cur]:
                        if comp[nb] == -1:
                            q.append(nb)
                c_id += 1

        PALETA_COMP = ["#4d9de0", "#f39c12", "#27ae60", "#9b59b6", "#e74c3c"]
        colores_v = {v: PALETA_COMP[comp[v] % len(PALETA_COMP)] for v in range(n)}
        colores_a = {ei: "#e74c3c" for ei in corte_set}

        self.visual.set_grafo(
            n, datos["aristas"], datos["etiquetas"], datos["pesos"]
        )
        if hasattr(self.visual, "set_colores"):
            self.visual.set_colores(
                colores_vertices=colores_v,
                colores_aristas=colores_a,
            )

        self.lbl_resultado.setText(
            f"Mostrando corte K{idx + 1} de {len(self._cortes)}"
        )


    def _ver_otro_corte(self):
        if not self._cortes:
            return
        self._corte_actual = (self._corte_actual + 1) % len(self._cortes)
        self._colorear_corte(self._corte_actual)

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
        l = QLabel(text); l.setStyleSheet("font-weight:bold;color:#7d3c00;")
        return l

    @staticmethod
    def _sep() -> QFrame:
        s = QFrame(); s.setFrameShape(QFrame.HLine)
        s.setStyleSheet("color: #f0c080;"); return s

    @staticmethod
    def _input_style() -> str:
        return "background-color:white;border:2px solid #f0c080;border-radius:4px;"

    @staticmethod
    def _cell_header() -> str:
        return (
            "background-color:#e67e22;color:white;font-weight:bold;"
            "padding:6px;border-radius:3px;min-width:42px;min-height:32px;"
        )

    @staticmethod
    def _cell_normal() -> str:
        return (
            "background-color:white;color:#003366;"
            "border:1px solid #f0c080;border-radius:3px;padding:4px;"
        )

    @staticmethod
    def _cell_highlight() -> str:
        return (
            "background-color:#fdebd0;color:#7d3c00;font-weight:bold;"
            "border:1px solid #e67e22;border-radius:3px;padding:4px;"
        )

    @staticmethod
    def _cell_neg() -> str:
        return (
            "background-color:#fde8e8;color:#c0392b;font-weight:bold;"
            "border:1px solid #e74c3c;border-radius:3px;padding:4px;"
        )

    @staticmethod
    def _cell_diag() -> str:
        return (
            "background-color:#fef9f0;color:#aaa;"
            "border:1px solid #f0c080;border-radius:3px;padding:4px;"
        )