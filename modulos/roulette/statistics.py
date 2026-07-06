from collections import Counter
from .wheel_layout import ROJOS


class Statistics:
    def __init__(self):
        self.numeros = []
        self.frecuencias = Counter()

    def registrar(self, numero):
        self.numeros.append(numero)
        self.frecuencias[numero] += 1

    @property
    def total(self):
        return len(self.numeros)

    def frecuencia_numero(self, numero):
        if self.total == 0:
            return 0
        return self.frecuencias[numero] / self.total * 100

    @property
    def pct_rojo(self):
        if self.total == 0:
            return 0
        rojos = sum(1 for n in self.numeros if n in ROJOS)
        return rojos / self.total * 100

    @property
    def pct_negro(self):
        if self.total == 0:
            return 0
        negros = sum(1 for n in self.numeros if n != 0 and n not in ROJOS)
        return negros / self.total * 100

    @property
    def pct_verde(self):
        if self.total == 0:
            return 0
        verdes = self.numeros.count(0)
        return verdes / self.total * 100

    @property
    def pct_par(self):
        if self.total == 0:
            return 0
        pares = sum(1 for n in self.numeros if n != 0 and n % 2 == 0)
        return pares / self.total * 100

    @property
    def pct_impar(self):
        if self.total == 0:
            return 0
        impares = sum(1 for n in self.numeros if n % 2 != 0)
        return impares / self.total * 100

    @property
    def pct_bajo(self):
        if self.total == 0:
            return 0
        bajos = sum(1 for n in self.numeros if 1 <= n <= 18)
        return bajos / self.total * 100

    @property
    def pct_alto(self):
        if self.total == 0:
            return 0
        altos = sum(1 for n in self.numeros if 19 <= n <= 36)
        return altos / self.total * 100

    def frecuencia_docena(self, docena):
        if self.total == 0:
            return 0
        inicio = (docena - 1) * 12 + 1
        count = sum(1 for n in self.numeros if inicio <= n <= inicio + 11)
        return count / self.total * 100

    def frecuencia_columna(self, columna):
        if self.total == 0:
            return 0
        count = sum(1 for n in self.numeros if n != 0 and n % 3 == columna % 3)
        return count / self.total * 100

    @property
    def racha_rojo(self):
        racha = 0
        for n in reversed(self.numeros):
            if n in ROJOS:
                racha += 1
            else:
                break
        return racha

    @property
    def racha_negro(self):
        racha = 0
        for n in reversed(self.numeros):
            if n != 0 and n not in ROJOS:
                racha += 1
            else:
                break
        return racha

    @property
    def racha_par(self):
        racha = 0
        for n in reversed(self.numeros):
            if n != 0 and n % 2 == 0:
                racha += 1
            else:
                break
        return racha

    @property
    def racha_impar(self):
        racha = 0
        for n in reversed(self.numeros):
            if n % 2 != 0:
                racha += 1
            else:
                break
        return racha

    @property
    def numeros_calientes(self):
        return [n for n, _ in self.frecuencias.most_common(5)]

    @property
    def numeros_frios(self):
        todos = range(37)
        if self.total == 0:
            return list(todos[:5])
        menos_comunes = sorted(todos, key=lambda n: self.frecuencias.get(n, 0))
        return menos_comunes[:5]

    @classmethod
    def from_historial(cls, historial):
        stats = cls()
        for entry in historial:
            stats.registrar(entry["numero"])
        return stats

    def ultimos(self, n=20):
        return self.numeros[-n:]

    def to_dict(self):
        return {
            "total": self.total,
            "pct_rojo": round(self.pct_rojo, 2),
            "pct_negro": round(self.pct_negro, 2),
            "pct_verde": round(self.pct_verde, 2),
            "pct_par": round(self.pct_par, 2),
            "pct_impar": round(self.pct_impar, 2),
            "pct_bajo": round(self.pct_bajo, 2),
            "pct_alto": round(self.pct_alto, 2),
            "frecuencia_d1": round(self.frecuencia_docena(1), 2),
            "frecuencia_d2": round(self.frecuencia_docena(2), 2),
            "frecuencia_d3": round(self.frecuencia_docena(3), 2),
            "frecuencia_c1": round(self.frecuencia_columna(1), 2),
            "frecuencia_c2": round(self.frecuencia_columna(2), 2),
            "frecuencia_c3": round(self.frecuencia_columna(3), 2),
            "racha_rojo": self.racha_rojo,
            "racha_negro": self.racha_negro,
            "racha_par": self.racha_par,
            "racha_impar": self.racha_impar,
            "calientes": self.numeros_calientes,
            "frios": self.numeros_frios,
            "ultimos": self.ultimos(20),
        }
