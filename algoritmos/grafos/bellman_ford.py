import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTextEdit, QComboBox, QSpinBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from controladores.bellman_ford_controller import BellmanFordController
from controladores.visualizador_grafo import VisualizadorGrafoDirigido
from algoritmos.funcion_mod import DialogoClave


class BellmanFordWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos = volver_a_grafos
        self.volver_a_principal = volver_a_principal
        self.controller = BellmanFordController()

        self.setWindowTitle("Algoritmo de Bellman-Ford")
        self.setGeometry(200, 100, 1400, 750)
        self.setStyleSheet("background-color: #f0f8ff;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- Header ---
        header = QFrame()
        header.setStyleSheet("background-color: #cce6ff; border-radius: 10px;")
        header_layout = QHBoxLayout(header)
        btn_back = QPushButton("← Volver a Grafos")
        btn_back.setStyleSheet(self._button_style("#e6f2ff", "#003366"))
        btn_back.clicked.connect(self.cerrar_y_volver_a_grafos)
        btn_home = QPushButton("🏠 Inicio")
        btn_home.setStyleSheet(self._button_style("#e6f2ff", "#003366"))
        btn_home.clicked.connect(self.cerrar_y_volver_a_principal)
        header_layout.addWidget(btn_back)
        header_layout.addWidget(btn_home)
        titulo = QLabel("BELLMAN-FORD")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        header_layout.addWidget(titulo, alignment=Qt.AlignCenter)
        layout.addWidget(header)

        # --- Contenedor principal ---
        contenedor = QHBoxLayout()

        # --- Panel izquierdo ---
        panel_izq = QVBoxLayout()

        frame_controles = QFrame()
        frame_controles.setStyleSheet("background-color: #e6f2ff; border-radius: 8px; padding: 10px;")
        frame_layout = QVBoxLayout(frame_controles)

        # Fila: número de vértices
        fila1 = QHBoxLayout()
        fila1.addWidget(QLabel("Vértices:"))
        self.spin_vertices = QSpinBox()
        self.spin_vertices.setRange(1, 10)
        self.spin_vertices.setValue(4)
        self.spin_vertices.setStyleSheet(self._spinbox_style())
        fila1.addWidget(self.spin_vertices)
        btn_crear = QPushButton("Crear Grafo")
        btn_crear.setStyleSheet(self._button_style("#4d9de0", "white"))
        btn_crear.clicked.connect(self.crear_grafo)
        fila1.addWidget(btn_crear)
        frame_layout.addLayout(fila1)

        # Fila: agregar arista
        fila2 = QHBoxLayout()
        fila2.addWidget(QLabel("Origen:"))
        self.combo_arista_origen = QComboBox()           # FIX: renamed from combo_origen
        self.combo_arista_origen.setStyleSheet(self._combo_style())
        fila2.addWidget(self.combo_arista_origen)
        fila2.addWidget(QLabel("Destino:"))
        self.combo_arista_destino = QComboBox()          # FIX: renamed from combo_destino
        self.combo_arista_destino.setStyleSheet(self._combo_style())
        fila2.addWidget(self.combo_arista_destino)
        fila2.addWidget(QLabel("Peso:"))
        self.spin_peso = QSpinBox()
        self.spin_peso.setRange(-99, 99)
        self.spin_peso.setValue(1)
        self.spin_peso.setStyleSheet(self._spinbox_style())
        fila2.addWidget(self.spin_peso)
        btn_agregar = QPushButton("+ Arista")
        btn_agregar.setStyleSheet(self._button_style("#27ae60", "white"))
        btn_agregar.clicked.connect(self.agregar_arista)
        fila2.addWidget(btn_agregar)
        frame_layout.addLayout(fila2)

        # Fila: eliminar, guardar, cargar
        fila3 = QHBoxLayout()
        btn_eliminar = QPushButton("- Eliminar última arista")
        btn_eliminar.setStyleSheet(self._button_style("#e74c3c", "white"))
        btn_eliminar.clicked.connect(self.eliminar_arista)
        btn_guardar = QPushButton("Guardar Grafo")
        btn_guardar.setStyleSheet(self._button_style("#3498db", "white"))
        btn_guardar.clicked.connect(self.guardar_grafo)
        btn_cargar = QPushButton("Cargar Grafo")
        btn_cargar.setStyleSheet(self._button_style("#3498db", "white"))
        btn_cargar.clicked.connect(self.cargar_grafo)
        fila3.addWidget(btn_eliminar)
        fila3.addWidget(btn_guardar)
        fila3.addWidget(btn_cargar)
        frame_layout.addLayout(fila3)

        panel_izq.addWidget(frame_controles)

        # Frame de ejecución
        frame_ejecutar = QFrame()
        frame_ejecutar.setStyleSheet("background-color: #e6f2ff; border-radius: 8px; padding: 10px;")
        ejecutar_layout = QHBoxLayout(frame_ejecutar)
        ejecutar_layout.addWidget(QLabel("Origen para Bellman-Ford:"))
        self.combo_origen_algoritmo = QComboBox()
        self.combo_origen_algoritmo.setStyleSheet(self._combo_style())
        ejecutar_layout.addWidget(self.combo_origen_algoritmo)
        btn_ejecutar = QPushButton("▶ Ejecutar Bellman-Ford")
        btn_ejecutar.setStyleSheet(self._button_style("#2c3e50", "white"))
        btn_ejecutar.clicked.connect(self.ejecutar_algoritmo)
        ejecutar_layout.addWidget(btn_ejecutar)
        panel_izq.addWidget(frame_ejecutar)

        # Visualizador
        self.visualizador = VisualizadorGrafoDirigido("Grafo Dirigido", es_editable=False)
        self.visualizador.setFixedSize(500, 500)
        panel_izq.addWidget(self.visualizador)

        contenedor.addLayout(panel_izq, stretch=2)

        # --- Panel derecho ---
        panel_der = QVBoxLayout()
        panel_der.addWidget(QLabel("<b>Iteraciones del algoritmo:</b>"))
        self.texto_iteraciones = QTextEdit()
        self.texto_iteraciones.setReadOnly(True)
        self.texto_iteraciones.setStyleSheet(self._textedit_style())
        panel_der.addWidget(self.texto_iteraciones)

        panel_der.addWidget(QLabel("<b>Resultado final:</b>"))
        self.texto_resultado = QTextEdit()
        self.texto_resultado.setReadOnly(True)
        self.texto_resultado.setStyleSheet(self._textedit_style())
        panel_der.addWidget(self.texto_resultado)

        contenedor.addLayout(panel_der, stretch=1)
        layout.addLayout(contenedor)

        # FIX: conectar señal del controller al visualizador
        self.controller.grafo_cambiado.connect(self.actualizar_visualizador)

        self.actualizar_combos()

    # ── Estilos ──────────────────────────────────────────────────────
    def _button_style(self, bg, fg):
        return (f"QPushButton {{background-color:{bg};color:{fg};font-weight:bold;"
                f"border:none;border-radius:5px;padding:6px 12px;}}"
                f"QPushButton:hover {{background-color:{self._darken(bg)};}}")

    def _darken(self, c):
        return {"#4d9de0":"#3b7cb0","#27ae60":"#1e8449","#e74c3c":"#c0392b",
                "#3498db":"#2980b9","#95a5a6":"#7f8c8d","#e6f2ff":"#cce6ff",
                "#2c3e50":"#1a252f"}.get(c, c)

    def _combo_style(self):
        return ("QComboBox {background-color:white;border:2px solid #99ccff;"
                "border-radius:4px;padding:4px;color:#003366;min-width:70px;}"
                "QComboBox:hover {border:2px solid #1e6bb8;}"
                "QComboBox::drop-down {border:none;}")

    def _spinbox_style(self):
        return ("QSpinBox {background-color:white;border:2px solid #99ccff;"
                "border-radius:4px;padding:4px;color:#003366;}")

    def _textedit_style(self):
        return ("QTextEdit {background-color:white;border:2px solid #99ccff;"
                "border-radius:4px;font-family:monospace;color:#003366;padding:5px;}")

    # ── Navegación ───────────────────────────────────────────────────
    def cerrar_y_volver_a_grafos(self):
        self.close(); self.volver_a_grafos()

    def cerrar_y_volver_a_principal(self):
        self.close(); self.volver_a_principal()

    # ── Grafo ────────────────────────────────────────────────────────
    def crear_grafo(self):
        n = self.spin_vertices.value()
        self.controller.crear_grafo_vacio(n)
        self.actualizar_combos()
        # actualizar_visualizador ya se llama por señal grafo_cambiado
        DialogoClave(0, "Éxito", "mensaje", self, f"Grafo creado con {n} vértices.").exec()

    def actualizar_combos(self):
        n = self.controller.num_vertices
        for combo in (self.combo_arista_origen, self.combo_arista_destino,
                      self.combo_origen_algoritmo):
            combo.clear()
        for i in range(n):
            etiq = self.controller.etiquetas.get(i, str(i+1))
            self.combo_arista_origen.addItem(etiq, i)
            self.combo_arista_destino.addItem(etiq, i)
            self.combo_origen_algoritmo.addItem(etiq, i)

    def actualizar_visualizador(self):
        datos = self.controller.obtener_datos()
        self.visualizador.set_grafo(
            datos['vertices'], datos['aristas'],
            datos['etiquetas'], datos['pesos']
        )

    def agregar_arista(self):
        if self.controller.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea el grafo.").exec(); return
        u = self.combo_arista_origen.currentData()
        v = self.combo_arista_destino.currentData()
        peso = self.spin_peso.value()
        if u is None or v is None:
            return
        self.controller.agregar_arista(u, v, peso)
        etiq_u = self.controller.etiquetas.get(u, str(u+1))
        etiq_v = self.controller.etiquetas.get(v, str(v+1))
        DialogoClave(0, "Arista agregada", "mensaje", self,
                     f"Arista {etiq_u} → {etiq_v} (peso {peso}).").exec()

    def eliminar_arista(self):
        if self.controller.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay grafo.").exec(); return
        self.controller.eliminar_ultima_arista()
        DialogoClave(0, "Arista eliminada", "mensaje", self, "Se eliminó la última arista.").exec()

    def guardar_grafo(self):
        if self.controller.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay grafo para guardar.").exec(); return
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Grafo", "", "JSON (*.json)")
        if ruta:
            self.controller.guardar_grafo(ruta)
            DialogoClave(0, "Éxito", "mensaje", self, "Grafo guardado.").exec()

    def cargar_grafo(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar Grafo", "", "JSON (*.json)")
        if ruta:
            try:
                self.controller.cargar_grafo_desde_archivo(ruta)
                self.spin_vertices.setValue(self.controller.num_vertices)
                self.actualizar_combos()
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error al cargar: {e}").exec()

    # ── Algoritmo ────────────────────────────────────────────────────
    def ejecutar_algoritmo(self):
        if self.controller.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea o carga un grafo.").exec(); return
        if not self.controller.aristas:
            DialogoClave(0, "Error", "mensaje", self, "El grafo debe tener al menos una arista.").exec(); return
        origen = self.combo_origen_algoritmo.currentData()
        if origen is None:
            origen = 0
        resultado = self.controller.ejecutar_bellman(origen)
        self.mostrar_resultados(resultado, origen)

    def mostrar_resultados(self, resultado, origen):
        text_iter = ""
        for it in resultado['iteraciones']:
            text_iter += f"<b>Iteración {it['iteracion']}:</b><br>"
            text_iter += f"Distancias: {', '.join(it['distancias'])}<br>"
            if it['cambios']:
                text_iter += (f"<span style='color:#c0392b;'>"
                              f"Cambios: {', '.join(it['cambios'])}</span><br>")
            text_iter += "<br>"
        self.texto_iteraciones.setHtml(text_iter)

        if resultado['ciclo_negativo']:
            self.texto_resultado.setHtml(
                "<h3 style='color:#c0392b;'>⚠ Ciclo negativo detectado. No existe solución.</h3>"
            )
            return

        final = resultado['resultado_final']
        html = f"<h3>Caminos mínimos desde V{origen+1}</h3>"
        html += ("<table style='width:100%;border-collapse:collapse;'>"
                 "<tr style='background-color:#4d9de0;color:white;'>"
                 "<th>Vértice</th><th>Distancia</th><th>Camino</th></tr>")
        for i in range(self.controller.num_vertices):
            info = final[i]
            d = info['distancia']
            d_str = "∞" if d == float('inf') else str(d)
            html += (f"<tr><td style='border:1px solid #99ccff;padding:5px;'>V{i+1}</td>"
                     f"<td style='border:1px solid #99ccff;padding:5px;'>{d_str}</td>"
                     f"<td style='border:1px solid #99ccff;padding:5px;'>{info['camino']}</td></tr>")
        html += "</table>"
        self.texto_resultado.setHtml(html)