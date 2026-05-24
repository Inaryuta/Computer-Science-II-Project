import json
from PySide6.QtCore import QObject, Signal

# Paleta de colores para el coloreado de vértices
PALETA_COLORES = [
    "#e74c3c",  # Rojo
    "#3498db",  # Azul
    "#2ecc71",  # Verde
    "#f39c12",  # Naranja
    "#9b59b6",  # Morado
    "#1abc9c",  # Teal
    "#e67e22",  # Naranja oscuro
    "#34495e",  # Gris azulado
    "#e91e63",  # Rosa
    "#00bcd4",  # Cyan
]

NOMBRES_COLORES = [
    "Rojo", "Azul", "Verde", "Naranja", "Morado",
    "Teal", "Naranja Oscuro", "Gris", "Rosa", "Cyan",
]


class GrafoControllerColoreable(QObject):
    """
    Controlador de grafo extendido con soporte para coloreado de vértices y aristas.
    Compatible con GrafoController original: misma API de aristas, vértices,
    etiquetas, serialización JSON. Agrega estado de color y métodos de coloreo.
    """
    grafo_cambiado = Signal()

    def __init__(self, vertices: int = 0):
        super().__init__()
        self._vertices: int = vertices
        # Lista de tuplas (u, v, peso)
        self._aristas: list[tuple] = []
        self._etiquetas: dict[int, str] = {i: str(i + 1) for i in range(vertices)}
        # Coloreado: índice de vértice/arista → color hex
        self._colores_vertices: dict[int, str] = {}
        self._colores_aristas: dict[int, str] = {}
        self._numero_cromatico: int | None = None

    # ------------------------------------------------------------------ #
    #  Vértices y aristas                                                  #
    # ------------------------------------------------------------------ #

    def set_vertices(self, n: int):
        """Reinicia el grafo con n vértices vacíos."""
        self._vertices = n
        self._aristas = []
        self._etiquetas = {i: str(i + 1) for i in range(n)}
        self._colores_vertices = {}
        self._colores_aristas = {}
        self._numero_cromatico = None
        self.grafo_cambiado.emit()

    def agregar_arista(self, u: int, v: int, peso: int = 1) -> bool:
        """Agrega arista (u, v, peso). Permite bucles y aristas paralelas."""
        self._aristas.append((u, v, peso))
        self._numero_cromatico = None
        self.grafo_cambiado.emit()
        return True

    def eliminar_arista(self, u: int, v: int, indice: int | None = None) -> bool:
        """
        Elimina una arista. Si se da índice, elimina esa posición exacta.
        Si no, elimina la primera coincidencia (u,v) o (v,u).
        Reindexar colores de aristas automáticamente.
        """
        if indice is not None:
            try:
                del self._aristas[indice]
                # Reindexar colores de aristas
                nuevos = {}
                for k, c in self._colores_aristas.items():
                    if k < indice:
                        nuevos[k] = c
                    elif k > indice:
                        nuevos[k - 1] = c
                self._colores_aristas = nuevos
                self._numero_cromatico = None
                self.grafo_cambiado.emit()
                return True
            except IndexError:
                return False
        else:
            for i, (a, b, _) in enumerate(self._aristas):
                if (a == u and b == v) or (a == v and b == u):
                    return self.eliminar_arista(u, v, indice=i)
        return False

    def eliminar_vertice(self, idx: int) -> bool:
        """Elimina un vértice y reindexar todo lo demás."""
        if idx < 0 or idx >= self._vertices:
            return False

        nuevas_aristas = []
        nuevos_colores_a: dict[int, str] = {}
        j = 0
        for i, (u, v, p) in enumerate(self._aristas):
            if u == idx or v == idx:
                continue  # arista eliminada
            nu = u if u < idx else u - 1
            nv = v if v < idx else v - 1
            nuevas_aristas.append((nu, nv, p))
            if i in self._colores_aristas:
                nuevos_colores_a[j] = self._colores_aristas[i]
            j += 1
        self._aristas = nuevas_aristas
        self._colores_aristas = nuevos_colores_a

        nuevas_etiquetas: dict[int, str] = {}
        nuevos_colores_v: dict[int, str] = {}
        for i in range(self._vertices):
            if i == idx:
                continue
            ni = i if i < idx else i - 1
            nuevas_etiquetas[ni] = self._etiquetas[i]
            if i in self._colores_vertices:
                nuevos_colores_v[ni] = self._colores_vertices[i]

        self._vertices -= 1
        self._etiquetas = nuevas_etiquetas
        self._colores_vertices = nuevos_colores_v
        self._numero_cromatico = None
        self.grafo_cambiado.emit()
        return True

    def cambiar_etiqueta(self, idx: int, nueva: str) -> bool:
        if idx in self._etiquetas:
            self._etiquetas[idx] = nueva
            self.grafo_cambiado.emit()
            return True
        return False

    # ------------------------------------------------------------------ #
    #  Coloreado                                                           #
    # ------------------------------------------------------------------ #

    def set_color_vertice(self, idx: int, color: str):
        """Asigna un color hex a un vértice y emite señal."""
        self._colores_vertices[idx] = color
        self.grafo_cambiado.emit()

    def set_color_arista(self, arista_idx: int, color: str):
        """Asigna un color hex a una arista por su índice en _aristas."""
        self._colores_aristas[arista_idx] = color
        self.grafo_cambiado.emit()

    def aplicar_coloreo(self, coloreo: dict[int, str]):
        """
        Aplica un diccionario {vertice_idx: color_hex} al grafo completo.
        Calcula el número cromático como cantidad de colores distintos usados.
        """
        self._colores_vertices = dict(coloreo)
        self._numero_cromatico = len(set(coloreo.values()))
        self.grafo_cambiado.emit()

    def resaltar_camino(self, camino: list[int], color: str = "#27ae60"):
        """
        Colorea las aristas que forman un camino (lista de vértices consecutivos).
        Útil para resaltar resultados de Dijkstra, Bellman, etc.
        """
        pares = set()
        for k in range(len(camino) - 1):
            pares.add((camino[k], camino[k + 1]))
            pares.add((camino[k + 1], camino[k]))  # no dirigido
        for i, (u, v, _) in enumerate(self._aristas):
            if (u, v) in pares:
                self._colores_aristas[i] = color
        self.grafo_cambiado.emit()

    def resetear_colores(self):
        """Quita todos los colores asignados."""
        self._colores_vertices = {}
        self._colores_aristas = {}
        self._numero_cromatico = None
        self.grafo_cambiado.emit()

    def get_color_vertice(self, idx: int) -> str | None:
        return self._colores_vertices.get(idx)

    def get_color_arista(self, arista_idx: int) -> str | None:
        return self._colores_aristas.get(arista_idx)

    @property
    def numero_cromatico(self) -> int | None:
        return self._numero_cromatico

    # ------------------------------------------------------------------ #
    #  Representaciones                                                    #
    # ------------------------------------------------------------------ #

    def matriz_adyacencia(self) -> list[list[int]]:
        mat = [[0] * self._vertices for _ in range(self._vertices)]
        for (u, v, _) in self._aristas:
            mat[u][v] += 1
            if u != v:
                mat[v][u] += 1
        return mat

    def lista_adyacencia(self) -> list[list[tuple]]:
        adj: list[list[tuple]] = [[] for _ in range(self._vertices)]
        for (u, v, p) in self._aristas:
            adj[u].append((v, p))
            if u != v:
                adj[v].append((u, p))
        return adj

    # ------------------------------------------------------------------ #
    #  Serialización                                                       #
    # ------------------------------------------------------------------ #

    def obtener_datos(self) -> dict:
        return {
            "vertices": self._vertices,
            "aristas": [(u, v) for (u, v, _) in self._aristas],
            "pesos": [p for (_, _, p) in self._aristas],
            "etiquetas": self._etiquetas,
            "colores_vertices": self._colores_vertices,
            "colores_aristas": self._colores_aristas,
        }

    def cargar_datos(self, datos: dict):
        self._vertices = datos["vertices"]
        aristas = datos.get("aristas", [])
        pesos = datos.get("pesos", [1] * len(aristas))
        self._aristas = [
            (u, v, pesos[i] if i < len(pesos) else 1)
            for i, (u, v) in enumerate(aristas)
        ]
        raw_etiq = datos.get("etiquetas", {})
        self._etiquetas = {int(k): v for k, v in raw_etiq.items()}
        raw_cv = datos.get("colores_vertices", {})
        self._colores_vertices = {int(k): v for k, v in raw_cv.items()}
        raw_ca = datos.get("colores_aristas", {})
        self._colores_aristas = {int(k): v for k, v in raw_ca.items()}
        self._numero_cromatico = None
        self.grafo_cambiado.emit()

    def guardar_json(self, ruta: str):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.obtener_datos(), f, indent=4)

    def cargar_json(self, ruta: str):
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
        self.cargar_datos(datos)
        
# Alias de compatibilidad — permite que el código existente siga funcionando
GrafoController = GrafoControllerColoreable