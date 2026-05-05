# Trophy

Parametric trophy model generated with [build123d](https://github.com/gumyr/build123d).

## Variants

| File | Description |
|------|-------------|
| `trophy.py` | Single-piece trophy (narrow stem, wide cup, handles) |
| `trophy_two_part.py` | Two-part screw-together trophy (M20×3 threads) |

## Two-part assembly

```
Base                          Cup+Stem
┌──────────────────┐ Z=14     ┌──────────────────┐ Z=115
│  flat annulus    │          │    cup bowl      │
│  ╔══════════╗    │          │    tapered stem  │
│  ║ M20×3    ║    │  ────►   │  ╔══════════╗    │
│  ║ threaded ║    │  screw   │  ║ M20×3    ║    │
│  ║  hole    ║    │          │  ║ threaded ║    │
│  ╚══════════╝    │          │  ║  boss    ║    │
│  flat bottom     │ Z=0      │  ╚══════════╝    │ Z=2
└──────────────────┘          └──────────────────┘
```

- **Thread:** M20×3 coarse pitch, 10mm engagement, 0.25mm radial clearance
- **Base:** 80×80×14mm — print flat-bottom down
- **Cup+Stem:** 92×92×118mm — print upside-down (flat rim on bed)

## Exports

Pre-built CAD files in `cad/`:

- `trophy.step` / `.stl` — single-piece
- `trophy_base.step` / `.stl` — base part
- `trophy_cup_stem.step` / `.stl` — cup + stem part

## Regeneration

Requires Python 3.11+ with build123d:

```bash
pip install build123d
python trophy.py                    # single-piece
python trophy_two_part.py           # two-part (exports STEP + STL)
```
