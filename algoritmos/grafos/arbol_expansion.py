# algoritmos/grafos/arbol_expansion.py
import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QFrame, QFileDialog, QComboBox,
    QScrollArea, QTextEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from controladores.grafo_controller import GrafoController
from controladores.visualizador_grafo import VisualizadorGrafo
from controladores.visualizador_grafo import VisualizadorGrafoColoreable  # asumiendo que existe
from algoritmos.grafos.dialogo_arista import DialogoArista
from algoritmos.funcion_mod import DialogoClave


# ══════════════════════════════════════════════════════════════════════
#  Algoritmo de Kruskal (árbol de expansión mínima)
# ══════════════════════════════════════════════════════════════════════
def kruskal(n: int, aristas: list[tuple]) -> tuple[list[int], list[int]]:
    """Devuelve (ramas, cuerdas) donde ramas son índices de aristas del árbol mínimo."""
    if n == 0:
        return [], []

    aristas_con_idx = [(peso, u, v, idx) for idx, (u, v, peso) in enumerate(aristas)]
    aristas_con_idx.sort(key=lambda x: x[0])

    parent = list(range(n))
    rank = [0] * n

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

    ramas = []
    cuerdas = []

    for peso, u, v, idx in aristas_con_idx:
        if u == v:
            cuerdas.append(idx)
        elif union(u, v):
            ramas.append(idx)
        else:
            cuerdas.append(idx)

    return ramas, cuerdas


