"""
algoritmos/grafos/pareamiento_grafo.py
Pareamiento (Matching) de Grafos No Dirigidos.
  • Pareamiento maximal  – greedy + todos los maximales por backtracking
  • Pareamiento máximo   – caminos aumentantes
"""
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
#  Algoritmos de pareamiento
# ══════════════════════════════════════════════════════════════════════

def _todos_los_maximales(n: int, aristas: list) -> list[list[int]]:
    """
    Backtracking para encontrar TODOS los pareamientos maximales.
    Cada resultado es una lista de índices de arista.
    Un pareamiento es maximal cuando no se puede agregar ninguna arista
    sin violar la condición de matching.
    """
    resultados: list[frozenset] = []
    salida: list[list[int]] = []

    def bt(idx: int, matching: list[int], saturados: set):
        extendido = False
        for i in range(idx, len(aristas)):
            u, v, _ = aristas[i]
            if u == v:          # ignorar bucles
                continue
            if u not in saturados and v not in saturados:
                bt(i + 1, matching + [i], saturados | {u, v})
                extendido = True
        if not extendido:
            clave = frozenset(matching)
            if clave not in resultados:
                resultados.append(clave)
                salida.append(list(matching))

    bt(0, [], set())
    return salida


def _pareamiento_maximo(n: int, aristas: list) -> list[int]:
    """
    Pareamiento máximo por caminos aumentantes (funciona bien en grafos
    generales pequeños; para grafos bipartitos es óptimo).
    Devuelve lista de índices de arista del matching máximo.
    """
    match_v = [-1] * n          # match_v[v] = vértice pareja de v, o -1
    adj: list[list[tuple]] = [[] for _ in range(n)]
    for i, (u, v, _) in enumerate(aristas):
        if u != v:
            adj[u].append((v, i))
            adj[v].append((u, i))

    def augmentar(v: int, visitados: set) -> bool:
        for (w, _) in adj[v]:
            if w in visitados:
                continue
            visitados.add(w)
            if match_v[w] == -1 or augmentar(match_v[w], visitados):
                match_v[v] = w
                match_v[w] = v
                return True
        return False

    for v in range(n):
        if match_v[v] == -1:
            augmentar(v, {v})

    # Extraer índices de arista sin duplicados
    resultado: list[int] = []
    vistos: set = set()
    for v in range(n):
        w = match_v[v]
        if w != -1 and w not in vistos:
            vistos.add(v)
            for i, (u, vv, _) in enumerate(aristas):
                if (u == v and vv == w) or (u == w and vv == v):
                    if i not in resultado:
                        resultado.append(i)
                    break
    return resultado


def _todos_los_maximos(n: int, aristas: list) -> list[list[int]]:
    """
    Todos los pareamientos máximos (mismo tamaño que el máximo).
    Se generan por backtracking filtrando solo los de cardinalidad máxima.
    """
    cardinalidad_max = len(_pareamiento_maximo(n, aristas))
    if cardinalidad_max == 0:
        return []

    resultados: list[frozenset] = []
    salida: list[list[int]] = []

    def bt(idx: int, matching: list[int], saturados: set):
        # Poda: incluso añadiendo todas las aristas restantes no llegamos
        aristas_restantes = sum(
            1 for i in range(idx, len(aristas))
            if aristas[i][0] != aristas[i][1]
            and aristas[i][0] not in saturados
            and aristas[i][1] not in saturados
        )
        if len(matching) + aristas_restantes < cardinalidad_max:
            return

        if len(matching) == cardinalidad_max:
            clave = frozenset(matching)
            if clave not in resultados:
                resultados.append(clave)
                salida.append(list(matching))
            return

        for i in range(idx, len(aristas)):
            u, v, _ = aristas[i]
            if u == v:
                continue
            if u not in saturados and v not in saturados:
                bt(i + 1, matching + [i], saturados | {u, v})

    bt(0, [], set())
    return salida if salida else [_pareamiento_maximo(n, aristas)]


