"""Build the Imperial Field Services coverage map (SVG + pin data) from
coverage.json (parsed from the Excel sheet) and the us-atlas TopoJSON files.

usage: python3 -I build_map.py <coverage.json> <usatlas dir> <out dir>
"""
import json, math, re, sys

cov_path, atlas_dir, out_dir = sys.argv[1:4]
coverage = json.load(open(cov_path))
counties_t = json.load(open(f"{atlas_dir}/counties-10m.json"))
states_t = json.load(open(f"{atlas_dir}/states-10m.json"))

FIPS = {"01":"AL","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT","10":"DE","11":"DC","12":"FL","13":"GA",
"16":"ID","17":"IL","18":"IN","19":"IA","20":"KS","21":"KY","22":"LA","23":"ME","24":"MD","25":"MA","26":"MI",
"27":"MN","28":"MS","29":"MO","30":"MT","31":"NE","32":"NV","33":"NH","34":"NJ","35":"NM","36":"NY","37":"NC",
"38":"ND","39":"OH","40":"OK","41":"OR","42":"PA","44":"RI","45":"SC","46":"SD","47":"TN","48":"TX","49":"UT",
"50":"VT","51":"VA","53":"WA","54":"WV","55":"WI","56":"WY"}

# ---------- TopoJSON decoding ----------
def decode_arcs(topo):
    sc, tr = topo["transform"]["scale"], topo["transform"]["translate"]
    out = []
    for arc in topo["arcs"]:
        x = y = 0; pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
        out.append(pts)
    return out

def ring_coords(ring, arcs):
    pts = []
    for i in ring:
        a = arcs[i] if i >= 0 else list(reversed(arcs[~i]))
        if pts and pts[-1] == a[0]: a = a[1:]
        pts.extend(a)
    return pts

def geom_rings(g, arcs):
    if g["type"] == "Polygon":
        return [ring_coords(r, arcs) for r in g["arcs"]]
    if g["type"] == "MultiPolygon":
        return [ring_coords(r, arcs) for poly in g["arcs"] for r in poly]
    return []

# ---------- Albers conic equal-area (lower 48) ----------
P0, P1, LAM0, PHIC = math.radians(29.5), math.radians(45.5), math.radians(-96), math.radians(37.5)
N = (math.sin(P0) + math.sin(P1)) / 2
C = math.cos(P0) ** 2 + 2 * N * math.sin(P0)
RHO0 = math.sqrt(C - 2 * N * math.sin(PHIC)) / N
def project(lon, lat):
    lam, phi = math.radians(lon), math.radians(lat)
    rho = math.sqrt(C - 2 * N * math.sin(phi)) / N
    th = N * (lam - LAM0)
    return rho * math.sin(th), RHO0 - rho * math.cos(th)

# ---------- states ----------
SKIP = {"02", "15", "60", "66", "69", "72", "78"}
s_arcs = decode_arcs(states_t)
state_rings = {}
for g in states_t["objects"]["states"]["geometries"]:
    if g["id"] in SKIP: continue
    state_rings[g["id"]] = [[project(*p) for p in r] for r in geom_rings(g, s_arcs)]

xs = [p[0] for rs in state_rings.values() for r in rs for p in r]
ys = [p[1] for rs in state_rings.values() for r in rs for p in r]
minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
W, H, PAD = 1200, 740, 16
scale = min((W - 2 * PAD) / (maxx - minx), (H - 2 * PAD) / (maxy - miny))
ox = (W - (maxx - minx) * scale) / 2
oy = (H - (maxy - miny) * scale) / 2
def to_px(p):  # y grows downward in SVG; Albers y grows upward
    return (ox + (p[0] - minx) * scale, oy + (maxy - p[1]) * scale)

