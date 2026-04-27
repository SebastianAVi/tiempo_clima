import csv
import json
import logging
import os
import urllib.request
import urllib.error
from datetime import datetime

os.makedirs("logs", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)

TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE    = f"logs/ingesta_{TIMESTAMP}.log"
DESTINO_CSV = "data/raw/clima_sucursales.csv"
COLUMNAS    = [
    "ciudad", "pais", "latitud", "longitud",
    "temperatura_c", "humedad_pct", "viento_kmh",
    "descripcion_viento", "fecha_consulta", "hora_consulta"
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("ingesta")


# Ciudades chilenas
SUCURSALES = [
    {"ciudad": "Santiago",     "pais": "Chile", "lat": -33.45, "lon": -70.65},
    {"ciudad": "Valparaiso",   "pais": "Chile", "lat": -33.05, "lon": -71.62},
    {"ciudad": "Concepcion",   "pais": "Chile", "lat": -36.82, "lon": -73.05},
    {"ciudad": "Antofagasta",  "pais": "Chile", "lat": -23.65, "lon": -70.40},
    {"ciudad": "La Serena",    "pais": "Chile", "lat": -29.91, "lon": -71.25},
    {"ciudad": "Temuco",       "pais": "Chile", "lat": -38.73, "lon": -72.59},
    {"ciudad": "Iquique",      "pais": "Chile", "lat": -20.21, "lon": -70.15},
    {"ciudad": "Puerto Montt", "pais": "Chile", "lat": -41.47, "lon": -72.94},
    {"ciudad": "Arica",        "pais": "Chile", "lat": -18.48, "lon": -70.33},
    {"ciudad": "Rancagua",     "pais": "Chile", "lat": -34.17, "lon": -70.74},
]

# URL api Open-Meteo
API_BASE = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
    "&timezone=America/Santiago"
    "&forecast_days=1"
)
#funcionalidades

def describir_viento(velocidad_kmh: float) -> str:
    if velocidad_kmh < 1:
        return "Calma"
    elif velocidad_kmh < 20:
        return "Brisa ligera"
    elif velocidad_kmh < 40:
        return "Viento moderado"
    elif velocidad_kmh < 60:
        return "Viento fuerte"
    else:
        return "Viento muy fuerte"


def obtener_clima_ciudad(sucursal: dict):

    url = API_BASE.format(lat=sucursal["lat"], lon=sucursal["lon"])
    logger.info(f"  Consultando clima de {sucursal['ciudad']}...")

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "DataMarket-Pipeline/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                raise ValueError(f"HTTP {resp.status}")
            datos = json.loads(resp.read().decode("utf-8"))

        current     = datos["current"]
        temperatura = current["temperature_2m"]
        humedad     = current["relative_humidity_2m"]
        viento      = current["wind_speed_10m"]
        ahora       = datetime.now()

        return {
            "ciudad":             sucursal["ciudad"],
            "pais":               sucursal["pais"],
            "latitud":            sucursal["lat"],
            "longitud":           sucursal["lon"],
            "temperatura_c":      temperatura,
            "humedad_pct":        humedad,
            "viento_kmh":         viento,
            "descripcion_viento": describir_viento(viento),
            "fecha_consulta":     ahora.strftime("%Y-%m-%d"),
            "hora_consulta":      ahora.strftime("%H:%M:%S"),
        }

    except (urllib.error.URLError, ValueError, KeyError, TimeoutError) as exc:
        logger.warning(f"  No se pudo obtener clima de {sucursal['ciudad']}: {exc}")
        return None


def obtener_datos_api(sucursales: list) -> list:
    """
    Recorre todas las sucursales y consulta el clima de cada una.
    Las ciudades que fallen se omiten y se registran en el log.
    Retorna unicamente los registros exitosos.
    """
    logger.info(f"Iniciando consultas para {len(sucursales)} sucursales...")
    registros = []
    exitosos  = 0
    fallidos  = 0

    for sucursal in sucursales:
        resultado = obtener_clima_ciudad(sucursal)
        if resultado:
            registros.append(resultado)
            exitosos += 1
        else:
            fallidos += 1

    logger.info(f"Consultas exitosas: {exitosos} | Fallidas: {fallidos}")
    return registros


def guardar_csv(registros: list, ruta: str) -> int:
    """
    Escribe la lista de registros climaticos en un archivo CSV.
    Retorna la cantidad de filas escritas (sin contar el encabezado).
    """
    os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(registros)
    logger.info(f"CSV guardado en: {ruta}  ({len(registros)} filas)")
    return len(registros)


def main():
    logger.info("=" * 60)
    logger.info("INICIO - Ingesta de Datos Climaticos - DataMarket")
    logger.info(f"Timestamp : {TIMESTAMP}")
    logger.info(f"Fuente    : Open-Meteo API (api.open-meteo.com)")
    logger.info(f"Sucursales: {len(SUCURSALES)} ciudades")
    logger.info(f"Log       : {LOG_FILE}")
    logger.info("=" * 60)

    try:
        # Paso 1: Consultar el clima de cada sucursal via API
        registros = obtener_datos_api(SUCURSALES)

        if not registros:
            logger.error("No se obtuvo ningun registro. Revisa tu conexion a internet.")
            raise SystemExit(1)

        # Paso 2: Guardar datos crudos en data/raw/
        total = guardar_csv(registros, DESTINO_CSV)

        # Paso 3: Resumen de trazabilidad
        logger.info("=" * 60)
        logger.info("FIN - Ingesta completada exitosamente")
        logger.info(f"  Registros almacenados : {total}")
        logger.info(f"  Archivo destino       : {DESTINO_CSV}")
        logger.info("=" * 60)

    except SystemExit:
        raise
    except Exception as exc:
        logger.error(f"ERROR critico: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
