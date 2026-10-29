"""EDA reproducible. Precisión completa interna; cuatro decimales al presentar."""
from __future__ import annotations
import hashlib
import json
import platform
from pathlib import Path
from importlib.metadata import version
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import mutual_info_score
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf, adfuller

EXPECTED_COLUMNS = ['id_transaccion', 'step', 'tipo_transaccion', 'monto',
                    'cuenta_origen', 'cuenta_destino', 'tipo_cuenta_destino']
SEED = 42
ALPHA = 0.05
SAMPLE_LIMIT = 200_000

def fmt(x):
    return 'No estimable' if x is None or pd.isna(x) else f'{float(x):.4f}'

def pformat(p):
    if p is None or not np.isfinite(p): return 'No estimable'
    return '<0.0001' if p < 0.0001 else f'{p:.4f}'

def json_safe(x):
    if isinstance(x, dict): return {str(k): json_safe(v) for k,v in x.items()}
    if isinstance(x, (list,tuple,np.ndarray)): return [json_safe(v) for v in x]
    if isinstance(x, np.integer): return int(x)
    if isinstance(x, (float,np.floating)): return float(x) if np.isfinite(x) else None
    if isinstance(x,np.bool_): return bool(x)
    return x

def load_dataset(path):
    path=Path(path)
    if not path.is_file(): raise FileNotFoundError(f'Falta el CSV: {path}. Copiar a data/transacciones.csv o usar --data.')
    head=pd.read_csv(path,nrows=0)
    if list(head.columns)!=EXPECTED_COLUMNS: raise ValueError(f'Esquema esperado: {EXPECTED_COLUMNS}. Recibido: {list(head.columns)}')
    df=pd.read_csv(path,dtype={'id_transaccion':'Int64','step':'Int32','monto':'float64',
          'tipo_transaccion':'category','tipo_cuenta_destino':'category','cuenta_origen':'string','cuenta_destino':'string'})
    if df.empty: raise ValueError('El CSV no tiene observaciones.')
    return df

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''): h.update(block)
    return h.hexdigest()

def values(s):
    return pd.to_numeric(s,errors='coerce').replace([np.inf,-np.inf],np.nan).dropna().astype(float)

def descriptive_stats(series,name,unit='transacción'):
    v=values(series)
    if len(v)<2: raise ValueError(f'{name}: se necesitan dos valores válidos.')
    freq=v.value_counts(); modes=sorted(freq[freq==freq.max()].index.tolist()) if freq.max()>1 else []
    q1,q2,q3=v.quantile([.25,.5,.75]); iqr=q3-q1; lo,hi=q1-1.5*iqr,q3+1.5*iqr
    keep=v.between(lo,hi); trimmed=v[keep]
    skew=float(stats.skew(v,bias=False)) if v.nunique()>1 and len(v)>2 else np.nan
    excess=float(stats.kurtosis(v,fisher=True,bias=False)) if v.nunique()>1 and len(v)>3 else np.nan
    return dict(variable=name,unidad=unit,n=len(v),media=v.mean(),mediana=v.median(),
        moda=modes[0] if modes else None,numero_modas=len(modes),modas=modes,frecuencia_moda=int(freq.max()),
        minimo=v.min(),maximo=v.max(),rango=v.max()-v.min(),varianza_muestral=v.var(ddof=1),desviacion_estandar=v.std(ddof=1),
        coeficiente_variacion_porcentaje=100*v.std(ddof=1)/abs(v.mean()) if v.mean()!=0 else None,
        p10=v.quantile(.1),q1=q1,q2=q2,q3=q3,p90=v.quantile(.9),asimetria_fisher=skew,
        curtosis_pearson=excess+3,exceso_curtosis=excess,
        clasificacion_asimetria=('no estimable' if not np.isfinite(skew) else 'aproximadamente simétrica' if abs(skew)<=.5 else 'asimétrica positiva' if skew>0 else 'asimétrica negativa'),
        clasificacion_curtosis=('no estimable' if not np.isfinite(excess) else 'leptocúrtica' if excess>.1 else 'platicúrtica' if excess<-.1 else 'mesocúrtica'),
        iqr=iqr,limite_inferior_iqr=lo,limite_superior_iqr=hi,n_outliers_iqr=int((~keep).sum()),
        porcentaje_outliers_iqr=100*(~keep).mean(),media_sin_atipicos=trimmed.mean(),
        mediana_sin_atipicos=trimmed.median(),desviacion_sin_atipicos=trimmed.std(ddof=1),
        nota='Exclusión IQR como sensibilidad, no limpieza automática.')

