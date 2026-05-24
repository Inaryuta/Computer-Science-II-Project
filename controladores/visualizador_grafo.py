import math
from collections import defaultdict

from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QPolygonF, QWheelEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QGraphicsScene, QGraphicsView,
)

# ------------------------------------------------------------------ #
#  Constantes de color por defecto                                    #
# ------------------------------------------------------------------ #
COLOR_VERTICE_DEFAULT = "#4d9de0"
COLOR_BORDE_VERTICE   = "#1e6bb8"
COLOR_ARISTA_DEFAULT  = "#336699"
COLOR_TEXTO_VERTICE   = "white"
COLOR_TEXTO_PESO      = "#003366"


# ------------------------------------------------------------------ #
#  Escena con arrastre de vértices                                    #
# ------------------------------------------------------------------ #
class GrafoSceneColoreable(QGraphicsScene):
    """Escena personalizada que permite arrastrar vértices cuando es_editable=True."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.visualizador = None
        self._dragging_vertex = None
        self._drag_start_pos = None

    def set_visualizador(self, vis):
        self.visualizador = vis

    def mousePressEvent(self, event):
        if not self.visualizador or not self.visualizador.es_editable:
            super().mousePressEvent(event)
            return
        pos = event.scenePos()
        for i, (x, y) in enumerate(self.visualizador.posiciones):
            if math.hypot(x - pos.x(), y - pos.y()) <= self.visualizador.radio:
                self._dragging_vertex = i
                self._drag_start_pos = pos
                self.visualizador.vertice_clicked.emit(i)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging_vertex is not None and self.visualizador:
            pos = event.scenePos()
            delta = pos - self._drag_start_pos
            x, y = self.visualizador.posiciones[self._dragging_vertex]
            self.visualizador.posiciones[self._dragging_vertex] = (x + delta.x(), y + delta.y())
            self._drag_start_pos = pos
            self.visualizador.dibujar(ajustar_vista=False)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging_vertex is not None:
            self._dragging_vertex = None
            self._drag_start_pos = None
            if self.visualizador:
                self.visualizador.ajustar_vista()
            event.accept()
            return
        super().mouseReleaseEvent(event)


# ------------------------------------------------------------------ #
#  Vista con zoom por rueda                                           #
# ------------------------------------------------------------------ #
class GraficoViewColoreable(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.1 if event.angleDelta().y() > 0 else 1 / 1.1
        self.scale(factor, factor)


# ------------------------------------------------------------------ #
#  Widget principal de visualización                                  #
# ------------------------------------------------------------------ #
class VisualizadorGrafoColoreable(QWidget):
    """
    Visualizador de grafos con soporte de coloreado de vértices y aristas.
    Parámetros:
        titulo      – etiqueta mostrada bajo el canvas
        es_editable – habilita arrastre de vértices con el ratón
        dirigido    – dibuja flechas en las aristas
    """
    vertice_clicked = Signal(int)

    def __init__(
        self,
        titulo: str = "Grafo",
        parent=None,
        es_editable: bool = False,
        dirigido: bool = False,
    ):
        super().__init__(parent)
        self.titulo = titulo
        self.es_editable = es_editable
        self.dirigido = dirigido

        # Estado del grafo
        self.num_vertices: int = 0
        self.aristas: list[tuple] = []
        self.pesos: list = []
        self.etiquetas: dict = {}
        self.posiciones: list[tuple] = []
        self.radio: int = 20

        # Estado de coloreado
        self.colores_vertices: dict[int, str] = {}   # idx → hex
        self.colores_aristas: dict[int, str] = {}    # arista_idx → hex

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.scene = GrafoSceneColoreable(self)
        self.scene.set_visualizador(self)

        self.view = GraficoViewColoreable(self.scene, self)
        self.view.setFixedSize(450, 450)
        self.view.setStyleSheet(
            "background-color: white; border: 2px solid #99ccff; border-radius: 8px;"
        )
        layout.addWidget(self.view)

        self.titulo_label = QLabel(self.titulo)
        self.titulo_label.setAlignment(Qt.AlignCenter)
        self.titulo_label.setStyleSheet("font-weight: bold; color: #003366;")
        layout.addWidget(self.titulo_label)

    # ---------------------------------------------------------------- #
    #  API pública                                                       #
    # ---------------------------------------------------------------- #

    def set_grafo(
        self,
        num_vertices: int,
        aristas: list,
        etiquetas: dict,
        pesos: list | None = None,
        colores_vertices: dict | None = None,
        colores_aristas: dict | None = None,
    ):
        """Actualiza el grafo completo y redibuja."""
        self.num_vertices = num_vertices
        self.aristas = aristas
        self.pesos = pesos if isinstance(pesos, list) else [1] * len(aristas)
        self.etiquetas = etiquetas
        self.colores_vertices = colores_vertices or {}
        self.colores_aristas = colores_aristas or {}

        # Recalcular posiciones solo si cambió el número de vértices
        if len(self.posiciones) != self.num_vertices:
            self._calcular_posiciones()

        self.dibujar()

    def set_colores(
        self,
        colores_vertices: dict | None = None,
        colores_aristas: dict | None = None,
    ):
        """Actualiza solo los colores y redibuja sin mover vértices."""
        if colores_vertices is not None:
            self.colores_vertices = colores_vertices
        if colores_aristas is not None:
            self.colores_aristas = colores_aristas
        self.dibujar(ajustar_vista=False)

    # ---------------------------------------------------------------- #
    #  Dibujo                                                            #
    # ---------------------------------------------------------------- #

    def dibujar(self, ajustar_vista: bool = True):
        self.scene.clear()

        if self.num_vertices == 0:
            t = self.scene.addText("Grafo vacío")
            t.setDefaultTextColor(QColor("#336699"))
            t.setPos(150, 200)
            if ajustar_vista:
                self.ajustar_vista()
            return

        self._dibujar_aristas()
        self._dibujar_vertices()

        if ajustar_vista:
            self.ajustar_vista()

    def ajustar_vista(self):
        if self.num_vertices > 0:
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    # ---------------------------------------------------------------- #
    #  Helpers internos                                                  #
    # ---------------------------------------------------------------- #

    def _calcular_posiciones(self):
        self.posiciones = []
        if self.num_vertices == 0:
            return
        cx, cy = 225, 225
        r_circ = 170
        a0 = -math.pi / 2
        paso = 2 * math.pi / self.num_vertices
        for i in range(self.num_vertices):
            a = a0 + i * paso
            self.posiciones.append((cx + r_circ * math.cos(a), cy + r_circ * math.sin(a)))

    def _pen_arista(self, idx: int) -> QPen:
        color = self.colores_aristas.get(idx, COLOR_ARISTA_DEFAULT)
        ancho = 3 if idx in self.colores_aristas else 2
        return QPen(QColor(color), ancho)

    def _dibujar_aristas(self):
        # Contar aristas paralelas para el desplazamiento de curvas
        contador: dict = defaultdict(int)
        for (u, v) in self.aristas:
            key = ("loop", u) if u == v else tuple(sorted((u, v)))
            contador[key] += 1
        offset_actual: dict = defaultdict(int)

        for idx, (u, v) in enumerate(self.aristas):
            pen = self._pen_arista(idx)
            x1, y1 = self.posiciones[u]
            x2, y2 = self.posiciones[v]
            peso = self.pesos[idx] if idx < len(self.pesos) else ""

            if u == v:
                self._dibujar_bucle(x1, y1, pen, peso)
                continue

            key = tuple(sorted((u, v)))
            total = contador[key]
            actual = offset_actual[key]
            offset_actual[key] += 1

            # Posición intermedia por defecto (línea recta)
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2

            if total > 1:
                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy)
                if dist > 0.01:
                    px, py = -dy / dist, dx / dist
                    factor = (actual - (total - 1) / 2) / total * 2
                    offset = factor * 40
                    mid_x = (x1 + x2) / 2 + px * offset
                    mid_y = (y1 + y2) / 2 + py * offset
                    path = QPainterPath()
                    path.moveTo(x1, y1)
                    path.quadTo(mid_x, mid_y, x2, y2)
                    self.scene.addPath(path, pen)
                else:
                    self.scene.addLine(x1, y1, x2, y2, pen)
            else:
                self.scene.addLine(x1, y1, x2, y2, pen)

            if self.dirigido:
                self._dibujar_flecha(x1, y1, x2, y2, mid_x, mid_y, total, pen)

            if peso:
                t = self.scene.addText(str(peso))
                t.setDefaultTextColor(QColor(COLOR_TEXTO_PESO))
                t.setPos(mid_x - 5, mid_y - 5)
                t.setScale(0.8)

    def _dibujar_bucle(self, x: float, y: float, pen: QPen, peso=""):
        rb = self.radio * 1.2
        cx, cy = x, y - rb
        path = QPainterPath()
        path.arcMoveTo(cx - rb, cy - rb, 2 * rb, 2 * rb, -90)
        path.arcTo(cx - rb, cy - rb, 2 * rb, 2 * rb, -90, 360)
        self.scene.addPath(path, pen)
        if peso:
            t = self.scene.addText(str(peso))
            t.setDefaultTextColor(QColor(COLOR_TEXTO_PESO))
            t.setPos(x - 10, y - 2 * rb - 10)
            t.setScale(0.8)

    def _dibujar_flecha(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        mid_x: float, mid_y: float,
        total: int,
        pen: QPen,
    ):
        """Dibuja la punta de flecha para aristas dirigidas."""
        if total > 1:
            dx, dy = x2 - mid_x, y2 - mid_y
        else:
            dx, dy = x2 - x1, y2 - y1

        dist = math.hypot(dx, dy)
        if dist < 0.01:
            return

        angulo = math.atan2(dy, dx)
        cos_a, sin_a = math.cos(angulo), math.sin(angulo)
        x2a = x2 - cos_a * self.radio
        y2a = y2 - sin_a * self.radio
        punta = QPointF(x2a, y2a)

        af = math.radians(25)
        lf = 15
        dfx, dfy = -cos_a * lf, -sin_a * lf
        a1 = QPointF(
            x2a + dfx * math.cos(af) - dfy * math.sin(af),
            y2a + dfx * math.sin(af) + dfy * math.cos(af),
        )
        a2 = QPointF(
            x2a + dfx * math.cos(-af) - dfy * math.sin(-af),
            y2a + dfx * math.sin(-af) + dfy * math.cos(-af),
        )
        flecha = QPolygonF([punta, a1, a2])
        self.scene.addPolygon(flecha, pen, QBrush(pen.color()))

    def _dibujar_vertices(self):
        for i, (x, y) in enumerate(self.posiciones):
            color = self.colores_vertices.get(i, COLOR_VERTICE_DEFAULT)
            pen = QPen(QColor(COLOR_BORDE_VERTICE), 2)
            brush = QBrush(QColor(color))
            self.scene.addEllipse(
                x - self.radio, y - self.radio,
                2 * self.radio, 2 * self.radio,
                pen, brush,
            )
            etiq = self.etiquetas.get(i, str(i + 1))
            texto = self.scene.addText(etiq)
            texto.setDefaultTextColor(QColor(COLOR_TEXTO_VERTICE))
            rect = texto.boundingRect()
            texto.setPos(x - rect.width() / 2, y - rect.height() / 2)
            
# Alias de compatibilidad
VisualizadorGrafo = VisualizadorGrafoColoreable
# Reemplaza también el dirigido
VisualizadorGrafoDirigido = VisualizadorGrafoColoreable