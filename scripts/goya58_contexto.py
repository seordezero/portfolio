# Goya 58: the neighbourhood as shadow casters for the viewer's sun.
# Reads Catastro INSPIRE building parts (bp.gml, EPSG:25830) and writes contexto.json in the
# viewer's model coordinates (x east along the Goya facade, z into the building, y up, metres,
# the flat's floor at y = 0).
#   py -3 goya58_contexto.py <bp.gml> <out contexto.json>
# Placement: the flat is the west half of parcel 2652301VK4725D, the corner of Goya and Francisca
# Moreno; its outer NW wall corner (model x -5.16, z -10.22) is the parcel's NW corner. Floor of
# the flat (6th of 7 above the ground floor): 4.0 m ground floor + 5 x 3.1 m = 19.5 m.
import json, math, re, sys

src, out = sys.argv[1], sys.argv[2]
NW, NE = (442501.04, 4475123.29), (442519.03, 4475121.97)       # Goya facade, parcel 2652301
THETA = math.atan2(NE[0] - NW[0], NE[1] - NW[1]) - math.pi / 2  # bearing of the facade normal
X0, Z0, ELEV, GROUND, STOREY = -5.16, -10.22, 19.5, 4.0, 3.1
FLAT_X1, CEIL = 5.16, 2.85                                       # the flat's east wall, ceiling top
c, s = math.cos(THETA), math.sin(THETA)


def model(e, n):
    de, dn = e - NW[0], n - NW[1]
    return X0 + de * c - dn * s, Z0 - (de * s + dn * c)


def clip(poly, keep):
    """Sutherland-Hodgman against one vertical line x = FLAT_X1; keep(x) says which side stays"""
    res = []
    for i in range(len(poly)):
        p, q = poly[i - 1], poly[i]
        if keep(q[0]):
            if not keep(p[0]):
                t = (FLAT_X1 - p[0]) / (q[0] - p[0]); res.append((FLAT_X1, p[1] + (q[1] - p[1]) * t))
            res.append(q)
        elif keep(p[0]):
            t = (FLAT_X1 - p[0]) / (q[0] - p[0]); res.append((FLAT_X1, p[1] + (q[1] - p[1]) * t))
    return res


parts = []
gml = open(src, encoding='latin-1').read()
for pid, body in re.findall(r'<bu-ext2d:BuildingPart gml:id="([^"]+)">(.*?)</bu-ext2d:BuildingPart>', gml, re.S):
    fl = re.search(r'numberOfFloorsAboveGround>(\d+)', body)
    n = int(fl.group(1)) if fl else 0
    if n == 0:
        continue
    top = GROUND + (n - 1) * STOREY - ELEV
    if top <= 0:                                  # all below the flat's floor: cannot shade it
        continue
    rings = re.findall(r'<gml:posList[^>]*>([^<]*)', body)
    v = list(map(float, rings[0].split()))        # outer ring only
    poly = [model(v[i], v[i + 1]) for i in range(0, len(v) - 2, 2)]
    cx, cz = sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)
    if math.hypot(cx, cz) > 160:
        continue
    pieces = [(poly, -ELEV)]
    if '2652301' in pid:                          # own building: not around the flat, only above it
        pieces = [(clip(poly, lambda x: x > FLAT_X1), -ELEV), (clip(poly, lambda x: x <= FLAT_X1), CEIL)]
    for pl, bottom in pieces:
        if len(pl) >= 3 and top > bottom:
            parts.append([round(top, 2), round(bottom, 2), [round(t, 2) for p in pl for t in p]])

json.dump({'theta': round(math.degrees(THETA), 3), 'lat': 40.42466, 'lon': -3.67772, 'parts': parts},
          open(out, 'w'), separators=(',', ':'))
print('parts', len(parts), 'theta', round(math.degrees(THETA), 2))
