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
        self.assertNotIn("All Rights Reserved", p)              # footer wording replaced by the CC BY + trademark statement
        self.assertIn("Licensed under CC BY 4.0", p)
        self.assertIn("unregistered trademarks", p)
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
    def test_canonical_and_merged_pages(self):
        import json
        src = Path(__file__).resolve().parent.parent / "aeternal_local_fix.py"
        ns = {}; exec(compile(src.read_text(encoding="utf-8").replace('if __name__ == "__main__":\n    main()', ""), "x", "exec"), ns)
        rel, url = next(iter(ns["CANON"].items()))
        f = self.r / rel; f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("<html><head>\n  <title>t</title>\n</head><body></body></html>", encoding="utf-8")
        run(self.r, "--apply")
        self.assertIn(f'<link rel="canonical" href="{url}">', f.read_text(encoding="utf-8"))
        self.assertIn("0 changed", run(self.r, "--apply"))
        old, new = next(iter(ns["MERGED"].items()))
        idx = self.r / "comparison" / "index.html"; idx.parent.mkdir(exist_ok=True)
        idx.write_text(f'<a href="{old}.html">English</a>', encoding="utf-8")
        run(self.r, "--apply")
        self.assertEqual(idx.read_text(encoding="utf-8"), f'<a href="{new}.html">English</a>')

    def test_sync_root_files(self):
        (self.r / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
        run(self.r, "--apply")                                   # without the flag robots.txt is left alone
        self.assertIn("Disallow: /", (self.r / "robots.txt").read_text(encoding="utf-8"))
        run(self.r, "--apply", "--sync-root-files")
        self.assertIn("Sitemap:", (self.r / "robots.txt").read_text(encoding="utf-8"))
        self.assertTrue((self.r / "_redirects").exists() and (self.r / "sitemap.xml").exists())
        self.assertNotIn("differs", run(self.r, "--sync-root-files"))

if __name__ == "__main__":
    unittest.main()
