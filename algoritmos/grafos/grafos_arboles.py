"""
algoritmos/grafos/grafos_arboles.py
Operaciones con árboles de grafos:
  • Árbol de expansión mínima  (Kruskal)
  • Árbol de expansión máxima  (Kruskal invertido)
  • Distancia entre dos árboles (diferencia simétrica de aristas)
  • Camino mínimo              (Dijkstra)
"""
import math
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QFrame, QFileDialog, QComboBox,
    QScrollArea, QTextEdit, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from controladores.grafo_controller import GrafoController
from controladores.visualizador_grafo import VisualizadorGrafo
from controladores.visualizador_grafo import VisualizadorGrafoColoreable
from algoritmos.funcion_mod import DialogoClave


# ══════════════════════════════════════════════════════════════════════
#  Algoritmos
# ══════════════════════════════════════════════════════════════════════

def _kruskal(n: int, aristas: list, maximo: bool = False) -> tuple[list[int], list[int]]:
    """
    Kruskal mínimo (maximo=False) o máximo (maximo=True).
    Devuelve (ramas, cuerdas) como índices en la lista de aristas.
    """
    if n == 0:
        return [], []
    items = [(p, u, v, i) for i, (u, v, p) in enumerate(aristas)]
    items.sort(key=lambda x: x[0], reverse=maximo)

    parent = list(range(n))
    rank   = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:  parent[rx] = ry
        elif rank[rx] > rank[ry]: parent[ry] = rx
        else:                     parent[ry] = rx; rank[rx] += 1
        return True

    ramas, cuerdas = [], []
    for p, u, v, i in items:
        if u == v:         cuerdas.append(i)
        elif union(u, v):  ramas.append(i)
        else:              cuerdas.append(i)
    return ramas, cuerdas


def _dijkstra(n: int, aristas: list, origen: int) -> tuple[list[float], list[int]]:
    """
    Dijkstra desde `origen`.
    Devuelve (distancias, predecesores).
    predecesores[v] = índice del vértice anterior en el camino más corto.
    """
    INF  = math.inf
    dist = [INF] * n
    prev = [-1]  * n
    dist[origen] = 0
    visitado = [False] * n

    adj: list[list[tuple]] = [[] for _ in range(n)]
    for u, v, p in aristas:
        w = p if p > 0 else 1
        adj[u].append((v, w))
        if u != v:
            adj[v].append((u, w))

    for _ in range(n):
        # Vértice no visitado con menor distancia
        u = min((i for i in range(n) if not visitado[i]), key=lambda i: dist[i], default=-1)
        if u == -1 or dist[u] == INF:
            break
        visitado[u] = True
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u

    return dist, prev


def _reconstruir_camino(prev: list[int], destino: int) -> list[int]:
    """Devuelve la lista de vértices del camino mínimo (vacío si no hay)."""
    camino = []
    cur    = destino
    while cur != -1:
        camino.append(cur)
        cur = prev[cur]
    camino.reverse()
    return camino if len(camino) > 1 or (len(camino) == 1 and camino[0] == destino) else []


def _distancia_arboles(
    aristas1: list, etiq1: dict,
    aristas2: list, etiq2: dict,
) -> tuple[int, set, set, set]:
    """
    Distancia entre dos árboles = |T1 △ T2| / 2  (aristas simétricas distintas).
    Las aristas se identifican por par de etiquetas (no por índice).
    Devuelve (distancia, solo_en_T1, solo_en_T2, comunes).
    """
    def arista_clave(u: int, v: int, etiq: dict) -> frozenset:
        return frozenset({etiq.get(u, str(u+1)), etiq.get(v, str(v+1))})

    set1 = {arista_clave(u, v, etiq1) for u, v, _ in aristas1}
    set2 = {arista_clave(u, v, etiq2) for u, v, _ in aristas2}

    solo1   = set1 - set2
    solo2   = set2 - set1
    comunes = set1 & set2
    dist    = len(solo1)        # = len(solo2) si son spanning trees del mismo grafo
    return dist, solo1, solo2, comunes


