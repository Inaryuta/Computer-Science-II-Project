"""
algoritmos/grafos/conjuntos_dominantes.py
Conjuntos Dominantes para Grafos No Dirigidos:
  • Dominante mínimo      (γ  – menor cardinalidad)
  • Dominante máximo      (Γ  – mayor cardinalidad minimal)
  • Dominante independiente
  • Dominante conexo
  • Dominante maximal     (minimal = no se puede quitar ningún vértice)
  • Número de independencia (α – mayor conjunto independiente)
"""
from collections import deque
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QFrame, QFileDialog, QComboBox,
    QScrollArea, QTextEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from controladores.grafo_controller import GrafoController
from controladores.visualizador_grafo import VisualizadorGrafoColoreable
from algoritmos.funcion_mod import DialogoClave


# ══════════════════════════════════════════════════════════════════════
#  Helpers de propiedades
# ══════════════════════════════════════════════════════════════════════

def _build_adj(n: int, aristas: list) -> list[set]:
    adj = [set() for _ in range(n)]
    for u, v, _ in aristas:
        if u != v:
            adj[u].add(v)
            adj[v].add(u)
    return adj


def _es_dominante(D: set, n: int, adj: list[set]) -> bool:
    """Todo vértice fuera de D tiene al menos un vecino en D."""
    for v in range(n):
        if v not in D and not adj[v] & D:
            return False
    return True


def _es_independiente(D: set, adj: list[set]) -> bool:
    """Ningún par de vértices en D es adyacente."""
    return all(adj[v].isdisjoint(D - {v}) for v in D)


def _es_conexo_inducido(D: set, adj: list[set]) -> bool:
    """El subgrafo inducido por D es conexo."""
    if len(D) <= 1:
        return True
    inicio = next(iter(D))
    visitado = {inicio}
    q = deque([inicio])
    while q:
        cur = q.popleft()
        for nb in adj[cur]:
            if nb in D and nb not in visitado:
                visitado.add(nb); q.append(nb)
    return visitado == D


def _es_minimal(D: set, n: int, adj: list[set]) -> bool:
    """Ningún subconjunto propio de D es también dominante."""
    return all(not _es_dominante(D - {v}, n, adj) for v in D)


# ══════════════════════════════════════════════════════════════════════
#  Algoritmos de búsqueda (backtracking)
# ══════════════════════════════════════════════════════════════════════

def _todos_los_dominantes(n: int, adj: list[set]) -> list[frozenset]:
    """Todos los conjuntos dominantes por backtracking (grafos ≤ 15 v)."""
    resultados: list[frozenset] = []

    def bt(idx: int, D: set):
        if _es_dominante(D, n, adj):
            resultados.append(frozenset(D))
            return
        if idx == n:
            return
        # Con v
        D.add(idx); bt(idx + 1, D); D.remove(idx)
        # Sin v (solo si aún es posible cubrir con los restantes)
        bt(idx + 1, D)

    bt(0, set())
    # Eliminar duplicados y superconjuntos si se quiere, pero devolvemos todos
    unicos: list[frozenset] = []
    vistos: set[frozenset] = set()
    for d in resultados:
        if d not in vistos:
            vistos.add(d); unicos.append(d)
    return unicos


def _dominantes_minimales(n: int, adj: list[set]) -> list[frozenset]:
    """Solo los dominantes donde no existe subconjunto propio dominante."""
    todos = _todos_los_dominantes(n, adj)
    return [d for d in todos if _es_minimal(d, n, adj)]


def _dominante_minimo(n: int, adj: list[set]) -> list[frozenset]:
    """Todos los dominantes de cardinalidad mínima (γ)."""
    minimales = _dominantes_minimales(n, adj)
    if not minimales:
        return []
    gamma = min(len(d) for d in minimales)
    return [d for d in minimales if len(d) == gamma]


def _dominante_maximo(n: int, adj: list[set]) -> list[frozenset]:
    """Todos los dominantes minimales de cardinalidad máxima (Γ)."""
    minimales = _dominantes_minimales(n, adj)
    if not minimales:
        return []
    gamma_upper = max(len(d) for d in minimales)
    return [d for d in minimales if len(d) == gamma_upper]


def _dominante_independiente(n: int, adj: list[set]) -> list[frozenset]:
    """Dominantes que además son independientes (mínimos primero)."""
    minimales = _dominantes_minimales(n, adj)
    result = [d for d in minimales if _es_independiente(d, adj)]
    if not result:
        return []
    gamma = min(len(d) for d in result)
    return [d for d in result if len(d) == gamma]


