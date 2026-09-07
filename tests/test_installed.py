"""Exercise original functions and dispatch with harmless local command doubles."""
import hashlib,json,os,pathlib,subprocess,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
CODE=(ROOT/'bin/backup').read_text()
FUNCTIONS=CODE[CODE.index('usage() {'):CODE.index('cmd="${1:-}"')]
DISPATCH=CODE[CODE.index('cmd="${1:-}"'):]
STUBS='''
set -euo pipefail
require_programs() { :; }
rb_die() { echo "ERROR: $*" >&2; exit 1; }
rb_log() { echo "$*"; }
rb_load_host() { HOST_NAME="$1"; MODE=local; RESTIC_REPOSITORY=/example/repository; RESTIC_PASSWORD_FILE=/example/password; KEEP_DAILY=5; KEEP_WEEKLY=2; KEEP_MONTHLY=3; MAX_AGE_HOURS=30; }
rb_require_repo() { :; }
rb_lock() { :; }
restic() { printf 'restic'; printf ' <%s>' "$@"; printf '\\n'; }
RESTIC_CHECK_SUBSET=5%
GLOBAL=/etc/portable-backup/global.conf
'''
def shell(text,*args):
 return subprocess.run(['bash','-c',text,'fixture',*args],capture_output=True,text=True)
class InstalledTests(unittest.TestCase):
 def test_parity_hashes(self):
  for entry in json.loads((ROOT/'docs/SOURCE-PARITY.json').read_text()):
   self.assertEqual(hashlib.sha256((ROOT/entry['file']).read_bytes()).hexdigest(),entry['sha256'],entry['file'])
 def test_syntax(self):
  files=[ROOT/'bin/backup',ROOT/'bin/rb-prepare-local',ROOT/'lib/common.sh',ROOT/'install.sh',*list((ROOT/'source').glob('*.sh')),*list((ROOT/'config').rglob('*.conf')),ROOT/'source/config/source-backup.conf']
  for f in files:self.assertEqual(subprocess.run(['bash','-n',f]).returncode,0,str(f))
 def test_usage_parity(self):
  p=shell(STUBS+FUNCTIONS+'usage')
  self.assertEqual(p.returncode,0,p.stderr)
  for cmd in ['init','run','status','snapshots','verify','health','restore','mount','unlock','report']:
   self.assertIn('backup '+cmd,p.stdout)
  for option in ['--confirm-init','--email-on-critical','--email']:self.assertIn(option,p.stdout)
  self.assertIn('server-a|server-b',p.stdout)
 def test_verify_subset(self):
  p=shell(STUBS+FUNCTIONS+DISPATCH,'verify','server-a');self.assertEqual(p.returncode,0,p.stderr);self.assertIn('<check> <--read-data-subset=5%>',p.stdout)
 def test_status_alias(self):
  for name in ['status','snapshots']:
   p=shell(STUBS+FUNCTIONS+DISPATCH,name,'server-a');self.assertEqual(p.returncode,0);self.assertIn('<snapshots> <--host> <server-a> <--tag> <portable-backup>',p.stdout)
 def test_init_confirmation_flag(self):
  p=shell(STUBS+FUNCTIONS+DISPATCH,'init','server-a');self.assertEqual(p.returncode,1);self.assertIn('--confirm-init',p.stderr);self.assertNotIn('restic <init>',p.stdout)
 def test_explicit_restore_target(self):
  with tempfile.TemporaryDirectory() as t:
   p=shell(STUBS+FUNCTIONS+DISPATCH,'restore','server-a','latest',t);self.assertEqual(p.returncode,0,p.stderr);self.assertIn('<restore> <latest> <--host> <server-a> <--target>',p.stdout)
 def test_missing_restore_target(self):
  p=shell(STUBS+FUNCTIONS+DISPATCH,'restore','server-a','/example/target');self.assertNotEqual(p.returncode,0);self.assertIn('target directory is required',p.stderr)
 def test_local_exit24(self):
  code=(ROOT/'bin/rb-prepare-local').read_text();function=code[code.index('run_rsync_live_copy()'):code.index('copy_one(){')]
  for rc in [0,24,23,12]:
   p=shell(STUBS+function+f'rsync() {{ return {rc}; }}\nrun_rsync_live_copy example')
   self.assertEqual(p.returncode,0 if rc in [0,24] else rc)
 def test_strict_remote_retained(self):
  text=(ROOT/'source/source-backup-prepare.sh').read_text();self.assertNotIn('run_rsync_live_copy',text);self.assertIn('rsync -aHAX',text)
 def test_mail_headers(self):
  p=shell(STUBS+FUNCTIONS+"validate_mail_header REPORT_EMAIL $'bad\\nBcc: bad'");self.assertNotEqual(p.returncode,0)
 def test_email_original_layout(self):
  with tempfile.TemporaryDirectory() as t:
   f=pathlib.Path(t)/'report';f.write_text('Synthetic <unsafe> & report\n')
   code=STUBS+FUNCTIONS+'''
sendmail() { cat; }
hostname() { echo coordinator.example.invalid; }
date() { echo EXAMPLE; }
REPORT_EMAIL=operator@example.invalid
REPORT_FROM=backup@coordinator.example.invalid
REPORT_SUBJECT_PREFIX='[Portable Backup Report]'
REPORT_STORAGE_PERCENT=85
REPORT_STORAGE_AVAILABLE=example
REPORT_STORAGE_STATUS=ALERT
send_report_email "$1" ALERT
'''
   p=shell(code,str(f));self.assertEqual(p.returncode,0,p.stderr)
   self.assertIn('Content-Type: multipart/alternative',p.stdout);self.assertIn('Content-Type: text/html',p.stdout)
   self.assertIn('width:85%',p.stdout);self.assertIn('&lt;unsafe&gt; &amp;',p.stdout)
   self.assertIn('From: backup@coordinator.example.invalid',p.stdout)
 def test_email_policy(self):
  for status,mode,sent in [('OK','--email',True),('OK','--email-on-critical',False),('ALERT','--email-on-critical',False),('CRITICAL','--email-on-critical',True)]:
   overrides=f'''\ngenerate_report() {{ REPORT_OVERALL_STATUS={status}; echo synthetic; return 0; }}\nsend_report_email() {{ echo SENT; }}\n'''
   p=shell(STUBS+FUNCTIONS+overrides+DISPATCH,'report',mode);self.assertEqual('SENT' in p.stdout,sent,p.stderr)
 def test_retention_and_pipeline_order(self):
  run=DISPATCH[DISPATCH.index('run)'):DISPATCH.index('status|snapshots)')]
  parts=['sha256sum -c SHA256SUMS','restic backup','restic forget','--keep-daily "$KEEP_DAILY"','--keep-weekly "$KEEP_WEEKLY"','--keep-monthly "$KEEP_MONTHLY"','--prune','restic check','--read-data-subset="$RESTIC_CHECK_SUBSET"']
  positions=[run.index(p) for p in parts];self.assertEqual(positions,sorted(positions))

