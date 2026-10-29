"""Empaqueta el proyecto y CSV original con manifiesto y verificación CRC."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]

def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''): h.update(block)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser(); p.add_argument('--data',required=True); args=p.parse_args()
    data=Path(args.data)
    summary=json.loads((ROOT/'results/analysis_summary.json').read_text(encoding='utf-8'))
    if digest(data)!=summary['metadata']['source_sha256']: raise ValueError('El CSV no coincide con el análisis.')
    verification=json.loads((ROOT/'results/verification.json').read_text(encoding='utf-8'))
    if verification.get('status')!='passed': raise ValueError('Falta verificación satisfactoria.')
    files=sorted(f for f in ROOT.rglob('*') if f.is_file() and not set(f.relative_to(ROOT).parts)&{'__pycache__','work','.venv','.git'} and f.name!='MANIFEST.json' and not f.name.endswith('.pyc'))
    manifest={'data_sha256':summary['metadata']['source_sha256'],'data_bytes':data.stat().st_size,
       'files':{str(f.relative_to(ROOT)).replace('\\','/'): {'bytes':f.stat().st_size,'sha256':digest(f)} for f in files},
       'verification':'results/verification.json','group_size':3}
    manifest_path=ROOT/'MANIFEST.json'; manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    dest=ROOT.parent/'Laboratorio_2_PaySim_Completo.zip'
    with ZipFile(dest,'w',compression=ZIP_DEFLATED,compresslevel=6,allowZip64=True) as archive:
        for f in files+[manifest_path]: archive.write(f,ROOT.name+'/'+str(f.relative_to(ROOT)).replace('\\','/'))
        archive.write(data,ROOT.name+'/data/transacciones.csv')
    with ZipFile(dest) as archive:
        bad=archive.testzip()
        if bad: raise ValueError('Error CRC: '+bad)
        names=archive.namelist()
        assert ROOT.name+'/data/transacciones.csv' in names
        assert len([n for n in names if '/notebooks/' in n and n.endswith('.ipynb')])==4
    log={'zip_file':dest.name,'bytes':dest.stat().st_size,'sha256':digest(dest),'archive_members':len(names),
         'crc_check':'passed','dataset_included':True,'notebooks_executed':4,'verification':'passed'}
    (ROOT.parent/'Verificacion_entrega.json').write_text(json.dumps(log,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(log,indent=2),flush=True)

if __name__=='__main__': main()
