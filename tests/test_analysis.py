import json
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from engine import descriptive_stats,build_hourly,correlation_pair,categorical_pair,load_dataset,pformat,run_full_analysis

class AnalysisTests(unittest.TestCase):
    def test_iqr_and_sample_variance(self):
        s=pd.Series([1,2,2,3,100]); d=descriptive_stats(s,'x')
        self.assertEqual(d['moda'],2)
        self.assertEqual(d['n_outliers_iqr'],1)
        self.assertEqual(d['media_sin_atipicos'],2)
        self.assertAlmostEqual(d['varianza_muestral'],s.var(ddof=1))
    def test_missing_hour_is_not_zero(self):
        df=pd.DataFrame({'step':[1,1,3],'id_transaccion':[1,2,3],'monto':[2.,4.,8.]})
        h=build_hourly(df)
        self.assertTrue(pd.isna(h.loc[1,'transacciones_hora']))
        self.assertEqual(h.transacciones_hora.sum(),3)
    def test_monotonic_but_nonlinear(self):
        d=correlation_pair(pd.DataFrame({'x':np.arange(1,31),'y':np.arange(1,31)**3}),'x','y','test')
        self.assertAlmostEqual(d['spearman_coef'],1)
        self.assertLess(d['pearson_coef'],.95)
    def test_independent_table(self):
        df=pd.DataFrame([(a,b) for a in ['A','B'] for b in ['X','Y'] for _ in range(20)],columns=['a','b'])
        c=categorical_pair(df,'a','b')
        self.assertAlmostEqual(c['chi2'],0)
        self.assertAlmostEqual(c['mutual_information_nats'],0)
        self.assertAlmostEqual(c['p_value'],1)
    def test_pvalue_display(self):
        self.assertEqual(pformat(1e-9),'<0.0001')
        self.assertEqual(pformat(.04996),'0.0500')
        # Aunque se muestre 0.0500, las decisiones se toman con el número original.
        self.assertLess(.04996,.05)
    def test_wrong_schema_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'wrong.csv'; p.write_text('x,y\n1,2\n',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Esquema'): load_dataset(p)
    def test_pipeline_synthetic_fixture(self):
        # Datos artificiales exclusivamente para prueba, no para resultados del laboratorio.
        rng=np.random.default_rng(9); rows=[]
        for hour in range(1,73):
            for _ in range(20+hour%9):
                kind=rng.choice(['PAYMENT','TRANSFER']); commerce=kind=='PAYMENT'
                rows.append([len(rows)+1,hour,kind,float(rng.lognormal(4 if commerce else 6,1)),
                    'C1','M1' if commerce else 'C2','COMERCIO' if commerce else 'CLIENTE'])
        from engine import EXPECTED_COLUMNS
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'fixture.csv'; pd.DataFrame(rows,columns=EXPECTED_COLUMNS).to_csv(p,index=False)
            r=run_full_analysis(p,Path(tmp)/'result')
            self.assertEqual(r['metadata']['rows'],len(rows))
            self.assertEqual(r['descriptive_statistics'][1]['n'],len(rows))
            self.assertEqual(r['categorical_association'][0]['n'],len(rows))
            self.assertEqual(r['seasonality']['n_steps'],72)
    def test_delivered_results_reconcile(self):
        r=json.loads((ROOT/'results/analysis_summary.json').read_text(encoding='utf-8'))
        h=pd.read_csv(ROOT/'results/hourly_series.csv')
        self.assertEqual(h.transacciones_hora.sum(),r['metadata']['rows'])
        self.assertEqual(r['descriptive_statistics'][1]['n'],r['metadata']['rows'])
        for pair in r['categorical_association']:
            self.assertGreaterEqual(pair['min_expected'],5)

if __name__=='__main__': unittest.main(verbosity=2)
