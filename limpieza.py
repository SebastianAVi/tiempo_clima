import csv
import logging
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

TIMESTAMP    = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE     = f"logs/limpieza_{TIMESTAMP}.log"
ORIGEN_CSV   = "data/raw/clima_sucursales.csv"
DESTINO_CSV    = "data/processed/clima_limpio.csv"
DUPLICADOS_CSV = f"data/processed/duplicados_{TIMESTAMP}.csv"

COLUMNAS_SALIDA = [
    "ciudad", "pais", "latitud", "longitud",
    "temperatura_c", "humedad_pct", "viento_kmh",
    "descripcion_viento", "categoria_temp",
    "fecha_consulta", "hora_consulta"
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("limpieza")


def leer_csv(ruta: str) -> list:
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontro el archivo origen: {ruta}")

    with open(ruta, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        registros = list(reader)

    logger.info(f"Archivo leido: {ruta}  ({len(registros)} registros)")
    return registros


CAMPOS_CLAVE_DUPLICADO = ["ciudad", "pais", "fecha_consulta"]


def _clave_duplicado(fila: dict) -> tuple:
    return tuple(fila.get(c, "").strip().lower() for c in CAMPOS_CLAVE_DUPLICADO)


def eliminar_duplicados(registros: list) -> list:
    vistos     = set()
    limpios    = []
    duplicados = []

    for num_fila, fila in enumerate(registros, start=1):
        clave = _clave_duplicado(fila)
        if clave not in vistos:
            vistos.add(clave)
            limpios.append(fila)
        else:
            duplicados.append(fila)
            logger.warning(
                f"  Fila {num_fila} - Duplicado eliminado: "
                f"ciudad='{fila.get('ciudad')}' | "
                f"fecha={fila.get('fecha_consulta')} | "
                f"hora={fila.get('hora_consulta')} | "
                f"temp={fila.get('temperatura_c')}C"
            )

    if duplicados:
        campos = list(registros[0].keys()) if registros else COLUMNAS_SALIDA
        with open(DUPLICADOS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(duplicados)
        logger.info(f"Duplicados guardados en: {DUPLICADOS_CSV}")

    logger.info(f"Duplicados eliminados: {len(duplicados)}")
    return limpios


def eliminar_nulos(registros: list) -> list:
    CAMPOS_CRITICOS = ["ciudad", "temperatura_c", "humedad_pct", "viento_kmh"]
    limpios   = []
    eliminados = 0

    for fila in registros:
        tiene_nulo = any(not fila.get(campo, "").strip() for campo in CAMPOS_CRITICOS)
        if tiene_nulo:
            eliminados += 1
            logger.warning(f"  Registro con campo vacio eliminado: {fila}")
        else:
            limpios.append(fila)

    logger.info(f"Registros con nulos eliminados: {eliminados}")
    return limpios

def transformacion_1_normalizar_ciudades(registros: list) -> list:
    modificados = 0
    for fila in registros:
        ciudad_original = fila["ciudad"]
        ciudad_limpia   = fila["ciudad"].strip().title()
        if ciudad_original != ciudad_limpia:
            logger.info(f"  Ciudad normalizada: '{ciudad_original}' -> '{ciudad_limpia}'")
            modificados += 1
        fila["ciudad"] = ciudad_limpia

    logger.info(f"T1 - Ciudades normalizadas: {modificados} modificaciones")
    return registros


def transformacion_2_clasificar_temperatura(registros: list) -> list:
    conteo = {"Frio": 0, "Templado": 0, "Calido": 0, "Muy calido": 0}

    for fila in registros:
        try:
            temp = float(fila["temperatura_c"])
            if temp < 10:
                categoria = "Frio"
            elif temp < 18:
                categoria = "Templado"
            elif temp < 25:
                categoria = "Calido"
            else:
                categoria = "Muy calido"
        except (ValueError, TypeError):
            categoria = "Desconocido"
            logger.warning(f"  No se pudo clasificar temperatura de {fila.get('ciudad')}: valor '{fila.get('temperatura_c')}'")

        fila["categoria_temp"] = categoria
        conteo[categoria] = conteo.get(categoria, 0) + 1

    logger.info(f"T2 - Categorias asignadas: {conteo}")
    return registros


def transformacion_3_redondear_valores(registros: list) -> list:
    modificados = 0

    for fila in registros:
        try:
            temp_original   = fila["temperatura_c"]
            viento_original = fila["viento_kmh"]

            fila["temperatura_c"] = round(float(fila["temperatura_c"]), 1)
            fila["viento_kmh"]    = round(float(fila["viento_kmh"]), 1)

            if str(temp_original) != str(fila["temperatura_c"]) or \
               str(viento_original) != str(fila["viento_kmh"]):
                modificados += 1

        except (ValueError, TypeError):
            logger.warning(f"  No se pudo redondear valores de {fila.get('ciudad')}")

    logger.info(f"T3 - Registros con valores redondeados: {modificados}")
    return registros


def guardar_csv(registros: list, ruta: str) -> int:
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS_SALIDA, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(registros)

    logger.info(f"Archivo procesado guardado en: {ruta}  ({len(registros)} registros)")
    return len(registros)


def main():
    logger.info("=" * 60)
    logger.info("INICIO - Limpieza y Transformacion - DataMarket")
    logger.info(f"Timestamp : {TIMESTAMP}")
    logger.info(f"Origen    : {ORIGEN_CSV}")
    logger.info(f"Destino   : {DESTINO_CSV}")
    logger.info(f"Log       : {LOG_FILE}")
    logger.info("=" * 60)

    try:
        registros = leer_csv(ORIGEN_CSV)
        total_inicio = len(registros)

        logger.info("--- LIMPIEZA ---")
        registros = eliminar_duplicados(registros)
        registros = eliminar_nulos(registros)

        logger.info("--- TRANSFORMACIONES ---")
        registros = transformacion_1_normalizar_ciudades(registros)
        registros = transformacion_2_clasificar_temperatura(registros)
        registros = transformacion_3_redondear_valores(registros)

        total_final = guardar_csv(registros, DESTINO_CSV)

        logger.info("=" * 60)
        logger.info("FIN - Limpieza completada exitosamente")
        logger.info(f"  Registros al inicio  : {total_inicio}")
        logger.info(f"  Registros al final   : {total_final}")
        logger.info(f"  Registros removidos  : {total_inicio - total_final}")
        logger.info(f"  Archivo destino      : {DESTINO_CSV}")
        logger.info("=" * 60)

    except FileNotFoundError as exc:
        logger.error(f"ERROR: {exc}")
        logger.error("Asegurate de ejecutar ingesta.py primero.")
        raise SystemExit(1)
    except Exception as exc:
        logger.error(f"ERROR critico: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
