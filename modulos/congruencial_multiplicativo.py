import math


def generar(a, m, semilla, iteraciones):
    resultados = []
    xn = semilla
    for i in range(iteraciones):
        xn = (a * xn) % m
        ri = xn / (m - 1)
        resultados.append((i + 1, xn, ri))
    return resultados


# Known (m, a) pairs with maximum period
_PERIODOS_CONOCIDOS = {
    (2147483647, 16807): 2147483646,   # m = 2^31 - 1 (Mersenne), a = 7^5
    (2147483647, 48271): 2147483646,   # m = 2^31 - 1, a = 48271
}


def _periodo_teorico_mcg(a, m):
    if m % 2 == 0:
        k = (m & -m).bit_length() - 1
        if m == 2 ** k and k >= 3:
            if a % 8 in (3, 5):
                return 2 ** (k - 2)
    return _PERIODOS_CONOCIDOS.get((m, a))


def calcular_periodo(a, m, semilla, max_iter=1000000):
    teorico = _periodo_teorico_mcg(a, m)
    if teorico is not None and teorico <= max_iter:
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
                    "teorico": teorico,
                }
            vistos[xn] = i
    if teorico is not None:
        return {
            "unicos": teorico,
            "longitud_ciclo": teorico,
            "m": m,
            "teorico": teorico,
        }
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
