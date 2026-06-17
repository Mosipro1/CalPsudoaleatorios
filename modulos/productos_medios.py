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


def calcular_periodo(semilla1, semilla2, digitos_centrales=4, max_iter=100000):
    vistos = {}
    s1, s2 = semilla1, semilla2
    for i in range(max_iter):
        estado = (s1, s2)
        if estado in vistos:
            valor_repetido = extraer_digitos_centrales(s1 * s2, digitos_centrales)
            return {
                "unicos": i,
                "valor_repetido": valor_repetido,
                "iteracion_repetida": vistos[estado] + 1,
                "longitud_ciclo": i - vistos[estado]
            }
        vistos[estado] = i
        producto = s1 * s2
        digitos = extraer_digitos_centrales(producto, digitos_centrales)
        s1, s2 = s2, digitos
    return None
