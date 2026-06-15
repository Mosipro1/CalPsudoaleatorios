from . import extraer_digitos_centrales


def generar(semilla, iteraciones, digitos_centrales=4):
    resultados = []
    xn = semilla
    for i in range(iteraciones):
        cuadrado = xn ** 2
        digitos = extraer_digitos_centrales(cuadrado, digitos_centrales)
        ri = digitos / (10 ** digitos_centrales)
        resultados.append((i + 1, digitos, ri))
        xn = digitos
    return resultados
