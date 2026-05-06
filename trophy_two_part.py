"""Trophy in two screw-together parts for side-by-side FDM printing.

Base:     flat bottom, M20x3 threaded blind hole.
Cup+stem: flat-top cup rim (print upside-down), M20x3 threaded boss.
"""

from build123d import *

# ── Thread parameters (trapezoidal for FDM) ──
PITCH = 3.0          # mm
TOL = 0.15           # clearance for FDM fit

# Male (cup stem boss) — external thread
MALE_R_MIN = 9.0     # core cylinder radius
MALE_R_MAX = 9.85    # thread crest radius

# Female (base hole) — internal thread
FEMALE_R_MIN = 9.15  # hole wall radius (minor diameter)
FEMALE_R_VALLEY = 10.15   # thread valley radius

BOSS_TOP = 14.0      # Z where boss meets stem (mating surface)
BOSS_BOT = 2.0       # Z where boss tip ends
THREAD_RELIEF = 1.4  # gap before mating face


def _sweep_male_turn(z_offset):
    """Sweep a single male trapezoidal thread turn.

    Profile is placed at the exact helix start position using a custom
    Plane so the sweep correctly aligns it with the path.
    """
    radius = MALE_R_MIN
    crest_offset = MALE_R_MAX - radius
    helix = Helix(PITCH, PITCH * 0.95, radius, center=(0, 0, 0))
    profile_plane = Plane(
        origin=(radius, 0, 0),
        x_dir=(1, 0, 0),
        z_dir=(0, 0, 1),
    )
    pts = [
        (0, 0.50),
        (crest_offset, 1.00),
        (crest_offset, 2.00),
        (0, 2.50),
    ]
    with BuildSketch(profile_plane) as sk:
        Polygon(*pts)
    ridge = sweep(sk.sketch.faces()[0], helix)
    if not ridge.is_valid:
        return None
    return ridge.moved(Location((0, 0, z_offset)))


def _sweep_female_plug_turn(z_offset):
    """Sweep a single female thread cutter plug turn.

    Core is shrunk by 0.2mm to overhang into hole cavity, guaranteeing
    a clean boolean subtraction in OCCT. Profile uses custom Plane at
    the exact helix start position.
    """
    plug_r = FEMALE_R_MIN - 0.2
    crest_offset = FEMALE_R_VALLEY - plug_r
    helix = Helix(PITCH, PITCH * 0.95, plug_r, center=(0, 0, 0))
    profile_plane = Plane(
        origin=(plug_r, 0, 0),
        x_dir=(1, 0, 0),
        z_dir=(0, 0, 1),
    )
    pts = [
        (0, 0.30),
        (crest_offset, 0.90),
        (crest_offset, 2.10),
        (0, 2.70),
    ]
    with BuildSketch(profile_plane) as sk:
        Polygon(*pts)
    ridge = sweep(sk.sketch.faces()[0], helix)
    if not ridge.is_valid:
        return None
    return ridge.moved(Location((0, 0, z_offset)))


def _add_external_thread(part, z_start, height):
    """Fuse external thread ridges onto a cylinder."""
    turns = int(height / PITCH) + 1
    ring = None
    for turn in range(turns):
        z = z_start + turn * PITCH
        ridge = _sweep_male_turn(z)
        if ridge and ridge.is_valid:
            ring = ridge if ring is None else ring + ridge
    if ring and ring.is_valid:
        return part + ring
    return part


def _add_internal_thread_plug(base_solid, z_start, height):
    """Create internal threads by subtracting an oversized threaded plug."""
    plug_r = FEMALE_R_MIN - 0.2

    with BuildPart() as plug_body:
        Cylinder(radius=plug_r, height=20,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))

    plug = plug_body.part
    turns = int(height / PITCH) + 2
    for turn in range(turns):
        z = z_start + turn * PITCH
        ridge = _sweep_female_plug_turn(z)
        if ridge:
            plug = plug + ridge

    return base_solid - plug


def gen_base():
    """Base — smooth hole at FEMALE_R_MIN, subtract threaded plug."""
    with BuildPart() as body:
        with BuildSketch(Plane.XZ) as profile:
            with BuildLine() as outline:
                l1  = Line((0, 0),    (40, 0))
                l2  = Line(l1 @ 1,    (40, 10))
                l3  = Line(l2 @ 1,    (26, 10))
                l4  = Line(l3 @ 1,    (26, BOSS_TOP))
                # Chamfer at hole entrance
                l5  = Line(l4 @ 1,    (FEMALE_R_VALLEY + 1.0, BOSS_TOP))
                l6  = Line(l5 @ 1,    (FEMALE_R_MIN, BOSS_TOP - 1.0))
                # Hole wall at FEMALE_R_MIN (narrow core, not valley)
                l7  = Line(l6 @ 1,    (FEMALE_R_MIN, BOSS_BOT - 0.5))
                l8  = Line(l7 @ 1,    (0, BOSS_BOT - 0.5))
                l9  = Line(l8 @ 1,    (0, 0))
            make_face()
        revolve(axis=Axis.Z, revolution_arc=360)

    result = _add_internal_thread_plug(
        body.part,
        BOSS_BOT - 1.0,
        BOSS_TOP - BOSS_BOT + 2.0
    )

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
    """Cup + stem — flat rim, M20x3 threaded boss with chamfered tip."""
    with BuildPart() as body:
        with BuildSketch(Plane.XZ) as profile:
            with BuildLine() as outline:
                # Chamfer at boss tip
                l1  = Line((0, BOSS_BOT),               (MALE_R_MIN - 1.0, BOSS_BOT))
                l1a = Line(l1 @ 1,                      (MALE_R_MIN, BOSS_BOT + 1.0))
                l2  = Line(l1a @ 1,                     (MALE_R_MIN, BOSS_TOP))
                # Stem taper
                l3  = Line(l2 @ 1,                      (8, 54))
                l4  = Line(l3 @ 1,                      (18, 58))
                l5  = Line(l4 @ 1,                      (35, 80))
                l6  = Line(l5 @ 1,                      (46, 104))
                l7  = Line(l6 @ 1,                      (44, 115))
                l8  = Line(l7 @ 1,                      (36, 115))
                l9  = Line(l8 @ 1,                      (34, 108))
                l10 = Line(l9 @ 1,                      (28, 78))
                l11 = Line(l10 @ 1,                     (12, 58))
                l12 = Line(l11 @ 1,                     (0, 54))
                l13 = Line(l12 @ 1,                     (0, BOSS_BOT))
            make_face()
        revolve(axis=Axis.Z, revolution_arc=360)

    return _add_external_thread(
        body.part,
        BOSS_BOT + 0.5,
        BOSS_TOP - BOSS_BOT - THREAD_RELIEF - 0.5
    )


if __name__ == "__main__":
    from build123d import export_step, export_stl

    base = gen_base()
    export_step(base, "cad/trophy_base.step")
    export_stl(base, "cad/trophy_base.stl")

    cup = gen_cup_stem()
    export_step(cup, "cad/trophy_cup_stem.step")
    export_stl(cup, "cad/trophy_cup_stem.stl")

    print("Exported cad/trophy_base.* + cad/trophy_cup_stem.*")