def variable_dictionary():
    return pd.DataFrame([
      ['id_transaccion','Nominal (identificador)','Clave entera; no usar como predictor cuantitativo.'],
      ['step','Cuantitativa discreta','Índice horario de la simulación; fase inicial sin hora civil documentada.'],
      ['tipo_transaccion','Nominal','CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER.'],
      ['monto','Cuantitativa continua','Unidades monetarias del simulador; no se asume COP.'],
      ['cuenta_origen','Nominal','Identificador de cuenta emisora.'],
      ['cuenta_destino','Nominal','Identificador de cuenta receptora.'],
      ['tipo_cuenta_destino','Nominal','CLIENTE o COMERCIO.'],
      ['transacciones_hora','Discreta derivada','Conteo de filas por step; unidad hora.'],
      ['monto_promedio / monto_mediano / monto_total','Continuas derivadas','Media, mediana y suma de monto por hora.'],
      ['fase_24 / franja_horaria','Cíclica discreta / nominal derivada','step % 24 y bloques 00-05, 06-11, 12-17, 18-23.']
    ],columns=['variable','tipo','definicion'])

def data_quality(df):
    dest=df.cuenta_destino.str.slice(0,1)
    expected=df.tipo_cuenta_destino.astype('string').map({'CLIENTE':'C','COMERCIO':'M'})
    return dict(missing_by_column=df.isna().sum().to_dict(),
      empty_text_by_column={c:int(df[c].astype('string').str.strip().eq('').sum()) for c in EXPECTED_COLUMNS if c not in ['id_transaccion','step','monto']},
      duplicate_id_transaccion=int(df.id_transaccion.dropna().duplicated().sum()),negative_monto=int(df.monto.lt(0).sum()),
      zero_monto=int(df.monto.eq(0).sum()),nonfinite_monto=int((~np.isfinite(df.monto)).sum()),
      invalid_step=int((df.step.lt(1)|df.step.isna()).sum()),
      invalid_tipo_transaccion=sorted(set(df.tipo_transaccion.dropna().astype(str))-{'CASH_IN','CASH_OUT','DEBIT','PAYMENT','TRANSFER'}),
      unknown_destination_type=int((expected.isna()&df.tipo_cuenta_destino.notna()).sum()),
      destination_prefix_inconsistency_known_types=int((expected.notna()&dest.ne(expected)).sum()))

def build_hourly(df):
    h=df.groupby('step',observed=True).agg(transacciones_hora=('id_transaccion','size'),
          monto_total=('monto','sum'),monto_promedio=('monto','mean'),monto_mediano=('monto','median'))
    h.index=h.index.astype(int)
    # Ausencias quedan como NA: no hay evidencia para imputar cero.
    h=h.reindex(range(int(h.index.min()),int(h.index.max())+1)).rename_axis('step').reset_index()
    h['hora_dia']=h.step%24
    return h

def correlation_pair(frame,left,right,scope):
    v=frame[[left,right]].replace([np.inf,-np.inf],np.nan).dropna().astype(float)
    if len(v)<3 or min(v.nunique())<2: return dict(estado='no calculado',left=left,right=right,n=len(v),alcance=scope)
    out=dict(estado='calculado',left=left,right=right,n=len(v),alcance=scope,covarianza_muestral=v[left].cov(v[right]))
    for name,test in [('pearson',stats.pearsonr),('spearman',stats.spearmanr),('kendall',stats.kendalltau)]:
        res=test(v[left],v[right]); out[name+'_coef']=float(res.statistic); out[name+'_p']=float(res.pvalue)
    return out

