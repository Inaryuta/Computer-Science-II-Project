# controladores/visualizador_grafo_dirigido.py
import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QPolygonF
from controladores.visualizador_grafo import VisualizadorGrafo

class VisualizadorGrafoDirigido(VisualizadorGrafo):
    def __init__(self, titulo="Grafo Dirigido", parent=None, es_editable=False):
        super().__init__(titulo, parent, es_editable)

    def dibujar(self):
        self.scene.clear()
        if self.num_vertices == 0:
            texto = self.scene.addText("Grafo vacío")
            texto.setDefaultTextColor(QColor("#336699"))
            texto.setPos(150, 200)
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            return

        pen_arista = QPen(QColor("#336699"), 2)
        brush_vertice = QBrush(QColor("#4d9de0"))
        pen_vertice = QPen(QColor("#1e6bb8"), 2)
        text_color = QColor("white")

        from collections import defaultdict
        contador = defaultdict(int)
        for (u,v) in self.aristas:
            if u == v:
                contador[('loop', u)] += 1
            else:
                key = tuple(sorted((u,v)))
                contador[key] += 1
        offset_actual = defaultdict(int)

        for idx, (u, v) in enumerate(self.aristas):
            x1, y1 = self.posiciones[u]
            x2, y2 = self.posiciones[v]
            peso = self.pesos[idx] if idx < len(self.pesos) else ""

            if u == v:
                # Bucle (sin flecha para simplificar)
                radio_bucle = self.radio * 1.2
                centro_x = x1
                centro_y = y1 - radio_bucle
                start_angle = -90
                span_angle = 360
                path = QPainterPath()
                path.arcMoveTo(centro_x - radio_bucle, centro_y - radio_bucle, 2*radio_bucle, 2*radio_bucle, start_angle)
                path.arcTo(centro_x - radio_bucle, centro_y - radio_bucle, 2*radio_bucle, 2*radio_bucle, start_angle, span_angle)
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
                max_offset = 40
                px = py = 0
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
                        offset = factor * max_offset
                        mid_x = (x1 + x2) / 2 + px * offset
                        mid_y = (y1 + y2) / 2 + py * offset
                        path = QPainterPath()
                        path.moveTo(x1, y1)
                        path.quadTo(mid_x, mid_y, x2, y2)
                        self.scene.addPath(path, pen_arista)
                    else:
                        self.scene.addLine(x1, y1, x2, y2, pen_arista)
                else:
                    self.scene.addLine(x1, y1, x2, y2, pen_arista)

                # Calcular ángulo de la arista en el punto final
                if total > 1:
                    # Utilizar la tangente aproximada de la curva en el punto final
                    # Para curvas cuadráticas, la tangente en el punto final es la línea
                    # desde el punto de control hasta el final.
                    # Usamos la dirección del segmento desde el punto de control al final
                    if 'mid_x' in locals():
                        dx = x2 - mid_x
                        dy = y2 - mid_y
                    else:
                        dx = x2 - x1
                        dy = y2 - y1
                else:
                    dx = x2 - x1
                    dy = y2 - y1
                dist = math.hypot(dx, dy)
                if dist > 0.01:
                    angulo = math.atan2(dy, dx)
                else:
                    angulo = 0

                radio_vertice = self.radio
                cos_a = math.cos(angulo)
                sin_a = math.sin(angulo)
                x2_ajustado = x2 - cos_a * radio_vertice
                y2_ajustado = y2 - sin_a * radio_vertice
                punta = QPointF(x2_ajustado, y2_ajustado)

                angulo_flecha = math.radians(25)
                largo_flecha = 15
                dx_f = -cos_a * largo_flecha
                dy_f = -sin_a * largo_flecha
                a1_x = x2_ajustado + dx_f * math.cos(angulo_flecha) - dy_f * math.sin(angulo_flecha)
                a1_y = y2_ajustado + dx_f * math.sin(angulo_flecha) + dy_f * math.cos(angulo_flecha)
                a2_x = x2_ajustado + dx_f * math.cos(-angulo_flecha) - dy_f * math.sin(-angulo_flecha)
                a2_y = y2_ajustado + dx_f * math.sin(-angulo_flecha) + dy_f * math.cos(-angulo_flecha)
                flecha = QPolygonF([punta, QPointF(a1_x, a1_y), QPointF(a2_x, a2_y)])
                self.scene.addPolygon(flecha, pen_arista, QBrush(QColor("#336699")))

                if peso:
                    if total > 1 and 'mid_x' in locals():
                        mx = mid_x
                        my = mid_y
                    else:
                        mx = (x1 + x2) / 2
                        my = (y1 + y2) / 2
                    text = self.scene.addText(str(peso))
                    text.setDefaultTextColor(QColor("#003366"))
                    text.setPos(mx - 5, my - 5)
                    text.setScale(0.8)

        # Dibujar vértices
        for i, (x, y) in enumerate(self.posiciones):
            self.scene.addEllipse(x-self.radio, y-self.radio, 2*self.radio, 2*self.radio,
                                  pen_vertice, brush_vertice)
            etiq = self.etiquetas.get(i, str(i+1))
            texto = self.scene.addText(etiq)
            texto.setDefaultTextColor(text_color)
            rect = texto.boundingRect()
            texto.setPos(x - rect.width()/2, y - rect.height()/2)

        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)