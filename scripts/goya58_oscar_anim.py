# Goya 58: Oscar's loop in Blender (run inside Blender after the route is computed:
# bpy.app.driver_namespace['goya_legs'] = (STOPS, legs) from the A* step).
# corridor -> bedroom (drinks) -> corridor -> entrance -> dining (sits, drinks) -> living room (sits)
# -> study (sits at the Think chair, works on a Mac) -> balcony (smokes) -> corridor. Loops.
# Poses are bone directions in character space (+X his left, -Y forward, +Z up), turned into local
# quaternions against the rest pose; the rig object carries position and heading.
import bpy, math
from mathutils import Vector, Quaternion, Matrix

FPS = 24
SPEED = 1.15            # m/s
STRIDE = 1.35           # m per full cycle (two steps)
rig = bpy.data.objects['Oscar_rig']
STOPS, LEGS = bpy.app.driver_namespace['goya_legs']
bones = rig.data.bones
BR = {b.name: b.matrix_local.to_quaternion() for b in bones}
RD = {b.name: (b.matrix_local.to_3x3() @ Vector((0, 1, 0))).normalized() for b in bones}
PARENT = {b.name: (b.parent.name if b.parent else None) for b in bones}
ORDER = [b.name for b in bones]          # parents come before children in Blender's list


def v(x, y, z):
    return Vector((x, y, z)).normalized()


def rot_about_x(d, deg):
    return Quaternion((1, 0, 0), math.radians(deg)) @ d


def leg(theta, bend, x=0.0):
    """thigh angle forward from vertical, knee bend; returns thigh, shin, foot directions"""
    t, s = math.radians(theta), math.radians(theta - bend)
    return v(x, -math.sin(t), -math.cos(t)), v(x * .5, -math.sin(s), -math.cos(s)), v(0, -1, -.25 + .3 * math.sin(s))


def stand():
    p = {}
    p['Thigh.L'], p['Shin.L'], p['Foot.L'] = leg(2, 2, .05)
    p['Thigh.R'], p['Shin.R'], p['Foot.R'] = leg(2, 2, -.05)
    p['UpperArm.R'], p['ForeArm.R'], p['Hand.R'] = v(-.12, .0, -1), v(-.04, -.12, -1), v(0, -.1, -1)
    return p, Vector()


def walk(phase):
    p, _ = stand()
    s, c = math.sin(phase), math.cos(phase)
    th = 24 * s
    p['Thigh.L'], p['Shin.L'], p['Foot.L'] = leg(th, 55 * max(0, c) ** 1.3 + 4, .05)
    p['Thigh.R'], p['Shin.R'], p['Foot.R'] = leg(-th, 55 * max(0, -c) ** 1.3 + 4, -.05)
    a = math.radians(20 * s)          # right arm swings with the left leg
    p['UpperArm.R'] = v(-.12, -math.sin(a), -math.cos(a)); p['ForeArm.R'] = v(-.04, -math.sin(a + .3), -math.cos(a + .3))
    p['UpperArm.L'] = rot_about_x(RD['UpperArm.L'], 10 * s)   # the bottle arm keeps its bend
    return p, Vector((0, 0, .018 * math.cos(2 * phase) - .012))


def sit(seat_h):
    p = {}
    p['Thigh.L'], p['Shin.L'], p['Foot.L'] = v(.06, -1, .06), v(.03, -.2, -1), v(0, -1, -.3)
    p['Thigh.R'], p['Shin.R'], p['Foot.R'] = v(-.06, -1, .06), v(-.03, -.2, -1), v(0, -1, -.3)
    p['Spine'] = rot_about_x(RD['Spine'], -6)
    p['UpperArm.R'], p['ForeArm.R'], p['Hand.R'] = v(-.12, -.3, -.95), v(-.02, -1, -.35), v(0, -1, -.3)
    return p, Vector((0, .12, seat_h + .1 - .92))


