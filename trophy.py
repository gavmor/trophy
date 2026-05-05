"""Trophy — narrow stem, wide cup, symmetrical handles."""

from build123d import *
from math import degrees

def gen_step():
    # ── Main body (revolved profile) ──
    with BuildPart() as body:
        with BuildSketch(Plane.XZ) as profile:
            with BuildLine() as outline:
                l1  = Line((0, 0),   (40, 0))
                l2  = Line(l1 @ 1,   (40, 10))
                l3  = Line(l2 @ 1,   (26, 10))
                l4  = Line(l3 @ 1,   (26, 14))
                l5  = Line(l4 @ 1,   (8, 54))
                l6  = Line(l5 @ 1,   (18, 58))
                l7  = Line(l6 @ 1,   (35, 80))
                l8  = Line(l7 @ 1,   (46, 104))
                l9  = Line(l8 @ 1,   (44, 115))
                l10 = Line(l9 @ 1,   (36, 115))
                l11 = Line(l10 @ 1,  (34, 108))
                l12 = Line(l11 @ 1,  (28, 78))
                l13 = Line(l12 @ 1,  (12, 58))
                l14 = Line(l13 @ 1,  (0, 54))
                l15 = Line(l14 @ 1,  (0, 0))
            make_face()
        revolve(axis=Axis.Z, revolution_arc=360)

    # ── Handle profile (D-shape on XZ plane, +X side, ~1mm into cup wall) ──
    with BuildPart() as handle_half:
        with BuildSketch(Plane.XZ):
            with BuildLine() as hl:
                l1 = Spline([(42, 96), (50, 90), (56, 82), (50, 75), (29, 74)])
                l2 = Spline([(29, 74), (31, 77), (35, 82), (38, 88), (40, 93)])
                l3 = Line(l2 @ 1, l1 @ 0)
            make_face()
        extrude(amount=2)

    handle_half_mirrored = mirror(handle_half.part, Plane.XZ)
    handle_right = handle_half.part + handle_half_mirrored
    handle_left = mirror(handle_right, Plane.YZ)

    # ── Boolean union ──
    trophy = body.part + handle_right + handle_left

    # ── Fillets on handle-to-cup intersection edges ──
    for edge in trophy.edges():
        if not edge.is_closed:
            continue
        c = edge.center()
        length = edge.length
        if not (70 < c.Z < 100):
            continue
        if length < 5 or length > 80:
            continue
        radial = (c.X**2 + c.Y**2)**0.5
        if not (25 < radial < 48):
            continue
        try:
            fillet(edge, 1.2)
        except Exception:
            pass

    return trophy


if __name__ == "__main__":
    from build123d import export_step, export_stl
    part = gen_step()
    export_step(part, "cad/trophy.step")
    export_stl(part, "cad/trophy.stl")
    print("Exported cad/trophy.step + cad/trophy.stl")
