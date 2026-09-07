import importlib.machinery, importlib.util, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch, Mock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lib'))
import core
def module(name,path):
 loader=importlib.machinery.SourceFileLoader(name,str(path));spec=importlib.util.spec_from_loader(name,loader)
 m=importlib.util.module_from_spec(spec);loader.exec_module(m);return m
pb=module('pb_cli',ROOT/'bin/pb');source=module('pb_source',ROOT/'bin/pb-source')
class Tests(unittest.TestCase):
 def test_live_copy(self):
  for code in (0,24):
   with patch('core.subprocess.run',return_value=Mock(returncode=code)):core.live_copy([])
  for code in (1,12,23,25,30,255):
   with patch('core.subprocess.run',return_value=Mock(returncode=code)):
    with self.assertRaises(subprocess.CalledProcessError):core.live_copy([])
 def test_cache(self):
  with tempfile.TemporaryDirectory() as t,patch.dict(os.environ,{'HOME':'','XDG_CACHE_HOME':t},clear=True),patch('core.run') as run:
   for command in ('backup','snapshots','restore','check','unlock','forget'):
    core.restic({'repository':'example','password_file':'/example'},command)
    self.assertEqual(run.call_args.kwargs['env']['HOME'],'/root')
    self.assertEqual(run.call_args.kwargs['env']['XDG_CACHE_HOME'],t)
 def test_retention(self):
  for value in ({},{'daily':0},{'daily':-1},{'unknown':2},{'daily':True},{'daily':'5'}):
   with self.assertRaises(ValueError):core.retention({'retention':value})
  self.assertEqual(core.retention({'retention':{'last':5}}),['--keep-last','5'])
 def test_alias(self):
  for name in ('../x','/etc','-host','A','a/b','a'*49):
   with self.assertRaises(ValueError):core.load(name)
 def test_mount(self):
  with patch('core.os.path.ismount',return_value=False):
   with self.assertRaises(ValueError):core.env({'required_mount':'/missing'})
 def test_manifest(self):
  import hashlib
  with tempfile.TemporaryDirectory() as t:
   stage=Path(t);(stage/'data').write_bytes(b'synthetic');(stage/'manifest.json').write_text(json.dumps({'data':hashlib.sha256(b'synthetic').hexdigest()}));pb.verify(stage)
   (stage/'data').write_bytes(b'changed')
   with self.assertRaises(ValueError):pb.verify(stage)
   (stage/'manifest.json').write_text(json.dumps({'../outside':'bad'}))
   with self.assertRaises(ValueError):pb.verify(stage)
 def test_lock(self):
  with tempfile.TemporaryDirectory() as t,patch.object(core,'STATE',Path(t)):
   with core.lock('test'):
    with self.assertRaises(BlockingIOError):
     with core.lock('test'):pass
 def test_failed_transfer(self):
  with tempfile.TemporaryDirectory() as t,patch.object(pb,'STATE',Path(t)),patch.object(pb.subprocess,'Popen',side_effect=OSError('synthetic failure')),patch.object(pb,'restic') as restic:
   with self.assertRaises(OSError):pb.backup('server-a',{'mode':'local'})
   restic.assert_not_called();self.assertEqual(json.loads((Path(t)/'server-a.status.json').read_text())['result'],'failed')
 def test_missing_source(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaises(ValueError):source.prepare(Path(t),{'include':['/nonexistent-synthetic-source']})
 def test_report_missing_state(self):
  import datetime
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);(d/'hosts').mkdir();(d/'hosts/server-a.json').write_text('{}');(d/'report.json').write_text('{"weekly_day": -1}')
   result=Mock(stdout=json.dumps([{'time':datetime.datetime.now(datetime.timezone.utc).isoformat()}]))
   with patch.object(pb,'CONFIG',d),patch.object(pb,'STATE',d),patch.object(pb,'load',return_value={}),patch.object(pb,'restic',return_value=result):self.assertEqual(pb.report(False),2)
 def test_restore_target(self):
  with tempfile.TemporaryDirectory() as t,patch.object(core,'STATE',Path(t)),patch.object(pb,'load',return_value={}),patch.object(pb.os,'geteuid',return_value=0),patch.object(sys,'argv',['pb','restore','server-a','--target',t]):
   with self.assertRaises(ValueError):pb.main()
if __name__=='__main__':unittest.main()
