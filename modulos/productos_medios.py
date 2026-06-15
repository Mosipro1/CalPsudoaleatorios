from . import extraer_digitos_centrales


def generar(semilla1, semilla2, iteraciones, digitos_centrales=4):
    resultados = []
    s1, s2 = semilla1, semilla2
    for i in range(iteraciones):
        producto = s1 * s2
        digitos = extraer_digitos_centrales(producto, digitos_centrales)
        ri = digitos / (10 ** digitos_centrales)
        resultados.append((i + 1, digitos, ri))
        s1, s2 = s2, digitos
    return resultados
