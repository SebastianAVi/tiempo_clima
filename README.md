# DataMarket – Pipeline de Datos
## Etapa 1: Ingesta de Datos Automatizada

---

## ¿Qué hace este script?

`ingesta.py` es la primera etapa del pipeline de datos de DataMarket.  
Su función es obtener registros de clientes desde una fuente externa (API HTTP) y almacenarlos como CSV crudo en `data/raw/`, listos para la siguiente etapa de limpieza.

El script implementa un patrón de **fallback**: si la API productiva no está disponible (entorno de desarrollo, red caída, etc.), utiliza automáticamente un dataset de respaldo con los mismos errores intencionales del caso DataMarket, garantizando que el pipeline pueda ejecutarse siempre.

---

## Fuente de datos

| Parámetro | Valor |
|---|---|
| URL productiva | `https://api.datamarket.cl/v1/clientes/export` |
| Método | `GET` |
| Respuesta esperada | JSON con clave `"clientes"` → lista de objetos |
| Fallback | `FALLBACK_DATA` (20 registros sintéticos en el propio script) |

Los datos de respaldo simulan los errores reales descritos en el caso:
- Correo sin `@`
- Ciudad en MAYÚSCULAS
- Fecha con formato `DD/MM/YYYY`
- Nombre vacío (valor nulo)
- Registros duplicados exactos

---

## Cómo ejecutarlo

```bash
# Desde la raíz del proyecto
python ingesta.py
```

No requiere librerías externas. Usa solo la biblioteca estándar de Python (`csv`, `json`, `logging`, `urllib`).

---

## Archivos generados

```
data/
└── raw/
    └── clientes.csv          ← dataset crudo (20 registros)
logs/
└── ingesta_YYYYMMDD_HHMMSS.log  ← log de la ejecución
```

---

## Estructura del proyecto

```
datamarket/
├── ingesta.py          ← script principal (Etapa 1)
├── README.md           ← este archivo
├── data/
│   ├── raw/            ← datos crudos ingresados
│   └── processed/      ← datos limpios (Etapa 2)
└── logs/               ← registros de ejecución
```

---

## Trazabilidad

Cada ejecución genera un log con timestamp único que registra:
- Inicio y fin del proceso
- URL de la API consultada
- Si se usó fallback y por qué
- Cantidad de registros almacenados
- Ruta del archivo destino

---

## Columnas del CSV de salida

| Columna | Descripción |
|---|---|
| `nombre` | Nombre del cliente |
| `apellido` | Apellido del cliente |
| `rut` | RUT en formato `XX.XXX.XXX-X` (puede venir sucio) |
| `correo` | Email (puede venir sin `@`) |
| `fecha_registro` | Fecha en formato `YYYY-MM-DD` (puede venir en otros formatos) |
| `ciudad` | Ciudad de la sucursal (puede venir en mayúsculas) |

---

## Próxima etapa

**Etapa 2 – `limpieza.py`**: leerá `data/raw/clientes.csv`, corregirá los errores detectados y generará `data/processed/clientes_limpios.csv`.
