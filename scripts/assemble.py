#!/usr/bin/env python3
"""Reassemble checked archives into an ignored local staging directory."""
from pathlib import Path
import argparse, json, os, shutil, tarfile, tempfile
from verify import ROOT, digest, verify_assets

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',default='local/bundle');a=p.parse_args()
    out=Path(a.output).resolve();local=(ROOT/'local').resolve()
    assert local in out.parents,'Output must remain inside this repository local/ directory'
    assert not out.exists(),'Use a new output directory; existing staging is never overwritten'
    assets=verify_assets();out.mkdir(parents=True)
    for asset in assets:
        with tempfile.TemporaryDirectory(prefix='asset-',dir=local) as tmp:
            archive=Path(tmp)/'data.tar.gz'
            with archive.open('wb') as f:
                for part in asset['parts']:
                    with (ROOT/part['file']).open('rb') as src:shutil.copyfileobj(src,f)
            assert digest(archive)==asset['sha256']
            with tarfile.open(archive) as z:
                for m in z.getmembers():
                    rel=Path(m.name);assert not rel.is_absolute() and '..' not in rel.parts
                    if m.isdir():continue
                    layout=asset['layout']
                    if layout=='stable':
                        if not rel.parts or rel.parts[0]!='payload':continue
                        rel=Path('rootfs',*rel.parts[1:])
                    elif layout=='runtime':rel=Path('rootfs')/rel
                    elif layout=='audio':rel=Path('optional-audio')/rel
                    dst=out/rel
                    assert out in dst.resolve().parents
                    dst.parent.mkdir(parents=True,exist_ok=True)
                    if m.issym():
                        assert not Path(m.linkname).is_absolute() and '..' not in Path(m.linkname).parts
                        assert not dst.exists();dst.symlink_to(m.linkname)
                    elif m.isfile():
                        assert not dst.is_symlink()
                        with z.extractfile(m) as src,dst.open('wb') as f:shutil.copyfileobj(src,f)
                        dst.chmod(m.mode & 0o755)
                    else:raise ValueError('Unsupported archive member '+m.name)
        print('Restored',asset['name'])
    for name,base in [('efi-files.json',out),('nvidia-files.json',out/'rootfs'),('metal-runtime-files.json',out/'rootfs')]:
        for rel,h in json.loads((ROOT/'manifests'/name).read_text()).items():assert digest(base/rel)==h,rel
    (out/'assembly.json').write_text(json.dumps({'assets_verified':True,'system_modified':False,'identity_required':True},indent=2)+'\n')
    print('Ready:',out,'(no system drivers installed)')

if __name__=='__main__':main()
