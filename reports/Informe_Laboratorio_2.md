# Laboratorio 2 - PaySim adaptado

Equipo de tres estudiantes. Completar nombres antes de entregar.

## 1. Contexto, población y calidad

El archivo verificado contiene 6,362,620 transacciones y 7 variables originales. La unidad original es una transacción. La población de referencia son las operaciones del sistema simulado PaySim bajo sus reglas generadoras; el archivo es la muestra disponible, no una muestra probabilística de todos los usuarios bancarios reales. Si se delimita la población al archivo, las descriptivas son censales.

La naturaleza analítica elegida es serie de tiempo. Se construye y(t) = número de filas con step = t para pronosticar el volumen de operaciones por hora. Al agregar cambia la unidad de observación a hora. step es tiempo discreto; monto es la única continua original. Los identificadores numéricos y de cuentas se clasifican como nominales. No hay variable ordinal original ni etiqueta de fraude en estas siete columnas.

Se observaron 0 valores faltantes, 0 identificadores duplicados, 0 montos negativos y 16 montos cero. Las comprobaciones de prefijo de destino dieron 0 inconsistencias. Los ceros se conservan y se dejan señalados para revisar su origen. No se eliminan operaciones solo por ser grandes.

La serie tiene 743 steps entre 1 y 743. Se valida continuidad antes de calcular ACF; una hora ausente no se interpreta automáticamente como cero. La fase step % 24 es reproducible, pero no se conoce una fecha ni un reloj civil. Tampoco se deducen días de la semana reales.

Método: descriptivas, tablas categóricas, Levene, ANOVA y Kruskal usan el archivo completo; Pearson/Spearman/Kendall a nivel transacción usan muestra aleatoria simple sin reemplazo de hasta 200000 filas (semilla 42). Las correlaciones horarias usan todas las horas. Shapiro usa hasta 5000 observaciones por grupo. Nivel de referencia alpha = 0.0500; no se redondea antes de decidir.

## 2. Tendencia central, dispersión y posición

Se analizan step y monto a nivel transacción, y transacciones_hora y monto_promedio a nivel hora. No se copia el conteo de una hora a cada transacción para volver a calcular sus descriptivas: eso ponderaría excesivamente las horas activas. La varianza usa n-1; cuantiles con interpolación lineal; CV = 100 s / |media|. La moda se calcula por valor exacto, se informa multiplicidad si existe empate.

Monto: media 179861.9035, mediana 74871.9400, moda 10000000.0000. La media superior a la mediana indica influencia de la cola derecha. La moda de un monto redondeado puede reflejar reglas o importes repetidos del simulador; no implica que sea un monto típico de la mayoría.

El 50% central de montos se sitúa entre Q1=13389.5700 y Q3=208721.4775. P10=4501.3000 y P90=365423.3090 delimitan el 80% central. El rango es 92445516.6400; la desviación estándar es 603858.2315.

La tabla adjunta contiene las medidas completas. Entre variables de razón comparables, la mayor dispersión relativa es monto. El CV de step se muestra para completar el cálculo, pero su origen temporal es arbitrario y cambia si se traslada el índice, por lo que no es una comparación sustantiva de variabilidad.

En el objetivo horario, media=8563.4186, mediana=529.0000. La diferencia refleja heterogeneidad entre horas activas y horas con actividad baja. No demuestra por sí sola una tendencia temporal.

## 3. Forma, gráficos y valores atípicos

Monto tiene asimetría Fisher=30.9939, curtosis Pearson=1800.9567 y exceso=1797.9567. Se clasifica como asimétrica positiva y leptocúrtica. El exceso se obtiene restando 3 a la curtosis Pearson. Una curtosis elevada describe colas y extremos; no equivale simplemente a mayor altura del pico.

Se usa la convención descriptiva |asimetría| <= 0.5 para simetría aproximada y |exceso| <= 0.1 para mesocurtosis aproximada; son umbrales de lectura, no pruebas de normalidad. Histogramas y boxplots se construyen para las variables cuantitativas, y barras para las categorías. Las figuras transaccionales usan hasta 100000 filas (semilla 42); las tablas usan el total.

Con IQR=Q3-Q1=195331.9075, los límites de Tukey son -279608.2913 y 501719.3387. Hay 338,078 montos fuera de ellos (5.3135%). Como sensibilidad, al excluirlos la media pasa de 179861.9035 a 111534.1803 y la desviación de 603858.2315 a 120398.3069. La mediana sin extremos es 63175.8150.

Los atípicos no son automáticamente errores ni fraude. Las horas de mayor actividad pueden ser parte de la estacionalidad. Para modelar monto se propone comparar log1p(monto) y métodos robustos conservando el original. No se garantiza normalidad ni homocedasticidad con una transformación.

## 4. Covarianza y correlaciones

