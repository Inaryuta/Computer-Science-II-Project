"""
algoritmos/grafos/funcion_ordinal.py
Función Ordinal de Grafos Dirigidos:
  • Ordenamiento topológico (Kahn)
  • Predecesores / sucesores de cada vértice
  • Grado de entrada / salida
  • Niveles BFS (capas desde un origen)
  • Clausura transitiva (alcanzabilidad)
  • Detección de DAG
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
#  Algoritmos
# ══════════════════════════════════════════════════════════════════════

def _build_adj_dirigido(n: int, aristas: list) -> tuple[list[list], list[list]]:
    """Devuelve (sucesores, predecesores) como listas de adyacencia."""
    suc  = [[] for _ in range(n)]
    pred = [[] for _ in range(n)]
    for u, v, _ in aristas:
        if u != v:
            suc[u].append(v)
            pred[v].append(u)
    return suc, pred


def _kahn(n: int, suc: list, pred: list) -> tuple[list[int], bool]:
    """
    Ordenamiento topológico de Kahn.
    Devuelve (orden, es_dag).
    Si hay ciclo, es_dag=False y orden contiene solo los vértices procesados.
    """
    in_deg = [len(pred[v]) for v in range(n)]
    cola   = deque(v for v in range(n) if in_deg[v] == 0)
    orden  = []
    while cola:
        u = cola.popleft()
        orden.append(u)
        for v in suc[u]:
            in_deg[v] -= 1
            if in_deg[v] == 0:
                cola.append(v)
    return orden, len(orden) == n


def _niveles_bfs(n: int, suc: list, origen: int) -> dict[int, int]:
    """
    BFS desde origen.
    Devuelve {vertice: nivel} para todos los vértices alcanzables.
    """
    nivel  = {origen: 0}
    cola   = deque([origen])
    while cola:
        u = cola.popleft()
        for v in suc[u]:
            if v not in nivel:
                nivel[v] = nivel[u] + 1
                cola.append(v)
    return nivel


def _clausura_transitiva(n: int, suc: list) -> list[set]:
    """
    Clausura transitiva por BFS desde cada vértice.
    ct[u] = conjunto de vértices alcanzables desde u.
    """
    ct = []
    for s in range(n):
        alcanzables: set[int] = set()
        cola = deque([s])
        while cola:
            u = cola.popleft()
            for v in suc[u]:
                if v not in alcanzables:
                    alcanzables.add(v)
                    cola.append(v)
        ct.append(alcanzables)
    return ct


# ══════════════════════════════════════════════════════════════════════
#  Paletas de colores
# ══════════════════════════════════════════════════════════════════════
PALETA_NIVELES = [
    "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71",
    "#1abc9c", "#3498db", "#9b59b6", "#34495e",
]


# ══════════════════════════════════════════════════════════════════════
#  Ventana principal
# ══════════════════════════════════════════════════════════════════════
class FuncionOrdinalWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos    = volver_a_grafos
        self.volver_a_principal = volver_a_principal

        self.controller = GrafoController()
        self.setWindowTitle("Función Ordinal de Grafos")
        self.setGeometry(80, 50, 1500, 860)
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
        root.setSpacing(10); root.setContentsMargins(10, 10, 10, 10)
        root.addWidget(self._make_header())

        body = QHBoxLayout(); body.setSpacing(12)

        # Visualizador
        self.visual = VisualizadorGrafoColoreable(
            "Dígrafo", es_editable=True, dirigido=True
        )
        self.visual.setFixedSize(520, 540)
        body.addWidget(self.visual, stretch=2)

        # Panel derecho
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
        t = QLabel("FUNCIÓN ORDINAL DE GRAFOS DIRIGIDOS")
        t.setFont(QFont("Arial", 16, QFont.Bold))
        t.setStyleSheet("color:#003366;")
        hl.addWidget(b1); hl.addWidget(b2)
        hl.addWidget(t, alignment=Qt.AlignCenter)
        return h

    def _build_panel(self):
        lay = self.rl

        # Crear grafo
        lay.addWidget(self._lbl("Número de vértices:"))
        self.spin_v = QSpinBox(); self.spin_v.setRange(1, 12); self.spin_v.setValue(5)
        self.spin_v.setStyleSheet(self._input_style()); lay.addWidget(self.spin_v)
        bc = QPushButton("Crear Grafo"); bc.setStyleSheet(self._btn("#4d9de0", "white"))
        bc.clicked.connect(self._crear_grafo); lay.addWidget(bc)

        # Aristas
        lay.addWidget(self._sep())
        lay.addWidget(self._lbl("Agregar Arista:"))
        row = QHBoxLayout()
        self.combo_u = QComboBox(); self.combo_u.setStyleSheet(self._input_style())
        self.combo_v = QComboBox(); self.combo_v.setStyleSheet(self._input_style())
        row.addWidget(QLabel("De:")); row.addWidget(self.combo_u)
        row.addWidget(QLabel("→"));  row.addWidget(self.combo_v)
        lay.addLayout(row)
        ba = QPushButton("+ Arista"); ba.setStyleSheet(self._btn("#27ae60", "white"))
        ba.clicked.connect(self._agregar_arista); lay.addWidget(ba)
        be = QPushButton("- Eliminar Arista"); be.setStyleSheet(self._btn("#e74c3c", "white"))
        be.clicked.connect(self._eliminar_arista); lay.addWidget(be)

        lay.addWidget(self._sep())
        r2 = QHBoxLayout()
        bs = QPushButton("💾 Guardar"); bs.setStyleSheet(self._btn("#3498db", "white"))
        bl = QPushButton("📂 Cargar");  bl.setStyleSheet(self._btn("#3498db", "white"))
        bs.clicked.connect(self._guardar); bl.clicked.connect(self._cargar)
        r2.addWidget(bs); r2.addWidget(bl); lay.addLayout(r2)

        # Operaciones
        lay.addWidget(self._sep())
        lay.addWidget(self._lbl("Operación:"))

        self.combo_op = QComboBox()
        self.combo_op.addItem("Predecesores y sucesores",   "pred_suc")
        self.combo_op.addItem("Grados de entrada y salida", "grados")
        self.combo_op.addItem("Ordenamiento",    "topologico")
        self.combo_op.addItem("Recorrido por niveles",    "niveles")
        self.combo_op.setStyleSheet(self._input_style())
        self.combo_op.currentIndexChanged.connect(self._on_op_changed)
        lay.addWidget(self.combo_op)

        # Frame extra para BFS: selección de origen
        self.frame_origen = QFrame(); self.frame_origen.setStyleSheet("border:none;")
        fo = QVBoxLayout(self.frame_origen); fo.setContentsMargins(0,0,0,0); fo.setSpacing(4)
        fo.addWidget(self._lbl("Vértice origen (BFS):"))
        self.combo_origen_bfs = QComboBox()
        self.combo_origen_bfs.setStyleSheet(self._input_style())
        fo.addWidget(self.combo_origen_bfs)
        self.frame_origen.setVisible(False)
        lay.addWidget(self.frame_origen)

        btn_calc = QPushButton("▶ Calcular")
        btn_calc.setStyleSheet(self._btn("#2c3e50", "white"))
        btn_calc.clicked.connect(self._calcular); lay.addWidget(btn_calc)

        btn_reset = QPushButton("↺ Limpiar colores")
        btn_reset.setStyleSheet(self._btn("#7f8c8d", "white"))
        btn_reset.clicked.connect(self._limpiar_colores); lay.addWidget(btn_reset)

        # Panel de información
        lay.addWidget(self._sep())
        info = QFrame()
        info.setStyleSheet("background-color:white;border:2px solid #99ccff;border-radius:8px;")
        il = QVBoxLayout(info)
        lt = QLabel("Resultado")
        lt.setStyleSheet("font-weight:bold;color:#003366;font-size:13px;padding:4px;")
        lt.setAlignment(Qt.AlignCenter); il.addWidget(lt)
        self.texto_info = QTextEdit()
        self.texto_info.setReadOnly(True)
        self.texto_info.setMinimumHeight(300)
        self.texto_info.setStyleSheet(
            "font-family:monospace;font-size:12px;border:none;padding:4px;"
        )
        il.addWidget(self.texto_info)
        lay.addWidget(info)

    # ──────────────────────────────────────────────────────────────────
    #  Acciones del usuario
    # ──────────────────────────────────────────────────────────────────
    def _crear_grafo(self):
        self.controller.set_vertices(self.spin_v.value())
        self._actualizar_combos()
        self.texto_info.clear()

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
        opts = [f"{etiq.get(u,u+1)} → {etiq.get(v,v+1)}" for (u,v) in aristas]
        sel, ok = QInputDialog.getItem(self, "Eliminar arco", "Arco:", opts, 0, False)
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
                self.texto_info.clear()
                DialogoClave(0, "Éxito", "mensaje", self, "Cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {e}").exec()

    # ──────────────────────────────────────────────────────────────────
    #  Cálculo
    # ──────────────────────────────────────────────────────────────────
    def _calcular(self):
        n   = self.controller._vertices
        raw = self.controller._aristas
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec(); return

        suc, pred = _build_adj_dirigido(n, raw)
        etiq      = self.controller._etiquetas
        op        = self.combo_op.currentData()

        self._limpiar_colores()

        if   op == "pred_suc":    self._op_pred_suc(n, suc, pred, etiq)
        elif op == "grados":      self._op_grados(n, suc, pred, etiq)
        elif op == "topologico":  self._op_topologico(n, suc, pred, etiq)
        elif op == "niveles":     self._op_niveles(n, suc, etiq)
        elif op == "clausura":    self._op_clausura(n, suc, etiq)

    # ── Predecesores y sucesores ──────────────────────────────────────
    def _op_pred_suc(self, n, suc, pred, etiq):
        lineas = ["<b>Predecesores y Sucesores</b><br>"]
        for v in range(n):
            lv   = etiq.get(v, str(v+1))
            p_s  = ", ".join(etiq.get(u, str(u+1)) for u in sorted(set(pred[v]))) or "∅"
            s_s  = ", ".join(etiq.get(w, str(w+1)) for w in sorted(set(suc[v])))  or "∅"
            lineas.append(
                f"<b>V{lv}</b>:<br>"
                f"&nbsp;&nbsp;Pred({lv}) = {{ {p_s} }}<br>"
                f"&nbsp;&nbsp;Suc({lv})  = {{ {s_s} }}<br>"
            )
        self.texto_info.setHtml("<br>".join(lineas))

    # ── Grados ───────────────────────────────────────────────────────
    def _op_grados(self, n, suc, pred, etiq):
        html = ("<b>Grados de Entrada y Salida</b><br><br>"
                "<table border='1' cellspacing='0' cellpadding='5' "
                "style='border-collapse:collapse;width:100%;'>"
                "<tr style='background:#4d9de0;color:white;'>"
                "<th>Vértice</th><th>Entrada (δ⁻)</th><th>Salida (δ⁺)</th>"
                "<th>Total</th></tr>")
        for v in range(n):
            lv  = etiq.get(v, str(v+1))
            deg_in  = len(pred[v])
            deg_out = len(suc[v])
            html += (f"<tr><td>{lv}</td><td>{deg_in}</td>"
                     f"<td>{deg_out}</td><td>{deg_in+deg_out}</td></tr>")
        html += "</table>"
        self.texto_info.setHtml(html)

        # Colorear: entrada alta = rojo, salida alta = verde
        max_in  = max((len(pred[v]) for v in range(n)), default=1) or 1
        max_out = max((len(suc[v])  for v in range(n)), default=1) or 1
        col_v   = {}
        for v in range(n):
            ratio = (len(suc[v]) / max_out + len(pred[v]) / max_in) / 2
            if ratio > 0.6:   col_v[v] = "#e74c3c"
            elif ratio > 0.3: col_v[v] = "#f39c12"
            else:             col_v[v] = "#27ae60"
        self._aplicar_colores(col_v, {})

    # ── Ordenamiento topológico ───────────────────────────────────────
    def _op_topologico(self, n, suc, pred, etiq):
        orden, es_dag = _kahn(n, suc, pred)

        if not es_dag:
            self.texto_info.setHtml(
                "<b>Ordenamiento Topológico</b><br><br>"
                "<span style='color:#e74c3c;'>⚠ El grafo contiene ciclos — "
                "no es un DAG. No existe ordenamiento topológico.</span><br><br>"
                f"<b>Vértices procesados antes del ciclo:</b> "
                f"{' → '.join(etiq.get(v,str(v+1)) for v in orden) or '(ninguno)'}"
            )
            return

        # Color por posición ordinal
        col_v = {}
        for pos, v in enumerate(orden):
            col_v[v] = PALETA_NIVELES[pos % len(PALETA_NIVELES)]

        orden_str = " → ".join(etiq.get(v, str(v+1)) for v in orden)
        lineas = [
            "<b>Ordenamiento Topológico (Kahn)</b><br>",
            f"<b>Es DAG:</b> ✔ Sí<br>",
            f"<b>Orden:</b> {orden_str}<br><br>",
            "<b>Posición ordinal de cada vértice:</b><br>",
        ]
        for pos, v in enumerate(orden):
            lineas.append(
                f"&nbsp;&nbsp;Pos {pos+1}: <b>{etiq.get(v,str(v+1))}</b><br>"
            )

        # Función ordinal: para cada v, su nivel = posición en el orden
        lineas.append("<br><b>Función ordinal f(v):</b><br>")
        for pos, v in enumerate(orden):
            lineas.append(f"&nbsp;&nbsp;f({etiq.get(v,str(v+1))}) = {pos+1}<br>")

        self.texto_info.setHtml("".join(lineas))
        self._aplicar_colores(col_v, {})

    # ── Niveles BFS ───────────────────────────────────────────────────
    def _op_niveles(self, n, suc, etiq):
        origen = self.combo_origen_bfs.currentData()
        if origen is None:
            origen = 0
        nivel  = _niveles_bfs(n, suc, origen)

        # Agrupar por nivel
        max_niv = max(nivel.values(), default=0)
        por_nivel: dict[int, list] = {k: [] for k in range(max_niv + 1)}
        for v, nv in nivel.items():
            por_nivel[nv].append(v)
        inalcanzables = [v for v in range(n) if v not in nivel]

        col_v = {}
        for v, nv in nivel.items():
            col_v[v] = PALETA_NIVELES[nv % len(PALETA_NIVELES)]
        for v in inalcanzables:
            col_v[v] = "#95a5a6"

        html = (f"<b>Niveles BFS desde {etiq.get(origen,str(origen+1))}</b><br><br>"
                f"<b>Total de niveles:</b> {max_niv + 1}<br><br>")
        for nv in range(max_niv + 1):
            verts = ", ".join(etiq.get(v, str(v+1)) for v in sorted(por_nivel[nv]))
            color = PALETA_NIVELES[nv % len(PALETA_NIVELES)]
            html += (f"<b><span style='color:{color};'>Nivel {nv}:</span></b> "
                     f"{{ {verts} }}<br>")
        if inalcanzables:
            iv = ", ".join(etiq.get(v, str(v+1)) for v in inalcanzables)
            html += f"<br><b>Inalcanzables:</b> {{ {iv} }}"

        self.texto_info.setHtml(html)
        self._aplicar_colores(col_v, {})

    # ── Clausura transitiva ───────────────────────────────────────────
    def _op_clausura(self, n, suc, etiq):
        ct = _clausura_transitiva(n, suc)

        html = "<b>Clausura Transitiva</b><br>"
        html += "<i>(CT(v) = conjunto de vértices alcanzables desde v)</i><br><br>"
        html += ("<table border='1' cellspacing='0' cellpadding='5' "
                 "style='border-collapse:collapse;width:100%;'>"
                 "<tr style='background:#4d9de0;color:white;'>"
                 "<th>Vértice v</th><th>CT(v)</th><th>|CT(v)|</th></tr>")
        for v in range(n):
            lv   = etiq.get(v, str(v+1))
            alcz = sorted(ct[v])
            a_s  = "{ " + ", ".join(etiq.get(w, str(w+1)) for w in alcz) + " }" if alcz else "∅"
            html += (f"<tr><td>{lv}</td><td>{a_s}</td><td>{len(alcz)}</td></tr>")
        html += "</table>"

        # Fuente: vértices que alcanzan a todos los demás
        fuentes = [v for v in range(n) if len(ct[v]) == n - 1]
        pozos   = [v for v in range(n) if len(ct[v]) == 0]

        if fuentes:
            f_s = ", ".join(etiq.get(v, str(v+1)) for v in fuentes)
            html += f"<br><b>Fuentes</b> (alcanzan a todos): {{ {f_s} }}"
        if pozos:
            p_s = ", ".join(etiq.get(v, str(v+1)) for v in pozos)
            html += f"<br><b>Pozos</b> (no alcanzan a nadie): {{ {p_s} }}"

        self.texto_info.setHtml(html)

        # Colorear por alcanzabilidad
        max_alc = max(len(ct[v]) for v in range(n)) if n > 0 else 0
        col_v   = {}
        for v in range(n):
            ratio = len(ct[v]) / max_alc if max_alc > 0 else 0
            if ratio > 0.66:   col_v[v] = "#27ae60"
            elif ratio > 0.33: col_v[v] = "#f39c12"
            else:              col_v[v] = "#e74c3c"
        self._aplicar_colores(col_v, {})

    # ──────────────────────────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────────────────────────
    def _on_op_changed(self):
        op = self.combo_op.currentData()
        self.frame_origen.setVisible(op == "niveles")

    def _aplicar_colores(self, col_v: dict, col_a: dict):
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(
            datos["vertices"], datos["aristas"],
            datos["etiquetas"], datos["pesos"],
            colores_vertices=col_v,
            colores_aristas=col_a,
        )

    def _limpiar_colores(self):
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(
            datos["vertices"], datos["aristas"],
            datos["etiquetas"], datos["pesos"],
        )

    def _actualizar_visual(self):
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(
            datos["vertices"], datos["aristas"],
            datos["etiquetas"], datos["pesos"],
        )

    def _actualizar_combos(self):
        n    = self.controller._vertices
        etiq = self.controller._etiquetas
        for combo in (self.combo_u, self.combo_v, self.combo_origen_bfs):
            combo.clear()
            for i in range(n):
                combo.addItem(etiq.get(i, str(i+1)), i)

    def _cerrar_grafos(self):
        self.close(); self.volver_a_grafos()

    def _cerrar_principal(self):
        self.close(); self.volver_a_principal()

    # ──────────────────────────────────────────────────────────────────
    #  Estilos
    # ──────────────────────────────────────────────────────────────────
    @staticmethod
    def _btn(bg, fg):
        return (f"QPushButton {{background-color:{bg};color:{fg};font-weight:bold;"
                f"border:none;border-radius:5px;padding:8px 12px;}}"
                f"QPushButton:hover {{opacity:0.85;}}")

    @staticmethod
    def _lbl(text):
        l = QLabel(text); l.setStyleSheet("font-weight:bold;color:#003366;"); return l

    @staticmethod
    def _sep():
        s = QFrame(); s.setFrameShape(QFrame.HLine)
        s.setStyleSheet("color:#99ccff;"); return s

    @staticmethod
    def _input_style():
        return "background-color:white;border:2px solid #99ccff;border-radius:4px;"