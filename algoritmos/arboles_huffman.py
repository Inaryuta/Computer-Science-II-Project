from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem,
    QGraphicsTextItem, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QBrush, QColor, QFont
from fractions import Fraction

from .funcion_mod import DialogoClave
from controladores.tree_huffman_controller import HuffmanController


class ArbolesHuffmanWindow(QMainWindow):
    def __init__(self, volver_a_busquedas, volver_a_principal):
        super().__init__()
        self.volver_a_busquedas = volver_a_busquedas
        self.volver_a_principal = volver_a_principal
        self.controller = HuffmanController()
        self.nodo_resaltado = None   # carácter a resaltar

        self.setWindowTitle("Árboles de Huffman")
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
            QLineEdit, QTextEdit {
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
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

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

        titulo = QLabel("ÁRBOLES DE HUFFMAN")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        header_layout.addWidget(titulo)

        header_layout.addStretch()
        main_layout.addWidget(header)

        # ----- CUERPO -----
        body_layout = QHBoxLayout()

        # Panel izquierdo: Árbol
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

        # Insertar texto
        lbl_insertar = QLabel("Insertar Texto:")
        lbl_insertar.setStyleSheet("font-weight: bold;")
        self.input_insertar = QTextEdit()
        self.input_insertar.setPlaceholderText("Ingrese el texto a comprimir")
        self.input_insertar.setMaximumHeight(100)
        btn_insertar = QPushButton("Generar Árbol de Huffman")
        btn_insertar.clicked.connect(self.generar_arbol)
        controls_layout.addWidget(lbl_insertar)
        controls_layout.addWidget(self.input_insertar)
        controls_layout.addWidget(btn_insertar)

        # Buscar letra
        lbl_buscar = QLabel("Buscar Letra:")
        lbl_buscar.setStyleSheet("font-weight: bold;")
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Ej: a")
        self.input_buscar.setMaxLength(1)
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.buscar_letra)
        controls_layout.addWidget(lbl_buscar)
        controls_layout.addWidget(self.input_buscar)
        controls_layout.addWidget(btn_buscar)

        # Eliminar letra
        lbl_eliminar = QLabel("Eliminar Letra:")
        lbl_eliminar.setStyleSheet("font-weight: bold;")
        self.input_eliminar = QLineEdit()
        self.input_eliminar.setPlaceholderText("Ej: e")
        self.input_eliminar.setMaxLength(1)
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(self.eliminar_letra)
        controls_layout.addWidget(lbl_eliminar)
        controls_layout.addWidget(self.input_eliminar)
        controls_layout.addWidget(btn_eliminar)

        # Limpiar todo
        btn_limpiar = QPushButton("Limpiar Todo")
        btn_limpiar.clicked.connect(self.limpiar_todo)
        controls_layout.addWidget(btn_limpiar)

        # Tabla de frecuencias y códigos
        lbl_tabla = QLabel("Frecuencias y Códigos:")
        lbl_tabla.setStyleSheet("font-weight: bold;")
        self.tabla_codigos = QTextEdit()
        self.tabla_codigos.setReadOnly(True)
        self.tabla_codigos.setMaximumHeight(200)
        self.tabla_codigos.setStyleSheet("""
            font-family: monospace;
            background-color: white;
            border: 1px solid #99ccff;
            border-radius: 4px;
        """)
        controls_layout.addWidget(lbl_tabla)
        controls_layout.addWidget(self.tabla_codigos)

        controls_layout.addStretch()
        body_layout.addWidget(controls_frame, stretch=1)
        main_layout.addLayout(body_layout)

        self.dibujar_arbol()

    # ---------- Dibujo ----------
    def dibujar_arbol(self):
        self.scene.clear()
        root = self.controller.root
        if not root:
            text_item = QGraphicsTextItem("Árbol vacío")
            text_item.setDefaultTextColor(QColor("#336699"))
            text_item.setScale(1.5)
            text_item.setPos(-60, -20)
            self.scene.addItem(text_item)
            self.view.setSceneRect(self.scene.itemsBoundingRect())
            return

        level_gap = 90
        start_offset = 280
        radio = 22
        pen_line = QPen(QColor("#336699"), 2)
        brush_node = QBrush(QColor("#4d9de0"))      # azul para nodos internos
        brush_leaf = QBrush(QColor("#2ecc71"))      # verde para hojas
        brush_resaltado = QBrush(QColor("#f1c40f")) # amarillo para búsqueda
        text_color = QColor("white")

        def draw(node, x, y, offset, depth):
            # Color según tipo
            if node.char == self.nodo_resaltado:
                brush = brush_resaltado
                pen = QPen(QColor("#e67e22"), 3)
            elif node.char is not None:
                brush = brush_leaf
                pen = QPen(QColor("#1e6bb8"), 2)
            else:
                brush = brush_node
                pen = QPen(QColor("#1e6bb8"), 2)

            circle = QGraphicsEllipseItem(x - radio, y - radio, 2*radio, 2*radio)
            circle.setBrush(brush)
            circle.setPen(pen)
            self.scene.addItem(circle)

            # Texto del nodo
            try:
                freq_frac = str(Fraction(node.freq).limit_denominator())
            except:
                freq_frac = str(node.freq)

            if node.char is not None:
                txt = f"{node.char}\n{freq_frac}"
            else:
                # Mostrar fracción (si es raíz con suma total 1, mostrar 1)
                if abs(node.freq - 1.0) < 1e-6:
                    txt = "1"
                else:
                    txt = freq_frac

            text_item = QGraphicsTextItem(txt)
            text_item.setDefaultTextColor(text_color)
            text_item.setPos(x - radio/1.3, y - 8)
            self.scene.addItem(text_item)

            # Hijo izquierdo (0)
            if node.left:
                child_x = x - offset
                child_y = y + level_gap
                self.scene.addLine(x, y + radio, child_x, child_y - radio, pen_line)
                mid_x = (x + child_x) / 2
                mid_y = (y + child_y) / 2 - 10
                bit_label = QGraphicsTextItem("0")
                bit_label.setDefaultTextColor(QColor("#336699"))
                bit_label.setPos(mid_x, mid_y)
                self.scene.addItem(bit_label)
                draw(node.left, child_x, child_y, max(40, offset/2), depth+1)

            # Hijo derecho (1)
            if node.right:
                child_x = x + offset
                child_y = y + level_gap
                self.scene.addLine(x, y + radio, child_x, child_y - radio, pen_line)
                mid_x = (x + child_x) / 2
                mid_y = (y + child_y) / 2 - 10
                bit_label = QGraphicsTextItem("1")
                bit_label.setDefaultTextColor(QColor("#336699"))
                bit_label.setPos(mid_x, mid_y)
                self.scene.addItem(bit_label)
                draw(node.right, child_x, child_y, max(40, offset/2), depth+1)

        draw(root, 0, 0, start_offset, 1)
        self.view.setSceneRect(self.scene.itemsBoundingRect())

    def mostrar_tabla(self):
        frec = self.controller.obtener_frecuencias()
        cod = self.controller.obtener_codigos()
        if not frec:
            self.tabla_codigos.setText("No hay datos")
            return
        texto = "Carácter | Frecuencia | Código\n"
        texto += "-" * 40 + "\n"
        for char in sorted(frec.keys()):
            char_disp = char if char != ' ' else '[espacio]'
            texto += f"{char_disp:^8} | {frec[char]:^10} | {cod.get(char, 'N/A')}\n"
        self.tabla_codigos.setText(texto)

    # ---------- Acciones ----------
    def generar_arbol(self):
        texto = self.input_insertar.toPlainText().strip()
        if not texto:
            DialogoClave(0, "Error", "mensaje", self, "Debe ingresar un texto.").exec()
            return
        try:
            self.controller.construir_arbol(texto)
            self.input_insertar.setReadOnly(True)
            self.input_insertar.setStyleSheet("""
                background-color: #cce6ff;
                border: 2px solid #99ccff;
                border-radius: 4px;
                padding: 5px;
                color: #003366;
                font-weight: bold;
            """)
            self.nodo_resaltado = None
            self.dibujar_arbol()
            self.mostrar_tabla()
            DialogoClave(0, "Éxito", "mensaje", self, "Árbol generado correctamente.").exec()
        except Exception as e:
            DialogoClave(0, "Error", "mensaje", self, f"Error: {str(e)}").exec()

    def buscar_letra(self):
        letra = self.input_buscar.text().strip()
        if not letra or len(letra) != 1:
            DialogoClave(0, "Advertencia", "mensaje", self, "Debe ingresar una sola letra.").exec()
            return
        if not self.controller.root:
            DialogoClave(0, "Advertencia", "mensaje", self, "Primero genere un árbol.").exec()
            return
        codigos = self.controller.obtener_codigos()
        frec = self.controller.obtener_frecuencias()
        if letra in codigos:
            self.nodo_resaltado = letra
            self.dibujar_arbol()
            msg = f"Letra '{letra}'\nCódigo: {codigos[letra]}\nFrecuencia: {frec.get(letra,0)}"
            DialogoClave(0, "Resultado", "mensaje", self, msg).exec()
        else:
            self.nodo_resaltado = None
            self.dibujar_arbol()
            DialogoClave(0, "Resultado", "mensaje", self, f"La letra '{letra}' no existe.").exec()
        self.input_buscar.clear()

    def eliminar_letra(self):
        letra = self.input_eliminar.text().strip()
        if not letra or len(letra) != 1:
            DialogoClave(0, "Advertencia", "mensaje", self, "Debe ingresar una sola letra.").exec()
            return
        if not self.controller.root:
            DialogoClave(0, "Advertencia", "mensaje", self, "Primero genere un árbol.").exec()
            return
        frec = self.controller.obtener_frecuencias()
        if letra not in frec:
            DialogoClave(0, "Error", "mensaje", self, f"La letra '{letra}' no está en el árbol.").exec()
            return

        confirm = DialogoClave(0, "Confirmar", "confirmar", self,
                               f"¿Eliminar '{letra}'? Se regenerará el árbol.")
        if confirm.exec() != DialogoClave.Accepted:
            return

        texto_actual = self.input_insertar.toPlainText()
        nuevo_texto = texto_actual.replace(letra, '')
        if not nuevo_texto.strip():
            DialogoClave(0, "Error", "mensaje", self,
                         "No se puede eliminar, quedaría texto vacío.").exec()
            return

        self.input_insertar.clear()
        self.input_insertar.setPlainText(nuevo_texto)
        self.input_insertar.setReadOnly(False)
        self.input_insertar.setStyleSheet("""
            background-color: white;
            border: 2px solid #99ccff;
            border-radius: 4px;
            padding: 5px;
            color: #003366;
        """)
        self.controller.construir_arbol(nuevo_texto)
        self.input_insertar.setReadOnly(True)
        self.input_insertar.setStyleSheet("""
            background-color: #cce6ff;
            border: 2px solid #99ccff;
            border-radius: 4px;
            padding: 5px;
            color: #003366;
            font-weight: bold;
        """)
        self.nodo_resaltado = None
        self.dibujar_arbol()
        self.mostrar_tabla()
        DialogoClave(0, "Éxito", "mensaje", self, f"Letra '{letra}' eliminada.").exec()
        self.input_eliminar.clear()

    def limpiar_todo(self):
        confirm = DialogoClave(0, "Confirmar", "confirmar", self,
                               "¿Limpiar todo el árbol?")
        if confirm.exec() != DialogoClave.Accepted:
            return
        self.controller.limpiar()
        self.input_insertar.clear()
        self.input_insertar.setReadOnly(False)
        self.input_insertar.setStyleSheet("""
            background-color: white;
            border: 2px solid #99ccff;
            border-radius: 4px;
            padding: 5px;
            color: #003366;
        """)
        self.tabla_codigos.clear()
        self.nodo_resaltado = None
        self.dibujar_arbol()
        DialogoClave(0, "Limpieza", "mensaje", self, "Árbol eliminado.").exec()

    def ir_a_principal(self):
        self.close()
        self.volver_a_principal()

    def ir_a_busquedas(self):
        self.close()
        self.volver_a_busquedas()