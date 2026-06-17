import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from modulos import multiplicador_constante, productos_medios, cuadrados_medios

PORT = 8000
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


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
            if path.endswith("/multiplicador_constante"):
                r = multiplicador_constante.generar(
                    int(body["constante_a"]),
                    int(body["valor_inicial"]), int(body["iteraciones"]), int(body["digitos"])
                )
            elif path.endswith("/multiplicador_constante/periodo"):
                r = multiplicador_constante.calcular_periodo(
                    int(body["constante_a"]), int(body["valor_inicial"]), int(body["digitos"])
                )
            elif path.endswith("/productos_medios"):
                r = productos_medios.generar(
                    int(body["semilla1"]), int(body["semilla2"]),
                    int(body["iteraciones"]), int(body["digitos"])
                )
            elif path.endswith("/productos_medios/periodo"):
                r = productos_medios.calcular_periodo(
                    int(body["semilla1"]), int(body["semilla2"]), int(body["digitos"])
                )
            elif path.endswith("/cuadrados_medios"):
                r = cuadrados_medios.generar(
                    int(body["semilla"]), int(body["iteraciones"]), int(body["digitos"])
                )
            elif path.endswith("/cuadrados_medios/periodo"):
                r = cuadrados_medios.calcular_periodo(
                    int(body["semilla"]), int(body["digitos"])
                )
            else:
                self._respond(404, "application/json", json.dumps({"error": "ruta no encontrada"}).encode())
                return

            if isinstance(r, list):
                d = int(body.get("digitos", 4))
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
