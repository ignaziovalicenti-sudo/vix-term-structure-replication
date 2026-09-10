#Paso 1: en una linea de codigo ejecutar el siguiente script

from google.colab import drive
drive.mount('/content/drive')

#Paso 2: en una nueva linea de codigo ejecutar el siguiente script

!pip install arch

#Paso 3: en una nueva linea de codigo ejecutar el siguiente script
# ============================================================
# PARTE F - Validación econométrica con GARCH(1,1)
# Dataset: research_dataset.parquet
# Columnas esperadas: Date, VX1, VX2, VX3, VX4, SPY
#
# Genera:
# - Tabla 4: parámetros estimados GARCH(1,1)
# - Tabla 5: volatilidad GARCH por régimen
# - Figura 7: retornos SPY y volatilidad GARCH
# ============================================================

# Si todavía no instalaste arch:
# !pip install arch openpyxl

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arch import arch_model

# ============================================================
# 1. Cargar parquet
# ============================================================

df = pd.read_parquet(
    "/content/drive/MyDrive/research_dataset.parquet"
)

print("Columnas disponibles:")
print(df.columns)

display(df.head())

# ============================================================
# 2. Preparar datos
# ============================================================

df_g = df.copy()
df_g = df_g.reset_index() # Convertir el índice 'Date' en una columna

# Columnas reales según tu archivo
date_col = "Date"
spy_col = "SPY"
vx1_col = "VX1"
vx2_col = "VX2"

# Convertir fecha
df_g[date_col] = pd.to_datetime(df_g[date_col])

# Ordenar por fecha
df_g = df_g.sort_values(date_col).reset_index(drop=True)

# Asegurar que las columnas sean numéricas
for col in [spy_col, vx1_col, vx2_col]:
    df_g[col] = pd.to_numeric(df_g[col], errors="coerce")

# Eliminar filas sin datos esenciales
df_g = df_g.dropna(subset=[date_col, spy_col, vx1_col, vx2_col]).copy()

# ============================================================
# 3. Construir pendiente de la curva: Slope12
# ============================================================
# Slope12 mide la pendiente entre el segundo y primer futuro del VIX:
# Slope12 = VX2 / VX1 - 1
#
# Positivo: contango
# Negativo: backwardation

df_g["Slope12"] = df_g[vx2_col] / df_g[vx1_col] - 1

# Suavizado de 5 días para reducir ruido diario
df_g["Slope12_smooth"] = (
    df_g["Slope12"]
    .rolling(window=5, min_periods=3)
    .mean()
)

# ============================================================
# 4. Crear regímenes por percentiles
# ============================================================
# 25% inferior: Estrés
# 50% central: Neutral
# 25% superior: Calma

p25 = df_g["Slope12_smooth"].quantile(0.25)
p75 = df_g["Slope12_smooth"].quantile(0.75)

def clasificar_regimen(x):
    if pd.isna(x):
        return np.nan
    elif x <= p25:
        return "Estrés"
    elif x >= p75:
        return "Calma"
    else:
        return "Neutral"

df_g["Regimen"] = df_g["Slope12_smooth"].apply(clasificar_regimen)

print("Percentil 25 Slope12_smooth:", p25)
print("Percentil 75 Slope12_smooth:", p75)

print("\nDistribución de regímenes:")
display(df_g["Regimen"].value_counts(dropna=False))

# ============================================================
# 5. Calcular retornos logarítmicos del SPY
# ============================================================

df_g["r_spy"] = np.log(df_g[spy_col] / df_g[spy_col].shift(1))

# Para estimar GARCH se suelen usar retornos en porcentaje
df_g["r_spy_pct"] = df_g["r_spy"] * 100

# Dataset limpio para GARCH
garch_data = df_g.dropna(subset=["r_spy_pct"]).copy()

# ============================================================
# 6. Estimar modelo GARCH(1,1)
# ============================================================

model = arch_model(
    garch_data["r_spy_pct"],
    mean="Constant",
    vol="GARCH",
    p=1,
    q=1,
    dist="normal"
)

res = model.fit(disp="off")

print("\nResumen del modelo GARCH(1,1):")
print(res.summary())

