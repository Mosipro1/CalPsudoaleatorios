# Calculadora de Simulación

Proyecto académico para la materia de Simulación. Implementa **6 métodos de generación de números pseudoaleatorios**, el **modelo depredador-presa de Lotka-Volterra** con integración RK4, y **7 pruebas estadísticas** para verificar uniformidad, independencia y aleatoriedad. Todo accesible desde interfaz gráfica Tkinter o interfaz web.

## Requisitos

- Python 3.6 o superior
- No requiere dependencias externas (usa `tkinter`, `http.server`, `math` y `random` de la biblioteca estándar)

## Instalación

```bash
git clone <repo-url>
cd CalDePseudoaleatorios
```

## Ejecución

### Interfaz gráfica (Tkinter)

```bash
python3 main.py
```

### Interfaz web

```bash
python3 server.py
```

Abrir en el navegador: [http://localhost:8000](http://localhost:8000)

## Métodos de generación incluidos

### 1. Multiplicador Constante

```
X_{n+1} = dígitos_centrales(a · X_n)
r_i = X_{n+1} / 10^d
```

Extrae los `d` dígitos centrales del producto entre el valor anterior y una constante `a`. Uno de los primeros métodos históricos (von Neumann, 1949).

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

Eleva al cuadrado el valor anterior y extrae los `d` dígitos centrales. Método propuesto por von Neumann y Metropolis en los años 1940.

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

Generador congruencial lineal general. Con parámetros bien elegidos (Hull-Dobell), alcanza período completo igual a `m`.

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

Wrapper del algoritmo MT19937 implementado en `random.Random` de Python. Período de `2¹⁹⁹³⁷ − 1` (el más largo de todos los generadores). Considerado el estándar moderno para simulaciones que no requieren criptografía.

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `semilla` | Semilla inicial | 42 |
| `iteraciones` | Cantidad de números a generar | 10 |

### 7. Lotka-Volterra (Modelo Depredador-Presa)

Sistema de ecuaciones diferenciales ordinarias:

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

**Promedio**: Verifica si la media de los números generados es significativamente distinta de 0.5 (valor esperado para una uniforme U(0,1)). El estadístico Z sigue una distribución normal estándar bajo H₀.

**Varianza**: Verifica si la varianza muestral es consistente con el valor teórico σ² = 1/12 ≈ 0.0833. El estadístico χ² sigue una distribución chi-cuadrada con `n` grados de libertad.

**Chi-cuadrada**: Prueba de bondad de ajuste. Divide [0, 1) en `k` intervalos de igual longitud y compara las frecuencias observadas contra las esperadas (n/k). Grados de libertad: `k − 1`.

**Kolmogorov-Smirnov**: Compara la función de distribución acumulada empírica con la FDA teórica de U(0,1). Calcula `D⁺` y `D⁻` (distancias máxima positiva y negativa). El valor crítico se calcula dinámicamente según el alpha ingresado usando la aproximación asintótica `D_α = √(−½·ln(α/2)) / √n` (no está hardcodeado para 0.05).

**Rachas (arriba/abajo)**: Cuenta el número de rachas (secuencias consecutivas de valores por encima o por debajo de la media) y lo compara con el valor esperado para una secuencia aleatoria. Detecta patrones como correlación positiva (pocas rachas) o negativa (muchas rachas).

**Rachas de tendencia (sube/baja)**: Cuenta rachas de incrementos/decrementos consecutivos. Detecta tendencias sistemáticas en la secuencia.

**Autocorrelación**: Calcula el coeficiente de autocorrelación con un rezago `lag` configurable y verifica si es significativamente distinto de cero. Evalúa la independencia entre observaciones separadas por `lag` posiciones.

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

## Flujo de trabajo recomendado

1. Seleccionar un método de generación en las pestañas superiores
2. Configurar parámetros y presionar **Generar**
3. Revisar la tabla de resultados (Xn y ri)
4. Presionar **Enviar a Pruebas** → los números ri se copian automáticamente a la pestaña de pruebas
5. En la pestaña de pruebas, seleccionar qué pruebas ejecutar
6. Presionar **Ejecutar Pruebas** y analizar los resultados
7. Usar **Verificar Período** en cualquier generador para conocer cuántos números únicos produce antes de ciclar

## Estructura del proyecto

```
├── main.py                        Interfaz gráfica con Tkinter (8 tabs)
├── server.py                      Servidor HTTP (14 endpoints API)
├── static/
│   └── index.html                 Interfaz web (8 tabs, JS fetch)
├── modulos/
│   ├── __init__.py                Utilidad compartida: extraer_digitos_centrales()
│   ├── multiplicador_constante.py Generador: multiplicador constante
│   ├── productos_medios.py        Generador: productos medios
│   ├── cuadrados_medios.py        Generador: cuadrados medios
│   ├── congruencial_lineal.py     Generador: LCG (X_{n+1} = (a·X_n + c) mod m)
│   ├── congruencial_multiplicativo.py  Generador: MCG (X_{n+1} = (a·X_n) mod m)
│   ├── mersenne_twister.py        Generador: MT19937 (wrapper random.Random)
│   ├── lotka_volterra.py          Modelo depredador-presa con RK4
│   └── pruebas_estadisticas.py    7 pruebas: promedio, varianza, χ², KS, 2×rachas, autocorr
├── README.md
└── .gitignore
```

## Funcionalidades clave

- **6 generadores** de números pseudoaleatorios con parámetros configurables
- **Verificación de período** en cada generador (detección de ciclos)
- **Modelo Lotka-Volterra** con integración RK4
- **7 pruebas estadísticas** con límites superior e inferior
- **KS dinámico:** valor crítico calculado según el alpha ingresado (no hardcodeado)
- **Botón "Enviar a Pruebas":** transfiere automáticamente los números generados a la pestaña de pruebas y cambia a ella
- **Dos interfaces completas:** Tkinter (escritorio) y web (navegador)
- **Sin dependencias externas:** solo biblioteca estándar de Python

## Librerías utilizadas

| Librería | Uso |
|----------|-----|
| `tkinter` / `ttk` | Interfaz gráfica de escritorio (notebook, treeview, entry) |
| `http.server` | Servidor web HTTP |
| `json` | Serialización de datos en API REST |
| `math` | Funciones matemáticas (sqrt, log) |
| `random` | Wrapper de Mersenne Twister MT19937 |
| `os`, `urllib.parse` | Utilidades del sistema y parsing de rutas |