Como solo hay una continua original, se explicita la adaptación del requisito: pares de continuas derivadas por hora (monto_promedio, monto_mediano) y (monto_total, monto_promedio). Se incluye step-monto como análisis adicional con step discreta. Las tres pruebas contrastan asociación nula de distinto tipo: Pearson lineal, Spearman monotónica por rangos y Kendall concordancia de pares con corrección por empates.

step vs monto (n=200000, Transacciones; step discreta. P nominal bajo independencia.): covarianza=1892173.2297; Pearson=0.0235 (p=<0.0001); Spearman=0.0004 (p=0.8729); Kendall=0.0001 (p=0.9582).

monto_promedio vs monto_mediano (n=743, Horas; continuas derivadas. P nominal por dependencia temporal.): covarianza=575819150580.5616; Pearson=0.8067 (p=<0.0001); Spearman=0.9019 (p=<0.0001); Kendall=0.7339 (p=<0.0001).

monto_total vs monto_promedio (n=743, Horas; continuas derivadas. P nominal por dependencia temporal.): covarianza=-735612500850691.2500; Pearson=-0.2873 (p=<0.0001); Spearman=-0.4944 (p=<0.0001); Kendall=-0.2151 (p=<0.0001).

step vs monto (n=189359, Sensibilidad IQR de la misma muestra.): covarianza=-174078.4140; Pearson=-0.0102 (p=<0.0001); Spearman=-0.0017 (p=0.4548); Kendall=-0.0013 (p=0.4019).

Los diagramas permiten revisar colas, puntos influyentes y curvatura. La sensibilidad IQR vuelve a estimar los tres índices sobre el mismo subconjunto de la muestra, y permite ver cuánto cambia Pearson al reducir extremos. Un coeficiente pequeño puede producir p pequeño con n grande. Spearman y Kendall son más resistentes a magnitudes extremas, pero una relación no monotónica también puede tener correlación por rangos cercana a cero.

La covarianza depende de unidades. monto_total = conteo * monto_promedio, de modo que su asociación con monto_promedio tiene un componente algebraico compartido. Ninguna correlación establece causalidad. Las horas sucesivas y las cuentas repetidas comprometen independencia: los p-valores son nominales exploratorios, no inferencia causal ni garantía de rendimiento fuera de muestra.

## 5. Independencia categórica e información mutua

Se estudian dos pares: tipo_transaccion vs tipo_cuenta_destino (ambas originales) y tipo_transaccion vs franja_horaria (derivada de step % 24 en bloques 00-05, 06-11, 12-17, 18-23). La franja es una adaptación temporal explícita. Se evita probar millones de identificadores nominales con frecuencias esperadas insuficientes. H0: independencia; H1: dependencia. Chi-cuadrado de Pearson sin corrección de Yates.

tipo_transaccion_vs_tipo_cuenta_destino: chi2=6362620.0000, gl=4, p=<0.0001, MI=0.6398 nats, NMI=0.6570, V de Cramér=1.0000. Mínima esperada=14010.0683, porcentaje de celdas esperadas <5=0.0000%. A alpha=0.0500, se rechaza independencia.

tipo_transaccion_vs_franja_horaria: chi2=49171.8336, gl=12, p=<0.0001, MI=0.0036 nats, NMI=0.0029, V de Cramér=0.0508. Mínima esperada=733.2593, porcentaje de celdas esperadas <5=0.0000%. A alpha=0.0500, se rechaza independencia.

Las tablas observadas y esperadas están en CSV y en los notebooks; esperada(i,j)=total_fila(i)*total_columna(j)/n. MI se obtiene con logaritmo natural y es una magnitud de dependencia, no un p-valor. NMI usa 2 MI/(H(X)+H(Y)); no debe confundirse con MI en nats.

La relación tipo-destino se explica por la regla observada: PAYMENT se dirige a COMERCIO y los otros tipos a CLIENTE. Esto implica redundancia para ciertos modelos; no mide fraude. Para la franja se compara el tamaño de efecto y MI con el p-valor, porque millones de filas permiten detectar efectos pequeños. Las reglas simuladas y la dependencia temporal limitan su generalización.

## 6. Variable mixta: monto por tipo de transacción

H0 de Shapiro-Wilk: distribución normal dentro de cada grupo. Se toman hasta 5000 montos aleatorios por grupo porque el p de Shapiro puede ser impreciso por encima de ese tamaño. H0 de Levene centrado en la mediana: varianzas iguales. ANOVA clásica contrasta igualdad de medias; Kruskal-Wallis contrasta igualdad de distribuciones/rangos. Con formas similares puede interpretarse como contraste de localización/medianas, condición que aquí no se da por supuesta.

Shapiro en CASH_IN: n_total=1,399,284, n_test=5000, W=0.9212, p=<0.0001.

Shapiro en CASH_OUT: n_total=2,237,500, n_test=5000, W=0.4636, p=<0.0001.

