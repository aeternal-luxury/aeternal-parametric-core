#!/usr/bin/env python3
"""Align licence wording with the repository's MIT LICENSE.

Replaces "All (Autonomous|Sovereign)? Rights Reserved" footers, the CC BY 4.0 / "retained
exclusively" paragraph, the JSON-LD licence URL, the README licence section and the
robots.txt comment block. Exact substrings only; dry-run by default.
Usage: python3 tools/geo_license_wording.py [--apply]
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTS = {".html", ".md", ".txt", ".yaml", ".json"}
MIT = "Released under the MIT License"
RX = [(re.compile(r"All (?:Autonomous |Sovereign )?Rights Reserved\.", re.I), MIT + ".")]
PLAIN = [
 ("This specification is published for reference purposes under\n            <a href=\"https://creativecommons.org/licenses/by/4.0/\" target=\"_blank\" rel=\"license\">Creative Commons Attribution 4.0 International (CC BY 4.0)</a>.\n            Full governance rights and commercial use of the framework are retained exclusively by AETERNAL Luxury.",
  "This specification is released under the\n            <a href=\"https://opensource.org/licenses/MIT\" target=\"_blank\" rel=\"license\">MIT License</a> (see LICENSE in the repository)."),
 ('"license": "https://creativecommons.org/licenses/by/4.0/"', '"license": "https://opensource.org/licenses/MIT"'),
 ("Proprietary Specification v1.5", "Specification v1.5"),
 ("PROPRIETARY SPECIFICATION v1.5", "SPECIFICATION v1.5"),
 ("is a proprietary methodology of", "is a methodology developed by"),
 ("See the repository license for permitted use of the public reference implementation and associated documentation.",
  "Released under the MIT License. See [LICENSE](LICENSE)."),
 ("# - Licensing terms: see the LICENSE file in the repository\n# - Crawling and indexing for search and retrieval (with attribution) is welcome\n# - robots.txt is advisory and cannot restrict how fetched content is later used;\n#   use of this content for model training or redistribution is governed by its\n#   license, and licensing enquiries go through the official channel below\n",
  "# - Content is released under the MIT License (see LICENSE in the repository)\n# - All crawlers are welcome, including search, AI retrieval and AI training crawlers\n"),
]

def main():
    apply, changed = "--apply" in sys.argv, 0
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    for f in out.split("\0"):
        if not f or f == "LICENSE" or (Path(f).suffix not in EXTS and f != "robots.txt") or f.startswith("tools/"):
            continue
        p = ROOT / f
        try: t = p.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        o = t
        for old, new in PLAIN: t = t.replace(old, new)
        for rx, new in RX: t = rx.sub(new, t)
        if t != o:
            if f.endswith(".json"):
                json.loads(t)
            changed += 1
            if apply: p.write_text(t, encoding="utf-8")
    print(f"{changed} file(s) {'written' if apply else 'would change (dry-run)'}")

if __name__ == "__main__":
    main()
