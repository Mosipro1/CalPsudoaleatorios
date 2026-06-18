from . import extraer_digitos_centrales


def generar(a, c, m, semilla, iteraciones):
    resultados = []
    xn = semilla
    for i in range(iteraciones):
        xn = (a * xn + c) % m
        ri = xn / (m - 1)
        resultados.append((i + 1, xn, ri))
    return resultados


def calcular_periodo(a, c, m, semilla, max_iter=1000000):
    vistos = {}
    xn = semilla
    for i in range(max_iter):
        xn = (a * xn + c) % m
        if xn in vistos:
            return {
                "unicos": i,
                "valor_repetido": xn,
                "iteracion_repetida": vistos[xn] + 1,
                "longitud_ciclo": i - vistos[xn],
                "m": m,
                "periodo_completo": (i - vistos[xn]) >= m,
            }
        vistos[xn] = i
    return None
