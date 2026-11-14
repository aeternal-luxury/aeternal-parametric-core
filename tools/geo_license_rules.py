"""Three-tier licence architecture (owner decision, 2026-11-13). Shared by the repo tool and the local tool.

  code / scripts ........ MIT                       (LICENSE; scope listed in NOTICE.md)
  documentation, research, whitepapers, page content ... CC BY 4.0   (LICENSE-DOCS.md)
  core engine & private assets .. All Rights Reserved (proprietary; not in this repository)
  brand identifiers ..... TRADEMARKS.md
Footer wording replaces the non-standard "All (Autonomous|Sovereign) Rights Reserved."
"""
import re

TM = "AETERNAL, ÆTERNAL, The Axiom, The Singularity and PGEF are unregistered trademarks of AETERNAL Luxury (see TRADEMARKS.md)."
FOOTER = "Licensed under CC BY 4.0. " + TM

RX = [
 ("footer: rights reserved -> CC BY + trademark", re.compile(r"All (?:Autonomous |Sovereign )?Rights Reserved\."), FOOTER),
]
PLAIN = [
 # statements that conflict with CC BY (commercial use allowed); repo wording and the live-site wording
 ("Full governance rights and commercial use of the framework are retained exclusively by AETERNAL Luxury.",
  "Commercial use and adaptation are permitted under the licence terms, with attribution."),
 ("AETERNAL Luxury retains full governance rights and commercial use of the framework.",
  "Commercial use and adaptation are permitted under the licence terms, with attribution."),
 # a page that still carries the interim (2026-11-13) NC-ND wording
 ("Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)", "Creative Commons Attribution 4.0 International (CC BY 4.0)"),
 ("https://creativecommons.org/licenses/by-nc-nd/4.0/", "https://creativecommons.org/licenses/by/4.0/"),
 ("CC BY-NC-ND 4.0", "CC BY 4.0"),
 ("are brand identifiers of AETERNAL Luxury (see TRADEMARKS.md).", "are unregistered trademarks of AETERNAL Luxury (see TRADEMARKS.md)."),
]