# ══════════════════════════════════════════════════════════════════════
#  Ventana principal
# ══════════════════════════════════════════════════════════════════════
class ArbolExpansionWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos = volver_a_grafos
        self.volver_a_principal = volver_a_principal

        self.controller = GrafoController()
        self._ramas: list[int] = []
        self._cuerdas: list[int] = []

        self.setWindowTitle("Árbol de Expansión Mínima")
        self.setGeometry(100, 50, 1500, 850)
        self.setStyleSheet("background-color: #f0f8ff;")

        self._build_ui()
        self.controller.grafo_cambiado.connect(self._actualizar_visual_original)

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

        # ── Tres visualizadores ────────────────────────────────────────
        vis_layout = QHBoxLayout()
        vis_layout.setSpacing(15)

        self.visual_original = VisualizadorGrafo("Grafo Original", es_editable=True)
        self.visual_original.setFixedSize(450, 450)
        vis_layout.addWidget(self.visual_original)

        self.visual_ramas = VisualizadorGrafoColoreable("Árbol de Expansión (Ramas)", es_editable=False)
        self.visual_ramas.setFixedSize(450, 450)
        vis_layout.addWidget(self.visual_ramas)

        self.visual_cuerdas = VisualizadorGrafoColoreable("Cuerdas", es_editable=False)
        self.visual_cuerdas.setFixedSize(450, 450)
        vis_layout.addWidget(self.visual_cuerdas)

        root.addLayout(vis_layout)

        # ── Panel inferior (controles + info) ─────────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(12)

        # Panel de controles
        controles = QFrame()
        controles.setStyleSheet("background-color: #e6f2ff; border-radius: 8px;")
        controles_layout = QVBoxLayout(controles)
        controles_layout.setSpacing(8)
        controles_layout.setAlignment(Qt.AlignTop)

        controles_layout.addWidget(self._lbl("Número de vértices:"))
        self.spin_v = QSpinBox()
        self.spin_v.setRange(1, 14)
        self.spin_v.setValue(5)
        self.spin_v.setStyleSheet(self._input_style())
        controles_layout.addWidget(self.spin_v)
        b = QPushButton("Crear grafo")
        b.setStyleSheet(self._btn("#4d9de0", "white"))
        b.clicked.connect(self._crear_grafo)
        controles_layout.addWidget(b)

        controles_layout.addWidget(self._sep())
        controles_layout.addWidget(self._lbl("Agregar arista:"))
        row = QHBoxLayout()
        self.combo_u = QComboBox(); self.combo_u.setStyleSheet(self._input_style())
        self.combo_v = QComboBox(); self.combo_v.setStyleSheet(self._input_style())
        self.spin_peso = QSpinBox()
        self.spin_peso.setRange(0, 9999)
        self.spin_peso.setValue(1)
        self.spin_peso.setStyleSheet(self._input_style())
        row.addWidget(QLabel("De:")); row.addWidget(self.combo_u)
        row.addWidget(QLabel("A:"));  row.addWidget(self.combo_v)
        row.addWidget(QLabel("Peso:")); row.addWidget(self.spin_peso)
        controles_layout.addLayout(row)
        ba = QPushButton("+ Arista")
        ba.setStyleSheet(self._btn("#27ae60", "white"))
        ba.clicked.connect(self._agregar_arista)
        controles_layout.addWidget(ba)
        be = QPushButton("- Eliminar arista")
        be.setStyleSheet(self._btn("#e74c3c", "white"))
        be.clicked.connect(self._eliminar_arista)
        controles_layout.addWidget(be)

        controles_layout.addWidget(self._sep())
        row2 = QHBoxLayout()
        bs = QPushButton("💾 Guardar"); bs.setStyleSheet(self._btn("#3498db", "white"))
        bc = QPushButton("📂 Cargar");  bc.setStyleSheet(self._btn("#3498db", "white"))
        bs.clicked.connect(self._guardar); bc.clicked.connect(self._cargar)
        row2.addWidget(bs); row2.addWidget(bc)
        controles_layout.addLayout(row2)

        controles_layout.addWidget(self._sep())
        br = QPushButton("▶ Calcular árbol de expansión mínima")
        br.setStyleSheet(self._btn("#2c3e50", "white"))
        br.clicked.connect(self._calcular)
        controles_layout.addWidget(br)

        bottom.addWidget(controles, stretch=1)

        # Panel de información
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 8px;")
        info_layout = QVBoxLayout(info_frame)
        lbl_titulo = QLabel("Información del árbol")
        lbl_titulo.setStyleSheet("font-weight: bold; color: #003366; font-size: 13px; padding: 4px;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(lbl_titulo)

        self.texto_info = QTextEdit()
        self.texto_info.setReadOnly(True)
        self.texto_info.setMinimumHeight(250)
        self.texto_info.setStyleSheet("font-family: monospace; font-size: 12px; border: none; padding: 4px;")
        info_layout.addWidget(self.texto_info)

        bottom.addWidget(info_frame, stretch=1)

        root.addLayout(bottom)

        self._actualizar_combos()

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
        titulo = QLabel("ÁRBOL DE EXPANSIÓN MÍNIMA (KRUSKAL)")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        hl.addWidget(b1); hl.addWidget(b2)
        hl.addWidget(titulo, alignment=Qt.AlignCenter)
        return h

    # ──────────────────────────────────────────────────────────────────
    #  Acciones
    # ──────────────────────────────────────────────────────────────────
    def _crear_grafo(self):
        n = self.spin_v.value()
        self.controller.set_vertices(n)
        self._actualizar_combos()
        self._reset_visualizaciones()
        self._actualizar_visual_original()
        self._limpiar_info()

    def _agregar_arista(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea el grafo.").exec()
            return
        u = self.combo_u.currentData()
        v = self.combo_v.currentData()
        peso = self.spin_peso.value()
        if u is None or v is None:
            return
        if u == v:
            DialogoClave(0, "Error", "mensaje", self, "No se permiten bucles.").exec()
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
                self._reset_visualizaciones()
                self._actualizar_visual_original()
                self._limpiar_info()
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {e}").exec()

    def _calcular(self):
        n = self.controller._vertices
        aristas = self.controller._aristas

        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec()
            return
        if len(aristas) < n - 1:
            DialogoClave(0, "Error", "mensaje", self, "El grafo debe tener al menos n-1 aristas.").exec()
            return

        ramas, cuerdas = kruskal(n, aristas)

        if len(ramas) != n - 1:
            DialogoClave(0, "Error", "mensaje", self, "El grafo no es conexo.").exec()
            return

        self._ramas = ramas
        self._cuerdas = cuerdas

        self._mostrar_ramas()
        self._mostrar_cuerdas()
        self._actualizar_info()

    def _mostrar_ramas(self):
        datos = self.controller.obtener_datos()
        n = datos["vertices"]
        etiq = datos["etiquetas"]
        aristas_completas = self.controller._aristas  # (u, v, peso)
        aristas_ramas = [(aristas_completas[ei][0], aristas_completas[ei][1]) for ei in self._ramas]
        pesos_ramas = [aristas_completas[ei][2] for ei in self._ramas]

        # Colorear todas las aristas de las ramas en naranja
        colores_aristas = {i: "#f39c12" for i in range(len(aristas_ramas))}

        self.visual_ramas.set_grafo(n, aristas_ramas, etiq, pesos_ramas)
        if hasattr(self.visual_ramas, 'set_colores'):
            self.visual_ramas.set_colores(colores_aristas=colores_aristas)

    def _mostrar_cuerdas(self):
        datos = self.controller.obtener_datos()
        n = datos["vertices"]
        etiq = datos["etiquetas"]
        aristas_completas = self.controller._aristas
        aristas_cuerdas = [(aristas_completas[ei][0], aristas_completas[ei][1]) for ei in self._cuerdas]
        pesos_cuerdas = [aristas_completas[ei][2] for ei in self._cuerdas]

        # Colorear todas las aristas de las cuerdas en verde
        colores_aristas = {i: "#2ecc71" for i in range(len(aristas_cuerdas))}

        self.visual_cuerdas.set_grafo(n, aristas_cuerdas, etiq, pesos_cuerdas)
        if hasattr(self.visual_cuerdas, 'set_colores'):
            self.visual_cuerdas.set_colores(colores_aristas=colores_aristas)

    def _actualizar_info(self):
        n = self.controller._vertices
        m = len(self.controller._aristas)
        ramas = len(self._ramas)
        cuerdas = len(self._cuerdas)

        html = f"""
        <b>Rango (ramas) =</b> {ramas}<br>
        <b>Nulidad (cuerdas) =</b> {cuerdas}<br>
        <br>
        <b>Detalles:</b><br>
        Vértices: {n}<br>
        Aristas totales: {m}<br>
        Ramas (árbol): {ramas}<br>
        Cuerdas (restantes): {cuerdas}<br>
        """
        aristas_raw = self.controller._aristas
        etiq = self.controller._etiquetas
        ramas_lista = [f"e{ei+1}({etiq.get(u, u+1)}–{etiq.get(v, v+1)})" for ei in self._ramas for (u, v, _) in [aristas_raw[ei]]]
        if ramas_lista:
            html += f"<br><b>Ramas:</b> {', '.join(ramas_lista)}"
        cuerdas_lista = [f"e{ei+1}({etiq.get(u, u+1)}–{etiq.get(v, v+1)})" for ei in self._cuerdas for (u, v, _) in [aristas_raw[ei]]]
        if cuerdas_lista:
            html += f"<br><b>Cuerdas:</b> {', '.join(cuerdas_lista)}"
        self.texto_info.setHtml(html)

    # ──────────────────────────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────────────────────────
    def _actualizar_visual_original(self):
        datos = self.controller.obtener_datos()
        self.visual_original.set_grafo(datos["vertices"], datos["aristas"], datos["etiquetas"], datos["pesos"])

    def _actualizar_combos(self):
        n = self.controller._vertices
        etiq = self.controller._etiquetas
        for combo in (self.combo_u, self.combo_v):
            combo.clear()
            for i in range(n):
                combo.addItem(etiq.get(i, str(i+1)), i)

    def _reset_visualizaciones(self):
        self.visual_ramas.set_grafo(0, [], {})
        self.visual_cuerdas.set_grafo(0, [], {})
        self._ramas = []
        self._cuerdas = []

    def _limpiar_info(self):
        self.texto_info.clear()

    def _cerrar_grafos(self):
        self.close(); self.volver_a_grafos()

    def _cerrar_principal(self):
        self.close(); self.volver_a_principal()

    # ──────────────────────────────────────────────────────────────────
    #  Estilos (igual que antes)
    # ──────────────────────────────────────────────────────────────────
    @staticmethod
    def _btn(bg: str, fg: str) -> str:
        return f"QPushButton {{background-color:{bg};color:{fg};font-weight:bold;border:none;border-radius:5px;padding:8px 12px;}} QPushButton:hover {{opacity:0.85;}}"

    @staticmethod
    def _lbl(text: str) -> QLabel:
        l = QLabel(text); l.setStyleSheet("font-weight:bold;color:#003366;"); return l

    @staticmethod
    def _sep() -> QFrame:
        s = QFrame(); s.setFrameShape(QFrame.HLine); s.setStyleSheet("color:#99ccff;"); return s

    @staticmethod
    def _input_style() -> str:
        return "background-color:white;border:2px solid #99ccff;border-radius:4px;"