Shapiro en DEBIT: n_total=41,432, n_test=5000, W=0.3114, p=<0.0001.

Shapiro en PAYMENT: n_total=2,151,495, n_test=5000, W=0.8318, p=<0.0001.

Shapiro en TRANSFER: n_total=532,909, n_test=5000, W=0.2662, p=<0.0001.

Levene-Brown-Forsythe: estadístico=177416.1244, p=<0.0001. ANOVA: F=278715.5421, p=<0.0001, eta2=0.1491. Kruskal-Wallis: H=3906986.6819, p=<0.0001, epsilon2=0.6141.

Como contraste de medias con heterocedasticidad se añade ANOVA de Welch: F=1039325.8302, p=<0.0001. Las pruebas globales significativas indican al menos un grupo diferente, sin identificar por sí solas qué parejas difieren.

En estos resultados se rechazan normalidad por grupo y homogeneidad de varianzas. Se prioriza Kruskal para diferencias distribucionales y Welch para medias. ANOVA clásica se reporta por exigencia de la guía. Kruskal no corrige dependencia entre operaciones ni convierte automáticamente el resultado en una comparación exclusiva de medianas. Para inferencia confirmatoria se necesitarían bloques horarios o agrupación por cuenta, además de post hoc si se requiere localizar diferencias.

## 7. Síntesis y conexión con SARIMA

Para el objetivo transacciones_hora, el historial y la fase diaria son candidatos directos. ACF(1)=0.9235 y ACF(24)=0.7546. La fase 19 tiene el mayor promedio (20897.2258 transacciones); la fase menos activa promedia 40.0323. El desfase entre step y reloj civil no está documentado.

Asociación del objetivo con rezago_1: Pearson=0.9239, Spearman=0.6842, Kendall=0.5221, n=742. Estos indicadores exploran utilidad de rezagos y no equivalen a importancia predictiva validada.

Asociación del objetivo con rezago_24: Pearson=0.8046, Spearman=0.6071, Kendall=0.4685, n=719. Estos indicadores exploran utilidad de rezagos y no equivalen a importancia predictiva validada.

Ljung-Box en 24 rezagos sobre la serie original: estadístico=3775.3124, p=<0.0001. Detecta autocorrelación conjunta, no demuestra por sí solo estacionalidad. ADF en log1p(conteo): estadístico=-2.3727, p=0.1496. H0 de ADF es raíz unitaria. En este archivo no se rechaza al 5%, por lo que no se asume estacionariedad del nivel. Su decisión no descarta cambios de régimen ni sustituye el diagnóstico estacional.

Se recomienda estudiar SARIMA(p,d,q)(P,D,Q,24), compararlo con un pronóstico ingenuo estacional y evaluar ventanas de validación cronológica. Las órdenes d y D se deciden después de inspeccionar diferenciación, ACF/PACF y estacionariedad; no se eligen solo por ADF. Reservar un bloque final y medir MAE/RMSE; revisar residuos y predicciones no negativas. Este laboratorio es EDA, no presenta un SARIMA entrenado ni resultados de pronóstico inventados.

Descartar identificadores de transacción y cuentas como predictores numéricos. Conservarlos para trazabilidad. Evaluar redundancia de tipo_cuenta_destino con tipo_transaccion. Para monto, considerar log1p y estadísticas robustas; para conteo, evaluar si log1p mejora residuos. La composición por tipo o monto de la misma hora solo se conoce al cerrar esa hora: no debe entrar como predictor contemporáneo del conteo futuro. Si se usa, rezagarlo y pasar a un modelo con exógenas (SARIMAX) validando disponibilidad.

Conclusión del grupo: el volumen horario se relaciona descriptivamente con su historial y la fase temporal. La asimetría y los extremos obligan a interpretar medias y correlaciones junto con medianas, rangos y tamaños de efecto. La evidencia es propia del simulador y del periodo observado; no atribuye causas reales como promociones, demanda de clientes o fraude que no se midieron.

## Fuentes

Duván Cataño. Laboratorio_2.pdf, pp. 1-2: requisitos de los siete apartados y entregable.

Duván Cataño. Presentación del curso (2026-II), pp. 10-15: EDA, asociación y series de tiempo.

Notebooks de referencia: Visualizacion_Frecuencias, Estadistica_Descriptiva, Exploration_Data_Regr y Exploration_Data_Class. Se adaptan a este esquema; sus datasets y conclusiones no se transfieren.

SciPy. Shapiro-Wilk: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.shapiro.html (consulta 2026-10-29).

SciPy. Kruskal-Wallis: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html (consulta 2026-10-29).

PaySim, repositorio del autor: https://github.com/EdgarLopezPhD/PaySim (consulta 2026-10-29). Respalda el carácter simulado; el esquema adaptado se verifica en el CSV local.