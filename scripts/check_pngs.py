from pathlib import Path
d = Path("data/processed/tutor/variant_diagrams/4.1")
if d.exists():
    pngs = sorted(d.glob("*.png"))
    print(f"\nPNGs on disk: {len(pngs)}")
    for p in pngs[:5]:
        print(f"  {p}  ({p.stat().st_size} bytes)")
else:
    print("\nNo PNGs on disk — need to re-run renderer")
