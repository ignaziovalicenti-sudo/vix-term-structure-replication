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
import time
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
elif "date" in df_lseg.columns: # Handle lowercase 'date' column
    dates = pd.to_datetime(df_lseg["date"], errors="coerce")
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
print("Método 1: yf.download")

vix_raw = None
download_error = None

try:
    vix_raw = yf.download(
        tickers="^VIX",
        start=start_date,
        interval="1d",
        auto_adjust=False,
        progress=False,
        keepna=True,
        threads=False,
        timeout=30
    )
except Exception as error:
    download_error = error
    print("Método 1 falló:")
    print(error)

if vix_raw is None or vix_raw.empty:
    print("\nEl método 1 no devolvió datos válidos.")
    print("Esperando 5 segundos antes de intentar método alternativo...")
    time.sleep(5)

    print("\nMétodo 2: yf.Ticker('^VIX').history")

    try:
        ticker = yf.Ticker("^VIX")
        vix_raw = ticker.history(
            start=start_date,
            interval="1d",
            auto_adjust=False
        )
    except Exception as error:
        print("Método 2 falló:")
        print(error)
        vix_raw = None

if vix_raw is None or vix_raw.empty:
    raise RuntimeError(
        "No fue posible descargar ^VIX desde Yahoo Finance. "
        "Puede tratarse de un problema temporal de conexión, bloqueo de Yahoo Finance "
        "o disponibilidad momentánea del servicio. Vuelva a ejecutar la celda en unos minutos."
    )

print("\nDescarga finalizada correctamente.")


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
# 6) Resolver columnas si Yahoo devuelve MultiIndex
# --------------------------------------------------------------

if isinstance(vix_raw.columns, pd.MultiIndex):
    vix_raw.columns = [
        "_".join([str(x) for x in col if str(x) != ""])
        for col in vix_raw.columns
    ]

close_candidates = [
    "Close",
    "Close_^VIX",
    "^VIX_Close"
]

close_column = None

for candidate in close_candidates:
    if candidate in vix_raw.columns:
        close_column = candidate
        break

if close_column is None:
    possible_close_columns = [
        col for col in vix_raw.columns
        if "close" in str(col).lower()
    ]

    if possible_close_columns:
        close_column = possible_close_columns[0]

if close_column is None:
    raise ValueError(
        "No se encontró la columna 'Close' o similar en los datos descargados de Yahoo Finance. "
        "Columnas disponibles: " + str(list(vix_raw.columns))
    )

vix_close = vix_raw[close_column]

# --------------------------------------------------------------
# 7) Validar columnas de Yahoo Finance
# --------------------------------------------------------------

required_yahoo_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
missing_yahoo_columns = [
    col for col in required_yahoo_columns if col not in vix_raw.columns
]

if missing_yahoo_columns:
    print("Advertencia: Faltan las siguientes columnas en los datos de Yahoo Finance:")
    print(missing_yahoo_columns)
    # Consider adding logic here to handle missing columns, e.g., filling with NaN or dropping

# --------------------------------------------------------------
# 8) Guardar datos VIX en formato Parquet
# --------------------------------------------------------------

print("\nGuardando datos VIX en Parquet:")
print(VIX_OUTPUT_FILE)
vix_raw.to_parquet(VIX_OUTPUT_FILE, index=True)

print("\nDatos VIX guardados correctamente.")

# --------------------------------------------------------------
# 9) Mostrar las primeras filas de los datos VIX descargados
# --------------------------------------------------------------

print("\nPrimeras 5 filas del VIX descargado:")
display(vix_raw.head())
print("Total de registros del VIX descargado:", vix_raw.shape[0])



