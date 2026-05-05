"""Trophy in two screw-together parts for side-by-side FDM printing.

Base:     flat bottom, M20×3 threaded blind hole.
Cup+stem: flat-top cup rim (print upside-down), M20×3 threaded boss.
"""

from build123d import *

# ── Thread parameters (coarse M20×3 for FDM) ──
PITCH = 3.0          # mm
DEPTH = 1.5          # mm thread depth
NOMINAL_R = 10.0     # M20 nominal radius
BOSS_R = 8.5         # boss cylinder radius (minor - clearance)
HOLE_R = 10.3        # clearance hole radius
HOLE_FLOOR_R = 8.8   # thread floor after cut
BOSS_TOP = 14.0      # Z where boss meets stem
BOSS_BOT = 2.0       # Z where boss/thread start
THREAD_H = 10.0      # threaded engagement height


def _cut_thread(part, helix_r, floor_r, z_start):
    """Subtract an internal triangular thread."""
    helix = Helix(PITCH, THREAD_H, helix_r, center=(0, 0, z_start))

    with BuildSketch(Plane.XZ.offset(z_start)) as sk:
        with BuildLine():
            l1 = Line((helix_r, 0), (floor_r, PITCH * 0.5))
            l2 = Line(l1 @ 1, (helix_r, PITCH))
            l3 = Line(l2 @ 1, (helix_r, 0))
        make_face()

    cutter = sweep(sk.sketch.faces()[0], helix)
    return part - cutter


def _add_thread(part, base_r, crest_r, z_start):
    """Add an external triangular thread to a cylinder."""
    helix = Helix(PITCH, THREAD_H, base_r, center=(0, 0, z_start))

    with BuildSketch(Plane.XZ.offset(z_start)) as sk:
        with BuildLine():
            l1 = Line((base_r, 0), (crest_r, PITCH * 0.5))
            l2 = Line(l1 @ 1, (base_r, PITCH))
            l3 = Line(l2 @ 1, (base_r, 0))
        make_face()

    ridge = sweep(sk.sketch.faces()[0], helix)
    return part + ridge


def gen_base():
    """Base — flat bottom, stepped profile, M20×3 threaded hole."""
    with BuildPart() as body:
        with BuildSketch(Plane.XZ) as profile:
            with BuildLine() as outline:
                l1  = Line((0, 0),    (40, 0))
                l2  = Line(l1 @ 1,    (40, 10))
                l3  = Line(l2 @ 1,    (26, 10))
                l4  = Line(l3 @ 1,    (26, BOSS_TOP))
                l5  = Line(l4 @ 1,    (HOLE_R, BOSS_TOP))
                l6  = Line(l5 @ 1,    (HOLE_R, BOSS_BOT))
                l7  = Line(l6 @ 1,    (0, BOSS_BOT))
                l8  = Line(l7 @ 1,    (0, 0))
            make_face()
        revolve(axis=Axis.Z, revolution_arc=360)

    result = body.part
    result = _cut_thread(result, HOLE_R, HOLE_FLOOR_R, BOSS_BOT)

    # Fillet base step
    for face in result.faces():
        c = face.center()
        if abs(c.Z - 10) < 1 and face.area < 500:
            try:
                fillet(face.edges(), 2)
            except Exception:
                pass
            break

    return result


def gen_cup_stem():
    """Cup + stem — flat rim, M20×3 threaded boss."""
    with BuildPart() as body:
        with BuildSketch(Plane.XZ) as profile:
            with BuildLine() as outline:
                l1  = Line((0, BOSS_BOT),      (BOSS_R, BOSS_BOT))
                l2  = Line(l1 @ 1,              (BOSS_R, BOSS_TOP))
                l3  = Line(l2 @ 1,              (8, 54))
                l4  = Line(l3 @ 1,              (18, 58))
                l5  = Line(l4 @ 1,              (35, 80))
                l6  = Line(l5 @ 1,              (46, 104))
                l7  = Line(l6 @ 1,              (44, 115))
                l8  = Line(l7 @ 1,              (36, 115))
                l9  = Line(l8 @ 1,              (34, 108))
                l10 = Line(l9 @ 1,              (28, 78))
                l11 = Line(l10 @ 1,             (12, 58))
                l12 = Line(l11 @ 1,             (0, 54))
                l13 = Line(l12 @ 1,             (0, BOSS_BOT))
            make_face()
        revolve(axis=Axis.Z, revolution_arc=360)

    result = body.part
    result = _add_thread(result, BOSS_R, NOMINAL_R, BOSS_BOT)

    return result


if __name__ == "__main__":
    from build123d import export_step, export_stl

    base = gen_base()
    export_step(base, "cad/trophy_base.step")
    export_stl(base, "cad/trophy_base.stl")

    cup = gen_cup_stem()
    export_step(cup, "cad/trophy_cup_stem.step")
    export_stl(cup, "cad/trophy_cup_stem.stl")

    print("Exported cad/trophy_base.* + cad/trophy_cup_stem.*")
