# algoritmos/grafos/floyd.py
import json
import math
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QGridLayout, QSpinBox,
    QFileDialog, QComboBox, QLineEdit, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from controladores.visualizador_grafo_dirigido import VisualizadorGrafoDirigido
from algoritmos.funcion_mod import DialogoClave


# ======================= DIÁLOGOS PERSONALIZADOS =======================
class DialogoAgregarArista(QDialog):
    def __init__(self, num_vertices, etiquetas, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Arista")
        self.setModal(True)
        self.resize(300, 200)
        self.setStyleSheet("background-color: #f0f8ff;")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Vértice Origen:"))
        self.combo_origen = QComboBox()
        for i in range(num_vertices):
            etiqueta = etiquetas.get(i, str(i+1))
            self.combo_origen.addItem(etiqueta, i)
        self.combo_origen.setStyleSheet(self._combo_style())
        layout.addWidget(self.combo_origen)

        layout.addWidget(QLabel("Vértice Destino:"))
        self.combo_destino = QComboBox()
        for i in range(num_vertices):
            etiqueta = etiquetas.get(i, str(i+1))
            self.combo_destino.addItem(etiqueta, i)
        self.combo_destino.setStyleSheet(self._combo_style())
        layout.addWidget(self.combo_destino)

        layout.addWidget(QLabel("Ponderación (opcional):"))
        self.input_ponderacion = QLineEdit()
        self.input_ponderacion.setPlaceholderText("Dejar vacío = 1")
        self.input_ponderacion.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 4px; padding: 5px;")
        layout.addWidget(self.input_ponderacion)

        btn_layout = QHBoxLayout()
        btn_aceptar = QPushButton("Agregar")
        btn_aceptar.setStyleSheet(self._button_style("#4d9de0", "white"))
        btn_aceptar.clicked.connect(self.accept)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(self._button_style("#e74c3c", "white"))
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_aceptar)
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)

    def _combo_style(self):
        return """
            QComboBox {
                background-color: white;
                border: 2px solid #99ccff;
                border-radius: 4px;
                padding: 4px;
                color: #003366;
            }
        """

    def _button_style(self, bg_color, text_color):
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(bg_color)};
            }}
        """

    def _darken_color(self, color):
        return {"#4d9de0": "#3b7cb0", "#e74c3c": "#c0392b"}.get(color, color)

    def obtener_datos(self):
        origen = self.combo_origen.currentData()
        destino = self.combo_destino.currentData()
        ponderacion = self.input_ponderacion.text().strip()
        return origen, destino, ponderacion


class DialogoEliminarArista(QDialog):
    def __init__(self, aristas, etiquetas, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Eliminar Arista")
        self.setModal(True)
        self.resize(300, 150)
        self.setStyleSheet("background-color: #f0f8ff;")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Selecciona la arista a eliminar:"))

        self.combo_aristas = QComboBox()
        for arista in aristas:
            origen, destino = arista
            etiq_o = etiquetas.get(origen, str(origen+1))
            etiq_d = etiquetas.get(destino, str(destino+1))
            self.combo_aristas.addItem(f"{etiq_o} → {etiq_d}", arista)
        self.combo_aristas.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 2px solid #99ccff;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        layout.addWidget(self.combo_aristas)

        btn_layout = QHBoxLayout()
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet(self._button_style("#e74c3c", "white"))
        btn_eliminar.clicked.connect(self.accept)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(self._button_style("#95a5a6", "white"))
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_eliminar)
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)

    def _button_style(self, bg_color, text_color):
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(bg_color)};
            }}
        """

    def _darken_color(self, color):
        return {"#e74c3c": "#c0392b", "#95a5a6": "#7f8c8d"}.get(color, color)

    def obtener_arista(self):
        return self.combo_aristas.currentData()


