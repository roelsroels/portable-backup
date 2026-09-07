"""Linux-only real Restic round trip; no root or production configuration used."""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
from test_core import core,pb
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);stage=root/'stage';stage.mkdir()
 for name in ('filesystem','exports','metadata','docker-volumes'):(stage/name).mkdir()
 data=stage/'filesystem'/'sample.txt';data.write_text('synthetic recovery fixture\n');data.chmod(0o640)
 (stage/'filesystem'/'link').symlink_to('sample.txt')
 (stage/'manifest.json').write_text(json.dumps({'filesystem/sample.txt':hashlib.sha256(data.read_bytes()).hexdigest()}))
 password=root/'password';password.write_text('disposable-test-password')
 c={'repository':str(root/'repository'),'password_file':str(password)}
 os.environ['XDG_CACHE_HOME']=str(root/'cache')
 core.restic(c,'init');pb.verify(stage)
 core.restic(c,'backup',*core.filters('server-a'),'--','filesystem','exports','metadata','docker-volumes','manifest.json',cwd=stage)
 core.restic(c,'forget',*core.filters('server-a'),*core.retention({'retention':{'last':1}}),'--prune')
 core.restic(c,'check','--read-data')
 core.restic(c,'restore','latest',*core.filters('server-a'),'--target',root/'restore')
 restored=root/'restore'/'filesystem'/'sample.txt'
 assert restored.read_bytes()==data.read_bytes()
 assert restored.stat().st_mode & 0o777 == 0o640
 assert (restored.parent/'link').is_symlink()
 print('Real Restic round trip passed')
