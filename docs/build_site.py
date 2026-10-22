"""Fills the coverage state/county lists into index.html from docs/coverage-data.json.

To update coverage: edit docs/coverage-sheet.json (state -> county list), run
  python3 -I docs/build_map.py docs/coverage-sheet.json <us-atlas dir> images-and-docs-out
then run this script:  python3 docs/build_site.py
"""
import html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.load(open(ROOT / "docs" / "coverage-data.json"))
NAMES = {"AL": "Alabama", "CT": "Connecticut", "DC": "Washington, DC", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
         "IL": "Illinois", "IN": "Indiana", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "MA": "Massachusetts",
         "MD": "Maryland", "MI": "Michigan", "MN": "Minnesota", "MO": "Missouri", "MS": "Mississippi", "NC": "North Carolina",
         "NH": "New Hampshire", "NJ": "New Jersey", "NY": "New York", "OH": "Ohio", "PA": "Pennsylvania", "SC": "South Carolina",
         "TN": "Tennessee", "TX": "Texas", "VA": "Virginia", "WI": "Wisconsin"}
LA_PARISH = "LA"

blocks = []
for st in sorted(data["listing"], key=lambda s: NAMES[s]):
    counties = sorted(data["listing"][st], key=str.lower)
    unit = "parishes" if st == LA_PARISH else ("district" if st == "DC" else "counties")
    lis = "".join(f"<li>{html.escape(c)}</li>" for c in counties)
    blocks.append(f'      <details data-st="{st}" data-name="{html.escape(NAMES[st])}"><summary><b>{html.escape(NAMES[st])}</b>'
                  f'<small>{len(counties)} {unit}</small></summary><ul>{lis}</ul></details>')

tpl = open(ROOT / "docs" / "index.template.html").read()
out = tpl.replace("<!--AREAS-->", "\n".join(blocks))
open(ROOT / "index.html", "w").write(out)
total = sum(len(v) for v in data["listing"].values())
print(f"index.html written: {len(data['listing'])} states, {total} entries, {len(data['pins'])} pins")
