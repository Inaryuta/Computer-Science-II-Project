import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from PySide6.QtCore import QObject, Signal

class BellmanFordController(QObject):
    grafo_cambiado = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.num_vertices = 0
        self.aristas = []          # lista de tuplas (origen, destino, peso)
        self.etiquetas = {}        # diccionario {indice: etiqueta}
        self.ultima_arista = None  # para eliminar
        self.original_aristas = [] # copia de seguridad

    def crear_grafo_vacio(self, num_vertices):
        """Crea un grafo sin aristas con el número de vértices dado"""
        self.num_vertices = num_vertices
        self.aristas = []
        self.etiquetas = {i: str(i+1) for i in range(num_vertices)}
        self.grafo_cambiado.emit()

    def agregar_arista(self, origen, destino, peso):
        """Agrega una arista al grafo"""
        self.aristas.append((origen, destino, peso))
        self.grafo_cambiado.emit()

    def eliminar_ultima_arista(self):
        """Elimina la última arista agregada"""
        if self.aristas:
            self.aristas.pop()
            self.grafo_cambiado.emit()

    def obtener_datos(self):
        """Devuelve los datos del grafo en formato para visualizador"""
        aristas_sin_peso = [(u, v) for (u, v, _) in self.aristas]
        pesos = [p for (_, _, p) in self.aristas]
        return {
            'vertices': self.num_vertices,
            'aristas': aristas_sin_peso,
            'pesos': pesos,
            'etiquetas': self.etiquetas
        }

    def guardar_grafo(self, ruta):
        """Guarda el grafo en formato JSON"""
        datos = {
            'vertices': self.num_vertices,
            'aristas': self.aristas,
            'etiquetas': self.etiquetas
        }
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def cargar_grafo_desde_archivo(self, ruta):
        """Carga un grafo desde un archivo JSON"""
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        self.num_vertices = datos['vertices']
        self.aristas = [tuple(a) for a in datos['aristas']]
        self.etiquetas = {int(k): v for k, v in datos.get('etiquetas', {}).items()}
        self.grafo_cambiado.emit()

    def ejecutar_bellman(self, origen):
        """
        Ejecuta el algoritmo de Bellman-Ford desde el vértice 'origen'.
        Retorna un diccionario con iteraciones y resultado final.
        """
        n = self.num_vertices
        INF = float('inf')
        dist = [INF] * n
        pred = [-1] * n
        dist[origen] = 0

        iteraciones = []
        # Realizar |V|-1 iteraciones
        for i in range(n-1):
            cambios = []
            for u, v, w in self.aristas:
                if dist[u] != INF and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    pred[v] = u
                    cambios.append(f"V{v+1}")
            iteraciones.append({
                'iteracion': i+1,
                'distancias': [f"V{j+1}:{d if d!=INF else '∞'}" for j,d in enumerate(dist)],
                'cambios': cambios
            })
        # Detección de ciclo negativo
        ciclo_negativo = False
        for u, v, w in self.aristas:
            if dist[u] != INF and dist[u] + w < dist[v]:
                ciclo_negativo = True
                break

        # Construir caminos
        final = {}
        for i in range(n):
            if i == origen:
                final[i] = {'distancia': 0, 'camino': f"V{i+1}"}
            elif dist[i] == INF:
                final[i] = {'distancia': INF, 'camino': '-'}
            else:
                camino = []
                actual = i
                while actual != -1:
                    camino.append(f"V{actual+1}")
                    actual = pred[actual]
                camino.reverse()
                final[i] = {'distancia': dist[i], 'camino': " → ".join(camino)}
        return {
            'iteraciones': iteraciones,
            'resultado_final': final,
            'ciclo_negativo': ciclo_negativo
        }