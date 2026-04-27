# ⛅ tiempo_clima

**Proyecto práctico** de la asignatura **Gestión de Datos para la IA**.

Este repositorio automatiza la **ingesta y limpieza** de datos climáticos en tiempo real de 10 sucursales en Chile. El objetivo es obtener datos meteorológicos confiables para posteriormente **correlacionar las condiciones climáticas con el comportamiento de ventas diarias**.

---

## ✨ Características

- Ingesta automática de datos climáticos mediante la API pública **Open-Meteo** (sin clave API).
- Limpieza y normalización de los datos crudos.
- Logging detallado con timestamp único en cada ejecución.
- Estructura organizada de carpetas (`raw` / `processed`).
- Sin dependencias externas (solo Python estándar).

---

## 🛠️ Tecnologías

- **Python 3.10+**
- **Open-Meteo API** (`https://api.open-meteo.com/v1/forecast`)
- Datos recolectados: temperatura, humedad relativa, velocidad del viento, descripción del viento (escala Beaufort), coordenadas y timestamp.

---

## 🚀 Cómo ejecutar

### 1. Ingesta de datos (Etapa 1)
```bash
python ingesta.py
2. Limpieza de datos (Etapa 2)
Bashpython limpieza.py
Requisitos:

Conexión a internet (solo para ingesta.py)
Python 3.10 o superior


📁 Estructura del proyecto
Bashtiempo_clima/
├── ingesta.py                  # Etapa 1: Consulta a la API y guarda datos crudos
├── limpieza.py                 # Etapa 2: Lee, limpia y normaliza los datos
├── README.md
├── .gitignore
├── data/
│   ├── raw/
│   │   └── clima_sucursales.csv          # Datos crudos desde la API
│   └── processed/
│       └── clima_limpio.csv              # Datos limpios y transformados
└── logs/
    └── ingesta_YYYYMMDD_HHMMSS.log       # Registro detallado de cada ingesta

📊 Archivos generados

data/raw/clima_sucursales.csv → Datos crudos obtenidos de Open-Meteo
data/processed/clima_limpio.csv → Datos limpios y listos para análisis
logs/ingesta_*.log → Log de ejecución con trazabilidad completa

Columnas principales del CSV


🌆 Sucursales monitoreadas

Santiago
Valparaíso
Concepción
Antofagasta
La Serena
Temuco
Iquique
Puerto Montt
Arica
Rancagua


📋 Etapas del proyecto

Etapa 1 (Completada): ingesta.py → Captura de datos en tiempo real
Etapa 2 (Completada): limpieza.py → Limpieza, transformación y normalización
Etapa 3 (Pendiente): Análisis exploratorio + correlación con datos de ventas


📌 Trazabilidad
Cada ejecución de ingesta.py genera un log que registra:

Inicio y fin del proceso
Ciudades consultadas
Cantidad de consultas exitosas y fallidas
Ruta del archivo CSV generado
