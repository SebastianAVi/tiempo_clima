"""
================================================================================
Pipeline de Datos – DataMarket
Etapa 1: Ingesta de Datos Automatizada
================================================================================
Fuente:  API interna de DataMarket (simulada con datos sintéticos).
         En un entorno real se reemplaza API_URL por el endpoint productivo,
         por ejemplo: https://api.datamarket.cl/v1/clientes/export

Destino: data/raw/clientes.csv

La función obtener_datos_api() realiza una llamada HTTP real (urllib).
Si el endpoint no está disponible, el script usa un dataset de respaldo
(FALLBACK_DATA) para garantizar que el pipeline siempre pueda ejecutarse
en entornos de desarrollo o prueba — patrón habitual en DataOps.

Autor:   DataMarket - Pipeline de Datos
Version: 1.0
================================================================================
"""

import csv
import json
import logging
import os
import urllib.request
import urllib.error
from datetime import datetime

# ──────────────────────────────────────────────
# CONFIGURACION
# ──────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)

TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE    = f"logs/ingesta_{TIMESTAMP}.log"
API_URL     = "https://api.datamarket.cl/v1/clientes/export"   # endpoint productivo
DESTINO_CSV = "data/raw/clientes.csv"
COLUMNAS    = ["nombre", "apellido", "rut", "correo", "fecha_registro", "ciudad"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("ingesta")


FALLBACK_DATA = [
    {"nombre": "juan",     "apellido": "perez",    "rut": "12.345.678-9", "correo": "jperez@gmail.com",    "fecha_registro": "2024-03-12", "ciudad": "santiago"},
    {"nombre": "maria",    "apellido": "lopez",    "rut": "98.765.432-1", "correo": "mlopez@gmail.com",    "fecha_registro": "2024-03-15", "ciudad": "valparaiso"},
    {"nombre": "carlos",   "apellido": "soto",     "rut": "11.222.333-4", "correo": "csotogmail.com",      "fecha_registro": "2024-04-01", "ciudad": "concepcion"},
    {"nombre": "ana",      "apellido": "munoz",    "rut": "55.666.777-8", "correo": "anamunoz@gmail.com",  "fecha_registro": "2024-04-03", "ciudad": "temuco"},
    {"nombre": "ana",      "apellido": "munoz",    "rut": "55.666.777-8", "correo": "anamunoz@gmail.com",  "fecha_registro": "2024-04-03", "ciudad": "temuco"},
    {"nombre": "pedro",    "apellido": "araya",    "rut": "33.444.555-6", "correo": "paraya@hotmail.com",  "fecha_registro": "2024-04-05", "ciudad": "ANTOFAGASTA"},
    {"nombre": "claudia",  "apellido": "vega",     "rut": "77.888.999-0", "correo": "cvega@yahoo.com",     "fecha_registro": "2024-04-07", "ciudad": "arica"},
    {"nombre": "roberto",  "apellido": "fuentes",  "rut": "22.111.000-3", "correo": "rfuentes@gmail.com",  "fecha_registro": "08/04/2024", "ciudad": "iquique"},
    {"nombre": "sofia",    "apellido": "castro",   "rut": "44.333.222-1", "correo": "scastro@gmail.com",   "fecha_registro": "2024-04-10", "ciudad": "rancagua"},
    {"nombre": "",         "apellido": "herrera",  "rut": "66.555.444-2", "correo": "herrera@gmail.com",   "fecha_registro": "2024-04-12", "ciudad": "talca"},
    {"nombre": "diego",    "apellido": "morales",  "rut": "88.777.666-5", "correo": "dmorales@gmail.com",  "fecha_registro": "2024-04-14", "ciudad": "chillan"},
    {"nombre": "valentina","apellido": "rios",     "rut": "99.000.111-7", "correo": "vrios@gmail.com",     "fecha_registro": "2024-04-16", "ciudad": "puerto montt"},
    {"nombre": "matias",   "apellido": "silva",    "rut": "10.203.040-5", "correo": "msilva@outlook.com",  "fecha_registro": "2024-04-18", "ciudad": "osorno"},
    {"nombre": "ana",      "apellido": "munoz",    "rut": "55.666.777-8", "correo": "anamunoz@gmail.com",  "fecha_registro": "2024-04-03", "ciudad": "temuco"},
    {"nombre": "camila",   "apellido": "flores",   "rut": "30.405.060-7", "correo": "cflores@gmail.com",   "fecha_registro": "2024-04-20", "ciudad": "valdivia"},
    {"nombre": "nicolas",  "apellido": "torres",   "rut": "50.607.080-9", "correo": "ntorres@gmail.com",   "fecha_registro": "2024-04-22", "ciudad": "copiapo"},
    {"nombre": "javiera",  "apellido": "pino",     "rut": "70.809.010-2", "correo": "jpino@gmail.com",     "fecha_registro": "2024-04-24", "ciudad": "coquimbo"},
    {"nombre": "ignacio",  "apellido": "salas",    "rut": "90.100.201-4", "correo": "isalas@gmail.com",    "fecha_registro": "2024-04-26", "ciudad": "la serena"},
    {"nombre": "antonia",  "apellido": "vargas",   "rut": "11.213.141-6", "correo": "avargas@hotmail.com", "fecha_registro": "2024-04-28", "ciudad": "san antonio"},
    {"nombre": "lucas",    "apellido": "orellana", "rut": "21.314.151-8", "correo": "lorellana@gmail.com", "fecha_registro": "2024-04-30", "ciudad": "curico"},
]


# ──────────────────────────────────────────────
# FUNCIONES
# ──────────────────────────────────────────────

def obtener_datos_api(url: str) -> list:
    """
    Realiza una peticion GET al endpoint indicado y espera una respuesta
    JSON con la clave 'clientes' conteniendo una lista de registros.

    Si el servidor no esta disponible (timeout, DNS, HTTP error), registra
    el motivo y retorna FALLBACK_DATA para no interrumpir el pipeline.
    """
    logger.info(f"Intentando conectar a la API: {url}")
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept":     "application/json",
                "User-Agent": "DataMarket-Pipeline/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                raise ValueError(f"Codigo HTTP inesperado: {resp.status}")
            payload   = json.loads(resp.read().decode("utf-8"))
            registros = payload.get("clientes", [])
            logger.info(f"Registros recibidos desde la API: {len(registros)}")
            return registros

    except (urllib.error.URLError, ValueError, TimeoutError) as exc:
        logger.warning(f"API no disponible ({exc}). Usando datos de respaldo (fallback).")
        logger.info(f"Registros en fallback: {len(FALLBACK_DATA)}")
        return FALLBACK_DATA


def guardar_csv(registros: list, ruta: str) -> int:
    """
    Escribe los registros en un CSV con las columnas definidas en COLUMNAS.
    Retorna la cantidad de filas escritas (sin contar el encabezado).
    """
    os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(registros)
    logger.info(f"Archivo CSV generado: {ruta}  ({len(registros)} filas)")
    return len(registros)


# ──────────────────────────────────────────────
# PROCESO PRINCIPAL
# ──────────────────────────────────────────────

def main():
    logger.info("=" * 60)
    logger.info("INICIO - Ingesta de Datos - DataMarket")
    logger.info(f"Timestamp : {TIMESTAMP}")
    logger.info(f"Log       : {LOG_FILE}")
    logger.info("=" * 60)

    try:
        # Paso 1: Obtener datos desde la API (o fallback si no esta disponible)
        registros = obtener_datos_api(API_URL)

        # Paso 2: Guardar datos crudos en data/raw/
        total = guardar_csv(registros, DESTINO_CSV)

        # Paso 3: Resumen de trazabilidad
        logger.info("=" * 60)
        logger.info("FIN - Proceso completado exitosamente")
        logger.info(f"  Total registros almacenados : {total}")
        logger.info(f"  Archivo destino             : {DESTINO_CSV}")
        logger.info("=" * 60)

    except Exception as exc:
        logger.error(f"ERROR critico durante la ingesta: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
