# -*- coding: utf-8 -*-
"""
Controlador para árboles de residuos (Trie binario).
Basado en el TriesController del proyecto anterior.
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


class NodoResiduo:
    """Nodo del árbol de residuos."""
    def __init__(self, letra=None, is_link=False):
        self.letra = letra          # Letra almacenada (si es hoja)
        self.is_link = is_link      # True si es nodo de enlace (*)
        self.children = {'0': None, '1': None}  # Hijos para bits 0 y 1


class ArbolResiduosController:
    def __init__(self):
        self.root = NodoResiduo(is_link=True)  # raíz siempre es enlace
        self.codigos = CODIGO_BINARIO
        self.letras_insertadas = set()  # conjunto de letras presentes

    # ------------------------------------------------------------
    # Inserción
    # ------------------------------------------------------------
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

    def _insertar_letra_rec(self, letra: str, nodo=None, pos=0):
        """
        Método recursivo que sigue la lógica de inserción con colisiones.
        Si no se pasa nodo, se empieza desde la raíz.
        """
        if nodo is None:
            nodo = self.root
        codigo = self.codigos[letra]

        while pos < len(codigo):
            bit = codigo[pos]

            # Si no existe el hijo para este bit
            if bit not in nodo.children or nodo.children[bit] is None:
                # Crear nodo hoja con la letra
                nodo.children[bit] = NodoResiduo(letra=letra, is_link=False)
                return

            hijo = nodo.children[bit]

            # Si el hijo es un nodo de enlace, continuamos bajando
            if hijo.is_link:
                nodo = hijo
                pos += 1
                continue

            # Si el hijo es un nodo hoja (tiene letra) -> COLISIÓN
            letra_existente = hijo.letra

            # Si es la misma letra, no debería ocurrir porque ya verificamos duplicado
            if letra == letra_existente:
                return

            # Convertir el nodo hoja en enlace
            hijo.is_link = True
            hijo.letra = None

            # Obtener códigos de ambas letras
            codigo_existente = self.codigos[letra_existente]
            codigo_nuevo = codigo

            # Reinsertar ambas desde la siguiente posición
            pos_siguiente = pos + 1

            # Insertar la letra existente
            self._insertar_desde_posicion(hijo, letra_existente, codigo_existente, pos_siguiente)

            # Insertar la letra nueva
            self._insertar_desde_posicion(hijo, letra, codigo_nuevo, pos_siguiente)

            return

        # Si se acabó el código sin colisión, pero llegamos a un nodo hoja? No debería pasar.
        # Si llegamos aquí, significa que el código terminó y el nodo actual debería ser hoja,
        # pero ya verificamos duplicado. En todo caso, si el nodo actual es enlace, lo convertimos en hoja.
        if nodo.is_link:
            nodo.is_link = False
            nodo.letra = letra
        else:
            # Esto no debería ocurrir
            raise Exception("Error inesperado en inserción")

    def _insertar_desde_posicion(self, nodo, letra, codigo, pos):
        """
        Inserta una letra desde una posición dada del código,
        manejando posibles colisiones en el camino.
        """
        while pos < len(codigo):
            bit = codigo[pos]

            # Si no existe el hijo
            if bit not in nodo.children or nodo.children[bit] is None:
                nodo.children[bit] = NodoResiduo(letra=letra, is_link=False)
                return

            hijo = nodo.children[bit]

            # Si es enlace, continuamos
            if hijo.is_link:
                nodo = hijo
                pos += 1
                continue

            # Si es hoja, hay otra colisión
            letra_existente = hijo.letra
            if letra_existente == letra:
                # No debería pasar porque la letra no está repetida
                return

            # Convertir en enlace
            hijo.is_link = True
            hijo.letra = None
            codigo_existente = self.codigos[letra_existente]

            # Reinsertar la letra existente desde pos+1
            self._insertar_desde_posicion(hijo, letra_existente, codigo_existente, pos + 1)

            # Continuar con la letra actual desde el mismo nodo (que ahora es enlace)
            nodo = hijo
            pos += 1

        # Fin del código: asignar letra al nodo actual
        if nodo.is_link:
            nodo.is_link = False
            nodo.letra = letra
        else:
            # No debería pasar
            raise Exception("Error en inserción desde posición")

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

    # ------------------------------------------------------------
    # Búsqueda
    # ------------------------------------------------------------
    def buscar_letra(self, letra: str):
        """
        Busca una letra y devuelve la ruta de bits (como string) si existe,
        o None si no existe.
        """
        letra = letra.upper()
        if letra not in self.codigos:
            return None
        codigo = self.codigos[letra]
        nodo = self.root
        pos = 0
        ruta = ""
        while pos < len(codigo):
            bit = codigo[pos]
            if bit not in nodo.children or nodo.children[bit] is None:
                return None
            hijo = nodo.children[bit]
            ruta += bit
            if hijo.is_link:
                nodo = hijo
                pos += 1
                continue
            # Es hoja
            if hijo.letra == letra:
                return ruta
            else:
                return None
        return None

    # ------------------------------------------------------------
    # Eliminación
    # ------------------------------------------------------------
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
        self.root = NodoResiduo(is_link=True)
        for l in self.letras_insertadas:
            self._insertar_letra_rec(l)
        return "OK"

    def eliminar_arbol(self):
        """Elimina todo el árbol."""
        self.root = NodoResiduo(is_link=True)
        self.letras_insertadas.clear()

    # ------------------------------------------------------------
    # Utilidades para dibujo (opcional)
    # ------------------------------------------------------------
    def obtener_raiz(self):
        return self.root