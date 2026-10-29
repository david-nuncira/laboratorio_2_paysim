"""Crea y ejecuta cuatro notebooks sin depender del CSV para abrir resultados."""
import argparse
import json
import os
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]
# Archivos de Jupyter/IPython locales, sin escribir en el perfil del usuario.
os.environ['IPYTHONDIR']=str(ROOT/'work/ipython')
os.environ['JUPYTER_RUNTIME_DIR']=str(ROOT/'work/jupyter_runtime')
SETUP="""from pathlib import Path
import os, sys, json
import numpy as np
import pandas as pd
from IPython.display import display, Markdown, Image
ROOT = Path.cwd() if (Path.cwd() / 'src').is_dir() else Path.cwd().parent
sys.path.insert(0, str(ROOT / 'src'))
from engine import fmt, pformat, load_dataset, run_full_analysis, descriptive_stats
from narrative import sections
r = json.loads((ROOT / 'results/analysis_summary.json').read_text(encoding='utf-8'))
h = pd.read_csv(ROOT / 'results/hourly_series.csv')
pd.options.display.float_format = lambda x: f'{x:.4f}'
def tabla(rows):
    frame = pd.DataFrame(rows)
    for col in frame:
        if col.endswith('_p') or col == 'p_value': frame[col] = frame[col].map(pformat)
    display(frame)
def apartado(i):
    title, texts = sections(r)[i-1]
    display(Markdown('## ' + title))
    for text in texts: display(Markdown(text))
def figura(name):
    display(Image(filename=str(ROOT / 'results/figures' / name), width=850))
"""

def md(t): return nbf.v4.new_markdown_cell(t)
def code(t): return nbf.v4.new_code_cell(t)

