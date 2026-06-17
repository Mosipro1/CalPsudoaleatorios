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


def calcular_periodo(semilla, digitos_centrales=4, max_iter=100000):
    vistos = {}
    xn = semilla
    for i in range(max_iter):
        cuadrado = xn ** 2
        digitos = extraer_digitos_centrales(cuadrado, digitos_centrales)
        if digitos in vistos:
            return {
                "unicos": i,
                "valor_repetido": digitos,
                "iteracion_repetida": vistos[digitos] + 1,
                "longitud_ciclo": i - vistos[digitos]
            }
        vistos[digitos] = i
        xn = digitos
    return None
