import json
from PySide6.QtCore import QObject, Signal

class GrafoController(QObject):
    grafo_cambiado = Signal()

    def __init__(self, vertices=0):
        super().__init__()
        self._vertices = vertices
        # Almacenamos las aristas como lista de tuplas (origen, destino, peso)
        self._aristas = []          # lista de tuplas (u, v, peso)
        self._etiquetas = {i: str(i+1) for i in range(vertices)}

    def set_vertices(self, n):
        self._vertices = n
        self._aristas = []
        self._etiquetas = {i: str(i+1) for i in range(n)}
        self.grafo_cambiado.emit()

    def agregar_arista(self, u, v, peso=1):
        # Permite bucles (u == v) y aristas paralelas
        self._aristas.append((u, v, peso))
        self.grafo_cambiado.emit()
        return True

    def eliminar_arista(self, u, v, indice=None):
        """
        Elimina una arista específica.
        Si hay múltiples iguales, se puede eliminar una en particular por índice.
        Si no se da índice, elimina la primera coincidencia.
        """
        if indice is not None:
            try:
                del self._aristas[indice]
                self.grafo_cambiado.emit()
                return True
            except IndexError:
                return False
        else:
            for i, (a, b, _) in enumerate(self._aristas):
                if (a == u and b == v) or (a == v and b == u):
                    del self._aristas[i]
                    self.grafo_cambiado.emit()
                    return True
        return False

    def eliminar_vertice(self, idx):
        if idx < 0 or idx >= self._vertices:
            return False
        # Remover aristas que involucran este vértice
        nuevas_aristas = []
        for (u, v, p) in self._aristas:
            if u != idx and v != idx:
                # Reindexar
                nu = u if u < idx else u-1
                nv = v if v < idx else v-1
                nuevas_aristas.append((nu, nv, p))
        self._aristas = nuevas_aristas
        # Reindexar etiquetas
        nuevas_etiquetas = {}
        for i in range(self._vertices):
            if i < idx:
                nuevas_etiquetas[i] = self._etiquetas[i]
            elif i > idx:
                nuevas_etiquetas[i-1] = self._etiquetas[i]
        self._vertices -= 1
        self._etiquetas = nuevas_etiquetas
        self.grafo_cambiado.emit()
        return True

    def cambiar_etiqueta(self, idx, nueva):
        if idx in self._etiquetas:
            self._etiquetas[idx] = nueva
            self.grafo_cambiado.emit()
            return True
        return False

    def obtener_datos(self):
        # Devuelve aristas como lista de tuplas (origen, destino) más pesos separados?
        # Para compatibilidad, dejamos aristas como lista de (u,v) y pesos por separado
        aristas_sin_peso = [(u, v) for (u, v, _) in self._aristas]
        pesos = [p for (_, _, p) in self._aristas]
        return {
            'vertices': self._vertices,
            'aristas': aristas_sin_peso,
            'pesos': pesos,           # lista en paralelo a aristas
            'etiquetas': self._etiquetas
        }

    def cargar_datos(self, datos):
        self._vertices = datos['vertices']
        aristas_sin_peso = datos.get('aristas', [])
        pesos = datos.get('pesos', [1]*len(aristas_sin_peso))
        self._aristas = []
        for i, (u, v) in enumerate(aristas_sin_peso):
            p = pesos[i] if i < len(pesos) else 1
            self._aristas.append((u, v, p))
        self._etiquetas = datos.get('etiquetas', {i: str(i+1) for i in range(self._vertices)})
        self.grafo_cambiado.emit()

    def guardar_json(self, ruta):
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(self.obtener_datos(), f, indent=4)

    def cargar_json(self, ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        self.cargar_datos(datos)

    def matriz_adyacencia(self):
        # Para multigrafos, la matriz de adyacencia puede ser el número de aristas entre i y j
        mat = [[0]*self._vertices for _ in range(self._vertices)]
        for (u, v, _) in self._aristas:
            mat[u][v] += 1
            if u != v:
                mat[v][u] += 1
        return mat

    def lista_adyacencia(self):
        adj = [[] for _ in range(self._vertices)]
        for (u, v, p) in self._aristas:
            adj[u].append((v, p))
            if u != v:
                adj[v].append((u, p))
        return adj