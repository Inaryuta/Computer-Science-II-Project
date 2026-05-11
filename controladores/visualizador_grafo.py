import math
from collections import defaultdict
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, QLabel
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainterPath, QWheelEvent


class GrafoScene(QGraphicsScene):
    """Escena personalizada que permite arrastrar vértices."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.visualizador = None
        self.dragging_vertex = None
        self.drag_start_pos = None

    def set_visualizador(self, vis):
        self.visualizador = vis

    def mousePressEvent(self, event):
        if not self.visualizador or not self.visualizador.es_editable:
            super().mousePressEvent(event)
            return
        pos = event.scenePos()
        for i, (x, y) in enumerate(self.visualizador.posiciones):
            if math.hypot(x - pos.x(), y - pos.y()) <= self.visualizador.radio:
                self.dragging_vertex = i
                self.drag_start_pos = pos
                self.visualizador.vertice_clicked.emit(i)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging_vertex is not None and self.visualizador:
            pos = event.scenePos()
            delta = pos - self.drag_start_pos
            x, y = self.visualizador.posiciones[self.dragging_vertex]
            self.visualizador.posiciones[self.dragging_vertex] = (x + delta.x(), y + delta.y())
            self.drag_start_pos = pos
            # Redibujar sin ajustar la vista
            self.visualizador.dibujar(ajustar_vista=False)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.dragging_vertex is not None:
            self.dragging_vertex = None
            self.drag_start_pos = None
            # Al final del arrastre, ajustar la vista
            if self.visualizador:
                self.visualizador.ajustar_vista()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class GraficoView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHints(self.renderHints())
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.1
        if event.angleDelta().y() > 0:
            self.scale(factor, factor)
        else:
            self.scale(1/factor, 1/factor)


class VisualizadorGrafo(QWidget):
    vertice_clicked = Signal(int)

    def __init__(self, titulo="Grafo", parent=None, es_editable=False):
        super().__init__(parent)
        self.titulo = titulo
        self.es_editable = es_editable
        self.num_vertices = 0
        self.aristas = []
        self.pesos = []
        self.etiquetas = {}
        self.posiciones = []
        self.radio = 20
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.scene = GrafoScene(self)
        self.scene.set_visualizador(self)
        self.view = GraficoView(self.scene, self)
        self.view.setFixedSize(450, 450)
        self.view.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 8px;")
        layout.addWidget(self.view)
        self.titulo_label = QLabel(self.titulo)
        self.titulo_label.setAlignment(Qt.AlignCenter)
        self.titulo_label.setStyleSheet("font-weight: bold; color: #003366;")
        layout.addWidget(self.titulo_label)

    def set_grafo(self, num_vertices, aristas, etiquetas, pesos=None):
        self.num_vertices = num_vertices
        self.aristas = aristas
        if pesos is None:
            self.pesos = [1] * len(aristas)
        elif isinstance(pesos, dict):
            self.pesos = [pesos.get(arista, 1) for arista in aristas]
        else:
            self.pesos = pesos
        self.etiquetas = etiquetas
        # Recalcular posiciones solo si el número de vértices cambió
        if len(self.posiciones) != self.num_vertices:
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

    def dibujar(self, ajustar_vista=True):
        self.scene.clear()
        if self.num_vertices == 0:
            texto = self.scene.addText("Grafo vacío")
            texto.setDefaultTextColor(QColor("#336699"))
            texto.setPos(150, 200)
            if ajustar_vista:
                self.ajustar_vista()
            return

        pen_arista = QPen(QColor("#336699"), 2)
        brush_vertice = QBrush(QColor("#4d9de0"))
        pen_vertice = QPen(QColor("#1e6bb8"), 2)
        text_color = QColor("white")

        # Contar aristas paralelas
        contador = defaultdict(int)
        for (u,v) in self.aristas:
            if u == v:
                contador[('loop', u)] += 1
            else:
                contador[tuple(sorted((u,v)))] += 1
        offset_actual = defaultdict(int)

        for idx, (u, v) in enumerate(self.aristas):
            x1, y1 = self.posiciones[u]
            x2, y2 = self.posiciones[v]
            peso = self.pesos[idx] if idx < len(self.pesos) else ""

            if u == v:
                radio_bucle = self.radio * 1.2
                centro_x = x1
                centro_y = y1 - radio_bucle
                path = QPainterPath()
                path.arcMoveTo(centro_x - radio_bucle, centro_y - radio_bucle, 2*radio_bucle, 2*radio_bucle, -90)
                path.arcTo(centro_x - radio_bucle, centro_y - radio_bucle, 2*radio_bucle, 2*radio_bucle, -90, 360)
                self.scene.addPath(path, pen_arista)
                if peso:
                    text = self.scene.addText(str(peso))
                    text.setDefaultTextColor(QColor("#003366"))
                    text.setPos(x1 - 10, y1 - radio_bucle - 10)
                    text.setScale(0.8)
            else:
                key = tuple(sorted((u,v)))
                total = contador[key]
                actual = offset_actual[key]
                offset_actual[key] += 1
                if total > 1:
                    dx = x2 - x1
                    dy = y2 - y1
                    dist = math.hypot(dx, dy)
                    if dist > 0.01:
                        ux = dx / dist
                        uy = dy / dist
                        px = -uy
                        py = ux
                        factor = (actual - (total-1)/2) / (total) * 2
                        offset = factor * 40
                        mid_x = (x1 + x2)/2 + px * offset
                        mid_y = (y1 + y2)/2 + py * offset
                        path = QPainterPath()
                        path.moveTo(x1, y1)
                        path.quadTo(mid_x, mid_y, x2, y2)
                        self.scene.addPath(path, pen_arista)
                    else:
                        self.scene.addLine(x1, y1, x2, y2, pen_arista)
                else:
                    self.scene.addLine(x1, y1, x2, y2, pen_arista)

                if peso:
                    if total > 1:
                        mx = (x1 + x2)/2 + px * offset/2
                        my = (y1 + y2)/2 + py * offset/2
                    else:
                        mx = (x1 + x2)/2
                        my = (y1 + y2)/2
                    text = self.scene.addText(str(peso))
                    text.setDefaultTextColor(QColor("#003366"))
                    text.setPos(mx - 5, my - 5)
                    text.setScale(0.8)

        # Vértices
        for i, (x, y) in enumerate(self.posiciones):
            self.scene.addEllipse(x-self.radio, y-self.radio, 2*self.radio, 2*self.radio,
                                  pen_vertice, brush_vertice)
            etiq = self.etiquetas.get(i, str(i+1))
            texto = self.scene.addText(etiq)
            texto.setDefaultTextColor(text_color)
            rect = texto.boundingRect()
            texto.setPos(x - rect.width()/2, y - rect.height()/2)

        if ajustar_vista:
            self.ajustar_vista()

    def ajustar_vista(self):
        if self.num_vertices > 0:
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)