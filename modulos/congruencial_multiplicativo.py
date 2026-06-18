def generar(a, m, semilla, iteraciones):
    resultados = []
    xn = semilla
    for i in range(iteraciones):
        xn = (a * xn) % m
        ri = xn / (m - 1)
        resultados.append((i + 1, xn, ri))
    return resultados


def calcular_periodo(a, m, semilla, max_iter=1000000):
    vistos = {}
    xn = semilla
    for i in range(max_iter):
        xn = (a * xn) % m
        if xn in vistos:
            return {
                "unicos": i,
                "valor_repetido": xn,
                "iteracion_repetida": vistos[xn] + 1,
                "longitud_ciclo": i - vistos[xn],
                "m": m,
            }
        vistos[xn] = i
    return None
