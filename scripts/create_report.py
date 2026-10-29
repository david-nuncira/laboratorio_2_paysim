"""Genera PDF y Markdown con los mismos resultados y conclusiones."""
from pathlib import Path
import json
import sys
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from engine import fmt, pformat
from narrative import sections, SOURCES
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image

def build():
    r=json.loads((ROOT/'results/analysis_summary.json').read_text(encoding='utf-8'))
    report=ROOT/'reports'; report.mkdir(exist_ok=True)
    doc=SimpleDocTemplate(str(report/'Informe_Laboratorio_2.pdf'),pagesize=A4,
        leftMargin=44,rightMargin=44,topMargin=46,bottomMargin=44,
        title='Laboratorio 2 - EDA y asociación - PaySim',author='Grupo de tres estudiantes')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyLab',fontName='Helvetica',fontSize=9.4,leading=13.4,spaceAfter=9,textColor=colors.HexColor('#253348')))
    styles.add(ParagraphStyle(name='CellLab',fontSize=7.4,leading=9.6,textColor=colors.HexColor('#253348')))
    styles.add(ParagraphStyle(name='CaptionLab',fontSize=8,leading=11,spaceAfter=8,textColor=colors.HexColor('#526174')))
    styles['Heading1'].textColor=colors.HexColor('#133e63'); styles['Heading1'].fontSize=18; styles['Heading1'].leading=22
    story=[]
    def para(text,style='BodyLab'):
        story.append(Paragraph(escape(text),styles[style]))
    def table(headers,rows,widths=None):
        data=[[Paragraph(escape(str(c)),styles['CellLab']) for c in row] for row in [headers]+rows]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#deebf7')),
          ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
          ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
          ('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#5a86ac')),
          ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f8fb')])]))
        story.append(t); story.append(Spacer(1,10))
    def figure(name,width=498):
        p=ROOT/'results/figures'/name
        w,h=ImageReader(str(p)).getSize(); story.append(Image(str(p),width=width,height=width*h/w))
        para(name.replace('_',' ').replace('.png',''),'CaptionLab')
    def footer(canvas,doc):
        canvas.saveState(); canvas.setStrokeColor(colors.HexColor('#b9cddd')); canvas.line(44,32,551,32)
        canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor('#526174'))
        canvas.drawString(44,21,'Estadística para Analítica de Datos | PaySim adaptado | Grupo de tres')
        canvas.drawRightString(551,21,str(doc.page)); canvas.restoreState()
    story.append(Spacer(1,70)); para('LABORATORIO 2','Heading1')
    para('Exploración de datos e hipótesis de asociación','Title')
    para('Especialización en Analítica Estratégica de Datos - UPTC')
    para('Profesor: Duván Cataño | Curso 2026-II | Fecha de análisis: 29 de octubre de 2026')
    para('Equipo de TRES estudiantes. Los nombres no fueron suministrados; completar la identificación antes de la entrega.')
    story.append(Spacer(1,18))
    table(['Datos verificados','Alcance'],[
       [f"{r['metadata']['rows']:,} transacciones",'7 variables originales; 4 cuantitativas analizadas, incluidas derivadas'],
       [f"{r['seasonality']['n_steps']} horas consecutivas",'Objetivo posterior: transacciones por hora'],
       ['Archivo real disponible','transacciones.csv; huella SHA-256 en manifiesto y JSON'],
       ['Evidencia reproducible','Notebooks ejecutados, 15 visualizaciones, dashboard y pruebas']],[180,318])
    para('Guía de lectura')
    para('1. Contexto y calidad. 2. Descriptivas. 3. Forma e IQR. 4. Correlaciones. 5. Contingencias. 6. Comparación de grupos. 7. Síntesis temporal. Anexo: visualizaciones y reproducibilidad.')
    para('Los cálculos usan precisión completa. Las medidas se muestran con cuatro decimales y los p-valores menores que 0.0001 se muestran con esa cota. Las pruebas se interpretan como exploratorias bajo sus supuestos, en datos simulados.')
    story.append(PageBreak())
    allsections=sections(r)
    for idx,(title,paragraphs) in enumerate(allsections):
        para(title,'Heading1')
        for text in paragraphs: para(text)
        if idx==0:
            table(['Variable original','Tipo'],[[d['variable'],d['tipo']] for d in r['variable_dictionary'][:7]],[155,343])
        if idx==1:
            story.append(PageBreak()); para('2. Tablas de medidas','Heading1')
            ds=r['descriptive_statistics']
            fields=['media','mediana','moda','rango','varianza_muestral','desviacion_estandar','coeficiente_variacion_porcentaje','p10','q1','q2','q3','p90']
            table(['Medida']+[d['variable'] for d in ds],[[f.replace('_',' ')]+[fmt(d[f]) for d in ds] for f in fields],[132,88,94,94,90])
            para('step y monto: 6.362.620 filas. Conteo y monto promedio: 743 horas. El CV del índice step no tiene interpretación invariante al cambio de origen. Conteos n se expresan como enteros. Medidas monetarias sin moneda real atribuida.','CaptionLab')
        if idx==2:
            table(['Variable','Asimetría','Curtosis','Exceso','Atípicos IQR (%)'],[[d['variable'],fmt(d['asimetria_fisher']),fmt(d['curtosis_pearson']),fmt(d['exceso_curtosis']),fmt(d['porcentaje_outliers_iqr'])] for d in r['descriptive_statistics']],[130,88,88,88,104])
        if idx==4:
            story.append(PageBreak()); para('5. Tablas observadas y esperadas','Heading1')
            for c in r['categorical_association']:
                para(c['pair'],'Heading2')
                for label in ['observed','expected']:
                    rows=c[label]; keys=list(rows[0]); para('Observadas' if label=='observed' else 'Esperadas bajo H0')
                    table(keys,[[row[k] if isinstance(row[k],str) else fmt(row[k]) for k in keys] for row in rows],[118]+[(498-118)/(len(keys)-1)]*(len(keys)-1))
        if idx==5:
            table(['Tipo','n','Media','Mediana','Desviación'],[[a['grupo'],a['n'],fmt(a['media']),fmt(a['mediana']),fmt(a['desviacion'])] for a in r['mixed_association']['group_summary']],[92,72,116,108,110])
        story.append(PageBreak())
    para('Anexo A. Visualizaciones','Heading1')
    para('Las figuras transaccionales usan una muestra fija de hasta 100000 filas para legibilidad. Las figuras horarias usan la serie completa. Los boxplots marcan extremos estadísticos, no fraude. En el gráfico por tipo se omiten puntos extremos por legibilidad y se informa una escala transformada.')
    figures=['histograma_monto.png','boxplot_monto.png','histograma_step.png','boxplot_step.png',
       'histograma_transacciones_hora.png','boxplot_transacciones_hora.png','distribucion_monto_promedio.png',
       'monto_transformado_grupos.png','barras_tipo_transaccion.png','barras_tipo_destino.png',
       'scatter_step_monto.png','scatter_montos_horarios.png','serie_transacciones_hora.png','perfil_intradia.png','acf_conteo.png']
    for i,name in enumerate(figures):
        figure(name,width=450)
        if i%2==1 and i<len(figures)-1: story.append(PageBreak())
    story.append(PageBreak()); para('Anexo B. Reproducibilidad y fuentes','Heading1')
    para('Ejecutar desde la raíz del proyecto: pip install -r requirements.txt; python scripts/run_analysis.py --data data/transacciones.csv; python scripts/create_report.py; streamlit run app.py. Los comandos se detallan para Windows en README. El CSV completo no se incorpora al ZIP por tamaño, pero las rutas, el esquema y su huella permiten verificar el mismo archivo.')
    para('SHA-256: '+r['metadata']['source_sha256'])
    para('Python: '+r['metadata']['python']+' | Versiones científicas: '+str(r['metadata']['package_versions']))
    for source in SOURCES: para(source)
    para('Distribución sugerida entre tres integrantes: 1) contextualización, calidad y descriptivas; 2) correlaciones, contingencias y pruebas mixtas; 3) síntesis temporal, aplicación y revisión de reproducibilidad. Los tres revisan las conclusiones y la sustentación.')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    md=['# Laboratorio 2 - PaySim adaptado','Equipo de tres estudiantes. Completar nombres antes de entregar.']
    for title,pars in allsections:
        md += ['## '+title]+pars
    md += ['## Fuentes']+SOURCES
    (report/'Informe_Laboratorio_2.md').write_text('\n\n'.join(md),encoding='utf-8')
    print(report/'Informe_Laboratorio_2.pdf')

if __name__=='__main__': build()
