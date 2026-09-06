# ==============================================================
# scripts/03_download_validate_vix.py
# ETAPA 2.5 - Descargar y validar VIX spot desde Yahoo Finance
#
# Objetivo:
# Descargar el índice VIX spot desde Yahoo Finance mediante el
# ticker ^VIX, usando como fecha inicial la primera fecha disponible
# en el archivo vix_term_structure_clean.parquet generado en CodeBook.
#
# Entrada:
#   data_raw/vix_term_structure_clean.parquet
#
# Salida:
#   data_raw/vix_yahoo_raw.parquet
# ==============================================================

import os
import pandas as pd
import yfinance as yf


# --------------------------------------------------------------
# 1) Definir rutas del proyecto dentro de Colab
# --------------------------------------------------------------

PROJECT_DIR = "/content/vix-term-structure-replication"
RAW_DIR = os.path.join(PROJECT_DIR, "data_raw")

INPUT_FILE = os.path.join(RAW_DIR, "vix_term_structure_clean.parquet")
VIX_OUTPUT_FILE = os.path.join(RAW_DIR, "vix_yahoo_raw.parquet")


# --------------------------------------------------------------
# 2) Verificar que existe el archivo generado en CodeBook
# --------------------------------------------------------------

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        "No se encontró vix_term_structure_clean.parquet en data_raw. "
        "Ejecute primero el script 02_upload_input_file.py."
    )

if os.path.getsize(INPUT_FILE) == 0:
    raise RuntimeError(
        "El archivo vix_term_structure_clean.parquet existe, "
        "pero tiene tamaño cero."
    )

print("Archivo de entrada encontrado:")
print(INPUT_FILE)
print("Tamaño en bytes:", os.path.getsize(INPUT_FILE))


# --------------------------------------------------------------
# 3) Leer archivo Parquet para identificar la fecha inicial
# --------------------------------------------------------------

df_lseg = pd.read_parquet(INPUT_FILE)

print("\nCOLUMNAS DEL ARCHIVO LSEG")
print(list(df_lseg.columns))
print("Dimensiones:", df_lseg.shape)

if "Date" in df_lseg.columns:
    dates = pd.to_datetime(df_lseg["Date"], errors="coerce")
else:
    dates = pd.to_datetime(df_lseg.index, errors="coerce")

dates = dates.dropna()

if dates.empty:
    raise RuntimeError(
        "No fue posible identificar fechas válidas en el archivo LSEG."
    )

start_date = dates.min().strftime("%Y-%m-%d")

print("\nFecha inicial detectada para descargar VIX:")
print(start_date)


# --------------------------------------------------------------
# 4) Descargar VIX spot desde Yahoo Finance
# --------------------------------------------------------------

print("\nDescargando ^VIX desde Yahoo Finance...")

vix_raw = yf.download(
    "^VIX",
    start=start_date,
    interval="1d",
    auto_adjust=False,
    progress=False,
    keepna=True,
    multi_level_index=False
)

if vix_raw is None or vix_raw.empty:
    raise RuntimeError("Yahoo Finance no devolvió datos para ^VIX.")


# --------------------------------------------------------------
# 5) Estandarizar índice de fechas
# --------------------------------------------------------------

vix_raw.index = pd.to_datetime(vix_raw.index, errors="coerce")
vix_raw = vix_raw.loc[~vix_raw.index.isna()].copy()

if getattr(vix_raw.index, "tz", None) is not None:
    vix_raw.index = vix_raw.index.tz_localize(None)

vix_raw = vix_raw[~vix_raw.index.duplicated(keep="last")]
vix_raw = vix_raw.sort_index()


# --------------------------------------------------------------
# 6) Validaciones mínimas de la descarga
# --------------------------------------------------------------

required_yahoo_columns = ["Open", "High", "Low", "Close", "Volume"]
missing_yahoo_columns = [
    col for col in required_yahoo_columns if col not in vix_raw.columns
]

if missing_yahoo_columns:
    raise ValueError(
        "Faltan columnas esperadas en la descarga de Yahoo Finance: "
        + str(missing_yahoo_columns)
    )

vix_close = pd.to_numeric(vix_raw["Close"], errors="coerce")

if vix_close.isna().all():
    raise RuntimeError("La columna Close del VIX no contiene valores válidos.")

if (vix_close.dropna() <= 0).any():
    raise RuntimeError("Se detectaron valores no positivos en el cierre del VIX.")


# --------------------------------------------------------------
# 7) Guardar archivo bruto de VIX
# --------------------------------------------------------------


