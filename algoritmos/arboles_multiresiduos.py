import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem,
    QGraphicsTextItem, QFrame, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QBrush, QColor, QFont

from .funcion_mod import DialogoClave
from controladores.tree_multiresiduos_controller import ArbolMultiResiduosController


class ArbolesMultiResiduosWindow(QMainWindow):
    def __init__(self, volver_a_busquedas, volver_a_principal):
        super().__init__()
        self.volver_a_busquedas = volver_a_busquedas
        self.volver_a_principal = volver_a_principal
        self.controller = ArbolMultiResiduosController()

        self.setWindowTitle("Árboles de Múltiples Residuos")
        self.setGeometry(100, 50, 1200, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f8ff;
            }
            QLabel {
                color: #003366;
            }
            QPushButton {
                background-color: #e6f2ff;
                color: #003366;
                font-weight: bold;
                border: 2px solid #99ccff;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #cce6ff;
            }
            QPushButton:pressed {
                background-color: #b3d9ff;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #99ccff;
                border-radius: 4px;
                padding: 5px;
                color: #003366;
            }
            QFrame {
                background-color: #e6f2ff;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QVBoxLayout(central)
        layout_principal.setSpacing(10)
        layout_principal.setContentsMargins(10, 10, 10, 10)

        # ----- HEADER -----
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #cce6ff;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)

        btn_inicio = QPushButton("🏠 Inicio")
        btn_inicio.setCursor(Qt.PointingHandCursor)
        btn_inicio.clicked.connect(self.ir_a_principal)
        header_layout.addWidget(btn_inicio)

        btn_menu_busqueda = QPushButton("🔍 Menú Búsqueda")
        btn_menu_busqueda.setCursor(Qt.PointingHandCursor)
        btn_menu_busqueda.clicked.connect(self.ir_a_busquedas)
        header_layout.addWidget(btn_menu_busqueda)

        header_layout.addStretch()

        titulo = QLabel("ÁRBOLES DE MÚLTIPLES RESIDUOS")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        header_layout.addWidget(titulo)

        header_layout.addStretch()
        layout_principal.addWidget(header)

        # ----- CUERPO (árbol + controles) -----
        body_layout = QHBoxLayout()

        # Panel izquierdo: Árbol (QGraphicsView)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints())
        self.view.setStyleSheet("background-color: #ffffff; border: 2px solid #99ccff; border-radius: 8px;")
        body_layout.addWidget(self.view, stretch=2)

        # Panel derecho: Controles
        controls_frame = QFrame()
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(15)
        controls_layout.setAlignment(Qt.AlignTop)

        # Insertar palabra (inserta letra por letra)
        lbl_insertar = QLabel("Insertar Palabra:")
        lbl_insertar.setStyleSheet("font-weight: bold;")
        self.input_insertar = QLineEdit()
        self.input_insertar.setPlaceholderText("Ej: CASA")
        btn_insertar = QPushButton("Insertar")
        btn_insertar.clicked.connect(self.insertar_palabra)
        controls_layout.addWidget(lbl_insertar)
        controls_layout.addWidget(self.input_insertar)
        controls_layout.addWidget(btn_insertar)

        # Buscar letra
        lbl_buscar = QLabel("Buscar Letra:")
        lbl_buscar.setStyleSheet("font-weight: bold;")
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Ej: A")
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.buscar_letra)
        controls_layout.addWidget(lbl_buscar)
        controls_layout.addWidget(self.input_buscar)
        controls_layout.addWidget(btn_buscar)

        # Eliminar letra
        lbl_eliminar = QLabel("Eliminar Letra:")
        lbl_eliminar.setStyleSheet("font-weight: bold;")
        self.input_eliminar = QLineEdit()
        self.input_eliminar.setPlaceholderText("Ej: R")
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(self.eliminar_letra)
        controls_layout.addWidget(lbl_eliminar)
        controls_layout.addWidget(self.input_eliminar)
        controls_layout.addWidget(btn_eliminar)

        # Eliminar todo el árbol
        btn_eliminar_arbol = QPushButton("Eliminar Árbol")
        btn_eliminar_arbol.clicked.connect(self.eliminar_arbol)
        controls_layout.addWidget(btn_eliminar_arbol)

        # Espaciador
        controls_layout.addStretch()

        # Mostrar alfabeto y códigos
        lbl_codigos = QLabel("Alfabeto y Códigos Binarios:")
        lbl_codigos.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(lbl_codigos)

        # Layout para dos columnas
        codigos_layout = QHBoxLayout()
        col1_text = ""
        col2_text = ""
        items = sorted(self.controller.codigos.items())
        mitad = len(items) // 2
        for i, (letra, codigo) in enumerate(items):
            linea = f"{letra} : {codigo}\n"
            if i < mitad:
                col1_text += linea
            else:
                col2_text += linea

        col1 = QLabel(col1_text)
        col1.setStyleSheet("""
            background-color: white;
            border: 1px solid #99ccff;
            border-radius: 4px;
            padding: 5px;
            font-family: monospace;
        """)
        col2 = QLabel(col2_text)
        col2.setStyleSheet(col1.styleSheet())

        codigos_layout.addWidget(col1)
        codigos_layout.addWidget(col2)
        controls_layout.addLayout(codigos_layout)

        body_layout.addWidget(controls_frame, stretch=1)
        layout_principal.addLayout(body_layout)

        self.dibujar_arbol()

    # ---------- Dibujo del árbol ----------
    def dibujar_arbol(self):
        self.scene.clear()
        raiz = self.controller.obtener_raiz()
        if raiz is None or (not raiz.children and not raiz.letra):
            # Árbol vacío
            text_item = QGraphicsTextItem("Árbol vacío")
            text_item.setDefaultTextColor(QColor("#336699"))
            text_item.setScale(1.5)
            text_item.setPos(-60, -20)
            self.scene.addItem(text_item)
            self.view.setSceneRect(self.scene.itemsBoundingRect())
            return

        # Parámetros de dibujo
        level_gap = 80
        start_offset = 300  # un poco más ancho porque puede haber más hijos
        radio = 20
        pen_line = QPen(QColor("#336699"), 2)
        brush_interno = QBrush(QColor("#4d9de0"))   # azul para nodos internos
        brush_hoja = QBrush(QColor("#2ecc71"))      # verde para hojas
        text_color = QColor("white")

        def draw(node, x, y, offset, depth):
            # Determinar color del círculo
            if node.is_leaf:
                brush = brush_hoja
            else:
                brush = brush_interno

            circle = QGraphicsEllipseItem(x - radio, y - radio, 2*radio, 2*radio)
            circle.setBrush(brush)
            circle.setPen(QPen(QColor("#1e6bb8"), 2))
            self.scene.addItem(circle)

            # Texto del nodo (si es hoja, la letra; si no, vacío)
            if node.is_leaf:
                txt = node.letra if node.letra else ""
            else:
                txt = ""
            text_item = QGraphicsTextItem(txt)
            text_item.setDefaultTextColor(text_color)
            text_item.setPos(x - radio/2, y - 8)
            self.scene.addItem(text_item)

            # Dibujar hijos (pueden ser 2 o 4 dependiendo del nivel)
            # En nuestro árbol, los hijos son strings de 2 bits (o 1 bit en último nivel)
            # Para simplificar, dibujamos todos los hijos existentes
            num_hijos = len(node.children)
            if num_hijos == 0:
                return

            # Distribuir hijos en un arco
            # Para mantener orden, podemos ordenar las claves
            keys = sorted(node.children.keys())
            # Calcular el espaciado horizontal
            total_width = offset * 2  # desde -offset hasta +offset
            step = total_width / (num_hijos + 1)
            start_x = x - total_width / 2 + step

            for i, key in enumerate(keys):
                hijo = node.children[key]
                child_x = start_x + i * step
                child_y = y + level_gap

                # Línea
                self.scene.addLine(x, y + radio, child_x, child_y - radio, pen_line)

                # Etiqueta del par de bits
                mid_x = (x + child_x) / 2
                mid_y = (y + child_y) / 2 - 10
                bit_label = QGraphicsTextItem(key)
                bit_label.setDefaultTextColor(QColor("#336699"))
                bit_label.setPos(mid_x, mid_y)
                self.scene.addItem(bit_label)

                # Dibujar hijo recursivamente con offset reducido
                draw(hijo, child_x, child_y, offset * 0.6, depth + 1)

        draw(raiz, 0, 0, start_offset, 1)
        self.view.setSceneRect(self.scene.itemsBoundingRect())

    # ---------- Acciones ----------
    def insertar_palabra(self):
        palabra = self.input_insertar.text().strip()
        if not palabra:
            QMessageBox.warning(self, "Error", "Debe ingresar una palabra.")
            return
        exito, mensaje = self.controller.insertar_palabra(palabra)
        self.input_insertar.clear()
        self.dibujar_arbol()
        if exito:
            QMessageBox.information(self, "Resultado", mensaje)
        else:
            QMessageBox.warning(self, "Error", mensaje)

    def buscar_letra(self):
        letra = self.input_buscar.text().strip()
        if not letra or len(letra) != 1 or not letra.isalpha():
            QMessageBox.warning(self, "Error", "Debe ingresar una sola letra.")
            return
        ruta = self.controller.buscar_letra(letra)
        if ruta is not None:
            QMessageBox.information(self, "Resultado", f"La letra '{letra.upper()}' se encuentra en la ruta: {ruta}")
        else:
            QMessageBox.information(self, "Resultado", f"La letra '{letra.upper()}' no está en el árbol.")

    def eliminar_letra(self):
        letra = self.input_eliminar.text().strip()
        if not letra or len(letra) != 1 or not letra.isalpha():
            QMessageBox.warning(self, "Error", "Debe ingresar una sola letra.")
            return
        resultado = self.controller.eliminar_letra(letra)
        self.input_eliminar.clear()
        self.dibujar_arbol()
        if resultado == "OK":
            QMessageBox.information(self, "Éxito", f"Letra '{letra.upper()}' eliminada.")
        else:
            QMessageBox.warning(self, "Error", resultado)

    def eliminar_arbol(self):
        resp = QMessageBox.question(
            self, "Confirmar",
            "¿Está seguro de eliminar todo el árbol?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            self.controller.eliminar_arbol()
            self.dibujar_arbol()
            QMessageBox.information(self, "Éxito", "Árbol eliminado.")

    def ir_a_principal(self):
        self.close()
        self.volver_a_principal()

    def ir_a_busquedas(self):
        self.close()
        self.volver_a_busquedas()