def drink(base):
    p, off = base
    p = dict(p)
    p['_reach'] = 'bottle'          # left hand brings the bottle's neck to the mouth (IK below)
    p['Head'] = v(-.07, .3, .95)
    return p, off


def smoke_up(base):
    p, off = base
    p = dict(p)
    p['_reach'] = 'cigarette'       # right fingertips to the corner of the mouth
    return p, off


def smoke_down(base):
    p, off = base
    p = dict(p)
    p['UpperArm.R'], p['ForeArm.R'], p['Hand.R'] = v(-.15, -.15, -.97), v(-.05, -.85, -.5), v(0, -1, -.2)
    return p, off


def typing(base, t):
    p, off = base
    p = dict(p)
    w = 6 * math.sin(t * 9)
    # desk top is 0.90 m: elbows forward, forearms slightly up so the hands land on the keyboard
    p['UpperArm.L'], p['ForeArm.L'], p['Hand.L'] = v(.12, -.6, -.78), v(-.15, -1, .3), rot_about_x(v(-.05, -1, -.1), w)
    p['UpperArm.R'], p['ForeArm.R'], p['Hand.R'] = v(-.12, -.6, -.78), v(.15, -1, .3), rot_about_x(v(.05, -1, -.1), -w)
    p['Head'] = v(-.07, -.22, .97)
    return p, off


RH = {b.name: b.head_local.copy() for b in bones}
RT = {b.name: b.tail_local.copy() for b in bones}
MOUTH = Vector((-.04, -.1, 1.58))
NECK = Vector((.02, -.16, 1.27)) - RH['Hand.L']       # bottle neck from the left wrist, rest pose
BOTTLE = Vector((-.1, -.08, .24)).normalized()          # bottle axis bottom -> neck, rest pose


def ik(S, T, l1, l2, pole):
    d = T - S; L = min(max(d.length, abs(l1 - l2) + 1e-3), l1 + l2 - 1e-3); n = d.normalized()
    a = (l1 * l1 - l2 * l2 + L * L) / (2 * L); h = math.sqrt(max(0, l1 * l1 - a * a))
    pp = (pole - n * pole.dot(n)).normalized()
    return S + n * a + pp * h, S + n * L


def deltas(pose, off=Vector()):
    """armature-space delta rotation per bone (unspecified bones follow their parent); '_reach' solves an arm"""
    D = {}
    for n in ORDER:
        par = PARENT[n]
        if n in pose:
            D[n] = RD[n].rotation_difference(pose[n])
        else:
            D[n] = D[par] if par else Quaternion()
    reach = pose.get('_reach')
    if reach:
        ph = {}
        for n in ORDER:
            par = PARENT[n]
            ph[n] = RH[n] + off if not par else ph[par] + D[par] @ (RH[n] - RH[par])
        mouth = ph['Head'] + D['Head'] @ (MOUTH - RH['Head'])
        sd = 'L' if reach == 'bottle' else 'R'
        up, fa, ha = 'UpperArm.' + sd, 'ForeArm.' + sd, 'Hand.' + sd
        l1, l2 = (RT[up] - RH[up]).length, (RT[fa] - RH[fa]).length
        if reach == 'bottle':
            R = BOTTLE.rotation_difference(Vector((.05, .8, -.55)).normalized())   # bottom up, neck to the lips
            T = mouth - R @ NECK
            pole = Vector((.8, .2, -.6))
        else:
            hd = Vector((.35, .3, .89)).normalized(); R = RD[ha].rotation_difference(hd)
            T = mouth + Vector((-.03, -.02, -.02)) - hd * (RT[ha] - RH[ha]).length
            pole = Vector((-.8, .2, -.6))
        E, W = ik(ph[up], T, l1, l2, pole)
        D[up] = RD[up].rotation_difference((E - ph[up]).normalized())
        D[fa] = RD[fa].rotation_difference((W - E).normalized())
        D[ha] = R
    return D