def build(execute=True):
    specs=[]
    specs.append(('00_Contexto_y_reproduccion',[
       md('# Laboratorio 2 · Contexto y ejecución\n\nGrupo de **tres estudiantes**. Completar nombres antes de entregar. Se usa el CSV PaySim adaptado del Laboratorio 1. Los archivos de `references/` son material docente; sus resultados no se usan como si fueran datos del grupo.'),
       code(SETUP), code("apartado(1)\ntabla(r['variable_dictionary'])\ndisplay(r['data_quality'])"),
       md('## Verificación de origen\n\nLa huella SHA-256 identifica el CSV utilizado. Si el archivo está disponible se puede recalcular desde este notebook o desde `scripts/run_analysis.py`. La apertura normal presenta las salidas reales guardadas.'),
       code("display(r['metadata'])\nassert r['metadata']['columns'] == 7\nassert int(h.transacciones_hora.sum()) == r['metadata']['rows']\nprint('Reconciliación de filas y conteos horarios: correcta')"),
       code("""# Cambiar a True para rehacer todo con el CSV original.
RECALCULAR = False
CSV = Path(os.environ.get('LAB2_CSV', str(ROOT / 'data/transacciones.csv')))
if RECALCULAR:
    df = load_dataset(CSV)
    r = run_full_analysis(CSV, ROOT / 'results', df=df)
    from engine import build_hourly
    from plots import generate_figures
    generate_figures(df, build_hourly(df), ROOT / 'results/figures')
    print('Análisis actualizado; regenerar PDF con scripts/create_report.py')
else:
    print('Mostrando resultados reales guardados. Para recalcular: RECALCULAR=True y ruta CSV.')"""),
       md('## Reparto sugerido\n\nIntegrante 1: contexto, calidad y descriptivas. Integrante 2: asociaciones y pruebas. Integrante 3: serie temporal, dashboard y ejecución. Los tres validan la interpretación final. No se suministraron nombres.\n\nLa guía exige siete apartados analíticos y un octavo entregable: notebooks, proyecto VSCode y Streamlit. La cobertura detallada está en `reports/Matriz_cumplimiento.md`.')
    ]))
    specs.append(('01_Descriptivas_Forma_IQR',[
       md('# Laboratorio 2 · Descriptivas, forma y atípicos\n\nDescriptivas calculadas con todas las filas. step y monto usan transacciones; conteo y monto promedio usan horas. No se mezclan las unidades.'),
       code(SETUP),code('apartado(2)'),
       code("""ds = pd.DataFrame(r['descriptive_statistics']).set_index('variable')
fields = ['n','media','mediana','moda','rango','varianza_muestral','desviacion_estandar',
          'coeficiente_variacion_porcentaje','p10','q1','q2','q3','p90']
display(ds[fields].T)
# Verificación independiente sobre la serie horaria completa.
check = descriptive_stats(h.transacciones_hora, 'transacciones_hora', 'hora')
assert np.isclose(check['media'], ds.loc['transacciones_hora', 'media'])
assert np.isclose(h.transacciones_hora.var(ddof=1), ds.loc['transacciones_hora','varianza_muestral'])"""),
       code('apartado(3)'),
       code("display(ds[['asimetria_fisher','curtosis_pearson','exceso_curtosis','clasificacion_asimetria','clasificacion_curtosis']])\ndisplay(ds[['iqr','limite_inferior_iqr','limite_superior_iqr','n_outliers_iqr','porcentaje_outliers_iqr','media_sin_atipicos','mediana_sin_atipicos','desviacion_sin_atipicos']])"),
       code("for name in ['histograma_monto.png','boxplot_monto.png','histograma_step.png','boxplot_step.png','histograma_transacciones_hora.png','boxplot_transacciones_hora.png','distribucion_monto_promedio.png','monto_transformado_grupos.png','barras_tipo_transaccion.png','barras_tipo_destino.png']:\n    figura(name)"),
       md('Las gráficas de transacciones usan hasta 100000 observaciones con semilla 42. El resultado numérico usa el total. En monto se incluyen escalas original y log1p para ver la cola y el cuerpo. La exclusión IQR se presenta como sensibilidad, no como borrado de datos.')
    ]))
    specs.append(('02_Asociaciones_e_Hipotesis',[
       md('# Laboratorio 2 · Hipótesis de asociación\n\nAlpha = 0.0500. Se decide con precisión completa; p pequeños se presentan como <0.0001. Los p-valores son exploratorios y nominales por las dependencias temporales y de cuenta.'),
       code(SETUP),code('apartado(4)\ntabla(r["continuous_association"])'),
       code("figura('scatter_step_monto.png')\nfigura('scatter_montos_horarios.png')"),
       code("""# Covarianza y Pearson independientes para el par de continuas horarias.
from scipy import stats
expected = next(a for a in r['continuous_association'] if a['left']=='monto_promedio')
assert np.isclose(h.monto_promedio.cov(h.monto_mediano), expected['covarianza_muestral'])
assert np.isclose(stats.pearsonr(h.monto_promedio,h.monto_mediano).statistic,expected['pearson_coef'])
print('Covarianza y Pearson horario reconciliados.')"""),
       code('apartado(5)'),
       code("""for pair in r['categorical_association']:
    display(Markdown('### ' + pair['pair']))
    observed = pd.DataFrame(pair['observed']).set_index(pair['left'])
    expected = pd.DataFrame(pair['expected']).set_index(pair['left'])
    display(observed); display(expected)
    manual = np.outer(observed.sum(axis=1), observed.sum(axis=0))/observed.to_numpy().sum()
    assert np.allclose(expected.to_numpy(), manual)
    assert np.isclose(((observed.to_numpy()-manual)**2/manual).sum(), pair['chi2'])
    tabla([{k:pair[k] for k in ['chi2','p_value','degrees_freedom','mutual_information_nats','normalized_mutual_information','cramers_v','min_expected','percent_expected_below_5']}])"""),
       code('apartado(6)\ntabla(r["mixed_association"]["normalidad_por_grupo"])\ntabla(r["mixed_association"]["group_summary"])'),
       code("""mix=r['mixed_association']
tabla([{'prueba': 'Levene mediana', 'estadistico':mix['levene_median_center']['statistic'], 'p_value':mix['levene_median_center']['p_value']},
       {'prueba': 'ANOVA clásica', 'estadistico':mix['anova']['F'], 'p_value':mix['anova']['p_value']},
       {'prueba': 'Welch ANOVA', 'estadistico':mix['welch_anova']['F'], 'p_value':mix['welch_anova']['p_value']},
       {'prueba': 'Kruskal-Wallis', 'estadistico':mix['kruskal_wallis']['H'], 'p_value':mix['kruskal_wallis']['p_value']}])
figura('monto_transformado_grupos.png')"""),
       md('Las pruebas son globales. Rechazar una hipótesis de igualdad no identifica qué pares difieren. No se interpreta Kruskal como igualdad exclusiva de medianas con distribuciones de forma distinta. Si se requieren comparaciones post hoc deben añadirse con control de multiplicidad.')
    ]))
    specs.append(('03_Sintesis_y_Estacionalidad',[
       md('# Laboratorio 2 · Síntesis y estacionalidad\n\nEste notebook conecta la EDA con el siguiente laboratorio de modelado. No entrena un SARIMA ni atribuye rendimiento predictivo no evaluado.'),
       code(SETUP),code('apartado(7)'),
       code("display(h.head(12))\nassert h.step.diff().dropna().eq(1).all()\nassert h.transacciones_hora.notna().all()\nprint('Frecuencia horaria regular verificada')"),
       code("""from statsmodels.tsa.stattools import acf
correlations=acf(h.transacciones_hora.astype(float),nlags=72,fft=True)
assert np.isclose(correlations[24], r['seasonality']['acf_lag_24'])
print('ACF(1):',fmt(correlations[1]),'ACF(24):',fmt(correlations[24]))
tabla(r['seasonality']['lag_target_correlations'])
display(r['seasonality']['adf_log1p'])"""),
       code("for name in ['serie_transacciones_hora.png','perfil_intradia.png','acf_conteo.png']:\n    figura(name)"),
       md('## Protocolo posterior de modelado\n\n1. Ordenar la serie por step y reservar un bloque final.\n2. Comparar ingenuo estacional y SARIMA con s=24.\n3. Elegir transformación, d y D usando entrenamiento, inspección y pruebas; no usar todo el archivo para ajustar decisiones.\n4. Evaluar ventanas cronológicas con MAE/RMSE.\n5. Revisar residuos y Ljung-Box de residuos, no confundirlo con la prueba de la serie original.\n6. Usar variables exógenas solo si se conocen al momento del pronóstico; rezagar los agregados de la misma hora.'),
       md('## Entregable\n\nEl proyecto incluye código compartido, pruebas, app Streamlit, resultados, figuras, informe PDF/Markdown, referencias del curso y guía VSCode. Las métricas se vinculan al SHA-256 del archivo analizado. Los resultados se pueden consultar sin copiar el CSV grande; para recalcular hay que anexarlo en `data/` o indicar su ruta.')
    ]))
    target=ROOT/'notebooks'; target.mkdir(exist_ok=True)
    for name,cells in specs:
        nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}})
        if execute:
            NotebookClient(nb,timeout=300,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
        nbf.write(nb,target/(name+'.ipynb'))
        print('Ejecutado:',name,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--no-execute',action='store_true'); args=p.parse_args(); build(not args.no_execute)
