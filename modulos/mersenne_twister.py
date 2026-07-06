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
    return {
        "unicos": None,
        "longitud_ciclo": "2^19937 - 1 (teórico)",
        "periodo_completo": True,
        "nota": "El período del Mersenne Twister es 2^19937-1, imposible de detectar empíricamente",
    }
