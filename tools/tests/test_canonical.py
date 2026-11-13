import subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from canonical_check import html_canonicals

def canon(html):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
    return html_canonicals(Path(f.name))

class Parser(unittest.TestCase):
    def test_attribute_order_quotes_whitespace(self):
        for h in ('<link rel="canonical" href="https://x/a.html">', "<link href='https://x/a.html' rel='canonical'>",
                  '<LINK  REL = "canonical"\n  HREF="https://x/a.html" />', '<link rel="alternate canonical" href="https://x/a.html">'):
            self.assertEqual(canon(h), ["https://x/a.html"], h)
    def test_missing_and_other_links(self):
        self.assertEqual(canon('<link rel="stylesheet" href="a.css">'), [])

class Repo(unittest.TestCase):
    def run_tool(self, *a):
        return subprocess.run([sys.executable, str(ROOT / "tools/canonical_check.py"), *a], cwd=ROOT, capture_output=True, text=True)
    def test_html_md_consistency_and_uniqueness(self):      # exit 1 on any ERROR (mismatch, conflict, //)
        r = self.run_tool(); self.assertEqual(r.returncode, 0, r.stdout[-800:])
    def test_sync_is_idempotent(self):
        before = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
        self.run_tool("--sync")
        after = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
        self.assertEqual(before, after)
if __name__ == "__main__":
    unittest.main()
