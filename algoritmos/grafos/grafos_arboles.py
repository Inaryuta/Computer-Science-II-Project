"""
algoritmos/grafos/grafos_arboles.py
Operaciones con árboles de grafos:
  • Árbol de expansión mínima (Kruskal)
  • Árbol de expansión máxima (Kruskal invertido)
  • Distancia entre dos árboles (diferencia simétrica de aristas)
  • Centro / Bicentro
  • Radio
  • Cintura
"""
import math
from collections import deque
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
        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1
        return True

    ramas, cuerdas = [], []
    for p, u, v, i in items:
        if u == v:
            cuerdas.append(i)
        elif union(u, v):
            ramas.append(i)
        else:
            cuerdas.append(i)
    return ramas, cuerdas


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


# ---------- Centro, radio, cintura ----------
def _matriz_distancias(n: int, aristas: list) -> list[list[float]]:
    """Matriz de distancias mínimas (Floyd-Warshall) para grafos pequeños."""
    INF = float('inf')
    dist = [[INF]*n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, p in aristas:
        if u != v:
            w = p if p > 0 else 1
            dist[u][v] = min(dist[u][v], w)
            dist[v][u] = min(dist[v][u], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist


def _centro_bicentro(n: int, aristas: list) -> tuple[list[int], int]:
    """
    Calcula el centro (vértices con excentricidad mínima) y el radio.
    Retorna (centro_lista, radio).
    """
    if n == 0:
        return [], 0
    dist = _matriz_distancias(n, aristas)
    excentricidad = [max(dist[i]) for i in range(n)]
    radio = min(excentricidad)
    centro = [i for i, e in enumerate(excentricidad) if e == radio]
    return centro, radio


def _cintura(n: int, aristas: list) -> int:
    """Longitud del ciclo más corto (girth). Retorna INF si es acíclico."""
    if n == 0:
        return float('inf')
    INF = float('inf')
    # Grafo no dirigido, calcular ciclo más corto mediante BFS
    adj = [[] for _ in range(n)]
    for u, v, p in aristas:
        if u != v:
            adj[u].append(v)
            adj[v].append(u)
    mejor = INF
    # BFS desde cada vértice
    for s in range(n):
        dist = [-1]*n
        parent = [-1]*n
        dist[s] = 0
        q = deque([s])
        while q and mejor > 2:  # si ya tenemos ciclo de longitud 3 no puede ser menor
            u = q.popleft()
            for v in adj[u]:
                if v == parent[u]:
                    continue
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    q.append(v)
                else:
                    # Ciclo encontrado
                    ciclo = dist[u] + dist[v] + 1
                    if ciclo < mejor:
                        mejor = ciclo
    return mejor if mejor != INF else INF


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
        self.combo_op.addItem("Centro / Bicentro",        "centro")
        self.combo_op.addItem("Radio",                    "radio")
        self.combo_op.addItem("Cintura",          "cintura")
        self.combo_op.setStyleSheet(self._input_style())
        lay.addWidget(self.combo_op)

        # Sobre qué grafo aplicar (solo para operaciones que requieren uno)
        lay.addWidget(self._lbl("Aplicar sobre:", "#1b5e20"))
        self.combo_grafo = QComboBox()
        self.combo_grafo.addItem("Grafo 1", 1)
        self.combo_grafo.addItem("Grafo 2", 2)
        self.combo_grafo.addItem("Ambos (solo distancia)", 0)
        self.combo_grafo.setStyleSheet(self._input_style())
        lay.addWidget(self.combo_grafo)

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
        elif op in ("min", "max"):
            if sobre == 0:
                self._op_kruskal(1, op)
                self._op_kruskal(2, op)
            else:
                self._op_kruskal(sobre, op)
        elif op == "centro":
            self._op_centro(sobre if sobre in (1,2) else 1)
        elif op == "radio":
            self._op_radio(sobre if sobre in (1,2) else 1)
        elif op == "cintura":
            self._op_cintura(sobre if sobre in (1,2) else 1)

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

    # ── Centro / Bicentro ────────────────────────────────────────────
    def _op_centro(self, num: int):
        ctrl = self.ctrl1 if num == 1 else self.ctrl2
        n    = ctrl._vertices
        raw  = ctrl._aristas
        etiq = ctrl._etiquetas

        if n == 0:
            DialogoClave(0, "Error", "mensaje", self,
                         f"Grafo {num} vacío.").exec(); return

        centro, radio = _centro_bicentro(n, raw)
        if not centro:
            DialogoClave(0, "Error", "mensaje", self, "No se pudo calcular el centro.").exec(); return

        centro_str = ", ".join(etiq.get(v, str(v+1)) for v in centro)
        tipo_centro = "Bicentro" if len(centro) == 2 else "Centro"

        # Visualización: resaltar los vértices del centro en el grafo original
        datos = ctrl.obtener_datos()
        self.vis_r1.titulo_label.setText(f"{tipo_centro} - Grafo {num}")
        self.vis_r1.set_grafo(
            n, datos["aristas"], etiq, datos["pesos"],
            colores_vertices={v: "#e74c3c" for v in centro},
        )
        self.vis_r2.set_grafo(0, [], {})  # limpiar resultado B

        self.texto_info.setHtml(
            f"<b>Centro del Grafo {num}</b><br><br>"
            f"<b>{tipo_centro}:</b> {centro_str}<br>"
            f"<b>Radio:</b> {radio}<br>"
            f"<i>(Vértices resaltados en rojo)</i>"
        )

    # ── Radio ─────────────────────────────────────────────────────────
    def _op_radio(self, num: int):
        ctrl = self.ctrl1 if num == 1 else self.ctrl2
        n    = ctrl._vertices
        raw  = ctrl._aristas

        if n == 0:
            DialogoClave(0, "Error", "mensaje", self,
                         f"Grafo {num} vacío.").exec(); return

        _, radio = _centro_bicentro(n, raw)

        self.texto_info.setHtml(
            f"<b>Radio del Grafo {num}</b><br><br>"
            f"<b>Radio (excentricidad mínima):</b> {radio}<br>"
            f"<i>Para calcular el centro, use la operación 'Centro / Bicentro'.</i>"
        )
        # Opcional: se puede resaltar algo, pero solo mostramos el valor
        self.vis_r1.set_grafo(0, [], {})
        self.vis_r2.set_grafo(0, [], {})

    # ── Cintura (girth) ───────────────────────────────────────────────
    def _op_cintura(self, num: int):
        ctrl = self.ctrl1 if num == 1 else self.ctrl2
        n    = ctrl._vertices
        raw  = ctrl._aristas

        if n == 0:
            DialogoClave(0, "Error", "mensaje", self,
                         f"Grafo {num} vacío.").exec(); return

        girth = _cintura(n, raw)
        if girth == float('inf'):
            girth_str = "∞ (el grafo es acíclico)"
        else:
            girth_str = str(girth)

        self.texto_info.setHtml(
            f"<b>Cintura del Grafo {num}</b><br><br>"
            f"<b>Longitud del ciclo más corto:</b> {girth_str}<br>"
            f"<i>(Ciclo mínimo: {girth} aristas)</i>"
        )
        self.vis_r1.set_grafo(0, [], {})
        self.vis_r2.set_grafo(0, [], {})

    # ──────────────────────────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────────────────────────
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