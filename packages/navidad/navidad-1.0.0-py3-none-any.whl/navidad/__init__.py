"""
Navidad - Un árbol de navidad colorido en tu terminal 🎄

Uso:
    Desde terminal:
        $ navidad
        $ navidad --grande
    
    Desde Python:
        >>> import navidad
        >>> navidad.mostrar_arbol()
        >>> navidad.mostrar_arbol(grande=True)
"""

__version__ = "1.0.0"
__author__ = "Tu Nombre"

from .main import mostrar_arbol, obtener_arbol, obtener_arbol_grande, main

__all__ = ["mostrar_arbol", "obtener_arbol", "obtener_arbol_grande", "main"]

# Mostrar el árbol automáticamente al hacer "import navidad"
mostrar_arbol()