class InteractiveTests(unittest.TestCase):
 def test_original_menu_cancel(self):
  import pty,select,time
  pid,fd=pty.fork()
  if pid==0:os.execlp('bash','bash','-c',STUBS+FUNCTIONS+'interactive_restore')
  output=b'';sent=False;deadline=time.monotonic()+5
  try:
   while time.monotonic()<deadline:
    if select.select([fd],[],[],0.1)[0]:
     try:chunk=os.read(fd,4096)
     except OSError:break
     if not chunk:break
     output+=chunk
     if b'Selection:' in output and not sent:os.write(fd,b'q\n');sent=True
   if not sent:os.kill(pid,9)
   _,status=os.waitpid(pid,0)
  finally:os.close(fd)
  self.assertEqual(os.waitstatus_to_exitcode(status),0,output)
  for text in [b'INTERACTIVE RESTORE ASSISTANT',b'1) server-a',b'2) server-b',b'Restore cancelled.']:self.assertIn(text,output)

class CacheTests(unittest.TestCase):
 def test_original_cache_defaults(self):
  code=(ROOT/'lib/common.sh').read_text().rsplit('load_global_config',1)[0]
  result=shell('HOME=""; XDG_CACHE_HOME="";\n'+code+'\nprintf "%s|%s" "$HOME" "$XDG_CACHE_HOME"')
  self.assertEqual(result.returncode,0,result.stderr)
  self.assertEqual(result.stdout,'/root|/root/.cache')

if __name__=='__main__':unittest.main()
