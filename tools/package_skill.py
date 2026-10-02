#!/usr/bin/env python3
"""Create a portable single-root ZIP with deterministic file order and checksums."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/agibot-x2-interfaces'
VERSION=(ROOT/'VERSION').read_text(encoding='utf-8').strip()


def main():
    if not re.fullmatch(r'\d+\.\d+\.\d+', VERSION):
        raise ValueError('VERSION must use MAJOR.MINOR.PATCH')
    if any(p.is_symlink() for p in SKILL.rglob('*')):
        raise ValueError('Symlinks cannot be packaged')
    files=sorted(p for p in SKILL.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name!='package-manifest.json')
    manifest=dict(name=SKILL.name,version=VERSION,distribution='official-links-only',license='MulanPSL-2.0',source_document_version='AimDK_X2 web links; no manufacturer document snapshot included',
                  files={p.relative_to(SKILL).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    mp=SKILL/'package-manifest.json'
    mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    files=sorted(files+[mp])
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    target=dist/(SKILL.name+'-'+VERSION+'.zip')
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for p in files:
            info=zipfile.ZipInfo(SKILL.name+'/'+p.relative_to(SKILL).as_posix(),date_time=(2026,10,2,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            archive.writestr(info,p.read_bytes())
    sha=hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(sha+'  '+target.name+'\n')
    stable=dist/(SKILL.name+'.zip')
    shutil.copyfile(target,stable)
    stable.with_suffix('.zip.sha256').write_text(sha+'  '+stable.name+'\n')
    print(json.dumps(dict(archive=str(target),files=len(files),bytes=target.stat().st_size,sha256=sha)))


if __name__=='__main__':
    main()
