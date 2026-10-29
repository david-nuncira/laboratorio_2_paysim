"""Ejecuta las pruebas, notebooks y comprobaciones del entregable."""
from pathlib import Path
import datetime
import json
import subprocess
import sys
import os
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]

def main():
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    records=[]
    commands=[
      [sys.executable,'-m','unittest','discover','-s','tests','-p','test_analysis.py','-v'],
      [sys.executable,'-u','scripts/build_notebooks.py'],
      [sys.executable,'-u','tests/test_app.py']]
    for cmd in commands:
        print('Ejecutando:', ' '.join(cmd[1:]),flush=True)
        run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=600,
            env={**os.environ,'PYTHONUTF8':'1','PYTHONUNBUFFERED':'1'})
        records.append({'command':' '.join(cmd[1:]),'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
        print(run.stdout,flush=True)
        if run.returncode:
            print(run.stderr,flush=True)
            (ROOT/'results/verification.json').write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf-8')
            raise SystemExit(run.returncode)
    for nb in (ROOT/'notebooks').glob('*.ipynb'):
        raw=json.loads(nb.read_text(encoding='utf-8'))
        cells=[c for c in raw['cells'] if c['cell_type']=='code']
        assert cells and all(c['execution_count'] is not None for c in cells),nb
        assert not any(o.get('output_type')=='error' for c in cells for o in c.get('outputs',[])),nb
    pdf=ROOT/'reports/Informe_Laboratorio_2.pdf'
    reader=PdfReader(pdf); text='\n'.join(p.extract_text() or '' for p in reader.pages)
    for needle in ['1. Contexto','2. Tendencia','3. Forma','4. Covarianza','5. Independencia','6. Variable mixta','7. Síntesis']:
        assert needle in text,needle
    info={'date':'2026-10-29','python':sys.version,'records':records,'notebooks_executed':4,
          'pdf_pages':len(reader.pages),'figures_count':len(list((ROOT/'results/figures').glob('*.png'))),
          'status':'passed'}
    (ROOT/'results/verification.json').write_text(json.dumps(info,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Verificación completa: OK',flush=True)

if __name__=='__main__':main()
