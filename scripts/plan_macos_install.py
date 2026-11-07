#!/usr/bin/env python3
"""Print a bounded macOS installation plan; execute no privileged commands."""
from pathlib import Path
import argparse, shlex
from verify import ROOT

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',required=True);a=p.parse_args()
    b=Path(a.bundle).resolve();assert (ROOT/'local').resolve() in b.parents
    assert (b/'assembly.json').exists()
    print('# Review docs/INSTALL.md and target identity before running any command.')
    print('# Back up each existing target first; stop if versions/hashes differ unexpectedly.')
    roots=[b/'rootfs/Library/Extensions'/f'{n}.kext' for n in ['NVRM','NVRMFB','NVAccel','NVRMAGDC']]
    roots += sorted((b/'rootfs/Library/GPUBundles').iterdir())
    roots += [b/'rootfs/Library/NullMoth']
    for src in roots:
        assert src.exists();target=Path('/')/src.relative_to(b/'rootfs')
        print('sudo /usr/bin/ditto',shlex.quote(str(src)),shlex.quote(str(target)))
        print('sudo /usr/sbin/chown -R root:wheel',shlex.quote(str(target)))
        print('sudo /bin/chmod -R go-w',shlex.quote(str(target)))
    print('# After approval/signature checks, rebuild with standard authorization; do not add -z or force flags:')
    print('sudo /usr/bin/kmutil install --volume-root / --update-all --update-preboot')
    print('# Check exit status and diagnostics. Do not reboot automatically.')

if __name__=='__main__':main()