def path_of(rings):
    d = []
    for r in rings:
        pts = [to_px(p) for p in r]
        d.append("M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts[::1]) + "Z")
    return "".join(d)

# ---------- counties ----------
c_arcs = decode_arcs(counties_t)
def norm(s):
    s = s.lower().strip()
    s = re.sub(r"[.'’\-]", " ", s)
    s = re.sub(r"\bsaint\b", "st", s)
    s = re.sub(r"\bcounty\b", "", s)
    s = re.sub(r"\s+", "", s)
    return s

atlas = {}  # (state, normname) -> list of (fips, name, centroid lon/lat, px)
for g in counties_t["objects"]["counties"]["geometries"]:
    st = FIPS.get(g["id"][:2])
    if not st: continue
    rings = geom_rings(g, c_arcs)
    if not rings: continue
    # centroid of the largest ring (area-weighted polygon centroid in lon/lat)
    best = max(rings, key=len)
    A = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(best, best[1:] + best[:1]):
        cr = x0 * y1 - x1 * y0
        A += cr; cx += (x0 + x1) * cr; cy += (y0 + y1) * cr
    if abs(A) < 1e-12:
        lon = sum(p[0] for p in best) / len(best); lat = sum(p[1] for p in best) / len(best)
    else:
        lon, lat = cx / (3 * A), cy / (3 * A)
    name = g["properties"]["name"]
    is_city = int(g["id"]) >= 51510 and st == "VA"
    atlas.setdefault((st, norm(name) + ("city" if is_city else "")), []).append((g["id"], name, lon, lat))
    atlas.setdefault((st, norm(name)), []).append((g["id"], name, lon, lat))

# spelling fixes and city -> county mappings from the spreadsheet
ALIAS = {
    ("MD", "annearunde"): "Anne Arundel", ("MD", "fredrick"): "Frederick", ("MD", "hartford"): "Harford",
    ("MN", "aitkini"): "Aitkin", ("IL", "jodavies"): "Jo Daviess", ("MN", "milelacs"): "Mille Lacs",
    ("VA", "roanokcity"): "Roanoke city", ("TX", "collins"): "Collin", ("DC", "fullstate"): "District of Columbia",
    ("MS", "southhaven"): "DeSoto", ("MS", "olivebranch"): "DeSoto", ("FL", "miamidade"): "Miami-Dade",
    ("FL", "desoto"): "DeSoto", ("IL", "dupage"): "DuPage", ("IL", "dekalb"): "DeKalb", ("IN", "dekalb"): "DeKalb",
    ("GA", "dekalb"): "DeKalb", ("LA", "stjohnthebaptist"): "St. John the Baptist", ("IN", "laporte"): "LaPorte",
    ("MO", "stlouis"): "St. Louis", ("MD", "stmarys"): "St. Mary's", ("MD", "queenannes"): "Queen Anne's",
    ("MD", "princegeorges"): "Prince George's", ("MI", "alconacounty"): "Alcona", ("PA", "mckean"): "McKean",
    ("VA", "isleofwight"): "Isle of Wight", ("VA", "princegeorge"): "Prince George", ("GA", "mcintosh"): "McIntosh",
    ("IL", "lasalle"): "LaSalle", ("IL", "mchenry"): "McHenry", ("TN", "mcnairy"): "McNairy",
}
DISPLAY_FIX = {"Anne Arunde": "Anne Arundel", "Fredrick": "Frederick", "Hartford": "Harford", "Aitkini": "Aitkin",
    "JoDavies": "Jo Daviess", "Mile Lacs": "Mille Lacs", "Roanok City": "Roanoke City", "Collins": "Collin",
    "Southhaven": "Southaven (DeSoto Co.)", "Olive Branch": "Olive Branch (DeSoto Co.)", "Full State": "Full District",
    "Miami-dade": "Miami-Dade", "Alcona County": "Alcona", "Mckean": "McKean", "scioto": "Scioto",
    "Chesapeake City": "Chesapeake", "Hampton City": "Hampton", "NEWPORT NEWS": "Newport News", "Norfolk City": "Norfolk",
    "Portsmouth City": "Portsmouth", "Suffolk City": "Suffolk", "Virginia Beach City": "Virginia Beach",
    "Williamsburg City": "Williamsburg", "New castle": "New Castle", "Mcintosh": "McIntosh", "Desoto": "DeSoto",
    "St. Landry": "St. Landry", "Saint Lawrence": "St. Lawrence", "Saint Johns": "St. Johns", "Saint Lucie": "St. Lucie",
    "Saint Marys": "St. Mary's", "Queen Annes": "Queen Anne's", "Prince Georges": "Prince George's",
    "Saint Charles": "St. Charles", "Saint Louis": "St. Louis", "Saint Clair": "St. Clair", "St John The Baptist": "St. John the Baptist",
    "Saint Bernard": "St. Bernard", "Saint Helena": "St. Helena", "Saint James": "St. James", "Saint Martin": "St. Martin",
    "Saint Tammany": "St. Tammany", "ARENAC": "Arenac", "GLADWIN": "Gladwin", "ROSCOMMON": "Roscommon", "OGEMAW": "Ogemaw",
    "SANDUSKY": "Sandusky", "Sedgwick": "Sedgwick", "Dekalb": "DeKalb", "Dupage": "DuPage", "Laporte": "LaPorte", "LaPorte": "LaPorte"}

MOVE = {("MS", "Tipton"): "TN", ("MN", "Bayfield"): "WI", ("MN", "Burnett"): "WI"}
pins, unmatched, listing = [], [], {}
seen = set()
for st0, names in coverage.items():
    st0 = st0.strip()
    listing[st0] = []
    for raw in names:
        raw = raw.strip()
        st = MOVE.get((st0, raw), st0)
        listing.setdefault(st, [])
        disp = DISPLAY_FIX.get(raw, raw.title() if raw.isupper() or raw.islower() else raw)
        if disp not in listing[st]: listing[st].append(disp)
        key = norm(raw)
        hit = None
        if (st, key) in ALIAS:
            hit = atlas.get((st, norm(ALIAS[(st, key)])))
        if not hit:
            hit = atlas.get((st, key))
        if not hit and key.endswith("city"):
            hit = atlas.get((st, key))  # already includes 'city' suffix for VA independent cities
        if not hit:
            unmatched.append((st, raw)); continue
        # prefer VA independent city when the sheet says "City"; else prefer the county (lower FIPS)
        hit = sorted(hit, key=lambda h: h[0])
        pick = hit[-1] if (st == "VA" and key.endswith("city")) else hit[0]
        if pick[0] in seen: continue
        seen.add(pick[0])
        x, y = to_px(project(pick[2], pick[3]))
        pins.append({"state": st, "county": pick[1], "fips": pick[0], "lon": round(pick[2], 4), "lat": round(pick[3], 4), "x": round(x, 1), "y": round(y, 1)})

covered_states = set(listing)
# ---------- SVG ----------
state_paths = []
for sid, rings in state_rings.items():
    ab = FIPS[sid]
    fill = "#DCE5F1" if ab in covered_states else "#F3F5F8"
    state_paths.append(f'<path fill="{fill}" stroke="#B9C2CF" stroke-width=".8" stroke-linejoin="round" d="{path_of(rings)}"><title>{ab}</title></path>')

pin_el = []
for p in sorted(pins, key=lambda p: p["y"]):
    pin_el.append(f'<use href="#pin" x="{p["x"]}" y="{p["y"]}"><title>{p["county"]}, {p["state"]}</title></use>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Map of the United States with a marker on every county Imperial Field Services covers">
<defs>
<path id="pin" d="M0,0 C-3.2,-5.2 -5.6,-7.6 -5.6,-11.2 A5.6,5.6 0 1 1 5.6,-11.2 C5.6,-7.6 3.2,-5.2 0,0 Z M0,-13.4 A2.2,2.2 0 1 0 0,-9 A2.2,2.2 0 1 0 0,-13.4 Z" fill="#C9A227" stroke="#0E2A4A" stroke-width="1" fill-rule="evenodd"/>
</defs>
<rect width="{W}" height="{H}" fill="#ffffff"/>
<g>{"".join(state_paths)}</g>
<g>{"".join(pin_el)}</g>
</svg>'''
open(f"{out_dir}/coverage-map.svg", "w").write(svg)
json.dump({"pins": pins, "listing": listing}, open(f"{out_dir}/coverage-data.json", "w"), indent=0)
print("states", len(covered_states), "sheet entries", sum(len(v) for v in listing.values()), "pins", len(pins))
print("UNMATCHED", unmatched)
