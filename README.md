# Calculadora de Simulación

Proyecto académico para la materia de **Simulación**. Implementa **6 métodos de generación de números pseudoaleatorios**, el **modelo depredador-presa de Lotka-Volterra** con integración RK4, **7 pruebas estadísticas** para verificar uniformidad, independencia y aleatoriedad, un **juego completo de ruleta europea** con sonidos procedurales y estadísticas, y un **reproductor de música** vía YouTube.

Todo accesible desde **interfaz gráfica Tkinter** (escritorio) o **interfaz web** (navegador con Chart.js y modo oscuro).

## Requisitos

### Obligatorios

- **Python 3.6 o superior**
- **matplotlib** (para la interfaz gráfica Tkinter)

### Opcionales

- **yt-dlp** + **ffmpeg/ffplay** → reproductor de música en Tkinter
- **pactl** (PipeWire/PulseAudio) → control de volumen del reproductor

## Instalación

```bash
git clone <repo-url>
cd CalDePseudoaleatorios

# (Opcional) Entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install matplotlib

# (Opcional) Para el reproductor de música
pip install yt-dlp
# Instalar ffmpeg: sudo apt install ffmpeg   (Linux)
```

## Ejecución

### Interfaz gráfica (Tkinter)

```bash
python3 main.py
```

- 12 pestañas: 6 generadores + Lotka-Volterra + Dólares + Quinua + Pruebas + Ruleta + Covid
- Gráficos de barras e histogramas con matplotlib
- Reproductor de música integrado

### Interfaz web

```bash
python3 server.py
```

