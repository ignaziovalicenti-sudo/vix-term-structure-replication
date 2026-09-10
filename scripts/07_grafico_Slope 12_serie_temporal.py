#Paso 1: en una linea de codigo ejecutar el siguiente script

from google.colab import drive
drive.mount('/content/drive')

#Paso 2: en una nueva linea de codigo ejecutar el siguiente script

import pandas as pd
import matplotlib.pyplot as plt

# =====================================================
# CARGAR DATASET
# =====================================================

df = pd.read_parquet(
    "/content/drive/MyDrive/research_dataset.parquet"
)

df = df.sort_index()

# =====================================================
# CALCULAR SLOPE12
# =====================================================

df["Slope12"] = (df["VX2"] - df["VX1"]) / df["VX1"]

# =====================================================
# GRAFICAR
# =====================================================

plt.figure(figsize=(15,8))

plt.plot(
    df.index,
    df["Slope12"] * 100,
    color="navy",
    linewidth=1.2
)

plt.axhline(
    y=0,
    color="red",
    linestyle="--",
    linewidth=1.5,
    label="Backwardation (0%)"
)

plt.fill_between(
    df.index,
    0,
    df["Slope12"]*100,
    where=(df["Slope12"] > 0),
    color="green",
    alpha=0.2
)

plt.fill_between(
    df.index,
    0,
    df["Slope12"]*100,
    where=(df["Slope12"] < 0),
    color="red",
    alpha=0.2
)

plt.title(
    "Figura 2. Evolución Temporal de la Pendiente Slope12",
    fontsize=20
)

plt.xlabel("Fecha", fontsize=20)
plt.ylabel("Pendiente (%)", fontsize=20)

plt.grid(
    alpha=0.3,
    linestyle="--"
)

plt.legend(fontsize=18)

plt.tight_layout()

plt.savefig(
    "Figura_2_Slope12.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()
