import secrets
from .wheel_layout import SECUENCIA_RUEDA, COLORES
from .bets import Bet


class Engine:
    def __init__(self):
        self._rng = secrets.SystemRandom()

    def spin(self):
        return self._rng.randint(0, 36)

    def calcular_pagos(self, apuestas, resultado):
        ganancia_total = 0
        detalles = []
        for apuesta in apuestas:
            pago = apuesta.pagar(resultado)
            ganancia_total += pago
            detalles.append({
                "tipo": type(apuesta).__name__,
                "monto": apuesta.monto,
                "pago": pago,
                "gana": pago > 0,
            })
        return ganancia_total, detalles

    def resultado_dict(self, numero):
        return {
            "numero": numero,
            "color": COLORES[numero],
            "par": numero % 2 == 0 if numero != 0 else None,
            "bajo": 1 <= numero <= 18,
            "alto": 19 <= numero <= 36,
            "docena": (numero - 1) // 12 + 1 if numero != 0 else 0,
            "columna": numero % 3 if numero != 0 else 0,
        }
