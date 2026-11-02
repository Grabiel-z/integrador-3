import hashlib
import json
import zipfile
from pathlib import Path

ROOTS={"sunat","gateway","tools","pruebas","chatbot","datos","infra","scripts","investigacion","diagramas","informe","output","evidencias"}
FILES={"compose.yaml","compose.gpu.yaml","requirements.txt","requirements.lock","pytest.ini",".env.example",".gitignore",".dockerignore","ESTADO_FINAL.json"}
DENY={".git",".agents",".aws",".codex","__pycache__",".pytest_cache","privadas","tmp","node_modules",".venv","venv"}


def selected():
    for path in sorted(Path('.').rglob('*')):
        if not path.is_file() or path.is_symlink() or path.stat().st_size==0:continue
        if set(path.parts)&DENY:continue
        if path.name.startswith('.env') and path.name!='.env.example':continue
        if path.suffix in {'.zip','.pyc','.db','.sqlite','.sqlite3'}:continue
        if path.name in {'build.log','pull.log','zip_validacion.json'}:continue
        if path.parts[0] in ROOTS or path.name in FILES or len(path.parts)==1 and path.suffix=='.md':yield path


def main():
    required=['output/pdf/Proyecto_RPA_1_GrupoX.pdf','informe/Proyecto_RPA_1_GrupoX.md','datos/RUC_entrada.xlsx','datos/RUC_resultados.xlsx',
              'chatbot/workflows/CORE_CHATBOT.json','chatbot/workflows/CHATBOT_TELEGRAM.json','chatbot/workflows/PRUEBAS_CHATBOT.json']
    for path in required:
        if not Path(path).is_file():raise SystemExit('Falta entregable requerido: '+path)
    paths=list(selected());manifest={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    # Comprueba que ningún secreto local haya acabado accidentalmente en evidencias.
    private=Path('.env')
    if private.exists():
        secrets=[]
        for line in private.read_text().splitlines():
            if '=' not in line or line.lstrip().startswith('#'):continue
            key,value=line.split('=',1)
            if any(term in key for term in ('KEY','TOKEN','PASSWORD')) and len(value.strip())>=8:
                secrets.append(value.strip().encode())
        for p in paths:
            data=p.read_bytes()
            if any(secret in data for secret in secrets):raise SystemExit('Se detectó contenido privado en '+str(p)+'; ZIP no generado')
    dest=Path('GrupoX_TA4.zip')
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as archive:
        for p in paths:archive.write(p,'GrupoX_TA4/'+str(p))
        archive.writestr('GrupoX_TA4/MANIFIESTO_SHA256.json',json.dumps(manifest,indent=2))
    with zipfile.ZipFile(dest) as archive:
        assert archive.testzip() is None
        names=archive.namelist()
        assert not any(n.endswith('/.env') or '/privadas/' in n for n in names)
        for name,digest in manifest.items():assert hashlib.sha256(archive.read('GrupoX_TA4/'+name)).hexdigest()==digest
    validation={'archivo':str(dest),'archivos':len(names),'bytes':dest.stat().st_size,'integridad_crc':'VERIFICADO','sha256_archivos':'VERIFICADO','exclusion_secretos':'VERIFICADO'}
    Path('evidencias/zip_validacion.json').write_text(json.dumps(validation,indent=2))
    print(json.dumps(validation,indent=2))


if __name__=='__main__':main()
