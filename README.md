DataMarket - Pipeline de Datos
Etapa 1: Ingesta de Datos Climaticos Automatizada
---
Contexto
DataMarket monitorea el clima de sus 10 sucursales en Chile para correlacionar
las condiciones climaticas con el comportamiento de ventas diarias.
Este script automatiza la captura de esos datos desde una API publica en tiempo real.
---
Fuente de datos: Open-Meteo API
Parametro	Detalle
URL	`https://api.open-meteo.com/v1/forecast`
Costo	Gratuita
Registro	No requerido
API Key	No requerida
Datos	Temperatura, humedad, velocidad del viento en tiempo real
La API recibe como parametros la latitud y longitud de cada ciudad
y responde con las condiciones climaticas actuales en formato JSON.
---
Como ejecutarlo
```bash
# No requiere librerias externas, solo Python 3.10+
python ingesta.py
```
Requiere conexion a internet para consultar la API de Open-Meteo.
---
Archivos generados
```
data/
└── raw/
    └── clima_sucursales.csv      <- datos crudos en tiempo real
logs/
└── ingesta_YYYYMMDD_HHMMSS.log  <- registro de la ejecucion
```
---
Columnas del CSV de salida
Columna	Descripcion
ciudad	Nombre de la sucursal
pais	Pais de la sucursal
latitud	Coordenada geografica
longitud	Coordenada geografica
temperatura_c	Temperatura en grados Celsius
humedad_pct	Humedad relativa en porcentaje
viento_kmh	Velocidad del viento en km/h
descripcion_viento	Descripcion segun escala Beaufort
fecha_consulta	Fecha en que se ejecuto la ingesta
hora_consulta	Hora exacta de la consulta
---
Estructura del proyecto
```
datamarket/
├── ingesta.py          <- script principal (Etapa 1)
├── README.md           <- este archivo
├── .gitignore          <- excluye logs y datos generados
├── data/
│   ├── raw/            <- datos crudos ingresados desde la API
│   └── processed/      <- datos limpios (Etapa 2)
└── logs/               <- registros de cada ejecucion
```
---
Trazabilidad
Cada ejecucion genera un log con timestamp unico que registra lo siguiente:
Inicio y fin del proceso
Ciudad consultada en cada llamada a la API
Cantidad de consultas exitosas y fallidas
Ruta del archivo CSV generado
---
Sucursales monitoreadas
Santiago, Valparaiso, Concepcion, Antofagasta, La Serena,
Temuco, Iquique, Puerto Montt, Arica, Rancagua.
---
Proxima etapa
Etapa 2 con limpieza.py: leera data/raw/clima_sucursales.csv,
aplicara transformaciones y normalizaciones, y generara
data/processed/clima_limpio.csv.
