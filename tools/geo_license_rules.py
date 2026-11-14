"""Three-tier licence architecture (owner decision, 2026-11-13). Shared by the repo tool and the local tool.

  code / scripts ........ MIT                       (LICENSE; scope listed in NOTICE.md)
  documentation, research, whitepapers, page content ... CC BY-NC-ND 4.0   (LICENSE-DOCS.md)
  core engine & private assets .. All Rights Reserved (proprietary; not in this repository)
  brand identifiers ..... TRADEMARKS.md
Footer wording replaces the non-standard "All (Autonomous|Sovereign) Rights Reserved."
"""
import re

TM = "AETERNAL, ÆTERNAL, The Axiom, The Singularity and PGEF are brand identifiers of AETERNAL Luxury (see TRADEMARKS.md)."
FOOTER = "Licensed under CC BY-NC-ND 4.0. " + TM

RX = [
 ("footer: rights reserved -> CC BY-NC-ND + trademark", re.compile(r"All (?:Autonomous |Sovereign )?Rights Reserved\."), FOOTER),
]
PLAIN = [
 ("https://creativecommons.org/licenses/by/4.0/", "https://creativecommons.org/licenses/by-nc-nd/4.0/"),
 ("Creative Commons Attribution 4.0 International (CC BY 4.0)", "Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)"),
 ("Full governance rights and commercial use of the framework are retained exclusively by AETERNAL Luxury.",
  "Commercial use and derivative works require prior written permission from AETERNAL Luxury."),
]
