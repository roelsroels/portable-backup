from test_core import pb
from pathlib import Path
from unittest.mock import Mock,patch
import tempfile,unittest,subprocess,json
class PipelineTests(unittest.TestCase):
 def exercise(self,tarcode=0,sourcecode=0,restic_fail=None):
  with tempfile.TemporaryDirectory() as t:
   proc=Mock();proc.wait.return_value=sourcecode;ctx=Mock();ctx.__enter__=Mock(return_value=proc);ctx.__exit__=Mock(return_value=False)
   calls=[]
   def restic(c,*args,**kw):
    calls.append((args,kw))
    if args[0]==restic_fail:raise subprocess.CalledProcessError(3,args)
   with patch.object(pb,'STATE',Path(t)),patch.object(pb.subprocess,'Popen',return_value=ctx),patch.object(pb.subprocess,'run',return_value=Mock(returncode=tarcode)),patch.object(pb,'verify'),patch.object(pb,'restic',side_effect=restic):
    if tarcode or sourcecode or restic_fail:
     with self.assertRaises((ValueError,subprocess.CalledProcessError)):pb.backup('server-a',{'mode':'local'})
    else:pb.backup('server-a',{'mode':'local'})
   return calls,json.loads((Path(t)/'server-a.status.json').read_text())
 def test_success_order_and_relative_paths(self):
  calls,status=self.exercise();self.assertEqual([x[0][0] for x in calls],['backup','forget','check']);self.assertEqual(status['result'],'success')
  self.assertEqual(calls[0][0][-5:],('filesystem','exports','metadata','docker-volumes','manifest.json'))
 def test_tar24_is_fatal(self):
  calls,status=self.exercise(tarcode=24);self.assertEqual(calls,[]);self.assertEqual(status['result'],'failed')
 def test_source_error_is_fatal(self):
  calls,status=self.exercise(sourcecode=24);self.assertEqual(calls,[]);self.assertEqual(status['result'],'failed')
 def test_partial_restic_skips_retention(self):
  calls,status=self.exercise(restic_fail='backup');self.assertEqual(len(calls),1);self.assertEqual(status['result'],'failed')
 def test_prune_failure_is_failed_pipeline(self):
  calls,status=self.exercise(restic_fail='forget');self.assertEqual(len(calls),2);self.assertEqual(status['result'],'failed')
