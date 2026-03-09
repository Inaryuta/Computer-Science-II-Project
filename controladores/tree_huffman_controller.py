import heapq
from collections import Counter


class NodoHuffman:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        # Si las frecuencias son iguales, comparar por el carácter
        if self.freq == other.freq:
            return (self.char or '') < (other.char or '')
        return self.freq < other.freq


class HuffmanController:
    def __init__(self):
        self.root = None
        self.codigos = {}          # {carácter: código binario}
        self.frecuencias = {}       # {carácter: frecuencia}
        self.texto_original = ""

    def construir_arbol(self, texto):
        """
        Construye el árbol de Huffman a partir de un texto.
        Lanza ValueError si el texto está vacío.
        """
        if not texto:
            raise ValueError("El texto no puede estar vacío")

        self.texto_original = texto
        self.frecuencias = Counter(texto)

        # Crear heap con nodos hoja
        heap = []
        for char, freq in self.frecuencias.items():
            nodo = NodoHuffman(char, freq)
            heapq.heappush(heap, nodo)

        # Construir árbol
        while len(heap) > 1:
            izq = heapq.heappop(heap)
            der = heapq.heappop(heap)
            padre = NodoHuffman(None, izq.freq + der.freq, izq, der)
            heapq.heappush(heap, padre)

        self.root = heap[0] if heap else None
        self.codigos = {}
        self._generar_codigos(self.root, "")

    def _generar_codigos(self, nodo, codigo_actual):
        if nodo is None:
            return
        if nodo.char is not None:  # hoja
            self.codigos[nodo.char] = codigo_actual if codigo_actual else "0"
            return
        self._generar_codigos(nodo.left, codigo_actual + "0")
        self._generar_codigos(nodo.right, codigo_actual + "1")

    def obtener_codigos(self):
        return self.codigos

    def obtener_frecuencias(self):
        return self.frecuencias

    def codificar_texto(self):
        if not self.texto_original or not self.codigos:
            return ""
        return "".join(self.codigos[char] for char in self.texto_original)

    def decodificar_texto(self, codigo_binario):
        if not self.root or not codigo_binario:
            return ""
        resultado = []
        nodo_actual = self.root
        for bit in codigo_binario:
            nodo_actual = nodo_actual.left if bit == '0' else nodo_actual.right
            if nodo_actual.char is not None:
                resultado.append(nodo_actual.char)
                nodo_actual = self.root
        return "".join(resultado)

    def calcular_compresion(self):
        if not self.texto_original or not self.codigos:
            return {}
        bits_originales = len(self.texto_original) * 8
        bits_comprimidos = sum(len(self.codigos[char]) for char in self.texto_original)
        ahorro = bits_originales - bits_comprimidos
        porcentaje = (ahorro / bits_originales) * 100 if bits_originales else 0
        return {
            "bits_originales": bits_originales,
            "bits_comprimidos": bits_comprimidos,
            "ahorro_bits": ahorro,
            "porcentaje_compresion": round(porcentaje, 2)
        }

    def limpiar(self):
        self.root = None
        self.codigos = {}
        self.frecuencias = {}
        self.texto_original = ""