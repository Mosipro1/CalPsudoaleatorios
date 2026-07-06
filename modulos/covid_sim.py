import random
import copy

SANO = 0
INFECTADO = 1
RECUPERADO = 2
FALLECIDO = 3
VACIO = 4

NOMBRES_ESTADOS = {SANO: "Sanos", INFECTADO: "Infectados", RECUPERADO: "Recuperados", FALLECIDO: "Fallecidos", VACIO: "Vacío"}
COLORES_ESTADOS = {SANO: "#60a5fa", INFECTADO: "#ef4444", RECUPERADO: "#22c55e", FALLECIDO: "#1e293b", VACIO: "#f1f5f9"}


class CovidSim:
    def __init__(self, filas=50, columnas=50, densidad_poblacion=0.85,
                 infectados_iniciales=5, probabilidad_contagio=0.3,
                 dias_recuperacion=14, probabilidad_muerte=0.02,
                 semilla=None):
        self.filas = filas
        self.columnas = columnas
        self.densidad_poblacion = densidad_poblacion
        self.infectados_iniciales = infectados_iniciales
        self.probabilidad_contagio = probabilidad_contagio
        self.dias_recuperacion = dias_recuperacion
        self.probabilidad_muerte = probabilidad_muerte
        self._rng = random.Random(semilla)

        self.grid = None
        self.dias_infectado = None
        self.iteracion = 0
        self.historial = []
        self._inicializar()

    def _inicializar(self):
        self.grid = [[VACIO] * self.columnas for _ in range(self.filas)]
        self.dias_infectado = [[0] * self.columnas for _ in range(self.filas)]
        self.iteracion = 0
        self.historial = []

        celdas_totales = self.filas * self.columnas
        celdas_ocupadas = int(celdas_totales * self.densidad_poblacion)

        posiciones = [(r, c) for r in range(self.filas) for c in range(self.columnas)]
        self._rng.shuffle(posiciones)

        for i in range(min(celdas_ocupadas, len(posiciones))):
            r, c = posiciones[i]
            self.grid[r][c] = SANO

        infectados_colocados = 0
        for r in range(self.filas):
            for c in range(self.columnas):
                if self.grid[r][c] == SANO and infectados_colocados < self.infectados_iniciales:
                    self.grid[r][c] = INFECTADO
                    self.dias_infectado[r][c] = 1
                    infectados_colocados += 1

        self._registrar_historial()

    def _vecinos_moore(self, r, c):
        vecinos = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.filas and 0 <= nc < self.columnas:
                    vecinos.append((nr, nc))
        return vecinos

    def step(self):
        nuevo_grid = [fila[:] for fila in self.grid]
        nuevo_dias = [fila[:] for fila in self.dias_infectado]

        for r in range(self.filas):
            for c in range(self.columnas):
                estado = self.grid[r][c]

                if estado == VACIO or estado == FALLECIDO:
                    continue

                if estado == SANO:
                    vecinos = self._vecinos_moore(r, c)
                    infectados_cerca = sum(1 for nr, nc in vecinos if self.grid[nr][nc] == INFECTADO)
                    if infectados_cerca > 0 and self._rng.random() < self.probabilidad_contagio:
                        nuevo_grid[r][c] = INFECTADO
                        nuevo_dias[r][c] = 1

                elif estado == INFECTADO:
                    nuevo_dias[r][c] = self.dias_infectado[r][c] + 1
                    if self._rng.random() < self.probabilidad_muerte:
                        nuevo_grid[r][c] = FALLECIDO
                    elif nuevo_dias[r][c] >= self.dias_recuperacion:
                        nuevo_grid[r][c] = RECUPERADO
                    else:
                        nuevo_grid[r][c] = INFECTADO

        self.grid = nuevo_grid
        self.dias_infectado = nuevo_dias
        self.iteracion += 1
        self._registrar_historial()

    def _registrar_historial(self):
        conteo = self._contar()
        self.historial.append({
            "iteracion": self.iteracion,
            **conteo,
        })

    def _contar(self):
        conteo = {SANO: 0, INFECTADO: 0, RECUPERADO: 0, FALLECIDO: 0, VACIO: 0}
        for r in range(self.filas):
            for c in range(self.columnas):
                conteo[self.grid[r][c]] += 1
        return conteo

    def obtener_estado(self):
        return {
            "iteracion": self.iteracion,
            "conteo": self._contar(),
            "historial": self.historial,
            "grid": [[self.grid[r][c] for c in range(self.columnas)] for r in range(self.filas)],
        }


def _formatear_resultado(estado):
    conteo = estado["conteo"]
    return {
        "iteracion": estado["iteracion"],
        "sanos": conteo[SANO],
        "infectados": conteo[INFECTADO],
        "recuperados": conteo[RECUPERADO],
        "fallecidos": conteo[FALLECIDO],
        "vacio": conteo[VACIO],
        "grid": estado["grid"],
    }


def simular(filas, columnas, densidad_poblacion, infectados_iniciales,
            probabilidad_contagio, dias_recuperacion, probabilidad_muerte,
            iteraciones, semilla=None):
    sim = CovidSim(
        filas=filas,
        columnas=columnas,
        densidad_poblacion=densidad_poblacion,
        infectados_iniciales=infectados_iniciales,
        probabilidad_contagio=probabilidad_contagio,
        dias_recuperacion=dias_recuperacion,
        probabilidad_muerte=probabilidad_muerte,
        semilla=semilla,
    )

    resultados = [_formatear_resultado(sim.obtener_estado())]
    for _ in range(iteraciones):
        sim.step()
        resultados.append(_formatear_resultado(sim.obtener_estado()))
    return resultados
