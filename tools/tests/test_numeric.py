import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from geo_numeric_lib import annotate

CASES = {
 "en_first": ("The collar keeps 99.8% adherence to the neck.", "The collar keeps 99.8% (design target) adherence to the neck."),
 "zh_first": ("領子保持 99.8% 的貼合度。", "領子保持 99.8%（設計目標） 的貼合度。"),
 "within3": ("The garment deformation stays within 3% over a 12-hour wear period.", "The garment deformation stays within 3% (design target) over a 12-hour wear period."),
 "below025": ("Shoulder displacement is below 0.25 mm.", "Shoulder displacement is below 0.25 mm (design target)."),
 "already_en": ("The collar keeps 99.8% (design target) adherence.", "The collar keeps 99.8% (design target) adherence."),
 "already_zh": ("領子保持 99.8%（設計目標） 的貼合度。", "領子保持 99.8%（設計目標） 的貼合度。"),
 "dup_en": ("The collar keeps 99.8% (design target) (design target) adherence.", "The collar keeps 99.8% (design target) adherence."),
 "dup_mixed": ("領子 99.8%（設計目標） (design target) 貼合", "領子 99.8%（設計目標） 貼合"),
 "redundant": ("The design goal is to keep deformation within 3% (design target) over wear.", "The design goal is to keep deformation within 3% over wear."),
 "math_untouched": ("Let adherence $A \\ge 99.8$ hold for the collar fit in 99.8% of samples.", None),
 "non_perf": ("The brand has 99.8% name recognition in the survey.", None),
}

class T(unittest.TestCase):
    def test_cases(self):
        for k, (src, want) in CASES.items():
            with self.subTest(k):
                self.assertEqual(annotate(src), src if want is None else want)
    def test_idempotent(self):
        for k, (src, _) in CASES.items():
            with self.subTest(k):
                once = annotate(src); self.assertEqual(annotate(once), once)
    def test_en_zh_consistent(self):
        self.assertIn("(design target)", annotate("collar adherence 99.9% over wear"))
        self.assertIn("（設計目標）", annotate("領口貼合 99.9% 穿著"))
if __name__ == "__main__":
    unittest.main()
