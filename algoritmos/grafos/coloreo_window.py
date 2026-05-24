from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QTextEdit, QFileDialog, QFrame,
    QComboBox, QScrollArea, QGridLayout, QInputDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from controladores.grafo_controller import (
    GrafoControllerColoreable, PALETA_COLORES, NOMBRES_COLORES,
)
from controladores.visualizador_grafo import VisualizadorGrafoColoreable
from algoritmos.funcion_mod import DialogoClave
from algoritmos.grafos.dialogo_arista import DialogoArista

# ================================================================== #
#  Algoritmos de coloreo                                              #
# ================================================================== #

def _greedy(n: int, adj: list) -> tuple[list[int], list[dict]]:
    """Coloreo voraz en orden natural 0 … n-1."""
    colores = [-1] * n
    pasos = []
    for v in range(n):
        usados = {colores[u] for u, _ in adj[v] if colores[u] != -1}
        c = 0
        while c in usados:
            c += 1
        colores[v] = c
        pasos.append({
            "vertice": v,
            "color_idx": c,
            "razon": f"Vecinos usan colores: {sorted(usados) if usados else '(ninguno)'}",
        })
    return colores, pasos


def _dsatur(n: int, adj: list) -> tuple[list[int], list[dict]]:
    """DSatur: elige el vértice no coloreado con mayor saturación en cada paso."""
    colores = [-1] * n
    saturacion = [0] * n
    grado = [len(adj[v]) for v in range(n)]
    coloreados: set[int] = set()
    pasos = []

    for _ in range(n):
        candidatos = [v for v in range(n) if v not in coloreados]
        v = max(candidatos, key=lambda x: (saturacion[x], grado[x]))

        usados = {colores[u] for u, _ in adj[v] if colores[u] != -1}
        c = 0
        while c in usados:
            c += 1
        colores[v] = c
        coloreados.add(v)

        # Actualizar saturación de vecinos
        for u, _ in adj[v]:
            if u not in coloreados:
                saturacion[u] = len({colores[w] for w, _ in adj[u] if colores[w] != -1})

        pasos.append({
            "vertice": v,
            "color_idx": c,
            "saturacion": saturacion[v],
            "razon": (
                f"Sat={saturacion[v]}, Grado={grado[v]}, "
                f"Vecinos usan colores: {sorted(usados) if usados else '(ninguno)'}"
            ),
        })

    return colores, pasos


# ================================================================== #
#  Ventana principal                                                  #
# ================================================================== #

class ColoreoWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos = volver_a_grafos
        self.volver_a_principal = volver_a_principal
        self.controller = GrafoControllerColoreable()

        self.setWindowTitle("Coloreo de Grafos")
        self.setGeometry(100, 50, 1400, 750)
        self.setStyleSheet("background-color: #f0f8ff;")

        self._build_ui()
        self.controller.grafo_cambiado.connect(self._actualizar_visualizador)

    # ---------------------------------------------------------------- #
    #  Construcción de la UI                                            #
    # ---------------------------------------------------------------- #

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(10, 10, 10, 10)

        root.addWidget(self._make_header())

        body = QHBoxLayout()
        body.setSpacing(15)

        # — Visualizador (izquierda) —
        self.visual = VisualizadorGrafoColoreable(
            "Grafo", es_editable=True, dirigido=False
        )
        self.visual.setFixedSize(500, 500)
        body.addWidget(self.visual, stretch=2)

        # — Panel de controles (derecha, con scroll) —
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        panel_widget = QWidget()
        panel_widget.setStyleSheet(
            "background-color: #e6f2ff; border-radius: 8px;"
        )
        self.panel_layout = QVBoxLayout(panel_widget)
        self.panel_layout.setSpacing(10)
        self.panel_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(panel_widget)
        body.addWidget(scroll, stretch=1)

        root.addLayout(body)
        self._build_panel()

    def _make_header(self) -> QFrame:
        header = QFrame()
        header.setStyleSheet("background-color: #cce6ff; border-radius: 10px;")
        hl = QHBoxLayout(header)

        btn_back = QPushButton("← Volver a Grafos")
        btn_back.setStyleSheet(self._btn_style("#e6f2ff", "#003366"))
        btn_back.clicked.connect(self._cerrar_grafos)

        btn_home = QPushButton("🏠 Inicio")
        btn_home.setStyleSheet(self._btn_style("#e6f2ff", "#003366"))
        btn_home.clicked.connect(self._cerrar_principal)

        titulo = QLabel("COLOREO DE GRAFOS")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")

        hl.addWidget(btn_back)
        hl.addWidget(btn_home)
        hl.addWidget(titulo, alignment=Qt.AlignCenter)
        return header

    def _build_panel(self):
        lay = self.panel_layout

        # ── Crear grafo ──────────────────────────────────────────────
        lay.addWidget(self._lbl("Número de vértices:"))
        self.spin_vertices = QSpinBox()
        self.spin_vertices.setRange(1, 15)
        self.spin_vertices.setValue(5)
        self.spin_vertices.setStyleSheet(
            "background-color: white; border: 2px solid #99ccff; border-radius: 4px;"
        )
        lay.addWidget(self.spin_vertices)

        btn_crear = QPushButton("Crear grafo")
        btn_crear.setStyleSheet(self._btn_style("#4d9de0", "white"))
        btn_crear.clicked.connect(self._crear_grafo)
        lay.addWidget(btn_crear)

        # ── Agregar arista ───────────────────────────────────────────
        lay.addWidget(self._separator())
        lay.addWidget(self._lbl("Agregar arista:"))

        fila_arista = QHBoxLayout()
        self.combo_u = QComboBox()
        self.combo_v = QComboBox()
        self.spin_peso = QSpinBox()
        self.spin_peso.setRange(1, 9999)
        self.spin_peso.setValue(1)
        for w in (self.combo_u, self.combo_v, self.spin_peso):
            w.setStyleSheet(
                "background-color: white; border: 2px solid #99ccff; border-radius: 4px;"
            )
        fila_arista.addWidget(QLabel("De:"))
        fila_arista.addWidget(self.combo_u)
        fila_arista.addWidget(QLabel("A:"))
        fila_arista.addWidget(self.combo_v)
        fila_arista.addWidget(QLabel("Peso:"))
        fila_arista.addWidget(self.spin_peso)
        lay.addLayout(fila_arista)

        btn_add = QPushButton("+ Arista")
        btn_add.setStyleSheet(self._btn_style("#27ae60", "white"))
        btn_add.clicked.connect(self._agregar_arista)
        lay.addWidget(btn_add)

        # ── Eliminar arista / vértice ────────────────────────────────
        btn_del_a = QPushButton("- Eliminar arista")
        btn_del_a.setStyleSheet(self._btn_style("#e74c3c", "white"))
        btn_del_a.clicked.connect(self._eliminar_arista)
        lay.addWidget(btn_del_a)

        btn_del_v = QPushButton("🗑 Eliminar vértice")
        btn_del_v.setStyleSheet(self._btn_style("#c0392b", "white"))
        btn_del_v.clicked.connect(self._eliminar_vertice)
        lay.addWidget(btn_del_v)

        # ── Guardar / Cargar ─────────────────────────────────────────
        lay.addWidget(self._separator())
        btn_save = QPushButton("💾 Guardar grafo")
        btn_save.setStyleSheet(self._btn_style("#3498db", "white"))
        btn_save.clicked.connect(self._guardar_grafo)
        lay.addWidget(btn_save)

        btn_load = QPushButton("📂 Cargar grafo")
        btn_load.setStyleSheet(self._btn_style("#3498db", "white"))
        btn_load.clicked.connect(self._cargar_grafo)
        lay.addWidget(btn_load)

        # ── Algoritmo ────────────────────────────────────────────────
        lay.addWidget(self._separator())
        lay.addWidget(self._lbl("Algoritmo de coloreo:"))
        self.combo_algo = QComboBox()
        self.combo_algo.addItem("Greedy (orden natural)", "greedy")
        self.combo_algo.addItem("DSatur (por saturación)", "dsatur")
        self.combo_algo.setStyleSheet(
            "background-color: white; border: 2px solid #99ccff; border-radius: 4px;"
        )
        lay.addWidget(self.combo_algo)

        btn_run = QPushButton("▶ Ejecutar coloreo")
        btn_run.setStyleSheet(self._btn_style("#2c3e50", "white"))
        btn_run.clicked.connect(self._ejecutar_coloreo)
        lay.addWidget(btn_run)

        btn_reset = QPushButton("↺ Resetear colores")
        btn_reset.setStyleSheet(self._btn_style("#7f8c8d", "white"))
        btn_reset.clicked.connect(self._resetear_colores)
        lay.addWidget(btn_reset)

        # ── Número cromático ─────────────────────────────────────────
        self.lbl_cromatico = QLabel("Número cromático: —")
        self.lbl_cromatico.setAlignment(Qt.AlignCenter)
        self.lbl_cromatico.setStyleSheet(
            "font-weight: bold; color: #003366; font-size: 14px;"
            "background-color: white; border: 2px solid #99ccff;"
            "border-radius: 6px; padding: 6px;"
        )
        lay.addWidget(self.lbl_cromatico)

        # ── Leyenda de colores ───────────────────────────────────────
        lay.addWidget(self._lbl("Leyenda:"))
        self.frame_leyenda = QFrame()
        self.frame_leyenda.setStyleSheet(
            "background-color: white; border: 1px solid #99ccff; border-radius: 6px;"
        )
        self.layout_leyenda = QGridLayout(self.frame_leyenda)
        self.layout_leyenda.setContentsMargins(6, 6, 6, 6)
        lay.addWidget(self.frame_leyenda)

        # ── Pasos del algoritmo ──────────────────────────────────────
        lay.addWidget(self._lbl("Pasos del algoritmo:"))
        self.texto_pasos = QTextEdit()
        self.texto_pasos.setReadOnly(True)
        self.texto_pasos.setMinimumHeight(200)
        self.texto_pasos.setStyleSheet(
            "background-color: white; font-family: monospace; font-size: 11px;"
            "border: 2px solid #99ccff; border-radius: 4px;"
        )
        lay.addWidget(self.texto_pasos)

    # ---------------------------------------------------------------- #
    #  Acciones del usuario                                             #
    # ---------------------------------------------------------------- #

    def _crear_grafo(self):
        n = self.spin_vertices.value()
        self.controller.set_vertices(n)
        self._actualizar_combos()
        self.texto_pasos.clear()
        self.lbl_cromatico.setText("Número cromático: —")
        self._limpiar_leyenda()

    def _agregar_arista(self):
        n = self.controller._vertices
        if n < 1:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea el grafo.").exec()
            return
        u = self.combo_u.currentData()
        v = self.combo_v.currentData()
        peso = self.spin_peso.value()
        if u is None or v is None:
            return
        self.controller.agregar_arista(u, v, peso)
        eu = self.controller._etiquetas.get(u, str(u + 1))
        ev = self.controller._etiquetas.get(v, str(v + 1))
        DialogoClave(
            0, "Arista agregada", "mensaje", self,
            f"Arista ({eu} ↔ {ev}) peso {peso} agregada."
        ).exec()

    def _eliminar_arista(self):
        datos = self.controller.obtener_datos()
        aristas = datos["aristas"]
        etiq = datos["etiquetas"]
        if not aristas:
            DialogoClave(0, "Info", "mensaje", self, "No hay aristas para eliminar.").exec()
            return
        opciones = [
            f"{etiq.get(u, u+1)} — {etiq.get(v, v+1)}"
            for (u, v) in aristas
        ]
        sel, ok = QInputDialog.getItem(
            self, "Eliminar arista", "Selecciona la arista:", opciones, 0, False
        )
        if ok:
            idx = opciones.index(sel)
            u, v = aristas[idx]
            self.controller.eliminar_arista(u, v, indice=idx)

    def _eliminar_vertice(self):
        n = self.controller._vertices
        if n == 0:
            return
        etiq = self.controller._etiquetas
        opciones = [etiq.get(i, str(i + 1)) for i in range(n)]
        sel, ok = QInputDialog.getItem(
            self, "Eliminar vértice", "Selecciona el vértice:", opciones, 0, False
        )
        if ok:
            idx = opciones.index(sel)
            self.controller.eliminar_vertice(idx)
            self._actualizar_combos()

    def _guardar_grafo(self):
        if self.controller._vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay grafo para guardar.").exec()
            return
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Grafo", "", "JSON (*.json)")
        if ruta:
            try:
                self.controller.guardar_json(ruta)
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo guardado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {e}").exec()

    def _cargar_grafo(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar Grafo", "", "JSON (*.json)")
        if ruta:
            try:
                self.controller.cargar_json(ruta)
                self.spin_vertices.setValue(self.controller._vertices)
                self._actualizar_combos()
                self.texto_pasos.clear()
                self.lbl_cromatico.setText("Número cromático: —")
                self._limpiar_leyenda()
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error: {e}").exec()

    def _ejecutar_coloreo(self):
        n = self.controller._vertices
        if n == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec()
            return

        adj = self.controller.lista_adyacencia()
        algo = self.combo_algo.currentData()

        if algo == "greedy":
            colores_idx, pasos = _greedy(n, adj)
        else:
            colores_idx, pasos = _dsatur(n, adj)

        # Mapear índice de color → hex
        coloreo = {
            v: PALETA_COLORES[c % len(PALETA_COLORES)]
            for v, c in enumerate(colores_idx)
        }
        self.controller.aplicar_coloreo(coloreo)

        nc = self.controller.numero_cromatico
        self.lbl_cromatico.setText(
            f"Número cromático: {nc} color{'es' if nc != 1 else ''}"
        )
        self._actualizar_leyenda(colores_idx)
        self._mostrar_pasos(pasos)

    def _resetear_colores(self):
        self.controller.resetear_colores()
        self.lbl_cromatico.setText("Número cromático: —")
        self._limpiar_leyenda()
        self.texto_pasos.clear()

    # ---------------------------------------------------------------- #
    #  Helpers de UI                                                    #
    # ---------------------------------------------------------------- #

    def _actualizar_visualizador(self):
        datos = self.controller.obtener_datos()
        self.visual.set_grafo(
            num_vertices=datos["vertices"],
            aristas=datos["aristas"],
            etiquetas=datos["etiquetas"],
            pesos=datos["pesos"],
            colores_vertices=self.controller._colores_vertices,
            colores_aristas=self.controller._colores_aristas,
        )

    def _actualizar_combos(self):
        n = self.controller._vertices
        etiq = self.controller._etiquetas
        for combo in (self.combo_u, self.combo_v):
            combo.clear()
            for i in range(n):
                combo.addItem(etiq.get(i, str(i + 1)), i)

    def _mostrar_pasos(self, pasos: list[dict]):
        self.texto_pasos.clear()
        etiq = self.controller._etiquetas
        lines = []
        for i, p in enumerate(pasos, 1):
            v = p["vertice"]
            c = p["color_idx"]
            nombre = NOMBRES_COLORES[c % len(NOMBRES_COLORES)]
            label_v = etiq.get(v, str(v + 1))
            lines.append(f"Paso {i}: Vértice {label_v}  →  Color {c + 1} ({nombre})")
            lines.append(f"         {p['razon']}")
            lines.append("")
        self.texto_pasos.setText("\n".join(lines))

    def _actualizar_leyenda(self, colores_idx: list[int]):
        self._limpiar_leyenda()
        for fila, c in enumerate(sorted(set(colores_idx))):
            hex_c = PALETA_COLORES[c % len(PALETA_COLORES)]
            nombre = NOMBRES_COLORES[c % len(NOMBRES_COLORES)]
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {hex_c}; font-size: 22px;")
            lbl = QLabel(f"Color {c + 1}: {nombre}")
            lbl.setStyleSheet("color: #003366;")
            self.layout_leyenda.addWidget(dot, fila, 0)
            self.layout_leyenda.addWidget(lbl, fila, 1)

    def _limpiar_leyenda(self):
        while self.layout_leyenda.count():
            child = self.layout_leyenda.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _cerrar_grafos(self):
        self.close()
        self.volver_a_grafos()

    def _cerrar_principal(self):
        self.close()
        self.volver_a_principal()

    # ---------------------------------------------------------------- #
    #  Estilos                                                          #
    # ---------------------------------------------------------------- #

    @staticmethod
    def _btn_style(bg: str, fg: str) -> str:
        return (
            f"QPushButton {{"
            f"  background-color: {bg}; color: {fg};"
            f"  font-weight: bold; border: none;"
            f"  border-radius: 5px; padding: 8px 12px;"
            f"}}"
            f"QPushButton:hover {{ opacity: 0.85; }}"
        )

    @staticmethod
    def _lbl(text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet("font-weight: bold; color: #003366;")
        return l

    @staticmethod
    def _separator() -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #99ccff;")
        return sep