def continuous_association(df,hourly):
    work=df[['step','monto']].dropna(); sample=work.sample(min(SAMPLE_LIMIT,len(work)),random_state=SEED)
    pairs=[correlation_pair(sample,'step','monto','Transacciones; step discreta. P nominal bajo independencia.')]
    pairs += [correlation_pair(hourly,a,b,'Horas; continuas derivadas. P nominal por dependencia temporal.') for a,b in [
        ('monto_promedio','monto_mediano'),('monto_total','monto_promedio')]]
    q1,q3=sample.monto.quantile([.25,.75]); iqr=q3-q1
    pairs.append(correlation_pair(sample[sample.monto.between(q1-1.5*iqr,q3+1.5*iqr)],'step','monto','Sensibilidad IQR de la misma muestra.'))
    return pairs

def categorical_pair(frame,left,right):
    observed=pd.crosstab(frame[left],frame[right]); chi,p,dof,exp=stats.chi2_contingency(observed,correction=False)
    n=int(observed.to_numpy().sum()); d=min(observed.shape)-1
    mi=mutual_info_score(None,None,contingency=observed.to_numpy())
    px=observed.sum(axis=1).to_numpy()/n; py=observed.sum(axis=0).to_numpy()/n; denom=stats.entropy(px)+stats.entropy(py)
    return dict(pair=left+'_vs_'+right,estado='calculado',left=left,right=right,n=n,chi2=chi,p_value=p,
        degrees_freedom=dof,mutual_information_nats=mi,normalized_mutual_information=2*mi/denom if denom else 0,
        cramers_v=np.sqrt(chi/(n*d)) if d else None,min_expected=exp.min(),percent_expected_below_5=100*(exp<5).mean(),
        observed=observed.reset_index().to_dict('records'),
        expected=pd.DataFrame(exp,index=observed.index,columns=observed.columns).reset_index().to_dict('records'))

def categorical_association(df):
    frame=df[['tipo_transaccion','tipo_cuenta_destino','step']].copy()
    frame['franja_horaria']=pd.cut(frame.step%24,bins=[-1,5,11,17,23],labels=['00-05','06-11','12-17','18-23'])
    return [categorical_pair(frame,'tipo_transaccion','tipo_cuenta_destino'),categorical_pair(frame,'tipo_transaccion','franja_horaria')]

def mixed_association(df):
    groups=[]; normal=[]; summaries=[]
    for name,g in df.groupby('tipo_transaccion',observed=True):
        v=values(g.monto)
        if len(v)<3: continue
        groups.append(v.to_numpy()); sh=stats.shapiro(v.sample(min(5000,len(v)),random_state=SEED))
        normal.append(dict(grupo=str(name),n_total=len(v),n_shapiro=min(5000,len(v)),W=sh.statistic,p_value=sh.pvalue))
        summaries.append(dict(grupo=str(name),n=len(v),media=v.mean(),mediana=v.median(),desviacion=v.std(ddof=1)))
    if len(groups)<2: return dict(estado='no calculado',motivo='Menos de dos grupos con 3 datos.')
    lev=stats.levene(*groups,center='median'); a=stats.f_oneway(*groups); kw=stats.kruskal(*groups)
    from statsmodels.stats.oneway import anova_oneway
    welch=anova_oneway(groups,use_var='unequal'); n=sum(map(len,groups)); k=len(groups)
    grand=sum(g.sum() for g in groups)/n; ssb=sum(len(g)*(g.mean()-grand)**2 for g in groups); sst=sum(((g-grand)**2).sum() for g in groups)
    return dict(estado='calculado',normalidad_por_grupo=normal,group_summary=summaries,
        levene_median_center=dict(statistic=lev.statistic,p_value=lev.pvalue),
        anova=dict(F=a.statistic,p_value=a.pvalue,df_between=k-1,df_within=n-k,eta_squared=ssb/sst),
        welch_anova=dict(F=welch.statistic,p_value=welch.pvalue,df=list(welch.df)),
        kruskal_wallis=dict(H=kw.statistic,p_value=kw.pvalue,epsilon_squared=max(0,(kw.statistic-k+1)/(n-k))))

