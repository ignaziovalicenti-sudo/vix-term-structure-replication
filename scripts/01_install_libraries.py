# ==============================================================
# scripts/01_install_libraries.py
# ETAPA 2.3 - Preparar entorno de Google Colab
#
# Objetivo:
# Instalar las librerías necesarias para ejecutar la Etapa 2.
# ==============================================================

import sys
import subprocess

packages = [
    "pandas",
    "numpy",
    "yfinance",
    "pyarrow"
]

subprocess.check_call([
    sys.executable,
    "-m",
    "pip",
    "install",
    *packages,
    "-q"
])

print("Librerías instaladas correctamente.")
