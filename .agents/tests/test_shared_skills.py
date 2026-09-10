"""Offline regression checks using exclusively synthetic fixtures."""
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / 'skills/operations/copilot-cowork-plugin/build_package.py'
VALIDATE = BUILD.with_name('validate_package.py')
RECALL = ROOT / 'skills/productivity/chat-recall/scripts/chat_recall.py'


def run(*args):
    return subprocess.run([sys.executable, *map(str,args)], capture_output=True, text=True)


class SharedSkills(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / 'example-skill'
        self.skill.mkdir()
        (self.skill/'SKILL.md').write_text('---\nname: example-skill\ndescription: Synthetic fixture\n---\n\nExample.\n')

    def build(self, *options):
        return run(BUILD, self.skill, '--out', self.root/'out', '--publisher', 'Example',
                   '--website', 'https://example.com', '--privacy', 'https://example.com/privacy',
                   '--terms', 'https://example.com/terms', *options)

    def test_package_is_valid_and_excludes_hidden_files(self):
        (self.skill/'.env').write_text('SYNTHETIC_PRIVATE_MARKER=hidden\n')
        (self.skill/'style.css').write_text('body { color: black; }')
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        archive = self.root/'out/example-skill-cowork.zip'
        with zipfile.ZipFile(archive) as z:
            self.assertIn('manifest.json', z.namelist())
            self.assertIn('skills/example-skill/style.md', z.namelist())
            self.assertNotIn('skills/example-skill/.env', z.namelist())
            self.assertFalse(any(b'SYNTHETIC_PRIVATE_MARKER' in z.read(n) for n in z.namelist()))
            m=json.loads(z.read('manifest.json'))
            self.assertEqual(m['developer']['name'],'Example')
        valid=run(VALIDATE,archive)
        self.assertEqual(valid.returncode,0,valid.stdout+valid.stderr)

    def test_symlink_cannot_import_an_external_file(self):
        external=self.root/'private.txt';external.write_text('synthetic private text')
        (self.skill/'linked.txt').symlink_to(external)
        result=self.build()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Symlinks',result.stderr)
        self.assertFalse((self.root/'out/example-skill-cowork.zip').exists())

    def test_excluded_directory_is_not_copied(self):
        private=self.skill/'excluded';private.mkdir()
        (private/'record.txt').write_text('SYNTHETIC_EXCLUDED_RECORD')
        result=self.build('--exclude','excluded')
        self.assertEqual(result.returncode,0,result.stderr)
        with zipfile.ZipFile(self.root/'out/example-skill-cowork.zip') as z:
            self.assertFalse(any('excluded' in n for n in z.namelist()))

    def test_manual_only_skill_requires_explicit_conversion(self):
        p=self.skill/'SKILL.md';p.write_text(p.read_text().replace('name: example-skill','disable-model-invocation: true\nname: example-skill'))
        result=self.build()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Manual-only',result.stderr)
        result=self.build('--allow-auto-invocation')
        self.assertEqual(result.returncode,0,result.stderr)

    def test_recall_ignores_tools_and_injected_context(self):
        codex=self.root/'codex';codex.mkdir()
        events=[
            {'type':'event_msg','payload':{'type':'user_message','message':'Discuss the synthetic lighthouse project.'}},
            {'type':'response_item','payload':{'role':'user','content':[{'type':'input_text','text':'tool-private-marker lighthouse'}]}},
            {'type':'event_msg','payload':{'type':'agent_message','message':'<environment_context>injected-private-marker</environment_context> lighthouse done'}}]
        transcript=codex/'example.jsonl';transcript.write_text('\n'.join(map(json.dumps,events)))
        result=run(RECALL,'--query','lighthouse','--platform','codex','--codex-root',codex,'--json')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(len(json.loads(result.stdout)['results']),1)
        self.assertNotIn('tool-private-marker',result.stdout)
        self.assertNotIn('injected-private-marker',result.stdout)

    def test_recall_rejects_out_of_scope_transcript(self):
        codex=self.root/'codex';codex.mkdir()
        external=self.root/'outside.jsonl';external.write_text('{}')
        result=run(RECALL,'--query','example','--platform','codex','--codex-root',codex,'--transcript',external)
        self.assertEqual(result.returncode,2)


if __name__=='__main__':
    unittest.main()
