# -*- coding: utf-8 -*-
"""
Controlador para árboles de múltiples residuos (Trie con pares de bits).
Basado en el MultiplesResiduosController del proyecto anterior.
"""

# Código binario de 5 bits para A-Z (mayúsculas)
CODIGO_BINARIO = {
    'A': '00001', 'B': '00010', 'C': '00011', 'D': '00100', 'E': '00101',
    'F': '00110', 'G': '00111', 'H': '01000', 'I': '01001', 'J': '01010',
    'K': '01011', 'L': '01100', 'M': '01101', 'N': '01110', 'O': '01111',
    'P': '10000', 'Q': '10001', 'R': '10010', 'S': '10011', 'T': '10100',
    'U': '10101', 'V': '10110', 'W': '10111', 'X': '11000', 'Y': '11001',
    'Z': '11010'
}


class NodoMultiple:
    """Nodo del árbol de múltiples residuos."""
    def __init__(self, letra=None, is_leaf=False):
        self.is_leaf = is_leaf      # True si es hoja (contiene letra)
        self.letra = letra          # Letra almacenada (si es hoja)
        self.children = {}          # Hijos: claves de 2 bits (para primeros niveles) o 1 bit (último)


class ArbolMultiResiduosController:
    def __init__(self):
        self.root = NodoMultiple()
        self.codigos = CODIGO_BINARIO
        self.letras_insertadas = set()

    def _dividir_en_pares(self, codigo):
        """
        Divide el código de 5 bits en pares: [2 bits, 2 bits, 1 bit]
        """
        if len(codigo) != 5:
            raise ValueError("Código debe tener 5 bits")
        return [codigo[0:2], codigo[2:4], codigo[4:5]]

    def insertar_letra(self, letra: str) -> str:
        """
        Inserta una letra en el árbol.
        Retorna "OK" si se insertó, o un mensaje de error.
        """
        letra = letra.upper()
        if letra not in self.codigos:
            return f"Letra no válida: {letra}"
        if letra in self.letras_insertadas:
            return "La letra ya existe"

        self._insertar_letra_rec(letra)
        self.letras_insertadas.add(letra)
        return "OK"

    def _insertar_letra_rec(self, letra: str):
        codigo = self.codigos[letra]
        pares = self._dividir_en_pares(codigo)
        nodo = self.root

        for i, par in enumerate(pares):
            # Si no existe el hijo para este par, crearlo
            if par not in nodo.children:
                # Si es el último nivel, crear hoja con la letra
                if i == len(pares) - 1:
                    nodo.children[par] = NodoMultiple(letra=letra, is_leaf=True)
                else:
                    # Crear nodo interno (no hoja)
                    nodo.children[par] = NodoMultiple()
                # Moverse al hijo recién creado (solo si no es el último, para continuar)
                if i < len(pares) - 1:
                    nodo = nodo.children[par]
                else:
                    # Último nivel, terminamos
                    return
            else:
                # El hijo ya existe
                hijo = nodo.children[par]
                if i == len(pares) - 1:
                    # Último nivel: debe ser hoja
                    # En múltiples residuos, si ya hay una letra diferente, se produce colisión.
                    # El proyecto anterior no implementaba resolución de colisiones (solo mantenía una letra).
                    # Por simplicidad, si ya hay una letra y es diferente, no hacemos nada (o podríamos manejar lista).
                    # En nuestro caso, si la letra ya existe (ya verificamos duplicado), no debería pasar.
                    # Si el nodo no es hoja, lo convertimos en hoja (esto no debería ocurrir en un árbol bien construido)
                    if not hijo.is_leaf:
                        hijo.is_leaf = True
                        hijo.letra = letra
                    # Si ya es hoja y tiene otra letra, no insertamos (colisión no resuelta)
                    # Podríamos implementar una lista, pero por ahora omitimos.
                else:
                    # Nivel intermedio: continuar
                    nodo = hijo

    def insertar_palabra(self, palabra: str):
        """
        Inserta todas las letras de una palabra.
        Retorna (éxito: bool, mensaje: str)
        """
        palabra = palabra.upper().strip()
        if not palabra:
            return False, "Palabra vacía"
        nuevas = []
        for letra in palabra:
            if letra not in self.codigos:
                return False, f"Letra no válida: {letra}"
            if letra not in self.letras_insertadas:
                self._insertar_letra_rec(letra)
                self.letras_insertadas.add(letra)
                nuevas.append(letra)
        if nuevas:
            return True, f"Letras insertadas: {', '.join(nuevas)}"
        else:
            return True, "Todas las letras ya existían"

    def buscar_letra(self, letra: str):
        """
        Busca una letra y devuelve la ruta de pares (como string, ej: "00-01-1") si existe,
        o None si no existe.
        """
        letra = letra.upper()
        if letra not in self.codigos:
            return None
        codigo = self.codigos[letra]
        pares = self._dividir_en_pares(codigo)
        nodo = self.root
        ruta = []
        for i, par in enumerate(pares):
            if par not in nodo.children:
                return None
            ruta.append(par)
            hijo = nodo.children[par]
            if i == len(pares) - 1:
                # Último nivel
                if hijo.is_leaf and hijo.letra == letra:
                    return "-".join(ruta)
                else:
                    return None
            nodo = hijo
        return None

    def eliminar_letra(self, letra: str):
        """
        Elimina una letra y reconstruye el árbol con las restantes.
        Retorna "OK" o mensaje de error.
        """
        letra = letra.upper()
        if letra not in self.codigos:
            return "Letra no válida"
        if letra not in self.letras_insertadas:
            return "La letra no existe"
        self.letras_insertadas.remove(letra)
        # Reconstruir árbol desde cero
        self.root = NodoMultiple()
        for l in self.letras_insertadas:
            self._insertar_letra_rec(l)
        return "OK"

    def eliminar_arbol(self):
        """Elimina todo el árbol."""
        self.root = NodoMultiple()
        self.letras_insertadas.clear()

    def obtener_raiz(self):
        return self.root