SECUENCIA_RUEDA = [
    0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36,
    11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9,
    22, 18, 29, 7, 28, 12, 35, 3, 26
]

ROJOS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

COLORES = {n: "rojo" if n in ROJOS else "negro" if n != 0 else "verde" for n in range(37)}

NUMEROS = list(range(37))

def obtener_color(numero):
    return COLORES.get(numero, "verde")