def blend(a, b, w):
    w = w * w * (3 - 2 * w)   # smoothstep
    Da, oa = a; Db, ob = b
    return {n: Da[n].slerp(Db[n], w) for n in ORDER}, oa.lerp(ob, w)


def key(frame, state, x, y, yaw):
    D, off = state
    rig.location = (x, y, 0); rig.rotation_euler = (0, 0, yaw)
    rig.keyframe_insert('location', frame=frame); rig.keyframe_insert('rotation_euler', index=2, frame=frame)
    for n in ORDER:
        pb = rig.pose.bones[n]; pb.rotation_mode = 'QUATERNION'
        par = PARENT[n]; Dp = D[par] if par else Quaternion()
        pb.rotation_quaternion = BR[n].inverted() @ Dp.inverted() @ D[n] @ BR[n]
        pb.keyframe_insert('rotation_quaternion', frame=frame)
    hb = rig.pose.bones['Hips']; hb.location = BR['Hips'].inverted() @ off
    hb.keyframe_insert('location', frame=frame)


def P(fn, *a):
    p, off = fn(*a)
    return deltas(p, off), off


# ---------------------------------------------------------------- timeline
rig.animation_data_clear()
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'   # every frame is keyed
for pb in rig.pose.bones:
    pb.rotation_mode = 'QUATERNION'
F = [1]
state = {'x': 0, 'y': 0, 'yaw': 0}


def yaw_of(dx, dy):
    return math.atan2(dx, -dy)     # rest faces -Y


def unwrap(a, ref):
    while a - ref > math.pi: a -= 2 * math.pi
    while a - ref < -math.pi: a += 2 * math.pi
    return a


def hold(seconds, pose_fn):
    """pose_fn(t) -> (D, off); keys every frame for `seconds`"""
    n = max(1, round(seconds * FPS))
    for k in range(n):
        key(F[0], pose_fn(k / FPS), state['x'], state['y'], state['yaw']); F[0] += 1


def turn_to(yaw, seconds=.7, pose=None):
    pose = pose or P(stand)
    y0 = state['yaw']; y1 = unwrap(yaw, y0); n = max(1, round(seconds * FPS))
    for k in range(n):
        w = (k + 1) / n; w = w * w * (3 - 2 * w)
        state['yaw'] = y0 + (y1 - y0) * w
        key(F[0], P(walk, math.pi * 2 * k / n * .5) if abs(y1 - y0) > .3 else pose, state['x'], state['y'], state['yaw']); F[0] += 1


def walk_path(pts):
    seg = [(Vector(a), Vector(b)) for a, b in zip(pts, pts[1:])]
    L = sum((b - a).length for a, b in seg)
    def at(s):
        s = max(0, min(L, s))
        for a, b in seg:
            l = (b - a).length
            if s <= l: return a + (b - a) * (s / max(l, 1e-9))
            s -= l
        return seg[-1][1]
    n = max(2, round(L / SPEED * FPS)); st = P(stand)
    for k in range(n + 1):
        s = L * k / n
        p = at(s); ahead = at(s + .35) - at(s - .05)
        if ahead.length > 1e-4:
            state['yaw'] = unwrap(yaw_of(ahead.x, ahead.y), state['yaw']) * .35 + state['yaw'] * .65 if k else unwrap(yaw_of(ahead.x, ahead.y), state['yaw'])
        state['x'], state['y'] = p.x, p.y
        w = P(walk, 2 * math.pi * s / STRIDE)
        e = min(1, s / .4, (L - s) / .4)              # ease in and out of the gait
        key(F[0], blend(st, w, max(0, e)), p.x, p.y, state['yaw']); F[0] += 1