# ══════════════════════════════════════════════════════════════════════
#  Colores
# ══════════════════════════════════════════════════════════════════════
COLORES_MATCHING = [
    "#27ae60", "#e74c3c", "#f39c12", "#8e44ad",
    "#2980b9", "#16a085", "#d35400",
]


# ══════════════════════════════════════════════════════════════════════
#  Ventana principal
# ══════════════════════════════════════════════════════════════════════
class PareamientoGrafoWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos = volver_a_grafos
        self.volver_a_principal = volver_a_principal

        self.controller = GrafoController()
        self._pareamientos: list[list[int]] = []   # lista de matchings
        self._idx_actual: int = 0

        self.setWindowTitle("Pareamiento de Grafos")
        self.setGeometry(100, 50, 1500, 820)
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
        root.setSpacing(10)
        root.setContentsMargins(10, 10, 10, 10)
        root.addWidget(self._make_header())

        body = QHBoxLayout()
        body.setSpacing(12)

        # ── Visualizador ──────────────────────────────────────────────
        self.visual = VisualizadorGrafoColoreable(
            "Grafo", es_editable=True, dirigido=False
        )
        self.visual.setFixedSize(520, 540)
        body.addWidget(self.visual, stretch=2)

        # ── Panel derecho ─────────────────────────────────────────────
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("border: none;")
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color:#e6f2ff; border-radius:8px;")
        self.right_layout = QVBoxLayout(right_widget)
        self.right_layout.setSpacing(8)
        self.right_layout.setAlignment(Qt.AlignTop)
        right_scroll.setWidget(right_widget)
        body.addWidget(right_scroll, stretch=1)

        root.addLayout(body)
        self._build_panel()

    def _make_header(self) -> QFrame:
        h = QFrame()
        h.setStyleSheet("background-color:#cce6ff; border-radius:10px;")
        hl = QHBoxLayout(h)
        b1 = QPushButton("← Volver a Grafos")
        b1.setStyleSheet(self._btn("#e6f2ff", "#003366"))
        b1.clicked.connect(self._cerrar_grafos)
        b2 = QPushButton("🏠 Inicio")
        b2.setStyleSheet(self._btn("#e6f2ff", "#003366"))
        b2.clicked.connect(self._cerrar_principal)
        titulo = QLabel("PAREAMIENTO DE GRAFOS")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setStyleSheet("color:#003366;")
        hl.addWidget(b1); hl.addWidget(b2)
        hl.addWidget(titulo, alignment=Qt.AlignCenter)
        return h

    def _build_panel(self):
        lay = self.right_layout

        # ── Crear grafo ───────────────────────────────────────────────
        lay.addWidget(self._lbl("Número de vértices:"))
        self.spin_v = QSpinBox()
        self.spin_v.setRange(1, 14); self.spin_v.setValue(5)
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
        self.spin_peso.setRange(0, 9999); self.spin_peso.setValue(0)
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
        lay.addWidget(self._lbl("Tipo de pareamiento:"))
        self.combo_op = QComboBox()
        self.combo_op.addItem("Pareamiento Maximal", "maximal")
        self.combo_op.addItem("Pareamiento Máximo",  "maximo")
        self.combo_op.setStyleSheet(self._input_style())
        lay.addWidget(self.combo_op)

        br = QPushButton("▶ Calcular pareamiento")
        br.setStyleSheet(self._btn("#2c3e50", "white"))
        br.clicked.connect(self._calcular)
        lay.addWidget(br)

        self.btn_otro = QPushButton("🔄 Ver otro pareamiento")
        self.btn_otro.setStyleSheet(self._btn("#8e44ad", "white"))
        self.btn_otro.clicked.connect(self._ver_otro)
        self.btn_otro.setVisible(False)
        lay.addWidget(self.btn_otro)

        self.btn_reset = QPushButton("↺ Limpiar colores")
        self.btn_reset.setStyleSheet(self._btn("#7f8c8d", "white"))
        self.btn_reset.clicked.connect(self._limpiar_colores)
        self.btn_reset.setVisible(False)
        lay.addWidget(self.btn_reset)

        # ── Panel de información ──────────────────────────────────────
        lay.addWidget(self._sep())
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet(
            "background-color:white; border:2px solid #99ccff;"
            "border-radius:8px; margin:2px;"
        )
        info_lay = QVBoxLayout(self.info_frame)
        lbl_titulo = QLabel("Información del pareamiento")
        lbl_titulo.setStyleSheet(
            "font-weight:bold; color:#003366; font-size:13px; padding:4px;"
        )
        lbl_titulo.setAlignment(Qt.AlignCenter)
        info_lay.addWidget(lbl_titulo)

        self.texto_info = QTextEdit()
        self.texto_info.setReadOnly(True)
        self.texto_info.setMinimumHeight(260)
        self.texto_info.setStyleSheet(
            "font-family:monospace; font-size:12px; border:none; padding:4px;"
        )
        info_lay.addWidget(self.texto_info)
        self.info_frame.setVisible(False)
        lay.addWidget(self.info_frame)

    # ──────────────────────────────────────────────────────────────────
    #  Acciones del usuario
    # ──────────────────────────────────────────────────────────────────
    def _crear_grafo(self):
        self.controller.set_vertices(self.spin_v.value())
        self._actualizar_combos()
        self._reset_estado()

    def _agregar_arista(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea el grafo.").exec()
            return
        u = self.combo_u.currentData()
        v = self.combo_v.currentData()
        if u is None or v is None or u == v:
            DialogoClave(0, "Error", "mensaje", self, "Selecciona dos vértices distintos.").exec()
            return
        self.controller.agregar_arista(u, v, self.spin_peso.value())

    def _eliminar_arista(self):
        datos = self.controller.obtener_datos()
        aristas = datos["aristas"]
        etiq = datos["etiquetas"]
        if not aristas:
            DialogoClave(0, "Info", "mensaje", self, "No hay aristas.").exec()
            return
        from PySide6.QtWidgets import QInputDialog
        opts = [f"{etiq.get(u,u+1)} — {etiq.get(v,v+1)}" for (u,v) in aristas]
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
                self._reset_estado()
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {e}").exec()

    def _calcular(self):
        n = self.controller._vertices
        aristas = self.controller._aristas

        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec()
            return

        op = self.combo_op.currentData()
        self._reset_estado()

        if op == "maximal":
            self._pareamientos = _todos_los_maximales(n, aristas)
        else:
            self._pareamientos = _todos_los_maximos(n, aristas)

        if not self._pareamientos:
            DialogoClave(0, "Info", "mensaje", self,
                         "No se encontraron pareamientos (¿el grafo tiene aristas?).").exec()
            return

        self._idx_actual = 0
        self._mostrar_pareamiento(self._idx_actual)
        self.btn_otro.setVisible(len(self._pareamientos) > 1)
        self.btn_reset.setVisible(True)
        self.info_frame.setVisible(True)

    def _ver_otro(self):
        if not self._pareamientos:
            return
        self._idx_actual = (self._idx_actual + 1) % len(self._pareamientos)
        self._mostrar_pareamiento(self._idx_actual)

    def _limpiar_colores(self):
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(
            datos["vertices"], datos["aristas"],
            datos["etiquetas"], datos["pesos"],
            colores_vertices={}, colores_aristas={},
        )
        self._reset_estado()

    # ──────────────────────────────────────────────────────────────────
    #  Lógica de visualización y resumen
    # ──────────────────────────────────────────────────────────────────
    def _mostrar_pareamiento(self, idx: int):
        datos = self.controller.obtener_datos()
        n        = datos["vertices"]
        aristas  = datos["aristas"]
        pesos    = datos["pesos"]
        etiq     = datos["etiquetas"]
        aristas_raw = self.controller._aristas

        matching = self._pareamientos[idx]
        matching_set = set(matching)
        op = self.combo_op.currentData()

        color = COLORES_MATCHING[idx % len(COLORES_MATCHING)]
        colores_a = {ei: color for ei in matching_set}

        # Vértices saturados
        saturados: set[int] = set()
        for ei in matching_set:
            u, v, _ = aristas_raw[ei]
            saturados.add(u); saturados.add(v)
        no_saturados = set(range(n)) - saturados

        # Color vértices
        colores_v = {}
        for v in saturados:
            colores_v[v] = color
        for v in no_saturados:
            colores_v[v] = "#4d9de0"   # azul por defecto

        self.visual.set_grafo(n, aristas, etiq, pesos, colores_v, colores_a)

        # ── Texto informativo ─────────────────────────────────────────
        S_str = "{ " + ",  ".join(etiq.get(i, str(i+1)) for i in range(n)) + " }"

        A_list = [
            f"e{i+1}({etiq.get(u,str(u+1))}–{etiq.get(v,str(v+1))})"
            for i, (u,v) in enumerate(aristas)
        ]
        A_str = "{ " + ",  ".join(A_list) + " }" if A_list else "∅"

        M_list = [
            f"e{ei+1}({etiq.get(aristas_raw[ei][0],str(aristas_raw[ei][0]+1))}–"
            f"{etiq.get(aristas_raw[ei][1],str(aristas_raw[ei][1]+1))})"
            for ei in sorted(matching_set)
        ]
        M_str = "{ " + ",  ".join(M_list) + " }" if M_list else "∅"

        sat_str = (
            "{ " + ",  ".join(etiq.get(v, str(v+1)) for v in sorted(saturados)) + " }"
            if saturados else "∅"
        )
        no_sat_str = (
            "{ " + ",  ".join(etiq.get(v, str(v+1)) for v in sorted(no_saturados)) + " }"
            if no_saturados else "∅"
        )

        # Perfecto: todos los vértices saturados
        es_perfecto = len(no_saturados) == 0

        # Maximal: no se puede agregar ninguna arista más
        saturados_check = set(saturados)
        puede_extender = any(
            u not in saturados_check and v not in saturados_check
            for i, (u, v, _) in enumerate(aristas_raw)
            if i not in matching_set and u != v
        )
        es_maximal = not puede_extender

        # Máximo: cardinalidad igual al máximo posible
        card_max = len(_pareamiento_maximo(n, aristas_raw))
        es_maximo = len(matching) == card_max

        tipo_op = "Maximal" if op == "maximal" else "Máximo"
        total = len(self._pareamientos)

        lineas = [
            f"Pareamiento {tipo_op}  ({idx+1}/{total})",
            "",
            f"S  =  {S_str}",
            "",
            f"A  =  {A_str}",
            "",
            f"M  =  {M_str}",
            "",
            f"│M│ (cardinalidad)  =  {len(matching)}",
            "",
            f"Vértices saturados     =  {sat_str}",
            f"Vértices no saturados  =  {no_sat_str}",
            "",
            f"¿Perfecto?   →  {'✔ Sí' if es_perfecto  else '✘ No'}",
            f"¿Maximal?    →  {'✔ Sí' if es_maximal   else '✘ No'}",
            f"¿Máximo?     →  {'✔ Sí  (cardinalidad = ' + str(card_max) + ')' if es_maximo else '✘ No  (máximo posible = ' + str(card_max) + ')'}",
        ]
        self.texto_info.setText("\n".join(lineas))

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
        n = self.controller._vertices
        etiq = self.controller._etiquetas
        for combo in (self.combo_u, self.combo_v):
            combo.clear()
            for i in range(n):
                combo.addItem(etiq.get(i, str(i+1)), i)

    def _reset_estado(self):
        self._pareamientos = []
        self._idx_actual = 0
        self.btn_otro.setVisible(False)
        self.btn_reset.setVisible(False)
        self.info_frame.setVisible(False)
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
        l = QLabel(text); l.setStyleSheet("font-weight:bold;color:#003366;")
        return l

    @staticmethod
    def _sep() -> QFrame:
        s = QFrame(); s.setFrameShape(QFrame.HLine)
        s.setStyleSheet("color:#99ccff;"); return s

    @staticmethod
    def _input_style() -> str:
        return "background-color:white;border:2px solid #99ccff;border-radius:4px;"