# ========================= MODELO INTERNO =========================
class ModeloGrafoFloyd:
    def __init__(self):
        self.num_vertices = 0
        self.aristas = []          # lista de tuplas (origen, destino)
        self.etiquetas = {}        # {índice: etiqueta}
        self.ponderaciones = {}     # {(origen, destino): peso (float)}
        self.ponderaciones_lista = []  # para el visualizador

    def crear_grafo(self, num_vertices):
        self.num_vertices = num_vertices
        self.aristas = []
        self.etiquetas = {i: str(i+1) for i in range(num_vertices)}
        self.ponderaciones = {}

    def agregar_arista(self, origen, destino, ponderacion=""):
        if origen < 0 or origen >= self.num_vertices or destino < 0 or destino >= self.num_vertices:
            return False
        if (origen, destino) in self.aristas:
            return False
        self.aristas.append((origen, destino))
        if ponderacion:
            try:
                self.ponderaciones[(origen, destino)] = float(ponderacion)
            except ValueError:
                self.ponderaciones[(origen, destino)] = 1.0
        else:
            self.ponderaciones[(origen, destino)] = 1.0
        return True

    def eliminar_arista(self, arista):
        if arista in self.aristas:
            self.aristas.remove(arista)
            if arista in self.ponderaciones:
                del self.ponderaciones[arista]
            return True
        return False

    def eliminar_todas_aristas(self):
        self.aristas = []
        self.ponderaciones = {}

    def obtener_datos_visualizador(self):
        # Convertir ponderaciones a lista en el mismo orden que aristas
        pesos_lista = []
        for arista in self.aristas:
            peso = self.ponderaciones.get(arista, 1.0)
            # Mostrar como entero si es entero
            if peso == int(peso):
                pesos_lista.append(str(int(peso)))
            else:
                pesos_lista.append(str(peso))
        return {
            'vertices': self.num_vertices,
            'aristas': self.aristas,
            'etiquetas': self.etiquetas,
            'pesos': pesos_lista
        }

    def guardar_grafo(self, ruta):
        datos = {
            'num_vertices': self.num_vertices,
            'aristas': self.aristas,
            'etiquetas': self.etiquetas,
            'ponderaciones': {f"{k[0]},{k[1]}": v for k, v in self.ponderaciones.items()}
        }
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4)

    def cargar_grafo(self, ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        self.num_vertices = datos['num_vertices']
        self.aristas = [tuple(a) for a in datos['aristas']]
        self.etiquetas = {int(k): v for k, v in datos['etiquetas'].items()}
        pond = datos.get('ponderaciones', {})
        self.ponderaciones = {}
        for k, v in pond.items():
            u, vtx = map(int, k.split(','))
            self.ponderaciones[(u, vtx)] = v


# ========================= VENTANA PRINCIPAL =========================
class FloydWindow(QMainWindow):
    def __init__(self, volver_a_grafos, volver_a_principal):
        super().__init__()
        self.volver_a_grafos = volver_a_grafos
        self.volver_a_principal = volver_a_principal

        self.modelo = ModeloGrafoFloyd()

        self.setWindowTitle("Algoritmo de Floyd")
        self.setGeometry(150, 80, 1300, 750)
        self.setStyleSheet("background-color: #f0f8ff;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # ----- Header -----
        header = QFrame()
        header.setStyleSheet("background-color: #cce6ff; border-radius: 10px;")
        header_layout = QHBoxLayout(header)

        btn_back = QPushButton("← Volver a Grafos")
        btn_back.setStyleSheet(self._button_style("#e6f2ff", "#003366"))
        btn_back.clicked.connect(self.cerrar_y_volver_a_grafos)

        btn_home = QPushButton("🏠 Inicio")
        btn_home.setStyleSheet(self._button_style("#e6f2ff", "#003366"))
        btn_home.clicked.connect(self.cerrar_y_volver_a_principal)

        titulo = QLabel("FLOYD (ALCANCE)")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        header_layout.addWidget(btn_back)
        header_layout.addWidget(btn_home)
        header_layout.addWidget(titulo, alignment=Qt.AlignCenter)

        layout.addWidget(header)

        # ----- Cuerpo (tres columnas) -----
        cuerpo = QHBoxLayout()

        # Panel izquierdo: visualización del grafo (sin edición)
        panel_visual = QFrame()
        panel_visual.setStyleSheet("background-color: #e6f2ff; border-radius: 8px; padding: 10px;")
        visual_layout = QVBoxLayout(panel_visual)
        self.visualizador = VisualizadorGrafoDirigido("Grafo Dirigido", parent=self, es_editable=False)
        visual_layout.addWidget(self.visualizador, alignment=Qt.AlignCenter)
        # Descripción del procedimiento
        descripcion = QLabel(
            "<b>Procedimiento de Floyd:</b><br>"
            "• Inicializar matriz de distancias: 0 en diagonal, peso de aristas, ∞ en resto.<br>"
            "• Para cada k desde 1 hasta n (vértice intermedio):<br>"
            "   Para cada i, j: si dist[i][k] + dist[k][j] < dist[i][j], actualizar dist[i][j].<br>"
            "• Al final, la matriz contiene las distancias mínimas entre todos los pares.<br>"
            "<i>Las celdas en verde indican cambios en cada iteración.</i>"
        )
        descripcion.setStyleSheet("background-color: white; border-radius: 4px; padding: 8px; color: #003366;")
        descripcion.setWordWrap(True)
        visual_layout.addWidget(descripcion)
        cuerpo.addWidget(panel_visual, 2)

        # Panel central: controles
        panel_controles = QFrame()
        panel_controles.setStyleSheet("background-color: #e6f2ff; border-radius: 8px; padding: 10px;")
        controles_layout = QVBoxLayout(panel_controles)

        # Número de vértices
        lbl_vertices = QLabel("Número de vértices:")
        lbl_vertices.setStyleSheet("font-weight: bold; color: #003366;")
        self.spin_vertices = QSpinBox()
        self.spin_vertices.setRange(2, 8)
        self.spin_vertices.setValue(4)
        self.spin_vertices.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 4px;")
        btn_crear = QPushButton("Crear Grafo")
        btn_crear.setStyleSheet(self._button_style("#4d9de0", "white"))
        btn_crear.clicked.connect(self.crear_grafo)

        controles_layout.addWidget(lbl_vertices)
        controles_layout.addWidget(self.spin_vertices)
        controles_layout.addWidget(btn_crear)
        controles_layout.addSpacing(15)

        # Botones de aristas
        lbl_aristas = QLabel("Aristas:")
        lbl_aristas.setStyleSheet("font-weight: bold; color: #003366;")
        btn_agregar = QPushButton("+ Agregar Arista")
        btn_agregar.setStyleSheet(self._button_style("#27ae60", "white"))
        btn_agregar.clicked.connect(self.agregar_arista)
        btn_eliminar = QPushButton("- Eliminar Arista")
        btn_eliminar.setStyleSheet(self._button_style("#e74c3c", "white"))
        btn_eliminar.clicked.connect(self.eliminar_arista)
        btn_limpiar = QPushButton("Limpiar Aristas")
        btn_limpiar.setStyleSheet(self._button_style("#95a5a6", "white"))
        btn_limpiar.clicked.connect(self.limpiar_aristas)

        controles_layout.addWidget(lbl_aristas)
        controles_layout.addWidget(btn_agregar)
        controles_layout.addWidget(btn_eliminar)
        controles_layout.addWidget(btn_limpiar)
        controles_layout.addSpacing(15)

        # Botones de archivo
        lbl_archivo = QLabel("Archivo:")
        lbl_archivo.setStyleSheet("font-weight: bold; color: #003366;")
        btn_guardar = QPushButton("Guardar Grafo")
        btn_guardar.setStyleSheet(self._button_style("#3498db", "white"))
        btn_guardar.clicked.connect(self.guardar_grafo)
        btn_cargar = QPushButton("Cargar Grafo")
        btn_cargar.setStyleSheet(self._button_style("#3498db", "white"))
        btn_cargar.clicked.connect(self.cargar_grafo)

        controles_layout.addWidget(lbl_archivo)
        controles_layout.addWidget(btn_guardar)
        controles_layout.addWidget(btn_cargar)
        controles_layout.addSpacing(15)

        # Botón ejecutar (movido aquí)
        btn_ejecutar = QPushButton("▶ Ejecutar Floyd")
        btn_ejecutar.setStyleSheet(self._button_style("#2c3e50", "white"))
        btn_ejecutar.clicked.connect(self.ejecutar_algoritmo)
        controles_layout.addWidget(btn_ejecutar)
        controles_layout.addStretch()

        cuerpo.addWidget(panel_controles, 1)

        # Panel derecho: matrices de resultado
        panel_matrices = QFrame()
        panel_matrices.setStyleSheet("background-color: #e6f2ff; border-radius: 8px; padding: 10px;")
        matrices_layout = QVBoxLayout(panel_matrices)

        lbl_matrices = QLabel("Matrices de Iteración")
        lbl_matrices.setStyleSheet("font-weight: bold; color: #003366;")
        self.scroll_matrices = QScrollArea()
        self.scroll_matrices.setWidgetResizable(True)
        self.scroll_matrices.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 4px;")
        self.widget_matrices = QWidget()
        self.layout_matrices = QVBoxLayout(self.widget_matrices)
        self.layout_matrices.setAlignment(Qt.AlignTop)
        self.scroll_matrices.setWidget(self.widget_matrices)

        matrices_layout.addWidget(lbl_matrices)
        matrices_layout.addWidget(self.scroll_matrices)

        cuerpo.addWidget(panel_matrices, 2)

        layout.addLayout(cuerpo)

        # No crear grafo al inicio

    # ----- Estilos -----
    def _button_style(self, bg_color, text_color):
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(bg_color)};
            }}
        """

    def _darken_color(self, color):
        return {
            "#4d9de0": "#3b7cb0",
            "#27ae60": "#1e8449",
            "#e74c3c": "#c0392b",
            "#3498db": "#2980b9",
            "#95a5a6": "#7f8c8d",
            "#2c3e50": "#1a252f",
        }.get(color, color)

    # ----- Navegación -----
    def cerrar_y_volver_a_grafos(self):
        self.close()
        self.volver_a_grafos()

    def cerrar_y_volver_a_principal(self):
        self.close()
        self.volver_a_principal()

    # ----- Gestión del grafo -----
    def crear_grafo(self):
        n = self.spin_vertices.value()
        self.modelo.crear_grafo(n)
        self.actualizar_visualizador()
        self.limpiar_matrices()
        DialogoClave(0, "Éxito", "mensaje", self, f"Grafo creado con {n} vértices.").exec()

    def actualizar_visualizador(self):
        datos = self.modelo.obtener_datos_visualizador()
        self.visualizador.set_grafo(datos['vertices'], datos['aristas'], datos['etiquetas'], datos['pesos'])

    def agregar_arista(self):
        if self.modelo.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec()
            return
        dlg = DialogoAgregarArista(self.modelo.num_vertices, self.modelo.etiquetas, self)
        if dlg.exec() == QDialog.Accepted:
            origen, destino, ponderacion = dlg.obtener_datos()
            if self.modelo.agregar_arista(origen, destino, ponderacion):
                self.actualizar_visualizador()
                DialogoClave(0, "Arista agregada", "mensaje", self,
                             f"Arista {self.modelo.etiquetas.get(origen, origen+1)} → "
                             f"{self.modelo.etiquetas.get(destino, destino+1)} agregada.").exec()
            else:
                DialogoClave(0, "Error", "mensaje", self, "La arista ya existe o es inválida.").exec()

    def eliminar_arista(self):
        if not self.modelo.aristas:
            DialogoClave(0, "Error", "mensaje", self, "No hay aristas para eliminar.").exec()
            return
        dlg = DialogoEliminarArista(self.modelo.aristas, self.modelo.etiquetas, self)
        if dlg.exec() == QDialog.Accepted:
            arista = dlg.obtener_arista()
            if self.modelo.eliminar_arista(arista):
                self.actualizar_visualizador()
                DialogoClave(0, "Arista eliminada", "mensaje", self, "Arista eliminada.").exec()

    def limpiar_aristas(self):
        if not self.modelo.aristas:
            DialogoClave(0, "Información", "mensaje", self, "No hay aristas para limpiar.").exec()
            return
        self.modelo.eliminar_todas_aristas()
        self.actualizar_visualizador()
        DialogoClave(0, "Limpieza", "mensaje", self, "Todas las aristas han sido eliminadas.").exec()

    def guardar_grafo(self):
        if self.modelo.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "No hay grafo para guardar.").exec()
            return
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Grafo", "", "JSON (*.json)")
        if ruta:
            try:
                self.modelo.guardar_grafo(ruta)
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo guardado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error al guardar: {str(e)}").exec()

    def cargar_grafo(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar Grafo", "", "JSON (*.json)")
        if ruta:
            try:
                self.modelo.cargar_grafo(ruta)
                self.spin_vertices.setValue(self.modelo.num_vertices)
                self.actualizar_visualizador()
                self.limpiar_matrices()
                DialogoClave(0, "Éxito", "mensaje", self, "Grafo cargado.").exec()
            except Exception as e:
                DialogoClave(0, "Error", "mensaje", self, f"Error al cargar: {str(e)}").exec()

    # ----- Algoritmo Floyd -----
    def limpiar_matrices(self):
        while self.layout_matrices.count():
            child = self.layout_matrices.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def ejecutar_algoritmo(self):
        if self.modelo.num_vertices == 0:
            DialogoClave(0, "Error", "mensaje", self, "Primero crea un grafo.").exec()
            return
        if not self.modelo.aristas:
            DialogoClave(0, "Error", "mensaje", self, "El grafo debe tener al menos una arista.").exec()
            return

        n = self.modelo.num_vertices
        INF = float('inf')
        dist = [[INF] * n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0
        for (u, v), peso in self.modelo.ponderaciones.items():
            dist[u][v] = peso

        iteraciones = []
        iteraciones.append({
            'iteracion': 0,
            'matriz': [row[:] for row in dist],
            'cambios': []
        })

        for k in range(n):
            cambios = []
            for i in range(n):
                for j in range(n):
                    if dist[i][k] != INF and dist[k][j] != INF:
                        nuevo = dist[i][k] + dist[k][j]
                        if nuevo < dist[i][j]:
                            dist[i][j] = nuevo
                            cambios.append((i, j))
            iteraciones.append({
                'iteracion': k+1,
                'matriz': [row[:] for row in dist],
                'cambios': cambios
            })

        self.mostrar_iteraciones(iteraciones)

    def mostrar_iteraciones(self, iteraciones):
        self.limpiar_matrices()
        INF = float('inf')

        for idx, it in enumerate(iteraciones):
            frame = QFrame()
            frame.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 8px; margin: 5px;")
            frame_layout = QVBoxLayout(frame)

            if idx == 0:
                titulo = QLabel("Matriz Inicial")
            else:
                titulo = QLabel(f"Iteración k = {it['iteracion']}")
            titulo.setStyleSheet("font-weight: bold; color: #003366; font-size: 14px;")
            titulo.setAlignment(Qt.AlignCenter)
            frame_layout.addWidget(titulo)

            matriz_widget = self.crear_matriz_widget(it['matriz'], it['cambios'], INF)
            frame_layout.addWidget(matriz_widget)

            self.layout_matrices.addWidget(frame)

    def crear_matriz_widget(self, matriz, cambios, INF):
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(3)

        n = len(matriz)
        # Cabeceras de columnas
        for j in range(n):
            label = QLabel(str(j+1))
            label.setStyleSheet("background-color: #4d9de0; color: white; font-weight: bold; text-align: center; padding: 8px; border-radius: 3px;")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label, 0, j+1)

        # Filas
        for i in range(n):
            # Cabecera de fila
            label_fila = QLabel(str(i+1))
            label_fila.setStyleSheet("background-color: #4d9de0; color: white; font-weight: bold; text-align: center; padding: 8px; border-radius: 3px;")
            label_fila.setAlignment(Qt.AlignCenter)
            layout.addWidget(label_fila, i+1, 0)

            for j in range(n):
                valor = matriz[i][j]
                if valor == INF:
                    texto = "∞"
                elif isinstance(valor, float) and valor == int(valor):
                    texto = str(int(valor))
                else:
                    texto = str(valor)

                cell = QLabel(texto)
                cell.setAlignment(Qt.AlignCenter)
                cell.setMinimumSize(50, 40)  # aumentar tamaño para evitar corte
                cell.setStyleSheet("padding: 5px;")

                if (i, j) in cambios:
                    cell.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; border: 2px solid #27ae60; border-radius: 3px; padding: 5px;")
                elif i == j:
                    cell.setStyleSheet("background-color: #cce6ff; color: #003366; border: 1px solid #99ccff; border-radius: 3px; padding: 5px;")
                else:
                    cell.setStyleSheet("background-color: white; color: #003366; border: 1px solid #99ccff; border-radius: 3px; padding: 5px;")

                layout.addWidget(cell, i+1, j+1)

        return widget