# Correspondencia con la guía

| Punto | Evidencia entregada | Decisión específica para PaySim |
|---|---|---|
| 1. Contexto | Notebook 00; informe §1; engine.variable_dictionary y data_quality | 6.362.620 transacciones, 7 columnas originales, población simulada, unidad transacción y objetivo horario. |
| 2. Descriptivas | Notebook 01; descriptive_statistics.csv; informe §2 | Cuatro cuantitativas con unidades explícitas; centro, dispersión, CV y cuantiles exactos. |
| 3. Forma y outliers | Notebook 01; figuras; informe §3 | Fisher, Pearson/exceso, IQR 1.5 y sensibilidad de media, mediana y desviación sin borrar originales. |
| 4. Continuas | Notebook 02; correlations.csv; informe §4 | Solo monto es continua original. Se agregan media-mediana y total-media por hora. step-monto es adicional discreta-continua. Covarianza, Pearson, Spearman, Kendall, p e IQR. |
| 5. Categóricas | Notebook 02; cuatro CSV de contingencias; informe §5 | Tipo vs destino original y tipo vs franja temporal derivada. Observadas, esperadas, chi2, MI en nats, NMI y V de Cramér. |
| 6. Mixtas | Notebook 02; JSON; informe §6 | Monto por tipo. Shapiro <=5000 por grupo, Levene mediana, ANOVA, Welch, Kruskal y tamaños de efecto. |
| 7. Síntesis | Notebook 03; informe §7; dashboard temporal | Objetivo conteo, rezagos, ACF24, Ljung-Box, ADF y protocolo SARIMA con s=24. Se explican independencia y fuga de información. |
| 8. Entregable | ZIP, configuración VSCode, 4 notebooks ejecutados, Streamlit, PDF/Markdown, tests | Grupo de tres. Datos reales incluidos en el ZIP y huella SHA-256 para trazabilidad. |

Los siete apartados analíticos están resueltos con datos reales. Se explicitan adaptaciones porque el esquema del Laboratorio 1 tiene una sola continua original y pocos atributos categóricos de baja cardinalidad. Estas adaptaciones no se presentan como columnas originales.
