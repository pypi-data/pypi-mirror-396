#!/usr/bin/env python3
"""
Navidad - Un árbol de navidad colorido en tu terminal 🎄
"""

def obtener_arbol():
    """Retorna el árbol de navidad con códigos de color ANSI."""
    
    # Códigos de color ANSI
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AMARILLO = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BLANCO = '\033[97m'
    DORADO = '\033[33m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Estrella
    estrella = f"{AMARILLO}{BOLD}    ★{RESET}"
    
    # Árbol con adornos
    arbol = f"""
{estrella}
{VERDE}    ▲{RESET}
{VERDE}   ▲{ROJO}●{VERDE}▲{RESET}
{VERDE}  ▲{CYAN}●{VERDE}▲{MAGENTA}●{VERDE}▲{RESET}
{VERDE} ▲{ROJO}●{VERDE}▲▲▲{CYAN}●{VERDE}▲{RESET}
{VERDE}▲{MAGENTA}●{VERDE}▲{AMARILLO}●{VERDE}▲▲▲{ROJO}●{VERDE}▲{RESET}
{DORADO}   ║║║{RESET}
{DORADO}  ══════{RESET}

{ROJO}{BOLD}  ¡Feliz Navidad!{RESET}
{BLANCO}   Merry Christmas{RESET}
"""
    return arbol


def obtener_arbol_grande():
    """Retorna un árbol de navidad más grande y elaborado."""
    
    # Códigos de color ANSI
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AMARILLO = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BLANCO = '\033[97m'
    DORADO = '\033[33m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    arbol = f"""
{AMARILLO}{BOLD}           ★{RESET}
{VERDE}          ▲▲▲{RESET}
{VERDE}         ▲{ROJO}●{VERDE}▲{CYAN}●{VERDE}▲{RESET}
{VERDE}        ▲▲▲{MAGENTA}●{VERDE}▲▲▲{RESET}
{VERDE}       ▲{CYAN}●{VERDE}▲▲▲{ROJO}●{VERDE}▲▲▲{RESET}
{VERDE}      ▲▲▲{AMARILLO}●{VERDE}▲▲▲{MAGENTA}●{VERDE}▲▲▲{RESET}
{VERDE}     ▲{ROJO}●{VERDE}▲▲▲{CYAN}●{VERDE}▲▲▲{AMARILLO}●{VERDE}▲▲▲{RESET}
{VERDE}    ▲▲▲{MAGENTA}●{VERDE}▲▲▲{ROJO}●{VERDE}▲▲▲{CYAN}●{VERDE}▲▲▲{RESET}
{VERDE}   ▲{AMARILLO}●{VERDE}▲▲▲{CYAN}●{VERDE}▲▲▲{MAGENTA}●{VERDE}▲▲▲{ROJO}●{VERDE}▲▲▲{RESET}
{DORADO}          ║║║{RESET}
{DORADO}         ║║║║║{RESET}
{DORADO}       ══════════{RESET}

{ROJO}{BOLD}     ★ ¡Feliz Navidad! ★{RESET}
{BLANCO}       Merry Christmas{RESET}
{CYAN}      Joyeux Noël{RESET}
{VERDE}      Frohe Weihnachten{RESET}
"""
    return arbol


def mostrar_arbol(grande=False):
    """Muestra el árbol de navidad en la terminal."""
    if grande:
        print(obtener_arbol_grande())
    else:
        print(obtener_arbol())


def main():
    """Punto de entrada para el comando CLI."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] in ['--grande', '-g', '--big']:
        mostrar_arbol(grande=True)
    else:
        mostrar_arbol(grande=False)


if __name__ == "__main__":
    main()