def seasonality_analysis(hourly):
    if hourly.transacciones_hora.isna().any(): return dict(estado='bloqueado por horas ausentes',n_steps=len(hourly))
    y=hourly.transacciones_hora.to_numpy(dtype=float); profile=hourly.groupby('hora_dia').transacciones_hora.mean()
    corr=acf(y,nlags=min(72,len(y)-1),fft=True)
    out=dict(n_steps=len(y),min_step=int(hourly.step.min()),max_step=int(hourly.step.max()),hora_pico_promedio=int(profile.idxmax()),
       promedio_hora_pico=profile.max(),promedio_hora_menor=profile.min(),acf_lag_1=corr[1] if len(corr)>1 else None,
       acf_lag_24=corr[24] if len(corr)>24 else None,lag_target_correlations=[])
    for lag in [1,24]:
        lagged=hourly[['transacciones_hora']].copy(); lagged[f'rezago_{lag}']=lagged.transacciones_hora.shift(lag)
        out['lag_target_correlations'].append(correlation_pair(lagged,f'rezago_{lag}','transacciones_hora','Horas; p nominal, autocorrelación no implica causalidad.'))
    if len(y)>48:
        lb=acorr_ljungbox(y,lags=[24],return_df=True).iloc[0]
        out['ljung_box_lag_24']=dict(statistic=lb.lb_stat,p_value=lb.lb_pvalue)
        adf=adfuller(np.log1p(y),autolag='AIC'); out['adf_log1p']=dict(statistic=adf[0],p_value=adf[1],used_lags=adf[2])
    return out

def run_full_analysis(data_path,output_dir,df=None):
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    if df is None: df=load_dataset(data_path)
    hourly=build_hourly(df)
    result=dict(metadata=dict(source_file=Path(data_path).name,source_sha256=sha256(data_path),source_bytes=Path(data_path).stat().st_size,
        rows=len(df),columns=len(df.columns),column_names=list(df.columns),sample_n_for_correlations=min(SAMPLE_LIMIT,len(df)),
        sample_seed=SEED,alpha=ALPHA,rounding_digits=4,python=platform.python_version(),
        package_versions={m:version(m) for m in ['pandas','numpy','scipy','statsmodels','scikit-learn','matplotlib','streamlit']}),
        variable_dictionary=variable_dictionary().to_dict('records'),data_quality=data_quality(df),
        descriptive_statistics=[descriptive_stats(v,name,unit) for name,v,unit in [
          ('step',df.step,'transacción'),('monto',df.monto,'transacción'),('transacciones_hora',hourly.transacciones_hora,'hora'),('monto_promedio',hourly.monto_promedio,'hora')]],
        continuous_association=continuous_association(df,hourly),categorical_association=categorical_association(df),
        mixed_association=mixed_association(df),seasonality=seasonality_analysis(hourly))
    result=json_safe(result)
    variable_dictionary().to_csv(out/'variable_dictionary.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(result['descriptive_statistics']).to_csv(out/'descriptive_statistics.csv',index=False,float_format='%.4f',encoding='utf-8-sig')
    hourly.to_csv(out/'hourly_series.csv',index=False,encoding='utf-8-sig')
    for pair in result['categorical_association']:
        for label in ['observed','expected']:
            pd.DataFrame(pair[label]).to_csv(out/f"contingency_{label}_{pair['pair']}.csv",index=False,float_format='%.4f',encoding='utf-8-sig')
    pd.DataFrame(result['continuous_association']).to_csv(out/'correlations.csv',index=False,float_format='%.4f',encoding='utf-8-sig')
    df.tipo_transaccion.value_counts().rename_axis('tipo_transaccion').reset_index(name='frecuencia').to_csv(out/'type_frequencies.csv',index=False)
    (out/'analysis_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    return result
