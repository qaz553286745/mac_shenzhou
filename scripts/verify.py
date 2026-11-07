#!/usr/bin/env python3
"""Offline integrity and public-configuration checks; never writes a system disk."""
from pathlib import Path
import hashlib, json, plistlib

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def verify_assets():
    assets=json.loads((ROOT/'manifests/assets.json').read_text())
    for asset in assets:
        combined=hashlib.sha256();size=0
        for part in asset['parts']:
            p=ROOT/part['file'];assert p.is_file(),f'Missing {p.name}'
            assert p.stat().st_size==part['bytes'] and digest(p)==part['sha256'],p.name
            with p.open('rb') as f:
                for b in iter(lambda:f.read(4*1024*1024),b''):combined.update(b);size+=len(b)
        assert combined.hexdigest()==asset['sha256'] and size==asset['bytes'],asset['name']
    return assets

def main():
    assets=verify_assets()
    for p in (ROOT/'configs').glob('*.plist'):
        d=plistlib.loads(p.read_bytes());g=d['PlatformInfo']['Generic']
        assert g['SystemSerialNumber']==g['MLB']=='' and g['ROM']==bytes(6)
        assert g['SystemUUID']=='00000000-0000-0000-0000-000000000000'
        assert g['SystemProductName']=='MacBookPro16,1'
        args=d['NVRAM']['Add']['7C436110-AB2A-4BBB-A880-FE41995C9F82']['boot-args'].split()
        assert 'cpus=12' in args and 'nvfbhidpi=1' in args
        assert '-dbgenhiolog' not in args and '-vsmcdbg' not in args
        assert d['DeviceProperties']['Add']['PciRoot(0x0)/Pci(0x1F,0x3)']['device-id']==bytes.fromhex('ffff0000')
    index=ROOT/'manifests/repository-files.json'
    if index.exists():
        for name,h in json.loads(index.read_text()).items():assert digest(ROOT/name)==h,name
    print(f'OK: {len(assets)} assets, public identities cleared, profiles consistent.')

if __name__=='__main__':main()
