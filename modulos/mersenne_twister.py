import random


class MersenneTwister:
    def __init__(self, semilla=None):
        self._rng = random.Random(semilla)

    def random(self):
        return self._rng.random()


def generar(semilla, iteraciones):
    mt = MersenneTwister(semilla)
    resultados = []
    for i in range(iteraciones):
        ri = mt.random()
        xn = int(ri * 10**10)
        resultados.append((i + 1, xn, ri))
    return resultados


def calcular_periodo(semilla, max_iter=1000000):
    vistos = {}
    mt = MersenneTwister(semilla)
    for i in range(max_iter):
        ri = mt.random()
        estado = round(ri, 10)
        if estado in vistos:
            return {
                "unicos": i,
                "valor_repetido": estado,
                "iteracion_repetida": vistos[estado] + 1,
                "longitud_ciclo": i - vistos[estado],
            }
        vistos[estado] = i
    return None
