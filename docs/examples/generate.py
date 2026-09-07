"""Rebuild synthetic HTML examples without contacting any live system."""
from pathlib import Path
import sys
from html import escape
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'lib'))
from report_email import render_html
HERE = Path(__file__).resolve().parent
SCREENS = {
 'cli-report': ('Health report', '''$ sudo /opt/portable-backup/bin/pb report
server-a: OK; snapshot age 2.0h; pipeline success
server-b: CRITICAL; snapshot age 42.0h; pipeline failed
Capacity /var/lib/portable-backup: OK; 24.0% used
Capacity /mnt/backup-storage: ALERT; 85.0% used

$ echo $?
2'''),
 'cli-restore': ('Inspect and recover', '''# List available snapshots, then inspect the selected snapshot.
$ sudo /opt/portable-backup/bin/pb snapshots server-a
$ sudo /opt/portable-backup/bin/pb ls server-a --snapshot latest

# Restore into a NEW directory for review.
$ sudo /opt/portable-backup/bin/pb restore server-a \\
    --snapshot latest \\
    --target /var/tmp/recovery-review

# Recover just one subtree into another NEW directory.
$ sudo /opt/portable-backup/bin/pb restore server-a \\
    --snapshot latest \\
    --target /var/tmp/recovery-subset \\
    --include '/filesystem/srv/**' '''),
 'cli-operations': ('Routine operations', '''# Preview retention before changing stored history.
$ sudo /opt/portable-backup/bin/pb retention-preview server-a

# Run the full backup, retention and integrity-check pipeline.
$ sudo /opt/portable-backup/bin/pb run server-a
Backup complete

# Read all repository data during a scheduled verification window.
$ sudo /opt/portable-backup/bin/pb check server-a --read-data

# Request an email report using the configured mail service.
$ sudo /opt/portable-backup/bin/pb report --email''')
}
for name, (title, transcript) in SCREENS.items():
 (HERE / (name + '.txt')).write_text('ILLUSTRATIVE EXAMPLE — synthetic data; abbreviated output.\n\n' + transcript + '\n')
 (HERE / (name + '.html')).write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>''' + escape(title) + '''</title><body style="margin:0;padding:32px;background:#e2e8f0;font-family:Arial,sans-serif;"><div style="max-width:1000px;margin:auto;"><p style="font-size:12px;letter-spacing:2px;color:#475569;font-weight:bold;">PORTABLE BACKUP · EXAMPLE</p><h1 style="color:#0f172a;font-size:28px;">''' + escape(title) + '''</h1><div style="border-radius:12px;overflow:hidden;background:#0f172a;"><div style="padding:14px 20px;background:#1e293b;color:#cbd5e1;font-size:13px;">Terminal · synthetic demonstration</div><pre style="padding:24px;margin:0;color:#e2e8f0;font:15px/1.8 Menlo,Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;">''' + escape(transcript) + '''</pre></div><p style="font-size:13px;color:#475569;">Illustrative commands and abbreviated output. No live host data is shown.</p></div></body></html>''')
lines = [
 'server-a: OK; snapshot age 2.0h; pipeline success',
 'server-b: CRITICAL; snapshot age 42.0h; pipeline failed',
 'Capacity /var/lib/portable-backup: OK; 24.0% used',
 'Capacity /mnt/backup-storage: ALERT; 85.0% used',
]
(HERE / 'email-report.html').write_text(render_html(2, lines))
print('Generated synthetic CLI pages and actual HTML email-template example')
