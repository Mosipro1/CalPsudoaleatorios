import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from modulos import (
    multiplicador_constante,
    productos_medios,
    cuadrados_medios,
    congruencial_lineal,
    congruencial_multiplicativo,
    mersenne_twister,
    lotka_volterra,
    pruebas_estadisticas,
    covid_sim,
    dolares,
    quinua,
)
from modulos.roulette import Engine, Player, Statistics
from modulos.roulette.player import SALDO_INICIAL

PORT = 8000
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def _formatear_periodo(periodo):
    if periodo is None:
        raise ValueError("No se encontró repetición en el límite establecido")
    return periodo


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/roulette/state":
            player = Player()
            stats = Statistics.from_historial(player.historial)
            self._respond(200, "application/json", json.dumps({
                "saldo": player.saldo,
                "historial": player.historial,
                "mayor_victoria": player.mayor_victoria,
                "mayor_derrota": player.mayor_derrota,
                "total_ganado": player.total_ganado,
                "total_perdido": player.total_perdido,
                "stats": stats.to_dict(),
            }).encode())
            return
        if path == "/":
            path = "/index.html"
        filepath = os.path.join(STATIC_DIR, path.lstrip("/"))
        if os.path.isfile(filepath):
            ext = path.rsplit(".", 1)[-1]
            ctype = {"html": "text/html", "css": "text/css", "js": "application/javascript"}.get(ext, "application/octet-stream")
            with open(filepath, "rb") as f:
                self._respond(200, ctype, f.read())
        else:
            self._respond(404, "text/plain", b"Not Found")

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode()) if length else {}

        try:
            # ── generadores ──
            if path.endswith("/multiplicador_constante"):
                r = multiplicador_constante.generar(
                    int(body["constante_a"]), int(body["valor_inicial"]), int(body["iteraciones"]), int(body["digitos"])
                )
            elif path.endswith("/multiplicador_constante/periodo"):
                r = _formatear_periodo(multiplicador_constante.calcular_periodo(int(body["constante_a"]), int(body["valor_inicial"]), int(body["digitos"])))
            elif path.endswith("/productos_medios"):
                r = productos_medios.generar(int(body["semilla1"]), int(body["semilla2"]), int(body["iteraciones"]), int(body["digitos"]))
            elif path.endswith("/productos_medios/periodo"):
                r = _formatear_periodo(productos_medios.calcular_periodo(int(body["semilla1"]), int(body["semilla2"]), int(body["digitos"])))
            elif path.endswith("/cuadrados_medios"):
                r = cuadrados_medios.generar(int(body["semilla"]), int(body["iteraciones"]), int(body["digitos"]))
            elif path.endswith("/cuadrados_medios/periodo"):
                r = _formatear_periodo(cuadrados_medios.calcular_periodo(int(body["semilla"]), int(body["digitos"])))
            elif path.endswith("/congruencial_lineal"):
                r = congruencial_lineal.generar(int(body["a"]), int(body["c"]), int(body["m"]), int(body["semilla"]), int(body["iteraciones"]))
            elif path.endswith("/congruencial_lineal/periodo"):
                r = _formatear_periodo(congruencial_lineal.calcular_periodo(int(body["a"]), int(body["c"]), int(body["m"]), int(body["semilla"])))
            elif path.endswith("/congruencial_multiplicativo"):
                r = congruencial_multiplicativo.generar(int(body["a"]), int(body["m"]), int(body["semilla"]), int(body["iteraciones"]))
            elif path.endswith("/congruencial_multiplicativo/periodo"):
                r = _formatear_periodo(congruencial_multiplicativo.calcular_periodo(int(body["a"]), int(body["m"]), int(body["semilla"])))
            elif path.endswith("/mersenne_twister"):
                r = mersenne_twister.generar(int(body["semilla"]), int(body["iteraciones"]))
            elif path.endswith("/mersenne_twister/periodo"):
                r = _formatear_periodo(mersenne_twister.calcular_periodo(int(body["semilla"])))
            elif path.endswith("/lotka_volterra"):
                r = lotka_volterra.generar(float(body["alpha"]), float(body["beta"]), float(body["delta"]), float(body["gamma"]), float(body["x0"]), float(body["y0"]), float(body["dt"]), int(body["iteraciones"]))
            # ── dolares ──
            elif path.endswith("/dolares_sim"):
                r = dolares.simular(
                    float(body["alpha"]), float(body["beta"]),
                    float(body["delta"]), float(body["gamma"]),
                    float(body["dolares0"]), float(body["presion0"]),
                    int(body["tiempo"]),
                )
            # ── quinua ──
            elif path.endswith("/quinua_sim"):
                r = quinua.simular(
                    float(body["alpha"]), float(body["beta"]),
                    float(body["delta"]), float(body["gamma"]),
                    float(body["stock0"]), float(body["proceso0"]),
                    int(body["tiempo"]),
                )
            # ── covid ──
            elif path.endswith("/covid_sim"):
                r = covid_sim.simular(
                    int(body["filas"]), int(body["columnas"]),
                    float(body["densidad_poblacion"]),
                    int(body["infectados_iniciales"]),
                    float(body["probabilidad_contagio"]),
                    int(body["dias_recuperacion"]),
                    float(body["probabilidad_muerte"]),
                    int(body["iteraciones"]),
                    semilla=body.get("semilla"),
                )
            # ── pruebas ──
            elif path.endswith("/pruebas_estadisticas"):
                numeros = [float(x) for x in body.get("numeros", "").replace(",", " ").split()]
                alpha = float(body.get("alpha", 0.05))
                intervalos = int(body.get("intervalos", 10))
                lag = int(body.get("lag", 1))
                tests = body.get("tests", ["promedio", "varianza", "chi2", "ks"])
                data = []
                if "promedio" in tests:
                    data.append(pruebas_estadisticas.prueba_promedio(numeros, alpha))
                if "varianza" in tests:
                    data.append(pruebas_estadisticas.prueba_varianza(numeros, alpha))
                if "chi2" in tests:
                    data.append(pruebas_estadisticas.prueba_chi_cuadrada(numeros, intervalos, alpha))
                if "ks" in tests:
                    data.append(pruebas_estadisticas.prueba_uniformidad_ks(numeros, alpha))
                if "rachas" in tests:
                    data.append(pruebas_estadisticas.prueba_rachas(numeros, alpha))
                if "rachas_tendencia" in tests:
                    data.append(pruebas_estadisticas.prueba_rachas_tendencia(numeros, alpha))
                if "autocorr" in tests:
                    data.append(pruebas_estadisticas.prueba_independencia_autocorrelacion(numeros, lag, alpha))
                self._respond(200, "application/json", json.dumps(data).encode())
                return
            elif path.endswith("/roulette/reset"):
                player = Player()
                player.saldo = SALDO_INICIAL
                player.historial = []
                player.mayor_victoria = 0
                player.mayor_derrota = 0
                player.total_ganado = 0
                player.total_perdido = 0
                player.guardar()
                r = {"saldo": player.saldo, "mensaje": "Saldo reiniciado"}
            elif path.endswith("/roulette/spin"):
                player = Player()
                stats = Statistics.from_historial(player.historial)
                engine = Engine()
                apuestas_raw = body.get("apuestas", [])
                from modulos.roulette.bets import StraightUp, Red, Black, Even, Odd, Low, High, Dozen, Column
                apuestas = []
                for a in apuestas_raw:
                    tipo = a.get("tipo")
                    monto_raw = a.get("monto", 0)
                    if isinstance(monto_raw, str):
                        monto_raw = float(monto_raw)
                    monto = int(monto_raw)
                    if monto <= 0:
                        raise ValueError("El monto de cada apuesta debe ser > 0")
                    if tipo == "straight":
                        apuestas.append(StraightUp(monto, int(a["numero"])))
                    elif tipo == "red":
                        apuestas.append(Red(monto))
                    elif tipo == "black":
                        apuestas.append(Black(monto))
                    elif tipo == "even":
                        apuestas.append(Even(monto))
                    elif tipo == "odd":
                        apuestas.append(Odd(monto))
                    elif tipo == "low":
                        apuestas.append(Low(monto))
                    elif tipo == "high":
                        apuestas.append(High(monto))
                    elif tipo == "dozen":
                        apuestas.append(Dozen(monto, int(a["docena"])))
                    elif tipo == "column":
                        apuestas.append(Column(monto, int(a["columna"])))
                monto_total = sum(a.monto for a in apuestas)
                if monto_total > player.saldo:
                    self._respond(400, "application/json", json.dumps({"error": "Saldo insuficiente"}).encode())
                    return
                for a in apuestas:
                    player.apostar(a.monto)
                resultado = engine.spin()
                ganancia_total, detalles = engine.calcular_pagos(apuestas, resultado)
                player.cobrar(ganancia_total)
                player.registrar_giro(resultado, apuestas, ganancia_total)
                player.guardar()
                stats.registrar(resultado)
                r = {
                    "resultado": engine.resultado_dict(resultado),
                    "ganancia_total": ganancia_total,
                    "detalles": detalles,
                    "saldo": player.saldo,
                    "mayor_victoria": player.mayor_victoria,
                    "mayor_derrota": player.mayor_derrota,
                    "beneficio": player.beneficio,
                    "stats": stats.to_dict(),
                }
            else:
                self._respond(404, "application/json", json.dumps({"error": "ruta no encontrada"}).encode())
                return

            if isinstance(r, list) and r and isinstance(r[0], tuple):
                if len(r[0]) == 4:
                    data = [{"iteracion": it, "t": t, "presas": x, "depredadores": y} for it, t, x, y in r]
                else:
                    d = int(body.get("digitos", 6))
                    data = [{"iteracion": it, "xn": xn, "ri": round(ri, d)} for it, xn, ri in r]
            else:
                data = r

            self._respond(200, "application/json", json.dumps(data).encode())
        except Exception as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode())

    def _respond(self, code, ctype, content):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)


if __name__ == "__main__":
    port = PORT
    for _ in range(10):
        try:
            server = HTTPServer(("0.0.0.0", port), Handler)
            print(f"Servidor iniciado en http://localhost:{port}")
            server.serve_forever()
            break
        except OSError:
            print(f"⚠ Puerto {port} ocupado, probando {port + 1}...")
            port += 1
