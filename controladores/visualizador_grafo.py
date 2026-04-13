import math
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, QLabel
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QFont

class VisualizadorGrafo(QWidget):
    vertice_clicked = Signal(int)

    def __init__(self, titulo="Grafo", parent=None, es_editable=False):
        super().__init__(parent)
        self.titulo = titulo
        self.es_editable = es_editable
        self.num_vertices = 0
        self.aristas = []
        self.etiquetas = {}
        self.pesos = {}
        self.posiciones = []
        self.radio = 20
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setFixedSize(400, 400)
        self.view.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 8px;")
        layout.addWidget(self.view)
        self.titulo_label = QLabel(self.titulo)
        self.titulo_label.setAlignment(Qt.AlignCenter)
        self.titulo_label.setStyleSheet("font-weight: bold; color: #003366;")
        layout.addWidget(self.titulo_label)
        self.scene.mousePressEvent = self.scene_mouse_press

    def scene_mouse_press(self, event):
        if not self.es_editable:
            return
        pos = event.scenePos()
        for i, (x, y) in enumerate(self.posiciones):
            dx = x - pos.x()
            dy = y - pos.y()
            if math.hypot(dx, dy) <= self.radio:
                self.vertice_clicked.emit(i)
                return

    def set_grafo(self, num_vertices, aristas, etiquetas, pesos=None):
        self.num_vertices = num_vertices
        self.aristas = aristas
        self.etiquetas = etiquetas
        self.pesos = pesos if pesos else {}
        self._calcular_posiciones()
        self.dibujar()

    def _calcular_posiciones(self):
        self.posiciones = []
        if self.num_vertices == 0:
            return
        centro_x, centro_y = 200, 200
        radio_circulo = 150
        angulo_inicial = -math.pi / 2  # -90° (parte superior)
        paso = 2 * math.pi / self.num_vertices
        for i in range(self.num_vertices):
            angulo = angulo_inicial - i * paso  # sentido horario
            x = centro_x + radio_circulo * math.cos(angulo)
            y = centro_y + radio_circulo * math.sin(angulo)
            self.posiciones.append((x, y))

    def dibujar(self):
        self.scene.clear()
        if self.num_vertices == 0:
            texto = self.scene.addText("Grafo vacío")
            texto.setDefaultTextColor(QColor("#336699"))
            texto.setPos(150, 180)
            return

        pen_arista = QPen(QColor("#336699"), 2)
        brush_vertice = QBrush(QColor("#4d9de0"))
        pen_vertice = QPen(QColor("#1e6bb8"), 2)
        text_color = QColor("white")

        for (u,v) in self.aristas:
            if u < len(self.posiciones) and v < len(self.posiciones):
                x1,y1 = self.posiciones[u]
                x2,y2 = self.posiciones[v]
                self.scene.addLine(x1,y1,x2,y2, pen_arista)
                peso = self.pesos.get((u,v), self.pesos.get((v,u), None))
                if peso is not None:
                    mx, my = (x1+x2)/2, (y1+y2)/2
                    peso_txt = self.scene.addText(str(peso))
                    peso_txt.setDefaultTextColor(QColor("#003366"))
                    peso_txt.setPos(mx-5, my-5)
                    peso_txt.setScale(0.8)

        for i, (x,y) in enumerate(self.posiciones):
            self.scene.addEllipse(x-self.radio, y-self.radio, 2*self.radio, 2*self.radio,
                                  pen_vertice, brush_vertice)
            etiq = self.etiquetas.get(i, str(i+1))
            texto = self.scene.addText(etiq)
            texto.setDefaultTextColor(text_color)
            rect = texto.boundingRect()
            texto.setPos(x - rect.width()/2, y - rect.height()/2)

        self.scene.setSceneRect(QRectF(0,0,400,400))