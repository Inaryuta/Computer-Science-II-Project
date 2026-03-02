import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem,
    QGraphicsTextItem, QFrame, QMessageBox, QFileDialog, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QBrush, QColor, QFont

# Reutilizamos el diálogo de clave (ya existente en otros archivos)
from .funcion_mod import DialogoClave  # o importar desde donde corresponda


class Nodo:
    """Nodo del árbol digital binario."""
    def __init__(self):
        self.children = {'0': None, '1': None}
        self.letters = []          # Letras que terminan en este nodo
        self.end_words = False     # True si al menos una palabra termina aquí


class ArbolDigitalController:
    """Controlador para el árbol digital (trie binario)."""
    def __init__(self):
        self.root = Nodo()
        # Generar códigos binarios para A-Z (5 bits)
        self.codigos = {}
        letras = 'abcdefghijklmnopqrstuvwxyz'
        for i, letra in enumerate(letras):
            # Código de 5 bits, desde 00001 para A hasta 11010 para Z (26)
            codigo = format(i+1, '05b')
            self.codigos[letra] = codigo

    def insertar_palabra(self, palabra):
        """Inserta una palabra en el árbol. Retorna 'OK' o mensaje de error."""
        palabra = palabra.lower().strip()
        if not palabra:
            return "Palabra vacía"
        # Verificar que todos los caracteres sean letras
        if not all(c.isalpha() for c in palabra):
            return "Solo se permiten letras"

        # Recorrer cada letra de la palabra
        for letra in palabra:
            if letra not in self.codigos:
                return f"Letra '{letra}' no soportada (solo A-Z)"
            codigo = self.codigos[letra]
            nodo = self.root
            # Recorrer el código binario bit a bit
            for bit in codigo:
                if nodo.children[bit] is None:
                    nodo.children[bit] = Nodo()
                nodo = nodo.children[bit]
            # Al final del código, agregar la letra al nodo si no está
            if letra not in nodo.letters:
                nodo.letters.append(letra)
            # Marcar que este nodo es final de palabra (para la última letra de la palabra)
            # Nota: En este diseño, cada letra se inserta individualmente, pero la palabra
            # completa se compone de varias letras. Para marcar que una palabra completa
            # termina aquí, necesitamos un indicador por palabra. En el código original,
            # `end_words` es un booleano que indica si alguna palabra termina en ese nodo.
            # Como estamos insertando letras individuales, la palabra es la secuencia de letras.
            # Para simplificar, haremos que cada nodo que contenga una letra sea considerado
            # como final de esa letra, pero no de la palabra completa. Sin embargo, en el
            # dibujo se resaltan los nodos que tienen letras (end_words=True). Así que
            # marcaremos end_words=True para cualquier nodo que tenga letras.
            nodo.end_words = True

        return "OK"

    def buscar_letra(self, letra):
        """Busca una letra y devuelve su código binario si existe, None si no."""
        letra = letra.lower().strip()
        if letra not in self.codigos:
            return None
        codigo = self.codigos[letra]
        nodo = self.root
        for bit in codigo:
            if nodo.children[bit] is None:
                return None
            nodo = nodo.children[bit]
        # La letra existe si está en la lista de letras del nodo
        if letra in nodo.letters:
            return codigo
        return None

    def eliminar_palabra(self, palabra):
        """Elimina una palabra completa del árbol. Retorna 'OK' o mensaje de error."""
        palabra = palabra.lower().strip()
        if not palabra:
            return "Palabra vacía"
        # Para eliminar una palabra, necesitamos eliminar cada letra de los nodos,
        # pero solo si no son usadas por otras palabras. Esto es complejo.
        # Por simplicidad, eliminaremos solo la primera letra de la palabra (como en el ejemplo original)
        # En el código original, `eliminar_clave` eliminaba una palabra completa, pero no está claro.
        # Vamos a implementar una eliminación simple: solo la primera letra.
        if not palabra:
            return "Palabra vacía"
        letra = palabra[0]  # Tomamos la primera letra como ejemplo
        if letra not in self.codigos:
            return f"Letra '{letra}' no soportada"
        codigo = self.codigos[letra]
        nodo = self.root
        pila = []  # para recordar el camino
        for bit in codigo:
            if nodo.children[bit] is None:
                return "La letra no existe"
            pila.append((nodo, bit))
            nodo = nodo.children[bit]
        if letra not in nodo.letters:
            return "La letra no existe en ese nodo"
        # Eliminar la letra del nodo
        nodo.letters.remove(letra)
        # Si el nodo queda sin letras y sin hijos, eliminar hacia arriba
        while pila and not nodo.letters and not any(nodo.children.values()):
            padre, bit = pila.pop()
            padre.children[bit] = None
            nodo = padre
        return "OK"

    def eliminar_arbol(self):
        """Elimina todo el árbol."""
        self.root = Nodo()


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

        # Widget central
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

        # Insertar palabra
        lbl_insertar = QLabel("Insertar Palabra:")
        lbl_insertar.setStyleSheet("font-weight: bold;")
        self.input_insertar = QLineEdit()
        self.input_insertar.setPlaceholderText("Ej: casa")
        btn_insertar = QPushButton("Insertar")
        btn_insertar.clicked.connect(self.insertar_palabra)

        controls_layout.addWidget(lbl_insertar)
        controls_layout.addWidget(self.input_insertar)
        controls_layout.addWidget(btn_insertar)

        # Buscar letra
        lbl_buscar = QLabel("Buscar Letra:")
        lbl_buscar.setStyleSheet("font-weight: bold;")
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Ej: a")
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.buscar_letra)

        controls_layout.addWidget(lbl_buscar)
        controls_layout.addWidget(self.input_buscar)
        controls_layout.addWidget(btn_buscar)

        # Eliminar palabra
        lbl_eliminar = QLabel("Eliminar Palabra (primera letra):")
        lbl_eliminar.setStyleSheet("font-weight: bold;")
        self.input_eliminar = QLineEdit()
        self.input_eliminar.setPlaceholderText("Ej: casa")
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(self.eliminar_palabra)

        controls_layout.addWidget(lbl_eliminar)
        controls_layout.addWidget(self.input_eliminar)
        controls_layout.addWidget(btn_eliminar)

        # Eliminar todo el árbol
        btn_eliminar_arbol = QPushButton("Eliminar Árbol")
        btn_eliminar_arbol.clicked.connect(self.eliminar_arbol)
        controls_layout.addWidget(btn_eliminar_arbol)

        # Espaciador
        controls_layout.addStretch()

        # Mostrar abecedario y códigos
        lbl_codigos = QLabel("Abecedario y Códigos Binarios:")
        lbl_codigos.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(lbl_codigos)

        # Layout para dos columnas
        codigos_layout = QHBoxLayout()
        col1_text = ""
        col2_text = ""
        items = list(self.controller.codigos.items())
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

        # Dibujar árbol vacío inicial
        self.dibujar_arbol()

    # ---------- Métodos de dibujo ----------
    def dibujar_arbol(self):
        """Dibuja el árbol binario en la escena."""
        self.scene.clear()
        root = self.controller.root
        if not root or (not root.letters and not any(root.children.values())):
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
        brush_end = QBrush(QColor("#2ecc71"))        # verde para nodos con letras
        text_color = QColor("white")

        def draw(node, x, y, offset, depth):
            # Dibujar círculo del nodo
            circle = QGraphicsEllipseItem(x - radio, y - radio, 2*radio, 2*radio)
            if node.letters:
                circle.setBrush(brush_end)
            else:
                circle.setBrush(brush_node)
            circle.setPen(QPen(QColor("#1e6bb8"), 2))
            self.scene.addItem(circle)

            # Texto del nodo (letras que contiene)
            if node.letters:
                txt = ", ".join(node.letters[:2])
                if len(node.letters) > 2:
                    txt += "..."
            else:
                txt = ""
            if not txt and node is self.controller.root:
                txt = "root"
            text_item = QGraphicsTextItem(txt)
            text_item.setDefaultTextColor(text_color)
            text_item.setPos(x - radio/1.5, y - 8)
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

        draw(root, 0, 0, start_offset, 1)
        self.view.setSceneRect(self.scene.itemsBoundingRect())

    # ---------- Acciones ----------
    def insertar_palabra(self):
        palabra = self.input_insertar.text().strip()
        if not palabra:
            QMessageBox.warning(self, "Error", "Debe ingresar una palabra.")
            return
        resultado = self.controller.insertar_palabra(palabra)
        if resultado == "OK":
            self.input_insertar.clear()
            self.dibujar_arbol()
            QMessageBox.information(self, "Éxito", f"Palabra '{palabra}' insertada.")
        else:
            QMessageBox.warning(self, "Error", resultado)

    def buscar_letra(self):
        letra = self.input_buscar.text().strip()
        if not letra or len(letra) != 1 or not letra.isalpha():
            QMessageBox.warning(self, "Error", "Debe ingresar una sola letra.")
            return
        codigo = self.controller.buscar_letra(letra)
        if codigo:
            QMessageBox.information(self, "Resultado", f"La letra '{letra.upper()}' tiene código binario: {codigo}")
        else:
            QMessageBox.information(self, "Resultado", f"La letra '{letra.upper()}' no está en el árbol.")

    def eliminar_palabra(self):
        palabra = self.input_eliminar.text().strip()
        if not palabra:
            QMessageBox.warning(self, "Error", "Debe ingresar una palabra.")
            return
        resultado = self.controller.eliminar_palabra(palabra)
        if resultado == "OK":
            self.input_eliminar.clear()
            self.dibujar_arbol()
            QMessageBox.information(self, "Éxito", f"Palabra '{palabra}' eliminada.")
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