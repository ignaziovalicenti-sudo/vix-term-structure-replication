# ==============================================================# =================================================/04_build_master_dataset.py
# ETAPA 2.6 - Construcción de la tabla maestra final
#
# Objetivo:
# Leer la salida de CodeBook, incorporar el VIX spot descargado
# desde Yahoo Finance, validar las fuentes, armonizar fechas,
# construir la muestra común y exportar la tabla maestra.
#
# Entradas:
#   data_raw/vix_term_structure_clean.parquet
#   data_raw/vix_yahoo_raw.parquet
#
# Salidas:
#   data_processed/research_dataset.parquet
#   data_processed/research_dataset.csv
#   data_processed/master_dataset_quality_report.csv
# ==============================================================

import os
import pandas as pd
import numpy as np


# --------------------------------------------------------------
# 1) Definir rutas del proyecto dentro de Colab
# --------------------------------------------------------------

PROJECT_DIR = "/content/vix-term-structure-replication"
RAW_DIR = os.path.join(PROJECT_DIR, "data_raw")
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data_processed")

INPUT_FILE = os.path.join(RAW_DIR, "vix_term_structure_clean.parquet")
VIX_FILE = os.path.join(RAW_DIR, "vix_yahoo_raw.parquet")

OUTPUT_PARQUET = os.path.join(PROCESSED_DIR, "research_dataset.parquet")
OUTPUT_CSV = os.path.join(PROCESSED_DIR, "research_dataset.csv")
QUALITY_REPORT = os.path.join(PROCESSED_DIR, "master_dataset_quality_report.csv")

os.makedirs(PROCESSED_DIR, exist_ok=True)


# --------------------------------------------------------------
# 2) Verificar archivos de entrada
# --------------------------------------------------------------

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        "No se encontró data_raw/vix_term_structure_clean.parquet. "
        "Ejecute primero el script 02_upload_input_file.py."
    )

if not os.path.exists(VIX_FILE):
    raise FileNotFoundError(
        "No se encontró data_raw/vix_yahoo_raw.parquet. "
        "Ejecute primero el script 03_download_validate_vix.py."
    )

if os.path.getsize(INPUT_FILE) == 0:
    raise RuntimeError("vix_term_structure_clean.parquet tiene tamaño cero.")

if os.path.getsize(VIX_FILE) == 0:
    raise RuntimeError("vix_yahoo_raw.parquet tiene tamaño cero.")

print("Archivos de entrada encontrados:")
print(INPUT_FILE, "| bytes:", os.path.getsize(INPUT_FILE))
print(VIX_FILE, "| bytes:", os.path.getsize(VIX_FILE))


# --------------------------------------------------------------
# 3) Leer archivo generado en LSEG CodeBook
# --------------------------------------------------------------

df_lseg_original = pd.read_parquet(INPUT_FILE)

print("\nCOLUMNAS ORIGINALES DEL ARCHIVO LSEG")


