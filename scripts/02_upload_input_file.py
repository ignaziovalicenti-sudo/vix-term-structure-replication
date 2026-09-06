# ==============================================================
# scripts/02_upload_input_file.py
# ETAPA 2.4 - Cargar archivo Parquet generado en CodeBook
#
# Objetivo:
# Cargar manualmente en Google Colab el archivo:
#   vix_term_structure_clean.parquet
#
# Este archivo fue generado en la Etapa 1 desde LSEG Workspace
# CodeBook. No se publica en GitHub porque puede estar sujeto
# a licencia de datos.
# ==============================================================

import os
import shutil
from google.colab import files

# --------------------------------------------------------------
# 1) Definir rutas del proyecto dentro de la sesión de Colab
# --------------------------------------------------------------

PROJECT_DIR = "/content/vix-term-structure-replication"
RAW_DIR = os.path.join(PROJECT_DIR, "data_raw")

INPUT_FILENAME = "vix_term_structure_clean.parquet"
DESTINATION_FILE = os.path.join(RAW_DIR, INPUT_FILENAME)

# Crear carpeta data_raw si no existiera.
os.makedirs(RAW_DIR, exist_ok=True)


# --------------------------------------------------------------
# 2) Cargar archivo desde la computadora local
# --------------------------------------------------------------

print("Seleccione el archivo generado en CodeBook:")
print(INPUT_FILENAME)
print("\nIMPORTANTE: el nombre del archivo debe coincidir exactamente.")

uploaded = files.upload()


# --------------------------------------------------------------
# 3) Validar que el archivo esperado fue cargado
# --------------------------------------------------------------

if INPUT_FILENAME not in uploaded:
    raise FileNotFoundError(
        "No se cargó el archivo esperado: "
        + INPUT_FILENAME
        + ". Verifique el nombre del archivo y vuelva a ejecutar este script."
    )

print("\nArchivo recibido en la sesión de Colab:")
print(list(uploaded.keys()))


# --------------------------------------------------------------
# 4) Mover archivo a data_raw
# --------------------------------------------------------------

# Si ya existía un archivo previo con el mismo nombre, se reemplaza.
if os.path.exists(DESTINATION_FILE):
    os.remove(DESTINATION_FILE)

shutil.move(INPUT_FILENAME, DESTINATION_FILE)


# --------------------------------------------------------------
# 5) Controles finales
# --------------------------------------------------------------

if not os.path.exists(DESTINATION_FILE):
    raise RuntimeError("El archivo no pudo moverse correctamente a data_raw.")

if os.path.getsize(DESTINATION_FILE) == 0:
    raise RuntimeError("El archivo cargado tiene tamaño cero.")

print("\nArchivo cargado y ubicado correctamente en:")
print(DESTINATION_FILE)

print("\nTamaño en bytes:")
print(os.path.getsize(DESTINATION_FILE))

print("\nContenido actual de data_raw:")
print(os.listdir(RAW_DIR))

print("\nCarga del archivo Parquet finalizada correctamente.")
