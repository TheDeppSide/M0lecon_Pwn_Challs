#!/usr/bin/env python3
import argparse
from datetime import datetime, timezone

def minutes(hhmm: str) -> int:
    hh, mm = hhmm.split(":")
    h = int(hh); m = int(mm)
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError("Invalid time format HH:MM (00<=HH<24, 00<=MM<60)")
    return h*60 + m

def norm_minutes(m: int) -> int:
    m %= 1440
    return m

def wrap_lon(lon: float) -> float:
    # Normalize to [-180, 180]
    while lon < -180.0:
        lon += 360.0
    while lon > 180.0:
        lon -= 360.0
    return lon

def compute_lon(target_hhmm: str, utc_hhmm: str | None) -> float:
    T = minutes(target_hhmm)
    if utc_hhmm is None:
        now = datetime.now(timezone.utc)
        U = now.hour*60 + now.minute
    else:
        U = minutes(utc_hhmm)
    # local_from_lon ≈ UTC + lon*4min/°  => lon ≈ (T - U)/4
    delta = ((T - U + 720) % 1440) - 720  # put in [-720, 719]
    lon = delta / 4.0
    return wrap_lon(lon)

def main():
    ap = argparse.ArgumentParser(description="Reverse target time to lat/lon for the 'catch me if you can' gate.")
    ap.add_argument("--target", required=True, help="Target local time HH:MM (from banner)")
    ap.add_argument("--utc", help="UTC time HH:MM (if omitted, uses current UTC from your system)")
    ap.add_argument("--lat", type=float, default=0.0, help="Latitude to use (default 0.0). You can choose anything in [-90,90].")
    ap.add_argument("--size", type=int, default=128, help="Optional size_hint to append on latitude line (default 128).")
    ap.add_argument("--print-only", action="store_true", help="Print computed lat/lon without prompts format.")
    args = ap.parse_args()

    lon = compute_lon(args.target, args.utc)
    lat = args.lat
    if lat < -90 or lat > 90:
        raise SystemExit("Latitude must be within [-90,90].")

    if args.print-only:
        print(f"lat={lat:.6f}")
        print(f"lon={lon:.6f}")
        return

    # Output exactly in the format the binary expects at the prompts:
    # First line: latitude with optional size hint; Second line: longitude
    print(f"{lat:.6f} {args.size}")
    print(f"{lon:.6f}")

if __name__ == "__main__":
    main()

# # Con UTC preso dal tuo sistema
# python3 reverse.py --target 19:45 --lat 0.0 --size 4096

# # Specificando anche l'UTC (utile se vuoi essere esplicito)
# python3 reverse.py --target 19:45 --utc 17:12 --lat 12.34 --size 8192

# # Solo stampa i valori (senza formattare per i prompt)
# python3 reverse.py --target 19:45 --print-only
