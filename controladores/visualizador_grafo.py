import math
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, QLabel
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainterPath, QPainter

class VisualizadorGrafo(QWidget):
    vertice_clicked = Signal(int)
    arista_clicked = Signal(tuple)  # (origen, destino, índice)

    def __init__(self, titulo="Grafo", parent=None, es_editable=False):
        super().__init__(parent)
        self.titulo = titulo
        self.es_editable = es_editable
        self.num_vertices = 0
        self.aristas = []          # lista de tuplas (origen, destino)
        self.pesos = []            # lista de pesos, en paralelo a aristas
        self.etiquetas = {}
        self.posiciones = []
        self.radio = 20
        self.curvatura = 0.3       # para curvar aristas paralelas

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setFixedSize(450, 450)
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
        self.aristas = aristas  # lista de (u,v)
        if pesos is None:
            self.pesos = [1] * len(aristas)
        elif isinstance(pesos, dict):
            # Si llegó como diccionario, convertirlo a lista en el orden de aristas
            self.pesos = [pesos.get(arista, 1) for arista in aristas]
        else:
            self.pesos = pesos  # asumimos lista
        self.etiquetas = etiquetas
        self._calcular_posiciones()
        self.dibujar()

    def _calcular_posiciones(self):
        self.posiciones = []
        if self.num_vertices == 0:
            return
        centro_x, centro_y = 225, 225
        radio_circulo = 170
        angulo_inicial = -math.pi / 2
        paso = 2 * math.pi / self.num_vertices
        for i in range(self.num_vertices):
            angulo = angulo_inicial + i * paso
            x = centro_x + radio_circulo * math.cos(angulo)
            y = centro_y + radio_circulo * math.sin(angulo)
            self.posiciones.append((x, y))

    def dibujar(self):
        self.scene.clear()
        if self.num_vertices == 0:
            texto = self.scene.addText("Grafo vacío")
            texto.setDefaultTextColor(QColor("#336699"))
            texto.setPos(150, 200)
            return

        pen_arista = QPen(QColor("#336699"), 2)
        brush_vertice = QBrush(QColor("#4d9de0"))
        pen_vertice = QPen(QColor("#1e6bb8"), 2)
        text_color = QColor("white")

        # Contar cuántas aristas hay entre cada par (para curvar)
        from collections import defaultdict
        contador = defaultdict(int)
        for (u,v) in self.aristas:
            if u == v:
                contador[('loop', u)] += 1
            else:
                key = tuple(sorted((u,v)))
                contador[key] += 1

        # Diccionario para llevar el desplazamiento de cada arista paralela
        offset_actual = defaultdict(int)

        for idx, (u, v) in enumerate(self.aristas):
            x1, y1 = self.posiciones[u]
            x2, y2 = self.posiciones[v]
            peso = self.pesos[idx] if idx < len(self.pesos) else ""

            # Determinar cuántas aristas paralelas hay y el desplazamiento actual
            if u == v:
                # Bucle: dibujar un arco circular
                radio_bucle = self.radio * 1.2
                centro_x = x1
                centro_y = y1 - radio_bucle
                start_angle = -90  # grados
                span_angle = 360
                path = QPainterPath()
                path.arcMoveTo(centro_x - radio_bucle, centro_y - radio_bucle, 2*radio_bucle, 2*radio_bucle, start_angle)
                path.arcTo(centro_x - radio_bucle, centro_y - radio_bucle, 2*radio_bucle, 2*radio_bucle, start_angle, span_angle)
                self.scene.addPath(path, pen_arista)
                # Etiqueta de peso cerca del bucle
                if peso:
                    text = self.scene.addText(str(peso))
                    text.setDefaultTextColor(QColor("#003366"))
                    text.setPos(x1 - 10, y1 - radio_bucle - 10)
                    text.setScale(0.8)
            else:
                key = tuple(sorted((u,v)))
                total = contador[key]
                # Índice de esta arista entre las paralelas
                # Usamos order interno; como los guardamos en lista, podemos contar cuántas veces ha aparecido este par
                # Simplificado: usamos un contador progresivo
                actual = offset_actual[key]
                offset_actual[key] += 1
                # Desplazamiento proporcional: entre -0.4 y 0.4 veces la distancia
                max_offset = 40  # píxeles máximos de curvatura
                if total > 1:
                    # Calcular un desplazamiento radial perpendicular a la línea
                    dx = x2 - x1
                    dy = y2 - y1
                    dist = math.hypot(dx, dy)
                    if dist < 0.01:
                        continue
                    # Vector unitario
                    ux = dx / dist
                    uy = dy / dist
                    # Perpendicular
                    px = -uy
                    py = ux
                    # Factor de desplazamiento: -0.4 a 0.4 veces la distancia, dependiendo del índice
                    factor = (actual - (total-1)/2) / (total) * 2  # rango -1..1
                    offset = factor * max_offset
                    # Puntos de control para curva cuadrática
                    mid_x = (x1 + x2) / 2 + px * offset
                    mid_y = (y1 + y2) / 2 + py * offset
                    path = QPainterPath()
                    path.moveTo(x1, y1)
                    path.quadTo(mid_x, mid_y, x2, y2)
                    self.scene.addPath(path, pen_arista)
                else:
                    # Línea recta
                    self.scene.addLine(x1, y1, x2, y2, pen_arista)

                # Peso en el centro (ligeramente desplazado si es curva)
                if peso:
                    if total > 1:
                        # Colocar el peso cerca del punto medio de la curva
                        mx = (x1 + x2) / 2 + px * offset/2
                        my = (y1 + y2) / 2 + py * offset/2
                    else:
                        mx = (x1 + x2) / 2
                        my = (y1 + y2) / 2
                    text = self.scene.addText(str(peso))
                    text.setDefaultTextColor(QColor("#003366"))
                    text.setPos(mx - 5, my - 5)
                    text.setScale(0.8)

        # Dibujar vértices
        for i, (x, y) in enumerate(self.posiciones):
            # Círculo
            self.scene.addEllipse(x-self.radio, y-self.radio, 2*self.radio, 2*self.radio,
                                  pen_vertice, brush_vertice)
            # Etiqueta
            etiq = self.etiquetas.get(i, str(i+1))
            texto = self.scene.addText(etiq)
            texto.setDefaultTextColor(text_color)
            rect = texto.boundingRect()
            texto.setPos(x - rect.width()/2, y - rect.height()/2)

        self.scene.setSceneRect(QRectF(0,0,450,450))