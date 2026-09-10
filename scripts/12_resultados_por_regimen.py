#Paso 1: en una linea de codigo ejecutar el siguiente script

from google.colab import drive
drive.mount('/content/drive')

#Paso 2: en una nueva linea de codigo ejecutar el siguiente script

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================
# 1. Cargar base
# =========================
# Si ya tenés df cargado, podés saltear esta parte.
# df = pd.read_csv("base_final.csv")

# Ajustar nombres si fuera necesario
date_col = "Date"
spy_col = "SPY"
vx1_col = "VX1"
vx2_col = "VX2"

df = pd.read_parquet(
    "/content/drive/MyDrive/research_dataset.parquet"
)

# Reset index to make 'Date' a column
df = df.reset_index()

# Asegurar formato fecha y ordenar
df[date_col] = pd.to_datetime(df[date_col])
df = df.sort_values(date_col).reset_index(drop=True)

# =========================
# 2. Calcular retorno logarítmico diario del SPY
# =========================
df["r_spy"] = np.log(df[spy_col] / df[spy_col].shift(1))

# =========================
# 3. Calcular pendiente corta Slope12
# =========================
df["Slope12"] = df[vx2_col] / df[vx1_col] - 1

# =========================
# 3.1 Suavizar Slope12 con media móvil de 20 ruedas
# =========================
# La clasificación principal de regímenes se realiza sobre Slope12 MA(20).
# Esta media móvil reduce el ruido diario y permite trabajar con una señal
# más estable de la pendiente corta de la curva de futuros del VIX.
#
# min_periods=20 implica que la media móvil solo se calcula cuando existen
# 20 observaciones disponibles. Por eso, las primeras observaciones quedan
# sin clasificación de régimen.

df["Slope12_MA20"] = df["Slope12"].rolling(window=20, min_periods=20).mean()

# Variable utilizada para clasificar regímenes
slope_var = "Slope12_MA20"

# =========================
# 4. Clasificación por percentiles
# =========================
p25 = df[slope_var].quantile(0.25)
p75 = df[slope_var].quantile(0.75)

def clasificar_regimen(x):
    if pd.isna(x):
        return np.nan
    elif x <= p25:
        return "Estrés"
    elif x >= p75:
        return "Calma"
    else:
        return "Neutral"

df["Regimen"] = df[slope_var].apply(clasificar_regimen)

print("Variable de clasificación:", slope_var)
print("Percentil 25:", p25)
print("Percentil 75:", p75)

# =========================
# 5. Calcular volatilidad realizada futura
# =========================
# Importante:
# Se usan retornos futuros t+1 a t+h.
# No incluye el retorno de la fecha t.

def future_realized_volatility(returns, window):
    """
    Calcula volatilidad realizada futura anualizada:
    std(r_{t+1}, ..., r_{t+window}) * sqrt(252)
    """
    return returns.shift(-1).rolling(window=window).std().shift(-(window-1)) * np.sqrt(252)

df["RVOL_5d"] = future_realized_volatility(df["r_spy"], 5)
df["RVOL_10d"] = future_realized_volatility(df["r_spy"], 10)
df["RVOL_20d"] = future_realized_volatility(df["r_spy"], 20)

# =========================
# 6. Calcular retornos futuros como análisis secundario
# =========================
# Retorno logarítmico acumulado futuro:
# ln(SPY_{t+h}/SPY_t)

df["Ret_5d"] = np.log(df[spy_col].shift(-5) / df[spy_col])
df["Ret_10d"] = np.log(df[spy_col].shift(-10) / df[spy_col])
df["Ret_20d"] = np.log(df[spy_col].shift(-20) / df[spy_col])

# =========================
# 7. Tabla resumen por régimen
# =========================
tabla_d = (
    df
    .dropna(subset=["Regimen", "RVOL_5d", "RVOL_10d", "RVOL_20d"])
    .groupby("Regimen")
    .agg(
        Observaciones=("Regimen", "count"),
        Slope12_MA20_promedio=("Slope12_MA20", "mean"),
        Vol_futura_5d=("RVOL_5d", "mean"),
        Vol_futura_10d=("RVOL_10d", "mean"),
        Vol_futura_20d=("RVOL_20d", "mean"),
        Retorno_futuro_5d=("Ret_5d", "mean"),
        Retorno_futuro_10d=("Ret_10d", "mean"),
        Retorno_futuro_20d=("Ret_20d", "mean")
    )
)

# Ordenar manualmente
orden = ["Estrés", "Neutral", "Calma"]
tabla_d = tabla_d.reindex(orden)

# Pasar volatilidades, retornos y pendiente a porcentaje
cols_pct = [
    "Slope12_MA20_promedio",
    "Vol_futura_5d",
    "Vol_futura_10d",
    "Vol_futura_20d",
    "Retorno_futuro_5d",
    "Retorno_futuro_10d",
    "Retorno_futuro_20d"
]

tabla_d_pct = tabla_d.copy()
tabla_d_pct[cols_pct] = tabla_d_pct[cols_pct] * 100

print(tabla_d_pct.round(2))

# Exportar a Excel
tabla_d_pct.round(2).to_excel("tabla_parte_D_volatilidad_por_regimen_MA20.xlsx")

# =========================
# 8. Boxplot de volatilidad futura 20 días por régimen
# =========================
plot_data = df.dropna(subset=["Regimen", "RVOL_20d"]).copy()

plot_data["RVOL_20d_pct"] = plot_data["RVOL_20d"] * 100

data_box = [
    plot_data.loc[plot_data["Regimen"] == "Estrés", "RVOL_20d_pct"],
    plot_data.loc[plot_data["Regimen"] == "Neutral", "RVOL_20d_pct"],
    plot_data.loc[plot_data["Regimen"] == "Calma", "RVOL_20d_pct"]
]

plt.figure(figsize=(9, 6))
plt.boxplot(
    data_box,
    tick_labels=["Estrés", "Neutral", "Calma"],
    showmeans=True
)
plt.title("Volatilidad futura del SPY a 20 días por régimen")
plt.ylabel("Volatilidad anualizada futura 20d (%)")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("boxplot_volatilidad_futura_20d_por_regimen_MA20.png", dpi=300)
plt.show()

# =========================
# 9. Barras de volatilidad promedio por régimen
# =========================
tabla_plot = tabla_d_pct[[
    "Vol_futura_5d",
    "Vol_futura_10d",
    "Vol_futura_20d"
]]

