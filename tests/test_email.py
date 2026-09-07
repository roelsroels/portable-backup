import unittest
from email import policy
from email.parser import BytesParser
from report_email import build_message, render_html
class EmailTests(unittest.TestCase):
 def test_html_mime(self):
  msg=BytesParser(policy=policy.default).parsebytes(build_message('operator@example.invalid',1,['Capacity /backup: ALERT; 85.0% used']))
  self.assertEqual(msg.get_content_type(),'multipart/alternative')
  self.assertEqual(msg.get_body().get_content_type(),'text/html')
  self.assertIn('85.0%',msg.get_body().get_content())
  self.assertEqual(len(list(msg.iter_parts())),2)
 def test_escape_runtime_data(self):
  html=render_html(2,['server-a: CRITICAL; <script>alert("x")</script> & failure'])
  self.assertNotIn('<script>',html);self.assertIn('&lt;script&gt;',html);self.assertIn('&amp;',html)
 def test_reject_header_injection(self):
  with self.assertRaises(ValueError):build_message('operator@example.invalid\nBcc: injected@example.invalid',0,[])
 def test_all_statuses(self):
  for i,status in enumerate(('OK','ALERT','CRITICAL')):
   self.assertIn(status,render_html(i,[f'server-a: {status}']))
