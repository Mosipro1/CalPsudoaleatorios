import math


def generar(a, c, m, semilla, iteraciones):
    resultados = []
    xn = semilla
    for i in range(iteraciones):
        xn = (a * xn + c) % m
        ri = xn / m
        resultados.append((i + 1, xn, ri))
    return resultados


def _factores_primos(n):
    factores = set()
    while n % 2 == 0:
        factores.add(2)
        n //= 2
    i = 3
    while i * i <= n:
        while n % i == 0:
            factores.add(i)
            n //= i
        i += 2
    if n > 1:
        factores.add(n)
    return factores


def _periodo_teorico_lcg(a, c, m):
    if math.gcd(c, m) != 1:
        return None
    for p in _factores_primos(m):
        if (a - 1) % p != 0:
            return None
    if m % 4 == 0 and (a - 1) % 4 != 0:
        return None
    return m


def calcular_periodo(a, c, m, semilla, max_iter=1000000):
    teorico = _periodo_teorico_lcg(a, c, m)
    if teorico is not None and teorico <= max_iter:
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
                    "teorico": teorico,
                }
            vistos[xn] = i
    if teorico is not None:
        return {
            "unicos": teorico,
            "longitud_ciclo": teorico,
            "m": m,
            "periodo_completo": True,
            "teorico": teorico,
        }
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
