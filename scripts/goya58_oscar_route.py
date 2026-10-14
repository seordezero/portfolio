# Goya 58: Oscar's route in Blender. Walkable grid of the flat (5 cm cells, 22 cm clearance at
# knee, waist and head height), then A* between the stops with a cost that keeps him in the middle
# of corridors. Stores bpy.app.driver_namespace['goya_legs'] for goya58_oscar_anim.py and draws 'Ruta'.
import bpy, heapq, math
from collections import deque
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ORDER = ['pasillo', 'comedor', 'salon', 'estudio', 'balcon', 'dormitorio', 'entrada', 'pasillo']
STOPS = {'pasillo': (.15, -2.0), 'comedor': (-1.3, .38), 'salon': (-3.5, 6.4), 'estudio': (2.15, 5.45),
         'balcon': (-1.6, 9.35), 'dormitorio': (-1.1, -9.0), 'entrada': (1.2, 3.0)}
CENTRE = 14.0     # weight of the stay-in-the-middle cost

if 'goya_grid' not in bpy.app.driver_namespace:
    verts, polys = [], []
    for o in bpy.data.collections['Piso'].all_objects:
        if o.type != 'MESH':
            continue
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        if max(p.z for p in bb) < .08 or min(p.z for p in bb) > 1.7:
            continue
        base = len(verts); verts.extend(o.matrix_world @ v.co for v in o.data.vertices)
        polys.extend([base + i for i in p.vertices] for p in o.data.polygons)
    bvh = BVHTree.FromPolygons(verts, polys)
    X0, Y0, S, NX, NY = -5.3, -10.7, .05, 214, 430
    free = bytearray(NX * NY)
    for j in range(NY):
        for i in range(NX):
            x, y = X0 + i * S, Y0 + j * S
            free[j * NX + i] = all(bvh.find_nearest(Vector((x, y, z)), .22)[0] is None for z in (.3, .9, 1.5))
    # the terrace doors are closed in the model but he opens them
    for j in range(NY):
        for i in range(NX):
            x, y = X0 + i * S, Y0 + j * S
            if (-3.06 < x < -1.48 and 8.25 < y < 9.1) or (-1.25 < x < -.45 and 9.41 < y < 9.77):
                free[j * NX + i] = 1
    bpy.app.driver_namespace['goya_grid'] = (X0, Y0, S, NX, NY, free)
X0, Y0, S, NX, NY, free = bpy.app.driver_namespace['goya_grid']

INF = 10 ** 9; dist = [INF] * (NX * NY); q = deque()
for k in range(NX * NY):
    if not free[k]:
        dist[k] = 0; q.append(k)
while q:
    k = q.popleft(); i, j = k % NX, k // NX
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = i + di, j + dj
        if 0 <= a < NX and 0 <= b < NY and dist[b * NX + a] > dist[k] + 1:
            dist[b * NX + a] = dist[k] + 1; q.append(b * NX + a)
cell = lambda p: (round((p[0] - X0) / S), round((p[1] - Y0) / S))
pt = lambda i, j: (X0 + i * S, Y0 + j * S)


def nearest_free(p, minc=4):
    i0, j0 = cell(p)
    for r in range(60):
        best = None
        for i in range(i0 - r, i0 + r + 1):
            for j in range(j0 - r, j0 + r + 1):
                if max(abs(i - i0), abs(j - j0)) != r or not (0 <= i < NX and 0 <= j < NY):
                    continue
                if dist[j * NX + i] >= minc:
                    d = (i - i0) ** 2 + (j - j0) ** 2
                    if best is None or d < best[0]:
                        best = (d, i, j)
        if best:
            return pt(best[1], best[2])


def astar(a, b):
    (ai, aj), (bi, bj) = cell(a), cell(b)
    start, goal = aj * NX + ai, bj * NX + bi
    g = {start: 0}; came = {}; h = lambda k: math.hypot(k % NX - bi, k // NX - bj)
    pq = [(h(start), start)]
    while pq:
        _, k = heapq.heappop(pq)
        if k == goal:
            break
        i, j = k % NX, k // NX
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if not (di or dj):
                    continue
                a2, b2 = i + di, j + dj
                if not (0 <= a2 < NX and 0 <= b2 < NY):
                    continue
                n = b2 * NX + a2
                if not free[n]:
                    continue
                # far from walls is cheap: in a corridor the cheapest line is its middle
                ng = g[k] + math.hypot(di, dj) * (1 + CENTRE / (1 + dist[n]) ** 1.5)
                if ng < g.get(n, 1e18):
                    g[n] = ng; came[n] = k; heapq.heappush(pq, (ng + h(n), n))
    path = [goal]
    while path[-1] != start:
        path.append(came[path[-1]])
    return [pt(k % NX, k // NX) for k in reversed(path)]


def simplify(path, eps=.04):
    if len(path) < 3:
        return path
    a, b = path[0], path[-1]; L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1e-9
    dmax, imax = 0, 0
    for i, p in enumerate(path[1:-1], 1):
        d = abs((b[0] - a[0]) * (a[1] - p[1]) - (a[0] - p[0]) * (b[1] - a[1])) / L
        if d > dmax:
            dmax, imax = d, i
    if dmax < eps:
        return [a, b]
    return simplify(path[:imax + 1], eps)[:-1] + simplify(path[imax:], eps)


STOPS = {k: nearest_free(v) for k, v in STOPS.items()}
legs = []
for a, b in zip(ORDER, ORDER[1:]):
    s = simplify(astar(STOPS[a], STOPS[b]))
    legs.append((a, b, s))
    print(a, '->', b, '%d pts %.1f m' % (len(s), sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(s, s[1:]))))
bpy.app.driver_namespace['goya_legs'] = (STOPS, legs)
print({k: tuple(round(c, 2) for c in v) for k, v in STOPS.items()})
cu = bpy.data.curves.get('Ruta') or bpy.data.curves.new('Ruta', 'CURVE'); cu.splines.clear(); cu.dimensions = '3D'; cu.bevel_depth = .015
for a, b, s in legs:
    sp = cu.splines.new('POLY'); sp.points.add(len(s) - 1)
    for k, (x, y) in enumerate(s):
        sp.points[k].co = (x, y, .03, 1)
ob = bpy.data.objects.get('Ruta') or bpy.data.objects.new('Ruta', cu)
if ob.name not in bpy.context.scene.collection.objects:
    bpy.context.scene.collection.objects.link(ob)