# ══════════════════════════════════════════════════════════════════════
#  Ventana principal
# ══════════════════════════════════════════════════════════════════════
class GrafosArbolesWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos   = volver_a_grafos
        self.volver_a_principal = volver_a_principal

        self.ctrl1 = GrafoController()
        self.ctrl2 = GrafoController()

        self.setWindowTitle("Árboles de Grafos")
        self.setGeometry(80, 40, 1700, 950)
        self.setStyleSheet("background-color: #f0f8ff;")

        self._build_ui()
        self.ctrl1.grafo_cambiado.connect(lambda: self._actualizar_visual(1))
        self.ctrl2.grafo_cambiado.connect(lambda: self._actualizar_visual(2))

    # ──────────────────────────────────────────────────────────────────
    #  UI: estructura principal
    # ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(8)
        root.setContentsMargins(8, 8, 8, 8)
        root.addWidget(self._make_header())

        # ── Fila de visualizadores ────────────────────────────────────
        vis_row = QHBoxLayout()
        vis_row.setSpacing(8)

        self.vis1 = VisualizadorGrafo("Grafo 1", es_editable=True)
        self.vis2 = VisualizadorGrafo("Grafo 2", es_editable=True)
        self.vis_r1 = VisualizadorGrafoColoreable("Resultado A", es_editable=False)
        self.vis_r2 = VisualizadorGrafoColoreable("Resultado B", es_editable=False)

        for vis in (self.vis1, self.vis2, self.vis_r1, self.vis_r2):
            vis.setFixedSize(390, 390)
            vis_row.addWidget(vis)

        root.addLayout(vis_row)

        # ── Fila inferior: controles G1 | controles G2 | operación | info ──
        bottom = QHBoxLayout()
        bottom.setSpacing(8)

        bottom.addWidget(self._panel_grafo(1), stretch=1)
        bottom.addWidget(self._panel_grafo(2), stretch=1)
        bottom.addWidget(self._panel_operacion(), stretch=1)
        bottom.addWidget(self._panel_info(), stretch=1)

        root.addLayout(bottom)

    # ──────────────────────────────────────────────────────────────────
    #  Paneles de control individuales
    # ──────────────────────────────────────────────────────────────────
    def _panel_grafo(self, num: int) -> QFrame:
        frame = QFrame()
        color_borde = "#99ccff" if num == 1 else "#f0c080"
        color_bg    = "#e6f2ff" if num == 1 else "#fff3e0"
        color_txt   = "#003366" if num == 1 else "#7d3c00"
        frame.setStyleSheet(
            f"background-color:{color_bg}; border:2px solid {color_borde};"
            f"border-radius:8px;"
        )
        lay = QVBoxLayout(frame)
        lay.setSpacing(6)
        lay.setAlignment(Qt.AlignTop)

        lbl = QLabel(f"GRAFO {num}")
        lbl.setStyleSheet(f"font-weight:bold;color:{color_txt};font-size:13px;")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)

        # Vértices
        lay.addWidget(self._lbl(f"Vértices:", color_txt))
        spin = QSpinBox(); spin.setRange(1, 14); spin.setValue(4)
        spin.setStyleSheet(self._input_style())
        lay.addWidget(spin)
        btn_crear = QPushButton("Crear grafo")
        btn_crear.setStyleSheet(self._btn("#4d9de0" if num==1 else "#e67e22", "white"))
        lay.addWidget(btn_crear)

        # Aristas
        lay.addWidget(self._sep())
        lay.addWidget(self._lbl("Agregar arista:", color_txt))
        row = QHBoxLayout()
        combo_u = QComboBox(); combo_u.setStyleSheet(self._input_style())
        combo_v = QComboBox(); combo_v.setStyleSheet(self._input_style())
        spin_p  = QSpinBox();  spin_p.setRange(0, 9999); spin_p.setValue(1)
        spin_p.setStyleSheet(self._input_style())
        row.addWidget(QLabel("De:")); row.addWidget(combo_u)
        row.addWidget(QLabel("A:"));  row.addWidget(combo_v)
        row.addWidget(QLabel("P:"));  row.addWidget(spin_p)
        lay.addLayout(row)

        btn_add = QPushButton("+ Arista")
        btn_add.setStyleSheet(self._btn("#27ae60", "white"))
        lay.addWidget(btn_add)
        btn_del = QPushButton("- Eliminar arista")
        btn_del.setStyleSheet(self._btn("#e74c3c", "white"))
        lay.addWidget(btn_del)

        # Guardar / Cargar
        lay.addWidget(self._sep())
        row2 = QHBoxLayout()
        btn_s = QPushButton("💾 Guardar"); btn_s.setStyleSheet(self._btn("#3498db", "white"))
        btn_l = QPushButton("📂 Cargar");  btn_l.setStyleSheet(self._btn("#3498db", "white"))
        row2.addWidget(btn_s); row2.addWidget(btn_l)
        lay.addLayout(row2)

        # Guardar referencias
        if num == 1:
            self.spin_v1 = spin
            self.combo_u1, self.combo_v1, self.spin_p1 = combo_u, combo_v, spin_p
            btn_crear.clicked.connect(lambda: self._crear_grafo(1))
            btn_add.clicked.connect(lambda:   self._agregar_arista(1))
            btn_del.clicked.connect(lambda:   self._eliminar_arista(1))
            btn_s.clicked.connect(lambda:     self._guardar(1))
            btn_l.clicked.connect(lambda:     self._cargar(1))
        else:
            self.spin_v2 = spin
            self.combo_u2, self.combo_v2, self.spin_p2 = combo_u, combo_v, spin_p
            btn_crear.clicked.connect(lambda: self._crear_grafo(2))
            btn_add.clicked.connect(lambda:   self._agregar_arista(2))
            btn_del.clicked.connect(lambda:   self._eliminar_arista(2))
            btn_s.clicked.connect(lambda:     self._guardar(2))
            btn_l.clicked.connect(lambda:     self._cargar(2))

        return frame

    def _panel_operacion(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            "background-color:#e8f5e9; border:2px solid #a5d6a7; border-radius:8px;"
        )
        lay = QVBoxLayout(frame)
        lay.setSpacing(6)
        lay.setAlignment(Qt.AlignTop)

        lbl = QLabel("OPERACIÓN")
        lbl.setStyleSheet("font-weight:bold;color:#1b5e20;font-size:13px;")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)

        # Tipo de operación
        lay.addWidget(self._lbl("Operación:", "#1b5e20"))
        self.combo_op = QComboBox()
        self.combo_op.addItem("Árbol expansión mínima",   "min")
        self.combo_op.addItem("Árbol expansión máxima",   "max")
        self.combo_op.addItem("Distancia entre árboles",  "dist")
        self.combo_op.addItem("Camino mínimo (Dijkstra)", "dijkstra")
        self.combo_op.setStyleSheet(self._input_style())
        self.combo_op.currentIndexChanged.connect(self._on_op_changed)
        lay.addWidget(self.combo_op)

        # Sobre qué grafo aplicar
        lay.addWidget(self._lbl("Aplicar sobre:", "#1b5e20"))
        self.combo_grafo = QComboBox()
        self.combo_grafo.addItem("Grafo 1", 1)
        self.combo_grafo.addItem("Grafo 2", 2)
        self.combo_grafo.addItem("Ambos (solo distancia)", 0)
        self.combo_grafo.setStyleSheet(self._input_style())
        lay.addWidget(self.combo_grafo)

        # Controles extras para Dijkstra
        self.frame_dijkstra = QFrame()
        self.frame_dijkstra.setStyleSheet("border:none;")
        dlay = QVBoxLayout(self.frame_dijkstra)
        dlay.setContentsMargins(0, 0, 0, 0)
        dlay.setSpacing(4)
        dlay.addWidget(self._lbl("Origen:", "#1b5e20"))
        self.combo_origen = QComboBox(); self.combo_origen.setStyleSheet(self._input_style())
        dlay.addWidget(self.combo_origen)
        dlay.addWidget(self._lbl("Destino:", "#1b5e20"))
        self.combo_destino = QComboBox(); self.combo_destino.setStyleSheet(self._input_style())
        dlay.addWidget(self.combo_destino)
        self.frame_dijkstra.setVisible(False)
        lay.addWidget(self.frame_dijkstra)

        lay.addWidget(self._sep())
        btn_calc = QPushButton("▶ Calcular")
        btn_calc.setStyleSheet(self._btn("#2c3e50", "white"))
        btn_calc.clicked.connect(self._calcular)
        lay.addWidget(btn_calc)

        btn_reset = QPushButton("↺ Limpiar resultados")
        btn_reset.setStyleSheet(self._btn("#7f8c8d", "white"))
        btn_reset.clicked.connect(self._limpiar_resultados)
        lay.addWidget(btn_reset)

        return frame

    def _panel_info(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            "background-color:white; border:2px solid #99ccff; border-radius:8px;"
        )
        lay = QVBoxLayout(frame)
        lbl = QLabel("Información")
        lbl.setStyleSheet("font-weight:bold;color:#003366;font-size:13px;padding:4px;")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)
        self.texto_info = QTextEdit()
        self.texto_info.setReadOnly(True)
        self.texto_info.setStyleSheet(
            "font-family:monospace;font-size:12px;border:none;padding:4px;"
        )
        lay.addWidget(self.texto_info)
        return frame

    def _make_header(self) -> QFrame:
        h = QFrame()
        h.setStyleSheet("background-color:#cce6ff;border-radius:10px;")
        hl = QHBoxLayout(h)
        b1 = QPushButton("← Volver a Grafos")
        b1.setStyleSheet(self._btn("#e6f2ff", "#003366"))
        b1.clicked.connect(self._cerrar_grafos)
        b2 = QPushButton("🏠 Inicio")
        b2.setStyleSheet(self._btn("#e6f2ff", "#003366"))
        b2.clicked.connect(self._cerrar_principal)
        titulo = QLabel("ÁRBOLES DE GRAFOS")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setStyleSheet("color:#003366;")
        hl.addWidget(b1); hl.addWidget(b2)
        hl.addWidget(titulo, alignment=Qt.AlignCenter)
        return h

    # ──────────────────────────────────────────────────────────────────
    #  Acciones: creación / edición de grafos
    # ──────────────────────────────────────────────────────────────────
    def _crear_grafo(self, num: int):
        ctrl  = self.ctrl1 if num == 1 else self.ctrl2
        spin  = self.spin_v1 if num == 1 else self.spin_v2
        ctrl.set_vertices(spin.value())
        self._actualizar_combos(num)
        self._limpiar_resultados()
        self._sincronizar_combos_dijkstra()

    def _agregar_arista(self, num: int):
        ctrl = self.ctrl1 if num == 1 else self.ctrl2
        if ctrl._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea el grafo.").exec(); return
        cu = self.combo_u1 if num == 1 else self.combo_u2
        cv = self.combo_v1 if num == 1 else self.combo_v2
        sp = self.spin_p1  if num == 1 else self.spin_p2
        u, v = cu.currentData(), cv.currentData()
        if u is None or v is None or u == v:
            DialogoClave(0, "Error", "mensaje", self, "Selecciona dos vértices distintos.").exec(); return
        ctrl.agregar_arista(u, v, sp.value())

    def _eliminar_arista(self, num: int):
        ctrl = self.ctrl1 if num == 1 else self.ctrl2
        datos = ctrl.obtener_datos()
        aristas, etiq = datos["aristas"], datos["etiquetas"]
        if not aristas:
            DialogoClave(0, "Info", "mensaje", self, "No hay aristas.").exec(); return
        from PySide6.QtWidgets import QInputDialog
        opts = [f"{etiq.get(u,u+1)} — {etiq.get(v,v+1)}" for (u,v) in aristas]
        sel, ok = QInputDialog.getItem(self, "Eliminar arista", "Arista:", opts, 0, False)
        if ok:
            idx = opts.index(sel); u, v = aristas[idx]
            ctrl.eliminar_arista(u, v, indice=idx)

    def _guardar(self, num: int):
        ctrl = self.ctrl1 if num == 1 else self.ctrl2
        if ctrl._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay grafo.").exec(); return
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar", "", "JSON (*.json)")
        if ruta:
            ctrl.guardar_json(ruta)
            DialogoClave(0, "Éxito", "mensaje", self, "Guardado.").exec()

    def _cargar(self, num: int):
        ctrl = self.ctrl1 if num == 1 else self.ctrl2
        spin = self.spin_v1 if num == 1 else self.spin_v2
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar", "", "JSON (*.json)")
        if ruta:
            try:
                ctrl.cargar_json(ruta)
                spin.setValue(ctrl._vertices)
                self._actualizar_combos(num)
                self._limpiar_resultados()
                self._sincronizar_combos_dijkstra()
                DialogoClave(0, "Éxito", "mensaje", self, "Cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {e}").exec()

    # ──────────────────────────────────────────────────────────────────
    #  Cálculo principal
    # ──────────────────────────────────────────────────────────────────
    def _calcular(self):
        op    = self.combo_op.currentData()
        sobre = self.combo_grafo.currentData()   # 1, 2, o 0 = ambos

        if op == "dist":
            self._op_distancia()
        elif op == "dijkstra":
            self._op_dijkstra(sobre if sobre in (1, 2) else 1)
        elif op in ("min", "max"):
            if sobre == 0:
                # Aplicar a ambos
                self._op_kruskal(1, op)
                self._op_kruskal(2, op)
            else:
                self._op_kruskal(sobre, op)

    # ── Kruskal ───────────────────────────────────────────────────────
    def _op_kruskal(self, num: int, modo: str):
        ctrl = self.ctrl1 if num == 1 else self.ctrl2
        n    = ctrl._vertices
        raw  = ctrl._aristas

        if n == 0:
            DialogoClave(0, "Error", "mensaje", self,
                         f"Grafo {num} vacío.").exec(); return

        ramas, cuerdas = _kruskal(n, raw, maximo=(modo == "max"))

        if len(ramas) != n - 1:
            DialogoClave(0, "Advertencia", "mensaje", self,
                         f"Grafo {num}: no es conexo o no tiene n-1 aristas.").exec()

        etiq  = ctrl._etiquetas
        datos = ctrl.obtener_datos()

        # Resultado A → ramas
        aristas_r = [(raw[i][0], raw[i][1]) for i in ramas]
        pesos_r   = [raw[i][2] for i in ramas]
        self.vis_r1.titulo_label.setText(
            f"Árbol {'Máximo' if modo=='max' else 'Mínimo'} G{num} — Ramas"
        )
        self.vis_r1.set_grafo(n, aristas_r, etiq, pesos_r)
        self.vis_r1.set_colores(
            colores_aristas={i: "#3498db" if modo=="max" else "#f39c12"
                             for i in range(len(aristas_r))}
        )

        # Resultado B → cuerdas
        aristas_c = [(raw[i][0], raw[i][1]) for i in cuerdas]
        pesos_c   = [raw[i][2] for i in cuerdas]
        self.vis_r2.titulo_label.setText(f"Cuerdas G{num}")
        self.vis_r2.set_grafo(n, aristas_c, etiq, pesos_c)
        self.vis_r2.set_colores(
            colores_aristas={i: "#95a5a6" for i in range(len(aristas_c))}
        )

        # Info
        tipo  = "Máxima" if modo == "max" else "Mínima"
        peso_total = sum(raw[i][2] for i in ramas)
        ramas_str  = ", ".join(
            f"e{i+1}({etiq.get(raw[i][0],str(raw[i][0]+1))}–"
            f"{etiq.get(raw[i][1],str(raw[i][1]+1))} p={raw[i][2]})"
            for i in ramas
        )
        cuerdas_str = ", ".join(
            f"e{i+1}({etiq.get(raw[i][0],str(raw[i][0]+1))}–"
            f"{etiq.get(raw[i][1],str(raw[i][1]+1))})"
            for i in cuerdas
        ) or "∅"

        self.texto_info.setHtml(
            f"<b>Árbol de Expansión {tipo} — Grafo {num}</b><br><br>"
            f"<b>Vértices:</b> {n}<br>"
            f"<b>Rango (ramas):</b> {len(ramas)}<br>"
            f"<b>Nulidad (cuerdas):</b> {len(cuerdas)}<br>"
            f"<b>Peso total árbol:</b> {peso_total}<br><br>"
            f"<b>Ramas:</b><br>{ramas_str}<br><br>"
            f"<b>Cuerdas:</b><br>{cuerdas_str}"
        )

    # ── Distancia entre árboles ───────────────────────────────────────
    def _op_distancia(self):
        n1, raw1 = self.ctrl1._vertices, self.ctrl1._aristas
        n2, raw2 = self.ctrl2._vertices, self.ctrl2._aristas

        if n1 == 0 or n2 == 0:
            DialogoClave(0, "Error", "mensaje", self,
                         "Ambos grafos deben tener vértices.").exec(); return

        # Calcular árbol mínimo de cada uno
        ramas1, _ = _kruskal(n1, raw1, maximo=False)
        ramas2, _ = _kruskal(n2, raw2, maximo=False)

        if len(ramas1) != n1 - 1 or len(ramas2) != n2 - 1:
            DialogoClave(0, "Advertencia", "mensaje", self,
                         "Alguno de los grafos no es conexo. "
                         "Se calculará con las ramas disponibles.").exec()

        aristas_t1 = [raw1[i] for i in ramas1]
        aristas_t2 = [raw2[i] for i in ramas2]

        dist, solo1, solo2, comunes = _distancia_arboles(
            aristas_t1, self.ctrl1._etiquetas,
            aristas_t2, self.ctrl2._etiquetas,
        )

        # Visualizar T1 (Resultado A) con aristas solo-en-T1 resaltadas
        etiq1 = self.ctrl1._etiquetas
        etiq2 = self.ctrl2._etiquetas

        aristas_vis1 = [(u, v) for u, v, _ in aristas_t1]
        pesos_vis1   = [p for _, _, p in aristas_t1]
        colores1 = {}
        for i, (u, v, _) in enumerate(aristas_t1):
            clave = frozenset({etiq1.get(u, str(u+1)), etiq1.get(v, str(v+1))})
            colores1[i] = "#e74c3c" if clave in solo1 else "#27ae60"

        self.vis_r1.titulo_label.setText("Árbol Mínimo G1 (rojo=exclusivo)")
        self.vis_r1.set_grafo(n1, aristas_vis1, etiq1, pesos_vis1)
        self.vis_r1.set_colores(colores_aristas=colores1)

        # Visualizar T2 (Resultado B)
        aristas_vis2 = [(u, v) for u, v, _ in aristas_t2]
        pesos_vis2   = [p for _, _, p in aristas_t2]
        colores2 = {}
        for i, (u, v, _) in enumerate(aristas_t2):
            clave = frozenset({etiq2.get(u, str(u+1)), etiq2.get(v, str(v+1))})
            colores2[i] = "#e74c3c" if clave in solo2 else "#27ae60"

        self.vis_r2.titulo_label.setText("Árbol Mínimo G2 (rojo=exclusivo)")
        self.vis_r2.set_grafo(n2, aristas_vis2, etiq2, pesos_vis2)
        self.vis_r2.set_colores(colores_aristas=colores2)

        # Info
        solo1_str = ", ".join("{" + ", ".join(sorted(e)) + "}" for e in solo1) or "∅"
        solo2_str = ", ".join("{" + ", ".join(sorted(e)) + "}" for e in solo2) or "∅"
        com_str   = ", ".join("{" + ", ".join(sorted(e)) + "}" for e in comunes) or "∅"

        self.texto_info.setHtml(
            f"<b>Distancia entre Árboles Mínimos</b><br><br>"
            f"<b>d(T1, T2) = {dist}</b><br><br>"
            f"<i>(Aristas en verde = comunes, en rojo = exclusivas)</i><br><br>"
            f"<b>Aristas solo en T1:</b><br>{solo1_str}<br><br>"
            f"<b>Aristas solo en T2:</b><br>{solo2_str}<br><br>"
            f"<b>Aristas comunes:</b><br>{com_str}"
        )

    # ── Dijkstra ──────────────────────────────────────────────────────
    def _op_dijkstra(self, num: int):
        ctrl = self.ctrl1 if num == 1 else self.ctrl2
        vis  = self.vis1  if num == 1 else self.vis2
        n    = ctrl._vertices
        raw  = ctrl._aristas
        etiq = ctrl._etiquetas

        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, f"Grafo {num} vacío.").exec(); return

        origen  = self.combo_origen.currentData()
        destino = self.combo_destino.currentData()

        if origen is None or destino is None:
            DialogoClave(0, "Error", "mensaje", self,
                         "Selecciona origen y destino.").exec(); return

        dist, prev = _dijkstra(n, raw, origen)
        camino     = _reconstruir_camino(prev, destino)

        # Aristas del camino
        camino_aristas: set[int] = set()
        for k in range(len(camino) - 1):
            u, v = camino[k], camino[k+1]
            for i, (a, b, _) in enumerate(raw):
                if (a == u and b == v) or (a == v and b == u):
                    camino_aristas.add(i); break

        # Colorear sobre el visualizador del grafo original
        datos = ctrl.obtener_datos()
        # Usamos VisualizadorGrafoColoreable en vis_r1
        self.vis_r1.titulo_label.setText(f"Camino mínimo G{num}")
        self.vis_r1.set_grafo(
            n, datos["aristas"], etiq, datos["pesos"],
            colores_aristas={i: "#27ae60" for i in camino_aristas},
            colores_vertices={v: "#e74c3c" if v in (origen, destino) else "#4d9de0"
                              for v in range(n)},
        )
        # Resultado B: distancias a todos los vértices
        self.vis_r2.titulo_label.setText(f"Grafo G{num} (todas las dist.)")
        self.vis_r2.set_grafo(n, datos["aristas"], etiq, datos["pesos"])

        # Info
        INF = math.inf
        dist_str = "".join(
            f"  {etiq.get(origen,str(origen+1))} → "
            f"{etiq.get(v,str(v+1))}: "
            f"{'∞' if dist[v]==INF else dist[v]}<br>"
            for v in range(n)
        )
        if camino:
            cam_str = " → ".join(etiq.get(v, str(v+1)) for v in camino)
            d_val   = dist[destino]
            d_txt   = "∞" if d_val == INF else str(d_val)
        else:
            cam_str = "No hay camino"
            d_txt   = "∞"

        self.texto_info.setHtml(
            f"<b>Dijkstra — Grafo {num}</b><br><br>"
            f"<b>Origen:</b> {etiq.get(origen,str(origen+1))}<br>"
            f"<b>Destino:</b> {etiq.get(destino,str(destino+1))}<br>"
            f"<b>Camino:</b> {cam_str}<br>"
            f"<b>Distancia:</b> {d_txt}<br><br>"
            f"<b>Distancias desde {etiq.get(origen,str(origen+1))}:</b><br>"
            f"{dist_str}"
        )

    # ──────────────────────────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────────────────────────
    def _on_op_changed(self):
        op = self.combo_op.currentData()
        self.frame_dijkstra.setVisible(op == "dijkstra")
        # Distancia siempre usa ambos grafos
        if op == "dist":
            for i in range(self.combo_grafo.count()):
                if self.combo_grafo.itemData(i) == 0:
                    self.combo_grafo.setCurrentIndex(i)
            self.combo_grafo.setEnabled(False)
        else:
            self.combo_grafo.setEnabled(True)

    def _sincronizar_combos_dijkstra(self):
        """Llena los combos de origen/destino con los vértices del grafo seleccionado."""
        num  = self.combo_grafo.currentData() or 1
        ctrl = self.ctrl1 if num != 2 else self.ctrl2
        n    = ctrl._vertices
        etiq = ctrl._etiquetas
        for combo in (self.combo_origen, self.combo_destino):
            combo.clear()
            for i in range(n):
                combo.addItem(etiq.get(i, str(i+1)), i)

    def _actualizar_visual(self, num: int):
        ctrl = self.ctrl1 if num == 1 else self.ctrl2
        vis  = self.vis1  if num == 1 else self.vis2
        d    = ctrl.obtener_datos()
        vis.set_grafo(d["vertices"], d["aristas"], d["etiquetas"], d["pesos"])

    def _actualizar_combos(self, num: int):
        ctrl = self.ctrl1 if num == 1 else self.ctrl2
        cu   = self.combo_u1 if num == 1 else self.combo_u2
        cv   = self.combo_v1 if num == 1 else self.combo_v2
        n, etiq = ctrl._vertices, ctrl._etiquetas
        for combo in (cu, cv):
            combo.clear()
            for i in range(n):
                combo.addItem(etiq.get(i, str(i+1)), i)

    def _limpiar_resultados(self):
        self.vis_r1.set_grafo(0, [], {})
        self.vis_r2.set_grafo(0, [], {})
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
            f"border:none;border-radius:5px;padding:6px 10px;}}"
            f"QPushButton:hover {{opacity:0.85;}}"
        )

    @staticmethod
    def _lbl(text: str, color: str = "#003366") -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(f"font-weight:bold;color:{color};border:none;")
        return l

    @staticmethod
    def _sep() -> QFrame:
        s = QFrame(); s.setFrameShape(QFrame.HLine)
        s.setStyleSheet("color:#99ccff;"); return s

    @staticmethod
    def _input_style() -> str:
        return "background-color:white;border:1px solid #99ccff;border-radius:4px;"