# ⛅ tiempo_clima

**Proyecto de práctica** para la asignatura **Gestión de Datos para la IA**.

Este script automatiza la **ingesta de datos climáticos en tiempo real** de 10 sucursales en Chile. El objetivo es recopilar información meteorológica para posteriormente **correlacionar las condiciones climáticas con el comportamiento de ventas diarias**.

---

## ✨ Características

- Consulta automática a la API pública **Open-Meteo** (gratuita y sin clave API).
- Monitoreo de 10 ciudades/sucursales clave de Chile.
- Generación de archivo CSV con datos crudos.
- Sistema de logging detallado con timestamp único.
- Sin dependencias externas (solo Python estándar).

---

## 🛠️ Tecnologías

- **Python 3.10+**
- **Open-Meteo API** (`https://api.open-meteo.com/v1/forecast`)
- Datos: temperatura, humedad, velocidad del viento, descripción (escala Beaufort), coordenadas y timestamp.

---

## 🚀 Cómo ejecutar

```bash
# Clonar el repositorio
git clone https://github.com/SebastianAVi/tiempo_clima.git
cd tiempo_clima

# Ejecutar el script de ingesta
python ingesta.py
Requisitos:

Conexión a internet
Python 3.10 o superior (no requiere instalación de paquetes)


📁 Estructura del proyecto
Bashtiempo_clima/
├── ingesta.py                  # Script principal (Etapa 1)
├── limpieza.py                 # (Próxima etapa)
├── README.md
├── .gitignore
├── data/
│   ├── raw/                    # Datos crudos de la API
│   └── processed/              # Datos limpios y transformados (Etapa 2)
└── logs/
    └── ingesta_YYYYMMDD_HHMMSS.log   # Registro de cada ejecución

📊 Archivos generados

data/raw/clima_sucursales.csv → Datos crudos en tiempo real
logs/ingesta_YYYYMMDD_HHMMSS.log → Log detallado de la ejecución

Columnas del CSV


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


📋 Próximas etapas

Etapa 2: limpieza.py → Lectura, limpieza, normalización y guardado en data/processed/clima_limpio.csv
Etapa 3: Análisis exploratorio y correlación con datos de ventas (pendiente)


📌 Trazabilidad
Cada ejecución genera un log que registra:

Inicio y fin del proceso
Ciudades consultadas
Cantidad de consultas exitosas/fallidas
Ruta del archivo CSV generado
