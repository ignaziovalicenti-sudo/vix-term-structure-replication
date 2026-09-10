
# Requisito previo:
# El archivo research_dataset.parquet debe estar disponible en:
# /content/drive/MyDrive/research_dataset.parquet

# PASO 1: Antes de ejecutar el script, montar Google Drive ejecutando:

from google.colab import drive
drive.mount('/content/drive')

# PASO 2: desde una nueva linea de codigo ejecutar

mport pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use("default")

# Cargar dataset maestro
df = pd.read_parquet(
    "/content/drive/MyDrive/research_dataset.parquet"
)

# Asegurar orden temporal
df = df.sort_index()

# Crear slope principal
df["Slope12"] = (df["VX2"] - df["VX1"]) / df["VX1"]

# Retornos diarios SPY
df["SPY_Return"] = df["SPY"].pct_change()

# Paso 3: desde una nueva linea de codigo ejecutar

plt.figure(figsize=(15,8))

plt.plot(df.index, df["VX1"],
         linewidth=1.5,
         label="VX1")

plt.plot(df.index, df["VX2"],
         linewidth=1.5,
         label="VX2")

plt.plot(df.index, df["VX3"],
         linewidth=1.5,
         label="VX3")

plt.plot(df.index, df["VX4"],
         linewidth=1.5,
         label="VX4")

plt.title(
    "Figura 1.1 Serie Temporal de los Contratos Continuos del Futuro VIX",
    fontsize=20
)

plt.ylabel("Nivel del Futuro", fontsize=20)
plt.xlabel("Fecha", fontsize=20)

plt.legend(
    frameon=True,
    loc="upper right",
    fontsize=18
)

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    "Figura_1_VIX_Futures.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()
