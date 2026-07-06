def rk4_step(f, t, y, dt):
    k1 = f(t, y)
    k2 = f(t + dt / 2, [yi + dt * k1i / 2 for yi, k1i in zip(y, k1)])
    k3 = f(t + dt / 2, [yi + dt * k2i / 2 for yi, k2i in zip(y, k2)])
    k4 = f(t + dt, [yi + dt * k3i for yi, k3i in zip(y, k3)])
    return [yi + dt * (k1i + 2 * k2i + 2 * k3i + k4i) / 6 for yi, k1i, k2i, k3i, k4i in zip(y, k1, k2, k3, k4)]


def simular(alpha, beta, delta, gamma, dolares0, presion0, tiempo):
    dt = 0.05
    iteraciones = int(round(tiempo / dt))
    resultados = []
    x, y = dolares0, presion0
    t = 0.0

    def sistema(_t, estado):
        xv, yv = estado
        dx = alpha * xv - beta * xv * yv
        dy = delta * xv * yv - gamma * yv
        return [dx, dy]

    for i in range(iteraciones):
        resultados.append({
            "t": round(t, 4),
            "dolares": round(x, 4),
            "presion": round(y, 4),
        })
        x, y = rk4_step(sistema, t, [x, y], dt)
        t += dt
        if x < 0:
            x = 0.0
        if y < 0:
            y = 0.0

    x_eq = round(gamma / delta, 4) if delta != 0 else 0
    y_eq = round(alpha / beta, 4) if beta != 0 else 0

    return {
        "resultados": resultados,
        "equilibrio": {"dolares": x_eq, "presion": y_eq},
    }
