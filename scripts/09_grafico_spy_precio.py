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

df = df.sort_index()

# ==========================================
# GRAFICO SPY
# ==========================================

plt.figure(figsize=(15,8))

plt.plot(
    df.index,
    df["SPY"],
    color="darkgreen",
    linewidth=1.5
)

plt.title(
    "Figura 4. Evolución Temporal del ETF SPY",
    fontsize=20
)

plt.xlabel("Fecha", fontsize=20)
plt.ylabel("Precio de Cierre Ajustado", fontsize=20)

plt.grid(
    alpha=0.3,
    linestyle="--"
)

plt.tight_layout()

plt.savefig(
    "Figura_4_SPY.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()