# ============================================================
# 7. Extraer volatilidad condicional GARCH
# ============================================================

# Volatilidad diaria en porcentaje
garch_data["garch_vol_daily_pct"] = res.conditional_volatility

# Volatilidad anualizada en porcentaje
garch_data["garch_vol_ann_pct"] = (
    garch_data["garch_vol_daily_pct"] * np.sqrt(252)
)

# Unir la volatilidad estimada al dataframe principal
df_g = df_g.merge(
    garch_data[[date_col, "garch_vol_daily_pct", "garch_vol_ann_pct"]],
    on=date_col,
    how="left"
)

# ============================================================
# 8. Tabla 4 - Parámetros estimados GARCH(1,1)
# ============================================================

params = res.params
pvalues = res.pvalues

mu = params.get("mu", np.nan)
omega = params.get("omega", np.nan)
alpha = params.get("alpha[1]", np.nan)
beta = params.get("beta[1]", np.nan)

mu_p = pvalues.get("mu", np.nan)
omega_p = pvalues.get("omega", np.nan)
alpha_p = pvalues.get("alpha[1]", np.nan)
beta_p = pvalues.get("beta[1]", np.nan)

tabla_4 = pd.DataFrame({
    "Parámetro": ["mu", "omega", "alpha[1]", "beta[1]", "alpha + beta"],
    "Estimación": [mu, omega, alpha, beta, alpha + beta],
    "p-value": [mu_p, omega_p, alpha_p, beta_p, np.nan],
    "Interpretación": [
        "Media condicional de los retornos diarios del SPY",
        "Nivel base de la varianza condicional",
        "Reacción de la volatilidad a shocks recientes",
        "Persistencia de la volatilidad condicional",
        "Persistencia total de la volatilidad"
    ]
})

tabla_4["Estimación"] = tabla_4["Estimación"].round(6)
tabla_4["p-value"] = tabla_4["p-value"].round(6)

print("\nTabla 4. Parámetros estimados del modelo GARCH(1,1)")
display(tabla_4)

tabla_4.to_excel(
    "tabla_4_parametros_garch.xlsx",
    index=False
)

# ============================================================
# 9. Tabla 5 - Volatilidad GARCH por régimen
# ============================================================

tabla_5 = (
    df_g
    .dropna(subset=["Regimen", "garch_vol_ann_pct"])
    .groupby("Regimen")
    .agg(
        Observaciones=("Regimen", "count"),
        Slope12_promedio=("Slope12", "mean"),
        Vol_GARCH_promedio=("garch_vol_ann_pct", "mean"),
        Vol_GARCH_mediana=("garch_vol_ann_pct", "median"),
        Vol_GARCH_min=("garch_vol_ann_pct", "min"),
        Vol_GARCH_max=("garch_vol_ann_pct", "max")
    )
)

# Ordenar filas
orden = ["Estrés", "Neutral", "Calma"]
tabla_5 = tabla_5.reindex(orden)

# Pasar Slope12 a porcentaje
tabla_5["Slope12_promedio"] = tabla_5["Slope12_promedio"] * 100

tabla_5 = tabla_5.round(2)

print("\nTabla 5. Volatilidad condicional GARCH del SPY por régimen")
display(tabla_5)

tabla_5.to_excel(
    "tabla_5_volatilidad_garch_por_regimen.xlsx"
)

# ============================================================
# 10. Figura 7 - Retornos SPY y volatilidad GARCH
# ============================================================

fig, axes = plt.subplots(
    2, 1,
    figsize=(13, 8),
    sharex=True
)

# Panel superior: retornos logarítmicos diarios del SPY
axes[0].plot(
    df_g[date_col],
    df_g["r_spy_pct"],
    color="black",
    linewidth=0.8
)

axes[0].axhline(
    0,
    color="gray",
    linestyle="--",
    linewidth=1
)

axes[0].set_title(
    "Retornos logarítmicos diarios del SPY",
    fontsize=13
)

axes[0].set_ylabel("Retorno diario (%)")
axes[0].grid(alpha=0.3)

# Panel inferior: volatilidad condicional GARCH anualizada
axes[1].plot(
    df_g[date_col],
    df_g["garch_vol_ann_pct"],
    color="darkred",
    linewidth=1.2
)

