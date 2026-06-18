import math


def _normal_inv(p):
    if p <= 0 or p >= 1:
        raise ValueError("p debe estar entre 0 y 1 exclusivo")
    if p < 0.5:
        signo = -1
        t = math.sqrt(-2 * math.log(p))
    else:
        signo = 1
        t = math.sqrt(-2 * math.log(1 - p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    z = t - (c0 + c1 * t + c2 * t ** 2) / (1 + d1 * t + d2 * t ** 2 + d3 * t ** 3)
    return signo * z


def _chi2_critico(k, p):
    if k <= 0:
        return 0.0
    zp = _normal_inv(p)
    chi2 = k * (1 - 2 / (9 * k) + zp * math.sqrt(2 / (9 * k))) ** 3
    return max(0.0, chi2)


def prueba_promedio(numeros, alpha=0.05):
    n = len(numeros)
    if n < 2:
        raise ValueError("Se necesitan al menos 2 números")
    media = sum(numeros) / n
    sigma = 1.0 / math.sqrt(12)
    z_calc = (media - 0.5) / (sigma / math.sqrt(n))
    z_alpha2 = _normal_inv(1 - alpha / 2)
    acepta = abs(z_calc) < z_alpha2
    error = sigma / math.sqrt(n)
    return {
        "prueba": "Promedio",
        "estadistico": "Z",
        "valor_calculado": z_calc,
        "valor_critico": z_alpha2,
        "limite_inferior": media - z_alpha2 * error,
        "limite_superior": media + z_alpha2 * error,
        "alpha": alpha,
        "media": media,
        "n": n,
        "acepta_H0": acepta,
        "interpretacion": (
            "No se rechaza H0 (μ = 0.5). Los números son uniformes en promedio."
            if acepta
            else "Se rechaza H0 (μ ≠ 0.5). Los números no tienen media 0.5."
        ),
    }


def prueba_varianza(numeros, alpha=0.05):
    n = len(numeros)
    if n < 2:
        raise ValueError("Se necesitan al menos 2 números")
    media = sum(numeros) / n
    varianza_muestral = sum((x - media) ** 2 for x in numeros) / (n - 1)
    chi2_calc = 12 * sum((x - 0.5) ** 2 for x in numeros)
    chi2_inf = _chi2_critico(n, alpha / 2)
    chi2_sup = _chi2_critico(n, 1 - alpha / 2)
    acepta = chi2_inf <= chi2_calc <= chi2_sup
    return {
        "prueba": "Varianza",
        "estadistico": "Chi-cuadrado",
        "valor_calculado": chi2_calc,
        "valor_critico_inferior": chi2_inf,
        "valor_critico_superior": chi2_sup,
        "limite_inferior": chi2_inf,
        "limite_superior": chi2_sup,
        "alpha": alpha,
        "varianza_muestral": varianza_muestral,
        "n": n,
        "acepta_H0": acepta,
        "interpretacion": (
            "No se rechaza H0 (σ² = 1/12). La varianza es consistente con uniformidad."
            if acepta
            else "Se rechaza H0 (σ² ≠ 1/12). La varianza no es consistente."
        ),
    }


def prueba_chi_cuadrada(numeros, intervalos=10, alpha=0.05):
    n = len(numeros)
    if n < intervalos:
        raise ValueError(f"Se necesitan al menos {intervalos} números")
    esperado = n / intervalos
    frecuencias = [0] * intervalos
    for x in numeros:
        idx = min(int(x * intervalos), intervalos - 1)
        frecuencias[idx] += 1
    chi2_calc = sum((f - esperado) ** 2 / esperado for f in frecuencias)
    chi2_crit = _chi2_critico(intervalos - 1, 1 - alpha)
    acepta = chi2_calc < chi2_crit
    return {
        "prueba": "Chi-cuadrada",
        "estadistico": "Chi-cuadrado",
        "valor_calculado": chi2_calc,
        "valor_critico": chi2_crit,
        "limite_inferior": 0,
        "limite_superior": chi2_crit,
        "alpha": alpha,
        "intervalos": intervalos,
        "frecuencias": frecuencias,
        "frecuencia_esperada": esperado,
        "n": n,
        "grados_libertad": intervalos - 1,
        "acepta_H0": acepta,
        "interpretacion": (
            "No se rechaza H0. Los números siguen una distribución uniforme."
            if acepta
            else "Se rechaza H0. Los números no siguen una distribución uniforme."
        ),
    }


def prueba_uniformidad_ks(numeros, alpha=0.05):
    n = len(numeros)
    if n < 2:
        raise ValueError("Se necesitan al menos 2 números")
    ordenados = sorted(numeros)
    d_mas = max((i + 1) / n - ordenados[i] for i in range(n))
    d_menos = max(ordenados[i] - i / n for i in range(n))
    d_calc = max(d_mas, d_menos)
    d_critico = math.sqrt(-0.5 * math.log(alpha / 2)) / math.sqrt(n)
    acepta = d_calc < d_critico
    return {
        "prueba": "Kolmogorov-Smirnov",
        "estadistico": "D",
        "valor_calculado": d_calc,
        "d_mas": d_mas,
        "d_menos": d_menos,
        "valor_critico": d_critico,
        "limite_inferior": 0,
        "limite_superior": d_critico,
        "alpha": alpha,
        "n": n,
        "acepta_H0": acepta,
        "interpretacion": (
            "No se rechaza H0. Los números siguen una distribución uniforme."
            if acepta
            else "Se rechaza H0. Los números no siguen una distribución uniforme."
        ),
    }


def prueba_rachas(numeros, alpha=0.05):
    n = len(numeros)
    if n < 2:
        raise ValueError("Se necesitan al menos 2 números")
    mediana = sum(numeros) / n
    secuencia = [1 if x >= mediana else 0 for x in numeros]
    runs = 1
    for i in range(1, n):
        if secuencia[i] != secuencia[i - 1]:
            runs += 1
    n1 = sum(secuencia)
    n2 = n - n1
    if n1 == 0 or n2 == 0:
        return {
            "prueba": "Rachas (arriba/abajo)",
            "estadistico": "Z",
            "valor_calculado": 0.0,
            "valor_critico": 0.0,
            "limite_inferior": 0,
            "limite_superior": 0,
            "alpha": alpha,
            "runs": runs,
            "n1": n1,
            "n2": n2,
            "n": n,
            "acepta_H0": True,
            "interpretacion": "Todos los valores son iguales a la mediana. No es posible evaluar.",
        }
    media_runs = 2 * n1 * n2 / (n1 + n2) + 1
    var_runs = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / ((n1 + n2) ** 2 * (n1 + n2 - 1))
    if var_runs <= 0:
        return {
            "prueba": "Rachas (arriba/abajo)",
            "estadistico": "Z",
            "valor_calculado": 0.0,
            "valor_critico": 0.0,
            "limite_inferior": 0,
            "limite_superior": 0,
            "alpha": alpha,
            "runs": runs,
            "n1": n1,
            "n2": n2,
            "n": n,
            "acepta_H0": True,
            "interpretacion": "Varianza cero. No es posible evaluar.",
        }
    desv_runs = math.sqrt(var_runs)
    z_calc = (runs - media_runs) / desv_runs
    z_alpha2 = _normal_inv(1 - alpha / 2)
    acepta = abs(z_calc) < z_alpha2
    return {
        "prueba": "Rachas (arriba/abajo)",
        "estadistico": "Z",
        "valor_calculado": z_calc,
        "valor_critico": z_alpha2,
        "limite_inferior": media_runs - z_alpha2 * desv_runs,
        "limite_superior": media_runs + z_alpha2 * desv_runs,
        "alpha": alpha,
        "runs": runs,
        "media_runs": media_runs,
        "desv_runs": desv_runs,
        "n1": n1,
        "n2": n2,
        "n": n,
        "acepta_H0": acepta,
        "interpretacion": (
            "No se rechaza H0. La secuencia es aleatoria (número de rachas esperado)."
            if acepta
            else "Se rechaza H0. La secuencia no es aleatoria (muy pocas o demasiadas rachas)."
        ),
    }


def prueba_rachas_tendencia(numeros, alpha=0.05):
    n = len(numeros)
    if n < 2:
        raise ValueError("Se necesitan al menos 2 números")
    runs = 1
    for i in range(1, n):
        if (numeros[i] >= numeros[i - 1] and i > 0 and
                i < n - 1 and numeros[i + 1] < numeros[i]):
            runs += 1
        elif (numeros[i] < numeros[i - 1] and i > 0 and
              i < n - 1 and numeros[i + 1] >= numeros[i]):
            runs += 1
    media_runs = (2 * n - 1) / 3
    var_runs = (16 * n - 29) / 90
    if var_runs <= 0:
        desv_runs = 0
        z_calc = 0
    else:
        desv_runs = math.sqrt(var_runs)
        z_calc = (runs - media_runs) / desv_runs
    z_alpha2 = _normal_inv(1 - alpha / 2)
    acepta = abs(z_calc) < z_alpha2
    return {
        "prueba": "Rachas de tendencia (sube/baja)",
        "estadistico": "Z",
        "valor_calculado": z_calc,
        "valor_critico": z_alpha2,
        "limite_inferior": media_runs - z_alpha2 * desv_runs if desv_runs > 0 else 0,
        "limite_superior": media_runs + z_alpha2 * desv_runs if desv_runs > 0 else 0,
        "alpha": alpha,
        "runs": runs,
        "media_runs": media_runs,
        "n": n,
        "acepta_H0": acepta,
        "interpretacion": (
            "No se rechaza H0. No hay tendencia significativa en la secuencia."
            if acepta
            else "Se rechaza H0. Hay tendencia en la secuencia."
        ),
    }


def prueba_independencia_autocorrelacion(numeros, lag=1, alpha=0.05):
    n = len(numeros)
    if n < lag + 2:
        raise ValueError(f"Se necesitan al menos {lag + 2} números para el rezago {lag}")
    media = sum(numeros) / n
    numerador = sum((numeros[i] - media) * (numeros[i + lag] - media) for i in range(n - lag))
    denominador = sum((x - media) ** 2 for x in numeros)
    if denominador == 0:
        return {
            "prueba": f"Autocorrelación (lag={lag})",
            "estadistico": "Z",
            "valor_calculado": 0.0,
            "valor_critico": 0.0,
            "limite_inferior": 0,
            "limite_superior": 0,
            "alpha": alpha,
            "autocorrelacion": 0.0,
            "lag": lag,
            "n": n,
            "acepta_H0": True,
            "interpretacion": "Varianza cero. No es posible evaluar.",
        }
    autocorr = numerador / denominador
    z_calc = autocorr * math.sqrt(n - lag)
    z_alpha2 = _normal_inv(1 - alpha / 2)
    acepta = abs(z_calc) < z_alpha2
    error = 1.0 / math.sqrt(n - lag)
    return {
        "prueba": f"Autocorrelación (lag={lag})",
        "estadistico": "Z",
        "valor_calculado": z_calc,
        "valor_critico": z_alpha2,
        "limite_inferior": autocorr - z_alpha2 * error,
        "limite_superior": autocorr + z_alpha2 * error,
        "alpha": alpha,
        "autocorrelacion": autocorr,
        "lag": lag,
        "n": n,
        "acepta_H0": acepta,
        "interpretacion": (
            f"No se rechaza H0. No hay correlación significativa con lag={lag}."
            if acepta
            else f"Se rechaza H0. Hay correlación significativa con lag={lag}."
        ),
    }


def ejecutar_todas(numeros, intervalos=10, alpha=0.05, lag=1):
    return [
        prueba_promedio(numeros, alpha),
        prueba_varianza(numeros, alpha),
        prueba_chi_cuadrada(numeros, intervalos, alpha),
        prueba_uniformidad_ks(numeros, alpha),
        prueba_rachas(numeros, alpha),
        prueba_rachas_tendencia(numeros, alpha),
        prueba_independencia_autocorrelacion(numeros, lag, alpha),
    ]
