"""Exercise the real Git ignore engine only in a temporary disposable repository."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class IgnoreTests(unittest.TestCase):
    def test_personal_library_is_excluded_and_shared_files_are_visible(self):
        git = shutil.which('git')
        if not git: self.skipTest('Git unavailable')
        with tempfile.TemporaryDirectory(prefix='vsuno-ignore-test-') as tmp:
            folder = Path(tmp)
            shutil.copyfile(ROOT/'.gitignore',folder/'.gitignore')
            subprocess.run([git,'-C',str(folder),'init','--quiet'],check=True,capture_output=True)
            for relative in ['personal/references/example.json','personal/tracks/example.json','personal/feedback/example.json','prompts/example.txt','work/report.json','.vsuno-stage.txt']:
                result = subprocess.run([git,'-C',str(folder),'check-ignore','--no-index','-q','--',relative],capture_output=True)
                self.assertEqual(result.returncode,0,relative)
            for relative in ['SKILL.md','references/STYLES_lib.md','tools/suno-fill.user.js','vsuno.cmd']:
                result = subprocess.run([git,'-C',str(folder),'check-ignore','--no-index','-q','--',relative],capture_output=True)
                self.assertEqual(result.returncode,1,relative)

if __name__ == '__main__': unittest.main()
