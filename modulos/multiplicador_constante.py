from . import extraer_digitos_centrales


def generar(constante_a, valor_inicial_X0, iteraciones, digitos_centrales=4):
    resultados = []
    xn = valor_inicial_X0
    for i in range(iteraciones):
        producto = xn * constante_a
        digitos = extraer_digitos_centrales(producto, digitos_centrales)
        ri = digitos / (10 ** digitos_centrales)
        resultados.append((i + 1, digitos, ri))
        xn = digitos
    return resultados


def calcular_periodo(constante_a, valor_inicial_X0, digitos_centrales=4, max_iter=100000):
    vistos = {}
    xn = valor_inicial_X0
    for i in range(max_iter):
        producto = xn * constante_a
        digitos = extraer_digitos_centrales(producto, digitos_centrales)
        if digitos in vistos:
            return {
                "unicos": i,
                "valor_repetido": digitos,
                "iteracion_repetida": vistos[digitos] + 1,
                "longitud_ciclo": i - vistos[digitos]
            }
        vistos[digitos] = i
        xn = digitos
    return None
