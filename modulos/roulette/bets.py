from dataclasses import dataclass
from .wheel_layout import ROJOS


@dataclass
class Bet:
    monto: int

    def pagar(self, resultado):
        return 0


@dataclass
class StraightUp(Bet):
    numero: int

    def pagar(self, resultado):
        return self.monto * 36 if self.numero == resultado else 0


@dataclass
class Split(Bet):
    numeros: list

    def pagar(self, resultado):
        return self.monto * 18 if resultado in self.numeros else 0


@dataclass
class Street(Bet):
    fila: int

    def pagar(self, resultado):
        inicio = (self.fila - 1) * 3 + 1
        return self.monto * 12 if inicio <= resultado <= inicio + 2 else 0


@dataclass
class Corner(Bet):
    numeros: list

    def pagar(self, resultado):
        return self.monto * 9 if resultado in self.numeros else 0


@dataclass
class SixLine(Bet):
    fila_inicio: int

    def pagar(self, resultado):
        inicio = (self.fila_inicio - 1) * 3 + 1
        return self.monto * 6 if inicio <= resultado <= inicio + 5 else 0


@dataclass
class Red(Bet):
    def pagar(self, resultado):
        return self.monto * 2 if resultado in ROJOS else 0


@dataclass
class Black(Bet):
    def pagar(self, resultado):
        return self.monto * 2 if resultado != 0 and resultado not in ROJOS else 0


@dataclass
class Even(Bet):
    def pagar(self, resultado):
        return self.monto * 2 if resultado != 0 and resultado % 2 == 0 else 0


@dataclass
class Odd(Bet):
    def pagar(self, resultado):
        return self.monto * 2 if resultado % 2 != 0 else 0


@dataclass
class Low(Bet):
    def pagar(self, resultado):
        return self.monto * 2 if 1 <= resultado <= 18 else 0


@dataclass
class High(Bet):
    def pagar(self, resultado):
        return self.monto * 2 if 19 <= resultado <= 36 else 0


@dataclass
class Dozen(Bet):
    docena: int

    def pagar(self, resultado):
        inicio = (self.docena - 1) * 12 + 1
        return self.monto * 3 if inicio <= resultado <= inicio + 11 else 0


@dataclass
class Column(Bet):
    columna: int

    def pagar(self, resultado):
        if resultado == 0:
            return 0
        return self.monto * 3 if resultado % 3 == self.columna % 3 else 0