def move_blend(to_xy, a, b, seconds):
    x0, y0 = state['x'], state['y']; n = max(1, round(seconds * FPS))
    for k in range(n):
        w = (k + 1) / n
        state['x'] = x0 + (to_xy[0] - x0) * w * w * (3 - 2 * w); state['y'] = y0 + (to_xy[1] - y0) * w * w * (3 - 2 * w)
        key(F[0], blend(a, b, w), state['x'], state['y'], state['yaw']); F[0] += 1


def gesture(base, fn, up=.9, holdt=1.6, down=.9):
    n = round(up * FPS)
    for k in range(n): key(F[0], blend(base, fn, (k + 1) / n), state['x'], state['y'], state['yaw']); F[0] += 1
    hold(holdt, lambda t: fn)
    for k in range(round(down * FPS)): key(F[0], blend(fn, base, (k + 1) / round(down * FPS)), state['x'], state['y'], state['yaw']); F[0] += 1


def sit_at(seat_xy, face_yaw, seat_h, during):
    """turn to face away from the seat back, settle (root moves so the hips land on the seat), act, get up"""
    turn_to(face_yaw)
    fwd = Vector((math.sin(face_yaw), -math.cos(face_yaw)))
    root = (seat_xy[0] + fwd.x * .12, seat_xy[1] + fwd.y * .12)
    stand_xy = (state['x'], state['y'])
    st, si = P(stand), P(sit, seat_h)
    move_blend(root, st, si, 1.3)
    during(si)
    move_blend(stand_xy, si, st, 1.2)


legs = {(a, b): s for a, b, s in LEGS}
x0, y0 = STOPS['pasillo']; state.update(x=x0, y=y0)
first = legs[('pasillo', 'dormitorio')]
state['yaw'] = yaw_of(first[1][0] - first[0][0], first[1][1] - first[0][1])
STAND = P(stand)

# 1 corridor -> bedroom, drink looking at the bed
walk_path(first)
turn_to(yaw_of(-2.45 - state['x'], -9.3 - state['y']))
hold(.6, lambda t: STAND)
gesture(STAND, P(drink, stand()), 1.0, 1.8, 1.0)
hold(.8, lambda t: STAND)
# 2 back along the corridor, through the entrance, into the dining room: sit, drink
walk_path(legs[('dormitorio', 'entrada')])
walk_path(legs[('entrada', 'comedor')])
def dining(si):
    hold(1.5, lambda t: si); gesture(si, P(drink, sit(.47)), 1.0, 1.8, 1.0); hold(1.2, lambda t: si)
sit_at((-2.03, .82), yaw_of(-1, 0), .47, dining)
# 3 living room: sofa
walk_path(legs[('comedor', 'salon')])
sit_at((-3.9, 5.15), yaw_of(1, 0), .42, lambda si: hold(5, lambda t: si))
# 4 study: Think chair, works on the Mac
walk_path(legs[('salon', 'estudio')])
sit_at((1.6, 5.9), yaw_of(-1, 0), .5, lambda si: hold(9, lambda t: P(typing, sit(.5), t)))
# 5 balcony: smoke three times looking out
walk_path(legs[('estudio', 'balcon')])
turn_to(yaw_of(0, 1))
CIG_ON = F[0]
for _ in range(3):
    gesture(P(smoke_down, stand()), P(smoke_up, stand()), .8, 1.4, .8)
    hold(1.6, lambda t: P(smoke_down, stand()))
CIG_OFF = F[0]
# 6 back to the corridor, facing where the loop starts
walk_path(legs[('balcon', 'pasillo')])
turn_to(yaw_of(first[1][0] - first[0][0], first[1][1] - first[0][1]))
END = F[0] - 1

act = rig.animation_data.action
act.name = 'Oscar_dia'
sc = bpy.context.scene
sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = END
bpy.app.driver_namespace['goya_cig'] = (CIG_ON, CIG_OFF)
print('frames', END, '(%.1f s)' % (END / FPS), 'cigarette', CIG_ON, CIG_OFF)
