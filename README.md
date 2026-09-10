# VIX Term Structure Replication

Este repositorio contiene los scripts utilizados para construir la tabla maestra, generar gráficos, clasificar regímenes de volatilidad y estimar el modelo GARCH(1,1) del trabajo.

## Estructura del repositorio

```text
vix-term-structure-replication/
│
├── README.md
├── requirements.txt
│
├── scripts/
│   ├── 01_install_libraries.py
│   ├── 02_upload_input_file.py
│   ├── 03_download_validate_vix.py
│   ├── 04_build_master_dataset.py
│   ├── 05_visualizacion_futuros_vix.py
│   ├── 06_vix_spot_vs_vx1.py
│   ├── 07_grafico_slope12_serie_temporal.py
│   ├── 08_distribucion_slope12.py
│   ├── 09_grafico_spy_precio.py
│   ├── 10_grafico_spy_retornos.py
│   ├── 11_clasificacion_regimenes_ma20.py
│   ├── 12_resultados_por_regimen.py
│   └── 13_estimacion_garch_11.py
│
├── data_raw/
│   └── README.md
│
├── data_processed/
│   └── README.md
│
├── outputs/
│   ├── figures/
│   │   └── README.md
│   └── tables/
│       └── README.md
│
└── docs/
    └── notas_replicacion.md
```

## Organización metodológica

Los scripts 01 a 04 corresponden al **Anexo I – Replicación de la construcción de la base de datos**.

Los scripts 05 a 13 corresponden al **Anexo II – Evidencia visual de resultados, tablas y gráficos**.

## Nota sobre datos licenciados

Los datos provenientes de LSEG/Refinitiv pueden estar sujetos a restricciones de uso y redistribución. Por ese motivo, este repositorio publica los scripts necesarios para replicar el proceso, pero no necesariamente los archivos de datos brutos obtenidos desde la plataforma.
