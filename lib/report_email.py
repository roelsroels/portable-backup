"""HTML email rendering with escaped runtime data and a compatibility text part."""
from email.message import EmailMessage
from email.policy import SMTP
from html import escape
from pathlib import Path
from string import Template

TEMPLATE = Path(__file__).resolve().parents[1] / 'templates' / 'report.html'
COLORS = {'OK': ('#dcfce7', '#166534'), 'ALERT': ('#fef3c7', '#92400e'), 'CRITICAL': ('#fee2e2', '#991b1b')}

def render_html(severity, lines):
    status = ('OK', 'ALERT', 'CRITICAL')[severity]
    background, foreground = COLORS[status]
    rows = []
    for line in lines:
        label, separator, detail = line.partition(':')
        level = 'CRITICAL' if 'CRITICAL' in line else 'ALERT' if 'ALERT' in line else 'OK'
        bg, fg = COLORS[level]
        rows.append('<tr><td style="padding:16px 20px;border-bottom:1px solid #e2e8f0;vertical-align:top;">'
                    '<span style="display:inline-block;padding:4px 8px;border-radius:4px;font-size:11px;font-weight:bold;background:' + bg + ';color:' + fg + ';">' + level + '</span>'
                    '<div style="margin-top:8px;font-weight:bold;color:#0f172a;overflow-wrap:anywhere;">' + escape(label) + '</div>'
                    '<div style="margin-top:5px;font-size:14px;color:#475569;line-height:1.6;overflow-wrap:anywhere;">' + escape(detail.strip() if separator else line) + '</div></td></tr>')
    return Template(TEMPLATE.read_text()).substitute(status=status, background=background, foreground=foreground,
        summary=('All monitored backups are healthy.' if severity == 0 else 'Review the items below and check the backup journal.'), rows=''.join(rows))

def build_message(recipient, severity, lines):
    if '\n' in recipient or '\r' in recipient:
        raise ValueError('Invalid recipient')
    msg = EmailMessage(policy=SMTP)
    msg['To'] = recipient
    msg['Subject'] = 'Backup report: ' + ('OK', 'ALERT', 'CRITICAL')[severity]
    msg.set_content('\n'.join(lines) + '\n')
    msg.add_alternative(render_html(severity, lines), subtype='html')
    return msg.as_bytes()
