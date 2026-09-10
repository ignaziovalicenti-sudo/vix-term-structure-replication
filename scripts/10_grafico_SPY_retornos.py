#Paso 1: en una linea de codigo ejecutar el siguiente script

from google.colab import drive
drive.mount('/content/drive')

#Paso 2: en una nueva linea de codigo ejecutar el siguiente script

# =====================================================
# FIGURA 5
# RETORNOS LOGARÍTMICOS DIARIOS DEL SPY
# =====================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =====================================================
# CARGAR DATASET
# =====================================================

df = pd.read_parquet(
    "/content/drive/MyDrive/research_dataset.parquet"
)

df = df.sort_index()

# =====================================================
# CALCULAR RETORNOS LOGARÍTMICOS
# =====================================================

df["SPY_LogReturn"] = (
    np.log(
        df["SPY"] /
        df["SPY"].shift(1)
    )
) * 100

# =====================================================
# ELIMINAR PRIMERA OBSERVACIÓN
# =====================================================

df_returns = df.dropna(subset=["SPY_LogReturn"])

# =====================================================
# VALIDACIONES
# =====================================================

print("=" * 60)
print("ESTADÍSTICAS DE RETORNOS LOGARÍTMICOS")
print("=" * 60)

print(df_returns["SPY_LogReturn"].describe())

print("\nRetorno máximo:")
print(df_returns["SPY_LogReturn"].max())

print("\nRetorno mínimo:")
print(df_returns["SPY_LogReturn"].min())

print("\nFecha del retorno máximo:")
print(
    df_returns["SPY_LogReturn"].idxmax()
)

print("\nFecha del retorno mínimo:")
print(
    df_returns["SPY_LogReturn"].idxmin()
)

# =====================================================
# GRÁFICO
# =====================================================

plt.figure(figsize=(15,8))

plt.bar(
    df_returns.index,
    df_returns["SPY_LogReturn"],
    width=2,
    color="steelblue",
    alpha=0.8
)

plt.axhline(
    0,
    color="black",
    linewidth=1
)

plt.title(
    "Figura 5. Retornos Logarítmicos Diarios del ETF SPY",
    fontsize=20
)

plt.xlabel("Fecha", fontsize=20)

plt.ylabel(
    "Retorno Logarítmico Diario (%)", fontsize=20
)

plt.grid(
    alpha=0.3,
    linestyle="--"
)

plt.tight_layout()

plt.savefig(
    "Figura_5_Retornos_Logaritmicos_SPY.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()
