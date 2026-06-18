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
)

PORT = 8000
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def _formatear_periodo(periodo):
    if periodo is None:
        return {"error": "No se encontró repetición en el límite establecido"}
    return periodo


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
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
            else:
                self._respond(404, "application/json", json.dumps({"error": "ruta no encontrada"}).encode())
                return

            if isinstance(r, list) and r and isinstance(r[0], tuple):
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
    print(f"Servidor iniciado en http://localhost:{PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