Abrir en el navegador: [http://localhost:8000](http://localhost:8000)

> Si el puerto 8000 está ocupado, el servidor busca automáticamente el siguiente puerto libre (8001, 8002, etc.) y muestra un mensaje indicando en cuál inició.

- Mismas funcionalidades que la interfaz Tkinter
- Gráficos con **Chart.js** (cargado desde CDN)
- **Modo oscuro** automático (respeta preferencia del sistema, persiste en localStorage)
- Diseño responsive

## Métodos de generación incluidos

### 1. Multiplicador Constante

```
X_{n+1} = dígitos_centrales(a · X_n)
r_i = X_{n+1} / 10^d
```

Extrae los `d` dígitos centrales del producto entre el valor anterior y una constante `a`. Propuesto por von Neumann en 1949.

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `a` | Constante multiplicadora | 5 |
| `X₀` | Semilla o valor inicial | 1234 |
| `iteraciones` | Cantidad de números a generar | 10 |
| `d` | Dígitos centrales a extraer | 4 |

### 2. Productos Medios

```
X_{n+1} = dígitos_centrales(X_{n-1} · X_n)
r_i = X_{n+1} / 10^d
```

Similar al método de cuadrados medios, pero multiplica las dos últimas semillas en lugar de elevar al cuadrado. Requiere dos semillas iniciales.

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `semilla1` | Primera semilla inicial | 1234 |
| `semilla2` | Segunda semilla inicial | 5678 |
| `iteraciones` | Cantidad de números a generar | 10 |
| `d` | Dígitos centrales a extraer | 4 |

### 3. Cuadrados Medios

```
X_{n+1} = dígitos_centrales(X_n²)
r_i = X_{n+1} / 10^d
```

Eleva al cuadrado el valor anterior y extrae los `d` dígitos centrales. Propuesto por von Neumann y Metropolis en los años 1940.

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `semilla` | Semilla inicial | 1234 |
| `iteraciones` | Cantidad de números a generar | 10 |
| `d` | Dígitos centrales a extraer | 4 |

### 4. Congruencial Lineal (LCG)

```
X_{n+1} = (a · X_n + c) mod m
r_i = X_n / (m - 1)
```

Generador congruencial lineal general. Con parámetros que cumplen Hull-Dobell alcanza período completo igual a `m`.

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `a` | Multiplicador | 1664525 |
| `c` | Incremento | 1013904223 |
| `m` | Módulo | 2³² = 4294967296 |
| `X₀` | Semilla inicial | 12345 |
| `iteraciones` | Cantidad de números a generar | 10 |

Los defaults corresponden al generador usado en la biblioteca glibc (DRNG).

### 5. Congruencial Multiplicativo (MCG)

```
X_{n+1} = (a · X_n) mod m
r_i = X_n / (m - 1)
```

Caso particular del LCG con `c = 0`. El generador Lewis-Good-Miller (MINSTD) con `a = 16807`, `m = 2³¹ − 1` es uno de los más estudiados.

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `a` | Multiplicador | 16807 |
| `m` | Módulo | 2³¹−1 = 2147483647 |
| `X₀` | Semilla inicial | 12345 |
| `iteraciones` | Cantidad de números a generar | 10 |

### 6. Mersenne Twister (MT19937)

Wrapper del algoritmo MT19937 implementado en `random.Random` de Python. Período de `2¹⁹⁹³⁷ − 1`, el más largo de todos los generadores. Estándar moderno para simulaciones no criptográficas.

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `semilla` | Semilla inicial | 42 |
| `iteraciones` | Cantidad de números a generar | 10 |

## Simulación Covid (Autómata Celular)

Simulación de propagación de enfermedades mediante **autómatas celulares**, similar al Juego de la Vida de Conway. Cada celda representa una persona y cambia de estado según reglas de transición locales y probabilísticas.

### Estados

| Estado | Color | Descripción |
|--------|-------|-------------|
| **Sano** (0) | Azul | Persona susceptible al contagio |
| **Infectado** (1) | Rojo | Persona contagiada activamente |
| **Recuperado** (2) | Verde | Persona inmune (no se reinfecta) |
| **Fallecido** (3) | Gris oscuro | Persona fallecida |
| **Vacío** (4) | Gris claro | Espacio sin persona (distancia social) |

### Reglas de transición

Por cada iteración (día simulado), se evalúa cada celda aplicando las siguientes reglas en orden:

1. **Sano → Infectado**: si al menos un vecino en la **vecindad de Moore** (8 celdas adyacentes) está infectado, la persona se contagia con probabilidad `P_contagio`
2. **Infectado → Fallecido**: en cada día que la persona está infectada, puede fallecer con probabilidad `P_muerte`
3. **Infectado → Recuperado**: si la persona ha estado infectada durante `días_recuperación` o más, se recupera y obtiene inmunidad
4. **Recuperado**: permanece recuperado (inmune) por el resto de la simulación
5. **Fallecido / Vacío**: permanecen en su estado (no cambian)

El modelo usa una **cuadrícula 2D** con **condiciones de frontera fijas** (los bordes no envuelven). La actualización es **síncrona** — todas las celdas se evalúan usando el estado de la iteración anterior y cambian simultáneamente.

### Parámetros configurables

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `Filas` | Altura de la cuadrícula | 50 |
| `Columnas` | Ancho de la cuadrícula | 50 |
| `Densidad población` | Fracción de celdas ocupadas (0–1) | 0.85 |
| `Infectados iniciales` | Cantidad de personas infectadas al inicio | 5 |
| `Prob. contagio` | Probabilidad de contagio por vecino infectado | 0.30 |
| `Días recuperación` | Días que tarda en recuperarse un infectado | 14 |
| `Prob. muerte` | Probabilidad diaria de fallecer estando infectado | 0.02 |
| `Iteraciones` | Número de días a simular | 100 |
| `Velocidad (ms)` | Intervalo entre pasos en milisegundos | 100 |

### Visualización

- **Grid**: mapa de calor donde cada celda se colorea según su estado (5 colores distintos)
- **Evolución**: gráfico de líneas que muestra la población S/I/R/D a lo largo del tiempo
- **Contadores**: número actual de personas en cada estado

### Controles

- ▶ **Iniciar**: comienza la simulación con los parámetros actuales
- ⏸ **Pausar/Reanudar**: pausa o reanuda la simulación
- ⏭ **Paso**: avanza una iteración manualmente
- ↺ **Reiniciar**: reinicia la simulación desde cero

## Simulación Quinua (Planta Procesadora)

Modelo Lotka-Volterra aplicado a una planta procesadora de quinua. Analiza la relación dinámica entre el **stock de quinua disponible** y el **nivel de procesamiento de la planta**.

### Analogía industrial

| Modelo clásico | Planta procesadora de quinua |
|----------------|------------------------------|
| Presas | Stock de quinua en almacén |
| Depredadores | Capacidad o nivel de procesamiento |
| Crecimiento de presas | Llegada de quinua de productores |
| Depredación | Consumo de quinua por la planta |
| Aumento de depredadores | Mayor procesamiento cuando hay suficiente stock |
| Muerte de depredadores | Reducción por mantenimiento, costos, fallas o baja demanda |

### Ecuaciones

```
dx/dt = α·x − β·x·y   (stock de quinua)
dy/dt = δ·x·y − γ·y   (nivel de procesamiento)
```

Integración numérica con **Runge-Kutta de 4º orden (RK4)**. Incluye animación con punto móvil que recorre las curvas en tiempo real.

### Parámetros

| Parámetro | Descripción | Default | Rango |
|-----------|-------------|---------|-------|
| `α` | Tasa de llegada de quinua | 0.50 | 0.01–1.0 |
| `β` | Tasa de consumo por procesamiento | 0.02 | 0.01–0.5 |
| `δ` | Conversión de stock disponible en producción activa | 0.01 | 0.001–0.3 |
| `γ` | Reducción por mantenimiento, costos, fallas o baja demanda | 0.30 | 0.01–1.0 |
| `stock₀` | Stock inicial de quinua (kg) | 100 | 1–500 |
| `proceso₀` | Nivel inicial de procesamiento (kg/día) | 30 | 1–200 |
| `tiempo` | Duración de la simulación (días) | 100 | 20–200 |

### Punto de equilibrio

```
x_eq = γ/δ   (stock de equilibrio)
y_eq = α/β   (procesamiento de equilibrio)
```

### Visualización

- **Evolución temporal**: stock (verde) y procesamiento (azul) a lo largo del tiempo con línea de equilibrio
- **Espacio de fases**: trayectoria stock vs. procesamiento con estrella del punto de equilibrio
- **Animación**: punto que avanza sobre ambas curvas simultáneamente

### Pregunta central

¿Cómo afecta la relación entre el stock de quinua y la capacidad de procesamiento al funcionamiento de una planta industrial?

Controles: ▶ Iniciar, ⏸ Pausar, ⏭ Paso, ↺ Reiniciar.

### Ejemplo de simulación

Parámetros default:
- α = 0.50, β = 0.02, δ = 0.01, γ = 0.30
- Stock inicial = 100 kg, Procesamiento inicial = 30 kg/día
- Tiempo = 100 días

Punto de equilibrio: stock_eq = γ/δ = 30 kg, proc_eq = α/β = 25 kg/día

| t (días) | Stock (kg) | Procesamiento (kg/día) |
|----------|-----------|----------------------|
| 0.0 | 100.00 | 30.00 |
| 12.5 | 67.09 | 21.41 |
| 25.0 | 44.01 | 18.89 |
| 37.5 | 23.46 | 26.88 |
| 50.0 | 28.75 | 37.82 |
| 62.5 | 72.34 | 30.54 |
| 75.0 | 72.74 | 18.90 |
| 87.5 | 35.79 | 14.21 |
| 100.0 | 11.53 | 24.55 |

**Interpretación**: La simulación muestra ciclos de aproximadamente 50 días donde el stock de quinua y el procesamiento oscilan alrededor del punto de equilibrio (stock=30 kg, proc=25 kg/día). Cuando el stock es alto (>70 kg), el procesamiento aumenta, lo que reduce el stock. Al bajar el stock (<20 kg), el procesamiento se reduce por falta de materia prima, permitiendo que el stock se recupere.

## Modelo Dólares (Económico Lotka-Volterra)

Modelo depredador-presa adaptado a la dinámica económica boliviana, donde la **disponibilidad de dólares** actúa como presa y la **presión cambiaria** como depredador:

```
dx/dt = α·x − β·x·y   (dólares — disponibilidad)
dy/dt = δ·x·y − γ·y   (presión cambiaria)
```

Integración numérica con **Runge-Kutta de 4º orden (RK4)**. Incluye animación con punto móvil que recorre las curvas en tiempo real.

### Punto de equilibrio

```
x_eq = γ/δ   (dólares de equilibrio)
y_eq = α/β   (presión de equilibrio)
```

### Parámetros

| Parámetro | Descripción | Default | Rango |
|-----------|-------------|---------|-------|
| `α` | Entrada de dólares (tasa de crecimiento) | 0.25 | 0.01–1.0 |
| `β` | Presión sobre dólares (tasa de depredación) | 0.08 | 0.01–0.5 |
| `δ` | Crecimiento de la presión cambiaria | 0.04 | 0.01–0.3 |
| `γ` | Estabilización (mortalidad de la presión) | 0.30 | 0.01–1.0 |
| `dólares₀` | Disponibilidad inicial de dólares | 10 | 1–30 |
| `presión₀` | Presión cambiaria inicial | 4 | 1–30 |
| `tiempo` | Duración de la simulación | 60 | 20–150 |

### Visualización

- **Evolución temporal**: gráfico de líneas mostrando dólares (ámbar) y presión (rojo) a lo largo del tiempo, con línea punteada del punto de equilibrio
- **Espacio de fases**: trayectoria cíclica dólares vs. presión con estrella verde del punto de equilibrio
- **Animación**: punto que avanza sobre ambas curvas simultáneamente con slider de parámetros

### Interpretación económica

- Si la **presión cambiaria** supera cierto umbral, la **disponibilidad de dólares** cae
- Con pocos dólares disponibles, la **presión** se desinfla por falta de demanda
- Al estabilizarse la presión, los **dólares** se recuperan gradualmente
- El **punto de equilibrio** representa el escenario estable ideal

Controles: ▶ Iniciar, ⏸ Pausar, ⏭ Paso, ↺ Reiniciar.

## Modelo Lotka-Volterra

Sistema de ecuaciones diferenciales ordinarias que modela la dinámica entre poblaciones de presas y depredadores:

```
dx/dt = α·x − β·x·y   (presa)
dy/dt = δ·x·y − γ·y   (depredador)
```

Integración numérica con **Runge-Kutta de 4º orden (RK4)**.

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `α` | Tasa de natalidad de las presas | 1.5 |
| `β` | Tasa de depredación | 1.0 |
| `δ` | Tasa de crecimiento de los depredadores | 3.0 |
| `γ` | Tasa de mortalidad de los depredadores | 1.0 |
| `x₀` | Población inicial de presas | 10 |
| `y₀` | Población inicial de depredadores | 5 |
| `dt` | Paso temporal de integración | 0.01 |
| `iteraciones` | Cantidad de pasos de integración | 500 |

La tabla de resultados se muestrea automáticamente (cada ~50 iteraciones) para no saturar la interfaz.

## Pruebas estadísticas incluidas

### Tabla comparativa

| Prueba | Estadístico | H₀ (hipótesis nula) |
|--------|-------------|---------------------|
| **Promedio** | `Z = (x̄ − 0.5) · √(12n)` | μ = 0.5 |
| **Varianza** | `χ² = 12 · Σ(xi − 0.5)²` | σ² = 1/12 |
| **Chi-cuadrada** | `χ² = Σ(Oᵢ − Eᵢ)² / Eᵢ` | Los datos siguen una uniforme |
| **Kolmogorov-Smirnov** | `D = max(D⁺, D⁻)` | Los datos siguen una uniforme |
| **Rachas (↑↓)** | `Z = (R − μ_R) / σ_R` | La secuencia es aleatoria |
| **Rachas de tendencia** | `Z = (R − μ_R) / σ_R` | No hay tendencia |
| **Autocorrelación** | `Z = ρ_k · √(n − k)` | ρ_k = 0 (independencia) |

### Detalle de cada prueba

**Promedio**: Verifica si la media de los números generados es significativamente distinta de 0.5 (valor esperado para una uniforme U(0,1)). El estadístico Z sigue una normal estándar bajo H₀.

**Varianza**: Verifica si la varianza muestral es consistente con σ² = 1/12 ≈ 0.0833. El estadístico χ² sigue una chi-cuadrada con `n` grados de libertad.

**Chi-cuadrada**: Prueba de bondad de ajuste. Divide [0, 1) en `k` intervalos de igual longitud y compara frecuencias observadas contra esperadas (n/k). Grados de libertad: `k − 1`.

**Kolmogorov-Smirnov**: Compara la FDA empírica con la FDA teórica de U(0,1). Calcula `D⁺` y `D⁻`. El valor crítico se calcula dinámicamente según el alpha ingresado: `D_α = √(−½·ln(α/2)) / √n`.

**Rachas (arriba/abajo)**: Cuenta rachas de valores consecutivos por encima/debajo de la media y compara con el valor esperado para una secuencia aleatoria. Detecta correlación positiva (pocas rachas) o negativa (muchas rachas).

**Rachas de tendencia (sube/baja)**: Cuenta rachas de incrementos/decrementos consecutivos. Detecta tendencias sistemáticas.

**Autocorrelación**: Calcula el coeficiente de autocorrelación con un rezago `lag` configurable y verifica si es significativamente distinto de cero.

### Salida de cada prueba

Todas las pruebas reportan:
- **Valor calculado** del estadístico
- **Valor(es) crítico(s)** según el nivel de significancia α
- **Límite inferior y superior** del intervalo de aceptación
- **Decisión** sobre H₀ (SÍ/NO) con interpretación en lenguaje natural

### Configuración de pruebas

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `α` | Nivel de significancia | 0.05 |
| `Intervalos` | Número de intervalos para χ² | 10 |
| `Lag` | Rezago para la prueba de autocorrelación | 1 |

## Juego de Ruleta Europea

Ruleta completa con números del 0 al 36, colores rojo/negro/verde, y múltiples tipos de apuesta. Toda la lógica de simulación está en `modulos/roulette/`.

### Cómo simula la ruleta

#### 1. Generación del número ganador (`engine.py`)

Cada vez que el jugador gira, el motor usa `secrets.SystemRandom().randint(0, 36)` para obtener un número entero uniforme entre 0 y 36. Se eligió `secrets` en lugar de `random` porque:
- Proporciona números **criptográficamente seguros** (impredecibles)
- Es apropiado para un juego donde la predictibilidad afecta la confianza
- Sigue una distribución uniforme real en el rango [0, 36]

No hay sesgo ni "casa" simulada — el resultado es puramente aleatorio. La ventaja de la casa emerge naturalmente del pago 36:1 para un pleno cuando hay 37 números posibles (la probabilidad real es 1/37 ≈ 2.70%, no 1/36 ≈ 2.78%).

#### 2. Layout de la rueda (`wheel_layout.py`)

La secuencia de números en la ruleta sigue el orden estándar de la ruleta europea:

```
0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36,
11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9,
22, 18, 29, 7, 28, 12, 35, 3, 26
```

Los colores se asignan según la ruleta europea real: 18 rojos (`ROJOS`), 18 negros y 1 verde (el 0). El color se determina por pertenencia al conjunto `ROJOS` — no hay alternancia simple.

#### 3. Sistema de apuestas (`bets.py`)

Cada tipo de apuesta es una **dataclass** que hereda de `Bet` e implementa el método `pagar(resultado) -> int`:

| Clase | Descripción | Pago |
|-------|-------------|------|
| `StraightUp` | Número único | 36 × monto |
| `Split` | Dos números adyacentes | 18 × monto |
| `Street` | Fila de 3 números | 12 × monto |
| `Corner` | Esquina de 4 números | 9 × monto |
| `SixLine` | Dos filas (6 números) | 6 × monto |
| `Red` / `Black` | Color del número | 2 × monto |
| `Even` / `Odd` | Paridad | 2 × monto |
| `Low` / `High` | Bajo (1-18) / Alto (19-36) | 2 × monto |
| `Dozen` | Docena (1-12, 13-24, 25-36) | 3 × monto |
| `Column` | Columna vertical (12 números) | 3 × monto |

El motor calcula los pagos iterando todas las apuestas, llamando a `pagar(resultado)` y sumando las ganancias. Si el resultado es 0, pierden todas las apuestas excepto `StraightUp(0)`.

#### 4. Flujo de una partida

```
Jugador → coloca apuesta(s) → se descuenta el saldo
  ↓
Jugador → presiona GIRAR
  ↓
Motor → secrets.randint(0, 36) → número ganador
  ↓
Motor → calcular_pagos(apuestas, resultado) → ganancia total
  ↓
Jugador → cobrar(ganancia) → se actualiza el saldo
  ↓
Jugador → registrar_giro() → guarda en historial
  ↓
Player → guardar() → persiste a roulette_data.json
  ↓
Statistics → registrar(resultado) → actualiza frecuencias
```

#### 5. Animación de la rueda

En la interfaz Tkinter, se dibuja la rueda en un `Canvas` dividiendo el círculo en 37 segmentos con `create_arc`. Cada segmento se colorea según el número (rojo/negro/verde). Al girar:

1. Se calcula el ángulo objetivo del número ganador
2. La rueda da 4 vueltas completas (1440°) + el ángulo objetivo
3. La animación usa **easing cúbico** (`1 - (1 - t)³`) para simular la desaceleración real
4. 90 frames a ~30 FPS (33ms por frame) para una animación suave de ~3 segundos

En la interfaz web, la animación se maneja de forma similar con `requestAnimationFrame` y el mismo easing cúbico, renderizando en un `<canvas>` HTML.

#### 6. Persistencia (`player.py`)

El estado del jugador se guarda en `roulette_data.json`:

```json
{
  "saldo": 10000,
  "historial": [...],
  "mayor_victoria": 0,
  "mayor_derrota": 0,
  "total_ganado": 0,
  "total_perdido": 0
}
```

- Se carga al iniciar el programa
- Se guarda después de cada giro
- Máximo 100 entradas en el historial (las más recientes)

#### 7. Estadísticas en vivo (`statistics.py`)

Después de cada giro se actualizan:
- **Frecuencias**: porcentaje de rojo, negro, verde, par, impar, bajo, alto
- **Rachas actuales**: racha consecutiva de rojo y negro
- **Números calientes**: los 5 números con mayor frecuencia
- **Números fríos**: los 5 números con menor frecuencia
- **Historial**: últimos 20 números mostrados como dots de colores

### Sonidos

Sonidos generados proceduralmente (sine, square, sawtooth, noise) mediante `wave` + `struct`. El `SoundManager` genera archivos WAV en memoria y los reproduce con el primer reproductor disponible (`paplay`, `aplay` o `ffplay`):

| Acción | Sonido |
|--------|--------|
| Clic en ficha | Click seco (square, 900 Hz) |
| Colocar ficha | Doble tono (sine, 600→800 Hz) |
| Giro de rueda | Barrido ascendente (sawtooth, 150→390 Hz, 20 ticks) |
| Ganar | Arpegio ascendente (Do-Mi-Sol, 523→659→784 Hz) |
| Perder | Descenso grave (sawtooth, 250→180 Hz) |

### Controles adicionales

- **Deshacer**: elimina la última apuesta colocada
- **Limpiar mesa**: devuelve todas las fichas al saldo

## Reproductor de música (Tkinter)

Reproduce música de YouTube directamente en la interfaz gráfica.

| Componente | Descripción |
|------------|-------------|
| **Fuente** | YouTube (actualmente: "Fondue — Instrumental") |
| **Dependencias** | `yt-dlp` + `ffplay` (ffmpeg) |
| **Control de volumen** | Slider integrado (vía pactl) |
| **Fallback** | Si ffplay no está disponible, abre el video en el navegador |

## API REST (servidor web)

El servidor en `server.py` expone los siguientes endpoints (`POST`):

| Endpoint | Función |
|----------|---------|
| `/api/multiplicador_constante` | Generar números con multiplicador constante |
| `/api/multiplicador_constante/periodo` | Verificar período del generador |
| `/api/productos_medios` | Generar números con productos medios |
| `/api/productos_medios/periodo` | Verificar período del generador |
| `/api/cuadrados_medios` | Generar números con cuadrados medios |
| `/api/cuadrados_medios/periodo` | Verificar período del generador |
| `/api/congruencial_lineal` | Generar números con LCG |
| `/api/congruencial_lineal/periodo` | Verificar período del generador |
| `/api/congruencial_multiplicativo` | Generar números con MCG |
| `/api/congruencial_multiplicativo/periodo` | Verificar período del generador |
| `/api/mersenne_twister` | Generar números con MT19937 |
| `/api/mersenne_twister/periodo` | Verificar período del generador |
| `/api/lotka_volterra` | Ejecutar simulación Lotka-Volterra |
| `/api/dolares_sim` | Ejecutar simulación económica Dólares |
| `/api/quinua_sim` | Ejecutar simulación planta procesadora de quinua |
| `/api/pruebas_estadisticas` | Ejecutar pruebas estadísticas |
| `/api/covid_sim` | Ejecutar simulación Covid (autómata celular) |
| `/api/roulette/spin` | Girar la ruleta (requiere cuerpo con apuestas) |

El servidor también sirve archivos estáticos desde `static/` y escucha en `0.0.0.0:8000`.

## Flujo de trabajo recomendado

### Generación y pruebas
1. Seleccionar un método de generación en las pestañas superiores
2. Configurar parámetros y presionar **Generar**
3. Revisar la tabla de resultados (Xn y ri) y los gráficos
4. Presionar **Enviar a Pruebas** → los números ri se copian automáticamente a la pestaña de pruebas
5. En la pestaña de pruebas, seleccionar qué pruebas ejecutar
6. Presionar **Ejecutar Pruebas** y analizar los resultados
7. Usar **Verificar Período** en cualquier generador para conocer cuántos números únicos produce antes de ciclar

### Ruleta
1. Seleccionar el valor de ficha deseado
2. Colocar una o más apuestas en la mesa
3. Presionar **GIRAR** y ver la animación
4. Revisar el resultado, ganancias y estadísticas actualizadas

## Estructura del proyecto

```
├── main.py                          Interfaz gráfica Tkinter (12 tabs)
├── server.py                        Servidor HTTP (17 endpoints API + estáticos)
├── roulette_data.json               Persistencia del saldo e historial de ruleta
├── static/
│   └── index.html                   Interfaz web (12 tabs, Chart.js, modo oscuro)
├── modulos/
│   ├── __init__.py                  Utilidad: extraer_digitos_centrales()
│   ├── multiplicador_constante.py   Generador: multiplicador constante
│   ├── productos_medios.py          Generador: productos medios
│   ├── cuadrados_medios.py          Generador: cuadrados medios
│   ├── congruencial_lineal.py       Generador: LCG (X_{n+1} = (a·X_n + c) mod m)
│   ├── congruencial_multiplicativo.py  Generador: MCG (X_{n+1} = (a·X_n) mod m)
│   ├── mersenne_twister.py          Generador: MT19937 (wrapper random.Random)
│   ├── lotka_volterra.py            Modelo depredador-presa con RK4
│   ├── dolares.py                   Modelo económico Dólares (LV adaptado) con RK4
│   ├── quinua.py                    Modelo planta procesadora de quinua (LV) con RK4
│   ├── pruebas_estadisticas.py      7 pruebas: promedio, varianza, χ², KS, 2×rachas, autocorr
│   ├── covid_sim.py                Simulación Covid (autómata celular, 5 estados, Moore)
│   └── roulette/
│       ├── __init__.py              Exportaciones del paquete
│       ├── wheel_layout.py          Secuencia de la rueda, colores, números rojos
│       ├── bets.py                  Tipos de apuesta (dataclasses, pagos)
│       ├── engine.py                Motor de la ruleta (spin, pagos)
│       ├── player.py                Jugador (saldo, historial, persistencia JSON)
│       ├── statistics.py            Estadísticas (frecuencias, rachas, calientes/fríos)
│       └── sounds.py                Sonidos procedurales (sine/square/sawtooth)
├── README.md
└── .gitignore
```

## Funcionalidades clave

- **6 generadores** de números pseudoaleatorios con parámetros configurables
- **Simulación Covid** con autómata celular, 5 estados, vecindad de Moore y reglas probabilísticas
- **Verificación de período** en cada generador con detección de ciclos
- **Período teórico** en LCG (criterio Hull-Dobell) y MCG (pares conocidos)
- **Modelo Lotka-Volterra** con integración RK4 y gráficos de población/espacio de fases
- **Modelo Dólares** (Lotka-Volterra económico): disponibilidad de dólares vs. presión cambiaria con animación y punto de equilibrio
- **7 pruebas estadísticas** con límites superior e inferior y valores críticos dinámicos
- **KS dinámico:** valor crítico calculado según el alpha ingresado (no hardcodeado)
- **Botón "Enviar a Pruebas":** transfiere automáticamente los números generados a la pestaña de pruebas
- **Juego de ruleta completa:** 6 tipos de ficha, 10 tipos de apuesta, animación de rueda, sonidos
- **Estadísticas de ruleta:** porcentajes, rachas, números calientes/fríos
- **Persistencia:** el saldo de la ruleta se guarda entre sesiones
- **Reproductor de música** integrado (YouTube vía yt-dlp + ffplay)
- **Modo oscuro** en interfaz web (respeta preferencia del sistema, persiste en localStorage)
- **Gráficos interactivos:** Chart.js (web) + matplotlib (Tkinter) — serie de barras e histograma
- **12 módulos de simulación:** 6 PRNG, Lotka-Volterra, Dólares, Quinua, Covid, Ruleta y Pruebas Estadísticas
- **Dos interfaces completas:** Tkinter (escritorio) y web (navegador)
- **Sin dependencias externas pesadas:** solo matplotlib es obligatorio; yt-dlp/ffmpeg son opcionales

## Librerías utilizadas

| Librería | Uso |
|----------|-----|
| `tkinter` / `ttk` | Interfaz gráfica de escritorio (notebook, treeview, canvas) |
| `matplotlib` | Gráficos en Tkinter (barras, histogramas, poblaciones) |
| `http.server` | Servidor web HTTP |
| `json` | Serialización de datos en API REST y persistencia de ruleta |
| `math` | Funciones matemáticas (sqrt, log, trigonométricas) |
| `random` | Wrapper de Mersenne Twister MT19937 |
| `secrets` | Generación criptográficamente segura para la ruleta |
| `threading` | Reproducción de sonidos y música en segundo plano |
| `subprocess` | Llamadas a ffplay/paplay/aplay para audio |
| `dataclasses` | Modelos de apuesta (Bet, StraightUp, Red, etc.) |
| `collections` | Contador de frecuencias para estadísticas de ruleta |
| `struct` / `wave` | Generación procedural de archivos WAV para sonidos |
| `os`, `urllib.parse` | Utilidades del sistema y parsing de rutas |
| `yt-dlp` (opcional) | Extracción de audio desde YouTube |
| `ffmpeg` / `ffplay` (opcional) | Reproducción de audio |
| `Chart.js` (web) | Gráficos interactivos en el navegador (cargado desde CDN) |