def _dominante_conexo(n: int, adj: list[set]) -> list[frozenset]:
    """Dominantes cuyo subgrafo inducido es conexo (mínimos primero)."""
    minimales = _dominantes_minimales(n, adj)
    result = [d for d in minimales if _es_conexo_inducido(d, adj)]
    if not result:
        return []
    gamma = min(len(d) for d in result)
    return [d for d in result if len(d) == gamma]


def _numero_independencia(n: int, adj: list[set]) -> list[frozenset]:
    """
    Todos los conjuntos independientes máximos (α = número de independencia).
    Un independiente máximo es aquel de mayor cardinalidad.
    """
    mejor: list[frozenset] = []
    alpha = 0

    def bt(idx: int, I: set):
        nonlocal alpha, mejor
        if idx == n:
            if len(I) > alpha:
                alpha = len(I); mejor = [frozenset(I)]
            elif len(I) == alpha:
                mejor.append(frozenset(I))
            return
        # Incluir idx si no tiene vecinos en I
        if not adj[idx] & I:
            I.add(idx); bt(idx + 1, I); I.remove(idx)
        # No incluir
        bt(idx + 1, I)

    bt(0, set())
    return mejor


# ══════════════════════════════════════════════════════════════════════
#  Colores de visualización
# ══════════════════════════════════════════════════════════════════════
COLORES_TIPO = {
    "minimo":        "#e74c3c",   # rojo
    "maximo":        "#8e44ad",   # morado
    "independiente": "#27ae60",   # verde
    "conexo":        "#053758",   # azul
    "maximal":       "#f39c12",   # naranja
    "independencia": "#16a085",   # teal
}
COLOR_FUERA  = "#4d9de0"          # azul claro para vértices fuera del conjunto
COLOR_BORDE_D = "#bdc3c7"         # aristas normales


