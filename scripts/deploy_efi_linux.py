#!/usr/bin/env python3
"""Explicit-target EFI deployment. Default is a plan; never formats or reboots."""
from pathlib import Path
import argparse, datetime, os, plistlib, shutil, subprocess, tempfile
from verify import ROOT, digest

def command(*args):return subprocess.check_output(args,text=True).strip()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',required=True);p.add_argument('--config',required=True)
    p.add_argument('--efi-device',required=True);p.add_argument('--expected-serial',required=True)
    p.add_argument('--expected-efi-uuid',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    bundle=Path(a.bundle).resolve();config=Path(a.config).resolve();local=(ROOT/'local').resolve()
    assert local in bundle.parents and local in config.parents
    assert (bundle/'assembly.json').exists()
    cfg=plistlib.loads(config.read_bytes());g=cfg['PlatformInfo']['Generic']
    assert g['SystemSerialNumber'] and g['MLB'] and any(g['ROM']) and g['SystemUUID']!='00000000-0000-0000-0000-000000000000'
    if not a.apply:
        print('PLAN ONLY: verify target serial/EFI UUID; back up EFI; copy BOOT and OC; preserve other OS directories; no reboot.')
        print('Run matching ocvalidate first. Append --apply only with current user authorization.');return
    assert os.geteuid()==0 and os.uname().sysname=='Linux'
    part=Path(a.efi_device).resolve(strict=True)
    assert command('blkid','-s','TYPE','-o','value',str(part)) in ['vfat','fat']
    assert command('blkid','-s','PARTUUID','-o','value',str(part)).lower()==a.expected_efi_uuid.lower()
    parent=Path('/dev')/command('lsblk','-ndo','PKNAME',str(part))
    assert command('lsblk','-ndo','SERIAL',str(parent))==a.expected_serial
    assert subprocess.run(['findmnt','-rn','--source',str(part)],capture_output=True).returncode==1,'Unmount target EFI first'
    assert subprocess.run(['pgrep','-f','qemu-system'],capture_output=True).returncode!=0,'Audit active QEMU disk use; do not automatically stop it'
    stamp=datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    backup=local/'backups'/stamp;backup.mkdir(parents=True,exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='hasee-efi-') as m:
        mount=Path(m);subprocess.run(['mount','-o','rw,nosuid,nodev,noexec',str(part),m],check=True)
        try:
            efi=mount/'EFI'
            if efi.exists():shutil.copytree(efi,backup/'EFI')
            for dirname in ['BOOT','OC']:
                src=bundle/'EFI'/dirname
                assert src.is_dir()
                for f in src.rglob('*'):
                    if not f.is_file():continue
                    dst=efi/dirname/f.relative_to(src);dst.parent.mkdir(parents=True,exist_ok=True)
                    pending=dst.with_name(dst.name+'.hasee-pending');shutil.copyfile(f,pending);os.replace(pending,dst)
                    assert digest(dst)==digest(f)
            dst=efi/'OC/config.plist';pending=dst.with_name('config.plist.hasee-pending')
            shutil.copyfile(config,pending);os.replace(pending,dst)
            subprocess.run(['sync'],check=True);assert digest(dst)==digest(config)
            for f in (backup/'EFI').rglob('*'):
                if f.is_file() and f.relative_to(backup/'EFI').parts[0] not in ['BOOT','OC']:
                    assert digest(efi/f.relative_to(backup/'EFI'))==digest(f)
        except Exception:
            print('Deployment failed; target is still mounted for orderly cleanup. Local backup:',backup)
            raise
        finally:subprocess.run(['umount',m],check=True)
    print('EFI files verified; other OS directories preserved. Backup is in local/backups/. Manual boot test pending.')

if __name__=='__main__':main()
