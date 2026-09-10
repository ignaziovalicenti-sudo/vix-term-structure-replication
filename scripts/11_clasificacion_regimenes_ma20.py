#Paso 1: en una linea de codigo ejecutar el siguiente script

from google.colab import drive
drive.mount('/content/drive')

#Paso 2: en una nueva linea de codigo ejecutar el siguiente script

# =====================================================
# FIGURA 6
# REGÍMENES SUAVIZADOS MEDIANTE SLOPE12 MA20
# =====================================================

import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------------------------------
# Cargar datos
# -----------------------------------------------------

df = pd.read_parquet(
    "/content/drive/MyDrive/research_dataset.parquet"
)

df = df.sort_index()

# -----------------------------------------------------
# Calcular Slope12
# -----------------------------------------------------

df["Slope12"] = (
    (df["VX2"] - df["VX1"])
    / df["VX1"]
)

# -----------------------------------------------------
# Media móvil 20 ruedas
# -----------------------------------------------------

df["Slope12_MA20"] = (
    df["Slope12"]
    .rolling(window=20)
    .mean()
)

# -----------------------------------------------------
# Percentiles usando serie suavizada
# -----------------------------------------------------

p25 = df["Slope12_MA20"].quantile(0.25)
p75 = df["Slope12_MA20"].quantile(0.75)

print(f"Percentil 25 = {p25:.4%}")
print(f"Percentil 75 = {p75:.4%}")

# -----------------------------------------------------
# Clasificación
# -----------------------------------------------------

df["Regime"] = "Neutral"

df.loc[
    df["Slope12_MA20"] <= p25,
    "Regime"
] = "Stress"

df.loc[
    df["Slope12_MA20"] >= p75,
    "Regime"
] = "Calm"

# -----------------------------------------------------
# Graficar SPY
# -----------------------------------------------------

fig, ax = plt.subplots(
    figsize=(16,8)
)

ax.plot(
    df.index,
    df["SPY"],
    color="black",
    linewidth=1.5,
    label="SPY"
)

# Estrés
ax.fill_between(
    df.index,
    df["SPY"].min(),
    df["SPY"].max(),
    where=(df["Regime"] == "Stress"),
    color="red",
    alpha=0.25,
    label="Estrés"
)

# Calma
ax.fill_between(
    df.index,
    df["SPY"].min(),
    df["SPY"].max(),
    where=(df["Regime"] == "Calm"),
    color="green",
    alpha=0.25,
    label="Calma"
)

ax.set_title(
    "Figura 6. Regímenes de Volatilidad usando Slope12 Suavizado (MA20)",
    fontsize=20
)

ax.set_xlabel("Fecha", fontsize=20)
ax.set_ylabel("Precio del SPY", fontsize=20)

ax.legend()

ax.grid(
    alpha=0.3,
    linestyle="--"
)

plt.savefig(
    "Figura_6_Regimenes_SPY_Slope 12 (MA20).png",
    dpi=600,
    bbox_inches="tight"
)

plt.tight_layout()

plt.show()

# -----------------------------------------------------
# Resumen
# -----------------------------------------------------

print("\nDistribución de observaciones:\n")
print(df["Regime"].value_counts())
