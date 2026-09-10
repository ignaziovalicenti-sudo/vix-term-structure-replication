#Paso 1: en una linea de codigo ejecutar el siguiente script

from google.colab import drive
drive.mount('/content/drive')

#Paso 2: en una nueva linea de codigo ejecutar el siguiente script

mport pandas as pd
import matplotlib.pyplot as plt

# =====================================================
# CARGAR DATASET MAESTRO
# =====================================================

df = pd.read_parquet(
    "/content/drive/MyDrive/research_dataset.parquet"
)

df = df.sort_index()

# =====================================================
# FIGURA 1.2
# VIX SPOT VS VX1
# =====================================================

plt.figure(figsize=(15,8))

plt.plot(
    df.index,
    df["VIX"],
    label="VIX Spot",
    color="darkred",
    linewidth=1.5
)

plt.plot(
    df.index,
    df["VX1"],
    label="VX1",
    color="navy",
    linewidth=1.5
)

plt.title(
    "Figura 1.2. Comparación entre VIX Spot y VX1",
    fontsize=20 # Increased title font size
)

plt.xlabel("Fecha", fontsize=20) # Increased x-label font size
plt.ylabel("Nivel", fontsize=20) # Increased y-label font size

plt.legend(
    frameon=True,
    loc="upper right",
    fontsize=18 # Increased legend font size
)

plt.grid(
    alpha=0.3,
    linestyle="--"
)

plt.tight_layout()

plt.savefig(
    "Figura_1_2_VIX_vs_VX1.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()
