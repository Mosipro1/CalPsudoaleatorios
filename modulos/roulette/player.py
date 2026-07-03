import json
import os

SALDO_INICIAL = 10000
ARCHIVO = os.path.join(os.path.dirname(__file__), "..", "..", "roulette_data.json")


class Player:
    def __init__(self):
        self.saldo = SALDO_INICIAL
        self.historial = []
        self.mayor_victoria = 0
        self.mayor_derrota = 0
        self.total_ganado = 0
        self.total_perdido = 0
        self._cargar()

    def puede_apostar(self, monto):
        return monto <= self.saldo

    def apostar(self, monto):
        if not self.puede_apostar(monto):
            return False
        self.saldo -= monto
        self.total_perdido += monto
        self.mayor_derrota = max(self.mayor_derrota, monto)
        return True

    def cobrar(self, ganancia):
        self.saldo += ganancia
        self.total_ganado += ganancia
        if ganancia > 0:
            self.mayor_victoria = max(self.mayor_victoria, ganancia)

    def registrar_giro(self, numero, apuestas, ganancia):
        entry = {
            "numero": numero,
            "apuestas": len(apuestas),
            "ganancia": ganancia,
            "saldo": self.saldo,
        }
        self.historial.append(entry)
        if len(self.historial) > 100:
            self.historial = self.historial[-100:]

    @property
    def beneficio(self):
        return self.total_ganado - self.total_perdido

    def _cargar(self):
        try:
            with open(ARCHIVO) as f:
                data = json.load(f)
            self.saldo = data.get("saldo", SALDO_INICIAL)
            self.historial = data.get("historial", [])
            self.mayor_victoria = data.get("mayor_victoria", 0)
            self.mayor_derrota = data.get("mayor_derrota", 0)
            self.total_ganado = data.get("total_ganado", 0)
            self.total_perdido = data.get("total_perdido", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def guardar(self):
        data = {
            "saldo": self.saldo,
            "historial": self.historial,
            "mayor_victoria": self.mayor_victoria,
            "mayor_derrota": self.mayor_derrota,
            "total_ganado": self.total_ganado,
            "total_perdido": self.total_perdido,
        }
        with open(ARCHIVO, "w") as f:
            json.dump(data, f, indent=2)
