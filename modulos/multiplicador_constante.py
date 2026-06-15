from . import extraer_digitos_centrales


def generar(semilla, constante_a, valor_inicial_X0, iteraciones, digitos_centrales=4):
    resultados = []
    xn = valor_inicial_X0
    for i in range(iteraciones):
        producto = xn * constante_a
        digitos = extraer_digitos_centrales(producto, digitos_centrales)
        ri = digitos / (10 ** digitos_centrales)
        resultados.append((i + 1, digitos, ri))
        xn = digitos
    return resultados
