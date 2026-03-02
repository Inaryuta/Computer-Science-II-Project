import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem,
    QGraphicsTextItem, QFrame, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QBrush, QColor, QFont

# Reutilizamos el diálogo de clave (de funcion_mod.py)
from .funcion_mod import DialogoClave


# ---------- Nodo del árbol binario ----------
class NodoBinario:
    def __init__(self, letra=None):
        self.letra = letra          # letra almacenada en este nodo
        self.children = {'0': None, '1': None}


# ---------- Controlador de Árboles Digitales ----------
class ArbolDigitalController:
    def __init__(self):
        self.root = NodoBinario()
        # Códigos binarios de 5 bits para a-z (a=00001, b=00010, ..., z=11010)
        self.codigos = {chr(97 + i): format(i + 1, "05b") for i in range(26)}
        self.letras_orden = []       # orden de inserción de las letras

    def _insertar_una_letra(self, letra):
        """Inserta una letra en el árbol siguiendo la lógica de primer lugar libre."""
        codigo = self.codigos[letra]
        nodo = self.root
        # Si la raíz está vacía, colocar allí
        if nodo.letra is None:
            nodo.letra = letra
            return True
        # Recorrer bits
        for bit in codigo:
            if nodo.children[bit] is None:
                nuevo = NodoBinario(letra)
                nodo.children[bit] = nuevo
                return True
            else:
                nodo = nodo.children[bit]
        # Si llegamos aquí, todos los bits tienen nodo y el último ya tiene letra
        return False

    def insertar_letra(self, letra):
        """Inserta una letra. Retorna mensaje de resultado."""
        letra = letra.lower()
        if letra not in self.codigos:
            return "Letra no válida (solo a-z)"
        if letra in self.letras_orden:
            return "La letra ya existe"
        if self._insertar_una_letra(letra):
            self.letras_orden.append(letra)
            return "OK"
        else:
            return "Error interno al insertar"

    def insertar_palabra(self, palabra):
        """Inserta todas las letras de una palabra. Retorna (éxito, mensaje)."""
        palabra = palabra.lower().strip()
        if not palabra:
            return False, "Palabra vacía"
        letras_ok = []
        for ch in palabra:
            if ch not in self.codigos:
                return False, f"Carácter no válido: {ch}"
            if ch in self.letras_orden:
                continue  # ya existe, se omite
            if self._insertar_una_letra(ch):
                self.letras_orden.append(ch)
                letras_ok.append(ch)
            else:
                return False, f"Error al insertar {ch}"
        if letras_ok:
            return True, f"Letras insertadas: {', '.join(letras_ok)}"
        else:
            return True, "Todas las letras ya existían"

    def buscar_letra(self, letra):
        """Devuelve la ruta de bits donde se encuentra la letra, o None si no existe."""
        letra = letra.lower()
        if letra not in self.letras_orden:
            return None

        def buscar(nodo, camino):
            if nodo.letra == letra:
                return camino
            for bit, hijo in nodo.children.items():
                if hijo:
                    res = buscar(hijo, camino + bit)
                    if res is not None:
                        return res
            return None

        return buscar(self.root, "")

    def eliminar_letra(self, letra):
        """Elimina una letra y reconstruye el árbol con las restantes."""
        letra = letra.lower()
        if letra not in self.letras_orden:
            return "La letra no existe"
        self.letras_orden.remove(letra)
        # Reconstruir árbol desde cero con el mismo orden
        self.root = NodoBinario()
        for l in self.letras_orden:
            self._insertar_una_letra(l)
        return "OK"

    def eliminar_arbol(self):
        """Elimina todo el árbol."""
        self.root = NodoBinario()
        self.letras_orden = []


# ---------- Ventana principal ----------
class ArbolesDigitalesWindow(QMainWindow):
    def __init__(self, volver_a_busquedas, volver_a_principal):
        super().__init__()
        self.volver_a_busquedas = volver_a_busquedas
        self.volver_a_principal = volver_a_principal
        self.controller = ArbolDigitalController()

        self.setWindowTitle("Árboles Digitales")
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

        titulo = QLabel("ÁRBOLES DIGITALES")
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
        self.input_insertar.setPlaceholderText("Ej: Casa")
        btn_insertar = QPushButton("Insertar")
        btn_insertar.clicked.connect(self.insertar_palabra)
        controls_layout.addWidget(lbl_insertar)
        controls_layout.addWidget(self.input_insertar)
        controls_layout.addWidget(btn_insertar)

        # Buscar letra
        lbl_buscar = QLabel("Buscar clave:")
        lbl_buscar.setStyleSheet("font-weight: bold;")
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Ej: A")
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.buscar_letra)
        controls_layout.addWidget(lbl_buscar)
        controls_layout.addWidget(self.input_buscar)
        controls_layout.addWidget(btn_buscar)

        # Eliminar letra
        lbl_eliminar = QLabel("Eliminar clave:")
        lbl_eliminar.setStyleSheet("font-weight: bold;")
        self.input_eliminar = QLineEdit()
        self.input_eliminar.setPlaceholderText("Ej: E")
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
        items = sorted(self.controller.codigos.items())  # orden alfabético
        mitad = len(items) // 2
        for i, (letra, codigo) in enumerate(items):
            linea = f"{letra.upper()} : {codigo}\n"
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
        if self.controller.root.letra is None and not any(self.controller.root.children.values()):
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
        start_offset = 250
        radio = 20
        pen_line = QPen(QColor("#336699"), 2)
        brush_node = QBrush(QColor("#4d9de0"))       # azul claro
        brush_letra = QBrush(QColor("#2ecc71"))      # verde para nodos con letra
        text_color = QColor("white")

        def draw(node, x, y, offset, depth):
            # Dibujar círculo del nodo
            circle = QGraphicsEllipseItem(x - radio, y - radio, 2*radio, 2*radio)
            if node.letra:
                circle.setBrush(brush_letra)
            else:
                circle.setBrush(brush_node)
            circle.setPen(QPen(QColor("#1e6bb8"), 2))
            self.scene.addItem(circle)

            # Texto del nodo (la letra)
            if node.letra:
                txt = node.letra.upper()
            else:
                txt = ""
            text_item = QGraphicsTextItem(txt)
            text_item.setDefaultTextColor(text_color)
            text_item.setPos(x - radio/2, y - 8)
            self.scene.addItem(text_item)

            # Dibujar hijos
            for bit in ('0', '1'):
                hijo = node.children.get(bit)
                if hijo:
                    child_x = x - offset if bit == '0' else x + offset
                    child_y = y + level_gap
                    # Línea
                    self.scene.addLine(x, y + radio, child_x, child_y - radio, pen_line)
                    # Etiqueta del bit
                    mid_x = (x + child_x) / 2
                    mid_y = (y + child_y) / 2 - 10
                    bit_label = QGraphicsTextItem(bit)
                    bit_label.setDefaultTextColor(QColor("#336699"))
                    bit_label.setPos(mid_x, mid_y)
                    self.scene.addItem(bit_label)
                    # Dibujar hijo recursivamente
                    draw(hijo, child_x, child_y, max(30, offset / 2), depth + 1)

        draw(self.controller.root, 0, 0, start_offset, 1)
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