# ══════════════════════════════════════════════════════════════════════
#  Ventana principal
# ══════════════════════════════════════════════════════════════════════
class ConjuntosDominantesWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos    = volver_a_grafos
        self.volver_a_principal = volver_a_principal

        self.controller = GrafoController()

        # Estado por tipo de operación
        self._tipo_actual: str = ""
        self._conjuntos: list[frozenset] = []
        self._idx_actual: int = 0

        self.setWindowTitle("Conjuntos Dominantes")
        self.setGeometry(80, 50, 1500, 860)
        self.setStyleSheet("background-color: #f0f8ff;")

        self._build_ui()
        self.controller.grafo_cambiado.connect(self._actualizar_visual)

    # ──────────────────────────────────────────────────────────────────
    #  Construcción UI
    # ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10); root.setContentsMargins(10, 10, 10, 10)
        root.addWidget(self._make_header())

        body = QHBoxLayout(); body.setSpacing(12)

        # ── Visualizador principal ────────────────────────────────────
        self.visual = VisualizadorGrafoColoreable("Grafo", es_editable=True)
        self.visual.setFixedSize(520, 540)
        body.addWidget(self.visual, stretch=2)

        # ── Panel derecho (scroll) ────────────────────────────────────
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")
        rw = QWidget(); rw.setStyleSheet("background-color:#e6f2ff;border-radius:8px;")
        self.rl = QVBoxLayout(rw); self.rl.setSpacing(8)
        self.rl.setAlignment(Qt.AlignTop)
        scroll.setWidget(rw)
        body.addWidget(scroll, stretch=1)

        root.addLayout(body)
        self._build_panel()

    def _make_header(self) -> QFrame:
        h = QFrame(); h.setStyleSheet("background-color:#cce6ff;border-radius:10px;")
        hl = QHBoxLayout(h)
        b1 = QPushButton("← Volver a Grafos")
        b1.setStyleSheet(self._btn("#e6f2ff", "#003366"))
        b1.clicked.connect(self._cerrar_grafos)
        b2 = QPushButton("🏠 Inicio")
        b2.setStyleSheet(self._btn("#e6f2ff", "#003366"))
        b2.clicked.connect(self._cerrar_principal)
        t = QLabel("CONJUNTOS DOMINANTES")
        t.setFont(QFont("Arial", 18, QFont.Bold))
        t.setStyleSheet("color:#003366;")
        hl.addWidget(b1); hl.addWidget(b2)
        hl.addWidget(t, alignment=Qt.AlignCenter)
        return h

    def _build_panel(self):
        lay = self.rl

        # ── Crear grafo ───────────────────────────────────────────────
        lay.addWidget(self._lbl("Número de vértices:"))
        self.spin_v = QSpinBox(); self.spin_v.setRange(1, 12); self.spin_v.setValue(5)
        self.spin_v.setStyleSheet(self._input_style())
        lay.addWidget(self.spin_v)
        bc = QPushButton("Crear grafo"); bc.setStyleSheet(self._btn("#4d9de0", "white"))
        bc.clicked.connect(self._crear_grafo); lay.addWidget(bc)

        # ── Aristas ───────────────────────────────────────────────────
        lay.addWidget(self._sep())
        lay.addWidget(self._lbl("Agregar arista:"))
        row = QHBoxLayout()
        self.combo_u = QComboBox(); self.combo_u.setStyleSheet(self._input_style())
        self.combo_v = QComboBox(); self.combo_v.setStyleSheet(self._input_style())
        row.addWidget(QLabel("De:")); row.addWidget(self.combo_u)
        row.addWidget(QLabel("A:"));  row.addWidget(self.combo_v)
        lay.addLayout(row)
        ba = QPushButton("+ Arista"); ba.setStyleSheet(self._btn("#27ae60", "white"))
        ba.clicked.connect(self._agregar_arista); lay.addWidget(ba)
        be = QPushButton("- Eliminar arista"); be.setStyleSheet(self._btn("#e74c3c", "white"))
        be.clicked.connect(self._eliminar_arista); lay.addWidget(be)

        # ── Guardar / Cargar ──────────────────────────────────────────
        lay.addWidget(self._sep())
        r2 = QHBoxLayout()
        bs = QPushButton("💾 Guardar"); bs.setStyleSheet(self._btn("#3498db", "white"))
        bl = QPushButton("📂 Cargar");  bl.setStyleSheet(self._btn("#3498db", "white"))
        bs.clicked.connect(self._guardar); bl.clicked.connect(self._cargar)
        r2.addWidget(bs); r2.addWidget(bl); lay.addLayout(r2)

        # ── Operaciones ───────────────────────────────────────────────
        lay.addWidget(self._sep())
        lay.addWidget(self._lbl("Tipo de conjunto dominante:"))

        operaciones = [
            ("🔴  Dominante Mínimo  (γ)",       "minimo"),
            ("🟣  Dominante Máximo  (Γ)",        "maximo"),
            ("🟢  Dominante Independiente",       "independiente"),
            ("🔵  Dominante Conexo",              "conexo"),
            ("🟠  Dominante Maximal",             "maximal"),
            ("🩵  Número de Independencia  (α)",  "independencia"),
        ]
        for label, tipo in operaciones:
            btn = QPushButton(label)
            color = COLORES_TIPO[tipo]
            btn.setStyleSheet(self._btn(color, "white"))
            btn.clicked.connect(lambda _, t=tipo: self._calcular(t))
            lay.addWidget(btn)

        # ── Botón "ver otro" ──────────────────────────────────────────
        lay.addWidget(self._sep())
        self.btn_otro = QPushButton("🔄 Ver otro conjunto")
        self.btn_otro.setStyleSheet(self._btn("#7f8c8d", "white"))
        self.btn_otro.clicked.connect(self._ver_otro)
        self.btn_otro.setVisible(False)
        lay.addWidget(self.btn_otro)

        self.lbl_idx = QLabel()
        self.lbl_idx.setAlignment(Qt.AlignCenter)
        self.lbl_idx.setStyleSheet(
            "font-weight:bold;color:#003366;font-size:13px;"
            "background-color:white;border:2px solid #99ccff;"
            "border-radius:6px;padding:6px;"
        )
        self.lbl_idx.setVisible(False)
        lay.addWidget(self.lbl_idx)

        # ── Leyenda de tipos ──────────────────────────────────────────
        lay.addWidget(self._sep())
        lay.addWidget(self._lbl("Leyenda de colores:"))
        for label, tipo in operaciones:
            color = COLORES_TIPO[tipo]
            fila = QHBoxLayout()
            dot = QLabel("●"); dot.setStyleSheet(f"color:{color};font-size:20px;")
            lbl = QLabel(label.split("  ")[1].strip()); lbl.setStyleSheet("color:#003366;font-size:11px;")
            fila.addWidget(dot); fila.addWidget(lbl); fila.addStretch()
            lay.addLayout(fila)

        # ── Panel de información ──────────────────────────────────────
        lay.addWidget(self._sep())
        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color:white;border:2px solid #99ccff;border-radius:8px;"
        )
        ilay = QVBoxLayout(info_frame)
        lbl_t = QLabel("Información del conjunto")
        lbl_t.setStyleSheet("font-weight:bold;color:#003366;font-size:13px;padding:4px;")
        lbl_t.setAlignment(Qt.AlignCenter)
        ilay.addWidget(lbl_t)
        self.texto_info = QTextEdit()
        self.texto_info.setReadOnly(True)
        self.texto_info.setMinimumHeight(220)
        self.texto_info.setStyleSheet(
            "font-family:monospace;font-size:12px;border:none;padding:4px;"
        )
        ilay.addWidget(self.texto_info)
        lay.addWidget(info_frame)

    # ──────────────────────────────────────────────────────────────────
    #  Acciones del usuario
    # ──────────────────────────────────────────────────────────────────
    def _crear_grafo(self):
        self.controller.set_vertices(self.spin_v.value())
        self._actualizar_combos()
        self._reset_estado()

    def _agregar_arista(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea el grafo.").exec(); return
        u = self.combo_u.currentData()
        v = self.combo_v.currentData()
        if u is None or v is None or u == v:
            DialogoClave(0, "Error", "mensaje", self, "Selecciona dos vértices distintos.").exec(); return
        self.controller.agregar_arista(u, v, 1)

    def _eliminar_arista(self):
        datos = self.controller.obtener_datos()
        aristas, etiq = datos["aristas"], datos["etiquetas"]
        if not aristas:
            DialogoClave(0, "Info", "mensaje", self, "No hay aristas.").exec(); return
        from PySide6.QtWidgets import QInputDialog
        opts = [f"{etiq.get(u,u+1)} — {etiq.get(v,v+1)}" for (u,v) in aristas]
        sel, ok = QInputDialog.getItem(self, "Eliminar arista", "Arista:", opts, 0, False)
        if ok:
            idx = opts.index(sel); u, v = aristas[idx]
            self.controller.eliminar_arista(u, v, indice=idx)

    def _guardar(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay grafo.").exec(); return
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar", "", "JSON (*.json)")
        if ruta:
            self.controller.guardar_json(ruta)
            DialogoClave(0, "Éxito", "mensaje", self, "Guardado.").exec()

    def _cargar(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar", "", "JSON (*.json)")
        if ruta:
            try:
                self.controller.cargar_json(ruta)
                self.spin_v.setValue(self.controller._vertices)
                self._actualizar_combos()
                self._reset_estado()
                DialogoClave(0, "Éxito", "mensaje", self, "Cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {e}").exec()

    # ──────────────────────────────────────────────────────────────────
    #  Cálculo
    # ──────────────────────────────────────────────────────────────────
    def _calcular(self, tipo: str):
        n   = self.controller._vertices
        raw = self.controller._aristas
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec(); return

        adj = _build_adj(n, raw)
        self._reset_estado()
        self._tipo_actual = tipo

        if tipo == "minimo":
            self._conjuntos = _dominante_minimo(n, adj)
        elif tipo == "maximo":
            self._conjuntos = _dominante_maximo(n, adj)
        elif tipo == "independiente":
            self._conjuntos = _dominante_independiente(n, adj)
        elif tipo == "conexo":
            self._conjuntos = _dominante_conexo(n, adj)
        elif tipo == "maximal":
            self._conjuntos = _dominantes_minimales(n, adj)   # maximal = minimal
        elif tipo == "independencia":
            self._conjuntos = _numero_independencia(n, adj)

        if not self._conjuntos:
            DialogoClave(0, "Info", "mensaje", self,
                         "No se encontró ningún conjunto de este tipo.").exec()
            return

        self._idx_actual = 0
        self._mostrar(self._idx_actual)
        self.btn_otro.setVisible(len(self._conjuntos) > 1)
        self.lbl_idx.setVisible(True)

    def _ver_otro(self):
        if not self._conjuntos: return
        self._idx_actual = (self._idx_actual + 1) % len(self._conjuntos)
        self._mostrar(self._idx_actual)

    # ──────────────────────────────────────────────────────────────────
    #  Visualización y texto
    # ──────────────────────────────────────────────────────────────────
    def _mostrar(self, idx: int):
        D     = self._conjuntos[idx]
        n     = self.controller._vertices
        adj   = _build_adj(n, self.controller._aristas)
        etiq  = self.controller._etiquetas
        datos = self.controller.obtener_datos()
        color = COLORES_TIPO[self._tipo_actual]

        # Colores de vértices: D en el color del tipo, resto azul claro
        colores_v = {
            v: color if v in D else COLOR_FUERA
            for v in range(n)
        }

        # Colores de aristas: resaltar las que conectan vértices de D entre sí
        colores_a = {}
        for i, (u, v, _) in enumerate(self.controller._aristas):
            if u in D and v in D:
                colores_a[i] = color

        self.visual.set_grafo(
            n, datos["aristas"], etiq, datos["pesos"],
            colores_vertices=colores_v,
            colores_aristas=colores_a,
        )

        # ── Propiedades del conjunto mostrado ─────────────────────────
        es_dom   = _es_dominante(D, n, adj)
        es_ind   = _es_independiente(D, adj)
        es_con   = _es_conexo_inducido(D, adj)
        es_min   = _es_minimal(D, n, adj)

        D_sorted = sorted(D)
        D_str    = "{ " + ",  ".join(etiq.get(v, str(v+1)) for v in D_sorted) + " }"

        # Vértices dominados (fuera de D con vecino en D)
        dominados = {
            v for v in range(n)
            if v not in D and adj[v] & D
        }
        no_dom = set(range(n)) - D - dominados
        dom_str = (
            "{ " + ",  ".join(etiq.get(v, str(v+1)) for v in sorted(dominados)) + " }"
            if dominados else "∅"
        )
        no_dom_str = (
            "{ " + ",  ".join(etiq.get(v, str(v+1)) for v in sorted(no_dom)) + " }"
            if no_dom else "∅"
        )

        NOMBRES = {
            "minimo":        f"Dominante Mínimo  (γ = {len(D)})",
            "maximo":        f"Dominante Máximo  (Γ = {len(D)})",
            "independiente": f"Dominante Independiente  (|D| = {len(D)})",
            "conexo":        f"Dominante Conexo  (|D| = {len(D)})",
            "maximal":       f"Dominante Maximal  (|D| = {len(D)})",
            "independencia": f"Conjunto Independiente Máximo  (α = {len(D)})",
        }

        total = len(self._conjuntos)
        self.lbl_idx.setText(
            f"{NOMBRES[self._tipo_actual]}  —  {idx+1} / {total}"
        )

        self.texto_info.setHtml(
            f"<b>{NOMBRES[self._tipo_actual]}</b><br><br>"
            f"<b>D  =</b>  {D_str}<br>"
            f"<b>|D|  =</b>  {len(D)}<br><br>"
            f"<b>Vértices dominados:</b>  {dom_str}<br>"
            f"<b>Vértices no dominados:</b>  {no_dom_str}<br><br>"
            f"<b>¿Es dominante?</b>  {'✔ Sí' if es_dom else '✘ No'}<br>"
            f"<b>¿Es independiente?</b>  {'✔ Sí' if es_ind else '✘ No'}<br>"
            f"<b>¿Es conexo?</b>  {'✔ Sí' if es_con else '✘ No'}<br>"
            f"<b>¿Es maximal?</b>  {'✔ Sí' if es_min else '✘ No'}<br><br>"
            f"<i>Conjuntos encontrados de este tipo: {total}</i>"
        )

    # ──────────────────────────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────────────────────────
    def _actualizar_visual(self):
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(
            datos["vertices"], datos["aristas"],
            datos["etiquetas"], datos["pesos"],
        )

    def _actualizar_combos(self):
        n, etiq = self.controller._vertices, self.controller._etiquetas
        for combo in (self.combo_u, self.combo_v):
            combo.clear()
            for i in range(n):
                combo.addItem(etiq.get(i, str(i+1)), i)

    def _reset_estado(self):
        self._conjuntos   = []
        self._idx_actual  = 0
        self._tipo_actual = ""
        self.btn_otro.setVisible(False)
        self.lbl_idx.setVisible(False)
        self.texto_info.clear()

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
        l = QLabel(text); l.setStyleSheet("font-weight:bold;color:#003366;"); return l

    @staticmethod
    def _sep() -> QFrame:
        s = QFrame(); s.setFrameShape(QFrame.HLine)
        s.setStyleSheet("color:#99ccff;"); return s

    @staticmethod
    def _input_style() -> str:
        return "background-color:white;border:2px solid #99ccff;border-radius:4px;"