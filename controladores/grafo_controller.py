import json
from PySide6.QtCore import QObject, Signal

class GrafoController(QObject):
    grafo_cambiado = Signal()

    def __init__(self, vertices=0):
        super().__init__()
        self._vertices = vertices
        self._aristas = []
        self._pesos = {}
        self._etiquetas = {i: str(i+1) for i in range(vertices)}

    def set_vertices(self, n):
        self._vertices = n
        self._aristas = []
        self._pesos = {}
        self._etiquetas = {i: str(i+1) for i in range(n)}
        self.grafo_cambiado.emit()

    def agregar_arista(self, u, v, peso=1):
        if u == v:
            return False
        arista = tuple(sorted((u, v)))
        if arista not in self._aristas:
            self._aristas.append(arista)
            self._pesos[arista] = peso
            self.grafo_cambiado.emit()
            return True
        return False

    def eliminar_arista(self, u, v):
        arista = tuple(sorted((u, v)))
        if arista in self._aristas:
            self._aristas.remove(arista)
            self._pesos.pop(arista, None)
            self.grafo_cambiado.emit()
            return True
        return False

    def eliminar_vertice(self, idx):
        if idx < 0 or idx >= self._vertices:
            return False
        nuevas_aristas = []
        nuevos_pesos = {}
        for (u, v) in self._aristas:
            if u != idx and v != idx:
                nu = u if u < idx else u-1
                nv = v if v < idx else v-1
                if nu > nv:
                    nu, nv = nv, nu
                nueva_arista = (nu, nv)
                nuevas_aristas.append(nueva_arista)
                nuevos_pesos[nueva_arista] = self._pesos[(u, v)]
        self._aristas = nuevas_aristas
        self._pesos = nuevos_pesos
        nuevas_etiquetas = {}
        for i in range(self._vertices):
            if i < idx:
                nuevas_etiquetas[i] = self._etiquetas[i]
            elif i > idx:
                nuevas_etiquetas[i-1] = self._etiquetas[i]
        self._etiquetas = nuevas_etiquetas
        self._vertices -= 1
        self.grafo_cambiado.emit()
        return True

    def cambiar_etiqueta(self, idx, nueva):
        if idx in self._etiquetas:
            self._etiquetas[idx] = nueva
            self.grafo_cambiado.emit()
            return True
        return False

    def obtener_datos(self):
        return {
            'vertices': self._vertices,
            'aristas': self._aristas,
            'pesos': self._pesos,
            'etiquetas': self._etiquetas
        }

    def cargar_datos(self, datos):
        self._vertices = datos['vertices']
        self._aristas = datos['aristas']
        self._pesos = datos['pesos']
        self._etiquetas = datos['etiquetas']
        self.grafo_cambiado.emit()

    def guardar_json(self, ruta):
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(self.obtener_datos(), f, indent=4)

    def cargar_json(self, ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        self.cargar_datos(datos)

    def matriz_adyacencia(self):
        INF = float('inf')
        n = self._vertices
        mat = [[INF]*n for _ in range(n)]
        for i in range(n):
            mat[i][i] = 0
        for (u,v), w in self._pesos.items():
            mat[u][v] = w
            mat[v][u] = w
        return mat

    def lista_adyacencia(self):
        adj = [[] for _ in range(self._vertices)]
        for (u,v), w in self._pesos.items():
            adj[u].append((v,w))
            adj[v].append((u,w))
        return adj