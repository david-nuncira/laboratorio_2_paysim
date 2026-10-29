"""Dashboard local de los resultados reales del Laboratorio 2."""
from pathlib import Path
import json
import subprocess
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from engine import fmt,pformat
from narrative import sections

st.set_page_config(page_title='Laboratorio 2 | PaySim',page_icon='📊',layout='wide')
st.title('Laboratorio 2 · Transacciones PaySim')
st.caption('Estadística para Analítica de Datos · Grupo de tres estudiantes · Resultados del CSV real')

result_path=ROOT/'results/analysis_summary.json'
with st.sidebar:
    st.header('Explorar el laboratorio')
    page=st.radio('Apartado',['Panorama','1. Contexto','2. Descriptivas','3. Forma e IQR','4. Correlaciones','5. Categóricas','6. Grupos','7. Serie de tiempo','Descargas'])
    with st.expander('Recalcular con el CSV'):
        path=st.text_input('Ruta local del archivo',str(ROOT/'data/transacciones.csv'))
        st.caption('Puede tardar varios minutos. El archivo se procesa en este equipo.')
        if st.button('Ejecutar análisis completo'):
            if not Path(path).is_file(): st.error('Archivo no encontrado. Revisa la ruta.')
            else:
                with st.spinner('Calculando estadísticas y figuras…'):
                    run=subprocess.run([sys.executable,str(ROOT/'scripts/run_analysis.py'),'--data',path],cwd=ROOT,capture_output=True,text=True)
                if run.returncode: st.error(run.stderr)
                else:
                    st.success('Resultados actualizados. El PDF se regenera con scripts/create_report.py.')
                    st.rerun()

if not result_path.is_file():
    st.info('Faltan resultados. Selecciona el CSV en la barra lateral para calcularlos.')
    st.stop()
r=json.loads(result_path.read_text(encoding='utf-8'))
h=pd.read_csv(ROOT/'results/hourly_series.csv')

def show_table(rows):
    df=pd.DataFrame(rows)
    # La precisión completa del JSON se mantiene; solo cambia la presentación.
    display=df.copy()
    for c in df:
        if pd.api.types.is_float_dtype(df[c]):
            display[c]=df[c].map(pformat if c.endswith('_p') or c=='p_value' else fmt)
    st.dataframe(display,hide_index=True,width='stretch')

def image(name):
    p=ROOT/'results/figures'/name
    if p.exists(): st.image(str(p),width='stretch')

if page=='Panorama':
    cols=st.columns(3)
    cols[0].metric('Transacciones',f"{r['metadata']['rows']:,}")
    cols[1].metric('Variables originales',r['metadata']['columns'])
    cols[2].metric('Horas',len(h))
    st.write('Objetivo posterior: pronosticar cuántas transacciones se registran en la siguiente hora. Este dashboard presenta EDA y pruebas exploratorias.')
    st.plotly_chart(px.line(h,x='step',y='transacciones_hora',title='Volumen horario'),width='stretch')
    st.info('El CSV se localizó y analizó. Las tablas usan el archivo completo, salvo correlaciones transaccionales y Shapiro documentados en el informe.')
elif page=='Descargas':
    for p in [ROOT/'reports/Informe_Laboratorio_2.pdf',ROOT/'reports/Informe_Laboratorio_2.md',result_path,ROOT/'results/descriptive_statistics.csv',ROOT/'results/hourly_series.csv']:
        if p.exists(): st.download_button('Descargar '+p.name,p.read_bytes(),file_name=p.name)
    st.code('streamlit run app.py',language='shell')
else:
    idx=int(page.split('.')[0])-1
    title,pars=sections(r)[idx]
    st.header(title)
    for text in pars: st.write(text)
    if idx==0:
        show_table(r['variable_dictionary']); st.json(r['data_quality'])
    elif idx==1:
        selected=st.selectbox('Variable',[a['variable'] for a in r['descriptive_statistics']])
        row=next(a for a in r['descriptive_statistics'] if a['variable']==selected)
        show_table([{'medida':k,'valor':fmt(v)} for k,v in row.items() if isinstance(v,(int,float))])
    elif idx==2:
        image('histograma_monto.png'); image('boxplot_monto.png'); image('monto_transformado_grupos.png')
        show_table([{k:d[k] for k in ['variable','asimetria_fisher','exceso_curtosis','n_outliers_iqr','porcentaje_outliers_iqr','media_sin_atipicos']} for d in r['descriptive_statistics']])
    elif idx==3:
        show_table(r['continuous_association']); image('scatter_montos_horarios.png'); image('scatter_step_monto.png')
    elif idx==4:
        name=st.selectbox('Par categórico',[a['pair'] for a in r['categorical_association']])
        a=next(x for x in r['categorical_association'] if x['pair']==name)
        st.subheader('Observadas'); show_table(a['observed'])
        st.subheader('Esperadas'); show_table(a['expected'])
        st.write(f"Chi2 = {fmt(a['chi2'])}; p {pformat(a['p_value'])}; MI = {fmt(a['mutual_information_nats'])} nats")
    elif idx==5:
        show_table(r['mixed_association']['normalidad_por_grupo']); show_table(r['mixed_association']['group_summary'])
        image('monto_transformado_grupos.png')
    elif idx==6:
        interval=st.slider('Intervalo de steps',int(h.step.min()),int(h.step.max()),(int(h.step.min()),int(h.step.max())))
        subset=h[h.step.between(*interval)]
        st.plotly_chart(px.line(subset,x='step',y='transacciones_hora'),width='stretch')
        profile=h.groupby('hora_dia',as_index=False).transacciones_hora.mean()
        st.plotly_chart(px.bar(profile,x='hora_dia',y='transacciones_hora',labels={'hora_dia':'Fase step % 24'}),width='stretch')
        image('acf_conteo.png')
