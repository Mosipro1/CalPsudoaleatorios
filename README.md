# Generador de Números Pseudoaleatorios

Tres métodos de generación de números pseudoaleatorios con interfaz web.

## Requisitos

- Python 3.6 o superior

## Instalación

```bash
git clone git@github.com:Mosipro1/CalPsudoaleatorios.git
cd CalPsudoaleatorios
```

## Iniciar el servidor

```bash
python3 server.py
```

Abrir en el navegador: [http://localhost:8000](http://localhost:8000)

## Uso

1. Seleccionar un método en las pestañas.
2. Ingresar los parámetros (semillas, constantes, iteraciones, dígitos centrales).
3. Presionar **Generar** para ver los resultados en la tabla.
4. Usar **Limpiar** para borrar la tabla.

## Métodos

### Multiplicador Constante

Parámetros: semilla, constante (a), valor inicial (X₀), iteraciones, dígitos centrales.

En cada iteración se multiplica el valor anterior por la constante `a`, se extraen los N dígitos centrales del producto, y se divide entre 10^N para obtener `ri ∈ [0,1)`. El valor extraído se usa como entrada de la siguiente iteración.

### Productos Medios

Parámetros: semilla 1, semilla 2, iteraciones, dígitos centrales.

Se multiplican las dos últimas semillas, se extraen los N dígitos centrales del producto, y se divide entre 10^N. El proceso se repite usando los dos valores más recientes (desplazando la semilla más antigua).

### Cuadrados Medios

Parámetros: semilla, iteraciones, dígitos centrales.

En cada iteración se eleva el valor anterior al cuadrado, se extraen los N dígitos centrales, y se divide entre 10^N. El resultado se usa como entrada de la siguiente iteración.

## Estructura del proyecto

```
├── server.py              Servidor HTTP (sin dependencias externas)
├── main.py                Interfaz gráfica con tkinter (opcional)
├── static/index.html      Interfaz web
└── modulos/
    ├── __init__.py         Función compartida extraer_digitos_centrales()
    ├── multiplicador_constante.py
    ├── productos_medios.py
    └── cuadrados_medios.py
```
