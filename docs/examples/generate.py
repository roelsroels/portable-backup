"""Render examples through the actual installed command functions, with synthetic inputs."""
from pathlib import Path
import sys, tempfile
from html import escape
from email import policy
from email.parser import Parser
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tests'))
from test_installed import FUNCTIONS,STUBS,shell
usage=shell(STUBS+FUNCTIONS+'usage').stdout
report_fixture=r'''
hostname() { echo coordinator.example.invalid; }
date() { echo 'EXAMPLE-TIME'; }
mountpoint() { return 0; }
df() { printf 'Filesystem Size Used Available Use%% Mounted\nexample 1T 850G 150G 85%% /mnt/backup-storage\n'; }
report_host() {
cat <<REPORT
Status             : OK
Restic host        : $1
Repository         : /mnt/backup-storage/backups/restic/$1
Repository usage   : <example-size>
Snapshots stored   : <example-count>
Latest snapshot    : <snapshot-id>
Latest timestamp   : <snapshot-time>
Latest age         : 2h
Latest data size   : <example-size>
Maximum age        : 30h

Timer
  Unit             : portable-backup-$1.timer
  Active           : active
  Enabled          : enabled
  Next run         : <next-run>

Last service
  Unit             : portable-backup@$1.service
  Result           : success
  Exit status      : 0
  Finished         : <finished-time>
REPORT
}
sendmail() { cat; }
REPORT_EMAIL=operator@example.invalid
REPORT_FROM=backup@coordinator.example.invalid
REPORT_SUBJECT_PREFIX='[Portable Backup Report]'
'''
with tempfile.TemporaryDirectory() as t:
 f=Path(t)/'report'
 p=shell(STUBS+FUNCTIONS+report_fixture+'\ngenerate_report > "$1" || :\nsend_report_email "$1" "$REPORT_OVERALL_STATUS"',str(f))
 if p.returncode:raise RuntimeError(p.stderr)
 report=f.read_text()
 message=Parser(policy=policy.default).parsestr(p.stdout)
 (HERE/'email-report.html').write_text(message.get_body(preferencelist=('html',)).get_content())
 (HERE/'cli-report.txt').write_text('$ sudo backup report\n'+report)
# The original menu labels are taken directly from the shipped function.
menu='\n'.join(['$ sudo backup restore','', '===========================================','        INTERACTIVE RESTORE ASSISTANT','===========================================','','Select the backup host:','','  1) server-a','  2) server-b','  q) Cancel','','Selection: q','Restore cancelled.'])
for label in ['1) server-a','2) server-b','Restore cancelled.']:
 assert label in FUNCTIONS
screens={
 'cli-usage':('Command overview','$ sudo backup\n'+usage),
 'cli-restore':('Interactive restore',menu),
 'cli-report':('Backup report','$ sudo backup report\n'+report),
}
for name,(title,text) in screens.items():
 (HERE/(name+'.txt')).write_text(text+'\n')
 (HERE/(name+'.html')).write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>'''+escape(title)+'''</title><body style="margin:0;padding:28px;background:#e2e8f0;font-family:Arial,sans-serif;"><div style="max-width:1024px;margin:auto;"><p style="font-size:12px;letter-spacing:2px;color:#475569;font-weight:bold;">PORTABLE BACKUP · SYNTHETIC EXAMPLE</p><h1 style="color:#0f172a;font-size:26px;">'''+escape(title)+'''</h1><div style="border-radius:12px;overflow:hidden;background:#0f172a;"><div style="padding:14px 20px;background:#1e293b;color:#cbd5e1;font-size:13px;">Original Bash command · anonymized demonstration</div><pre style="padding:22px;margin:0;color:#e2e8f0;font:14px/1.6 Menlo,Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;">'''+escape(text)+'''</pre></div><p style="font-size:12px;color:#475569;">Synthetic placeholders; no live repository, timestamps or server data shown.</p></div></body></html>''')
print('Original usage/report/HTML renderer examples generated')
