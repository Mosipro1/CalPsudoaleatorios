def extraer_digitos_centrales(numero, n):
    if n <= 0:
        raise ValueError("El número de dígitos centrales debe ser positivo")
    s = str(int(numero))
    if len(s) < n:
        s = s.zfill(n)
    start = (len(s) - n) // 2
    return int(s[start:start + n])
