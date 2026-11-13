import subprocess, sys, tempfile, unittest
from pathlib import Path
TOOL = Path(__file__).resolve().parent.parent / "aeternal_local_fix.py"

def run(root, *a):
    return subprocess.run([sys.executable, str(TOOL), str(root), *a], capture_output=True, text=True).stdout

class LocalTool(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); r = Path(self.d.name) / "site"
        (r / "answers").mkdir(parents=True); (r / "evidence").mkdir(); (r / "whitepapers").mkdir()
        self.page = r / "answers" / "p.html"; self.wp = r / "whitepapers" / "w.html"; self.ev = r / "evidence" / "e.html"
        self.page.write_text("<p>The collar keeps 99.8% adherence. We absolutely stay autonomously calm. AETERNAL guarantees structural stability. All Rights Reserved.</p>", encoding="utf-8")
        self.wp.write_text("<p>The collar keeps 99.8% adherence.</p>", encoding="utf-8")
        self.ev.write_text("<p>EMPIRICAL_PROOF</p>", encoding="utf-8")
        self.r = r
    def tearDown(self): self.d.cleanup()
    def test_scope_idempotency_and_untouched_wording(self):
        run(self.r, "--apply")
        p = self.page.read_text(encoding="utf-8")
        self.assertIn("99.8% (design target)", p)
        self.assertIn("autonomously", p)                       # style wording is NOT swept by default
        self.assertIn("All Rights Reserved", p)                 # licence wording is never touched
        self.assertNotIn("guarantees structural", p)            # guarantee-type claim IS corrected
        self.assertNotIn("design target", self.wp.read_text(encoding="utf-8"))   # review-only folder: no numeric rule
        self.assertIn("ENGINEERING_SCENARIO", self.ev.read_text(encoding="utf-8"))
        snap = {f: f.read_text(encoding="utf-8") for f in (self.page, self.wp, self.ev)}
        out = run(self.r, "--apply")
        self.assertIn("0 changed", out)
        self.assertEqual(snap, {f: f.read_text(encoding="utf-8") for f in snap})
    def test_wide_flag_applies_pr2_lexicon(self):
        run(self.r, "--apply", "--with-pr2-lexicon")
        self.assertNotIn("autonomously", self.page.read_text(encoding="utf-8"))
if __name__ == "__main__":
    unittest.main()