axes[1].set_title(
    "Volatilidad condicional estimada GARCH(1,1)",
    fontsize=13
)

axes[1].set_ylabel("Volatilidad anualizada (%)")
axes[1].set_xlabel("Fecha")
axes[1].grid(alpha=0.3)

plt.suptitle(
    "Figura 7. Retornos del SPY y volatilidad condicional GARCH(1,1)",
    fontsize=15,
    y=0.98
)

plt.tight_layout()

plt.savefig(
    "figura_7_retornos_spy_volatilidad_garch.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ============================================================
# 11. Guardar base enriquecida con variables GARCH
# ============================================================

df_g.to_parquet(
    "/content/drive/MyDrive/research_dataset_con_garch.parquet",
    index=False
)


#Paso 4

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ============================================================
# Figura 7 mejorada - Retornos SPY y volatilidad GARCH con regímenes
# ============================================================

date_col = "Date"

fig, axes = plt.subplots(
    2, 1,
    figsize=(14, 8),
    sharex=True
)

# ------------------------------------------------------------
# Función para sombrear regímenes
# ------------------------------------------------------------

def shade_regimes(ax, data, date_col="Date", regime_col="Regimen"):
    """
    Sombrea zonas de estrés y calma.
    Estrés: rojo claro
    Calma: verde claro
    Neutral: sin sombrear
    """
    for i in range(len(data)):
        regime = data.iloc[i][regime_col]
        date = data.iloc[i][date_col]

        if i < len(data) - 1:
            next_date = data.iloc[i + 1][date_col]
        else:
            next_date = date

        if regime == "Estrés":
            ax.axvspan(
                date,
                next_date,
                color="red",
                alpha=0.12,
                linewidth=0
            )
        elif regime == "Calma":
            ax.axvspan(
                date,
                next_date,
                color="green",
                alpha=0.10,
                linewidth=0
            )

# ------------------------------------------------------------
# Panel 1: retornos diarios del SPY
# ------------------------------------------------------------

shade_regimes(axes[0], df_g, date_col="Date", regime_col="Regimen")

axes[0].plot(
    df_g["Date"],
    df_g["r_spy_pct"],
    color="black",
    linewidth=0.8,
    label="Retorno SPY"
)

axes[0].axhline(
    0,
    color="gray",
    linestyle="--",
    linewidth=1
)

axes[0].set_title(
    "Retornos logarítmicos diarios del SPY",
    fontsize=13
)

axes[0].set_ylabel("Retorno diario (%)")
axes[0].grid(alpha=0.3)

# ------------------------------------------------------------
# Panel 2: volatilidad condicional GARCH
# ------------------------------------------------------------

shade_regimes(axes[1], df_g, date_col="Date", regime_col="Regimen")

axes[1].plot(
    df_g["Date"],
    df_g["garch_vol_ann_pct"],
    color="darkred",
    linewidth=1.2,
    label="Volatilidad GARCH"
)

axes[1].set_title(
    "Volatilidad condicional estimada GARCH(1,1)",
    fontsize=13
)

axes[1].set_ylabel("Volatilidad anualizada (%)")
axes[1].set_xlabel("Fecha")
axes[1].grid(alpha=0.3)

# ------------------------------------------------------------
# Leyenda común
# ------------------------------------------------------------

stress_patch = mpatches.Patch(
    color="red",
    alpha=0.12,
    label="Estrés"
)

calm_patch = mpatches.Patch(
    color="green",
    alpha=0.10,
    label="Calma"
)

line_return = mpatches.Patch(
    color="black",
    label="Retornos SPY"
)

line_garch = mpatches.Patch(
    color="darkred",
    label="Volatilidad GARCH"
)

axes[0].legend(
    handles=[stress_patch, calm_patch],
    loc="upper right"
)

axes[1].legend(
    handles=[stress_patch, calm_patch],
    loc="upper right"
)

plt.suptitle(
    "Figura 7. Retornos del SPY y volatilidad condicional GARCH(1,1) por régimen",
    fontsize=15,
    y=0.98
)

plt.tight_layout()

plt.savefig(
    "figura_7_retornos_spy_volatilidad_garch_regimenes.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
