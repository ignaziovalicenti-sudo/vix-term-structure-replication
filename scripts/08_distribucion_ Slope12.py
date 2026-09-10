#Paso 1: en una linea de codigo ejecutar el siguiente script

from google.colab import drive
drive.mount('/content/drive')

#Paso 2: en una nueva linea de codigo ejecutar el siguiente script

import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# CARGAR DATASET
# ==========================================

df = pd.read_parquet(
    "/content/drive/MyDrive/research_dataset.parquet"
)

# ==========================================
# CALCULAR SLOPE12
# ==========================================

df["Slope12"] = (
    (df["VX2"] - df["VX1"])
    / df["VX1"]
)

# ==========================================
# HISTOGRAMA
# ==========================================

plt.figure(figsize=(12,8))

plt.hist(
    df["Slope12"] * 100,
    bins=50,
    edgecolor="black",
    alpha=0.8,
    color="steelblue"
)

plt.axvline(
    x=0,
    color="red",
    linestyle="--",
    linewidth=2
)

plt.title(
    "Figura 3. Distribución de la Pendiente Slope12",
    fontsize=20
)

plt.xlabel("Slope12 (%)")
plt.ylabel("Frecuencia")

plt.grid(
    alpha=0.3,
    linestyle="--"
)

plt.tight_layout()

plt.savefig(
    "Figura_3_Histograma_Slope12.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()
