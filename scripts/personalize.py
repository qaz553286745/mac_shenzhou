#!/usr/bin/env python3
"""Insert privately supplied SMBIOS identifiers without printing them."""
from pathlib import Path
import argparse, json, os, plistlib, re, uuid
from verify import ROOT

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile',choices=['stable-sdr-100s','candidate-sdr-50s','recovery-igpu-audio-off'],required=True)
    p.add_argument('--identity',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    local=(ROOT/'local').resolve();src=Path(a.identity).resolve();dst=Path(a.output).resolve()
    assert local in src.parents and local in dst.parents,'Private files must remain under local/'
    v=json.loads(src.read_text());gkeys=['SystemSerialNumber','MLB','SystemUUID','ROM']
    assert set(v)==set(gkeys),'Expected exactly four identity fields'
    assert re.fullmatch(r'[A-Z0-9]{12}',v['SystemSerialNumber'])
    assert re.fullmatch(r'[A-Z0-9]{17}',v['MLB'])
    u=uuid.UUID(v['SystemUUID']);assert u.int!=0
    assert re.fullmatch(r'[0-9a-fA-F]{12}',v['ROM']) and int(v['ROM'],16)!=0
    d=plistlib.loads((ROOT/f'configs/{a.profile}.plist').read_bytes());g=d['PlatformInfo']['Generic']
    for k in gkeys:g[k]=bytes.fromhex(v[k]) if k=='ROM' else str(u).upper() if k=='SystemUUID' else v[k]
    assert not dst.exists(),'Refusing to replace an existing private configuration'
    dst.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(dst,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(plistlib.dumps(d,sort_keys=False))
    print('Private configuration created. Run OpenCore1.0.8 ocvalidate before deployment.')

if __name__=='__main__':main()
