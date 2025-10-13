
import pandas as pd
from pathlib import Path
from typing import Dict, List, Union

# --- Core placement rule ---
# For each set k with size M_k and repeats R_k:
#   Block size on 384 = 96 wells
#   Offset blocks before set k = sum_{i<k} R_i
#   Repeat j of set k starts at: start = 1 + 96 * (offset_blocks + (j-1))
#   Dest wells used within that repeat: start .. start + (M_k - 1)
#
# Output schema: Source, Well, Dest, Well.1, Volume  (Source/Dest left empty)

def build_janus(
    df: pd.DataFrame,
    repeats_per_set: Dict[Union[str,int], int],
    default_volume_uL: float = 5.0,
) -> pd.DataFrame:
    # Normalize columns
    cols = {c.lower(): c for c in df.columns}
    if "setid" not in cols or ("well" not in cols and "sourcewell" not in cols):
        raise ValueError("Input must have columns: SetID and Well (1-96).")
    set_col = cols["setid"]
    well_col = cols["well"] if "well" in cols else cols["sourcewell"]
    vol_col = cols.get("volume", None)

    # Keep original order within each set as given by the file
    df = df.copy()
    # Ensure Well is numeric 1..96
    df["_Well"] = pd.to_numeric(df[well_col], errors="raise").astype(int)
    if not ((df["_Well"] >= 1) & (df["_Well"] <= 96)).all():
        bad = df.loc[~((df["_Well"] >= 1) & (df["_Well"] <= 96)), well_col].unique().tolist()
        raise ValueError(f"Found out-of-range Well values (not 1..96): {bad}")

    # Group by SetID in ascending order of first appearance
    # Preserve the input order of sets as they appear in the file
    set_order = pd.unique(df[set_col])
    # Build rows
    rows = []
    prior_blocks = 0  # accumulated repeats from previous sets
    for set_id in set_order:
        block_repeats = int(repeats_per_set.get(str(set_id), repeats_per_set.get(int(set_id), 1)))
        subset = df[df[set_col] == set_id].copy()
        # Use the current row order as the sequence within the set
        wells_src = subset["_Well"].tolist()
        # Optional per-row volume, else default
        vols = None
        if vol_col is not None and vol_col in df.columns:
            vols = pd.to_numeric(subset[vol_col], errors="coerce").fillna(default_volume_uL).tolist()

        M = len(wells_src)
        for j in range(1, block_repeats + 1):
            start = 1 + 96 * (prior_blocks + (j - 1))
            # Assign destination wells for the first M positions
            dest_wells = list(range(start, start + M))
            for i, src_well in enumerate(wells_src):
                rows.append({
                    "Source": "",
                    "Well": int(src_well),
                    "Dest": "",
                    "Well.1": int(dest_wells[i]),
                    "Volume": float(vols[i] if vols is not None else default_volume_uL),
                    "SetID": set_id,
                    "Repeat": j,
                })
        # After finishing this set, advance prior_blocks by its repeat count
        prior_blocks += block_repeats

    out = pd.DataFrame(rows, columns=["Source","Well","Dest","Well.1","Volume","SetID","Repeat"])
    return out

def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)

#if __name__ == "__main__":
    #import argparse, json
    #ap = argparse.ArgumentParser(description="Generate JANUS CSV from sets + repeats.")
    #ap.add_argument("--input", required=True, help="CSV/XLSX with columns: SetID, Well (1-96), optional Volume")
    #ap.add_argument("--repeats", required=True, help="JSON mapping of SetID -> repeats, e.g. '{\"1\":3, \"2\":2}'")
    #ap.add_argument("--default_volume", type=float, default=5.0, help="Default volume (uL) if Volume column absent")
    #ap.add_argument("--output", default="janus_generated.csv", help="Output CSV filename")
    #args = ap.parse_args()

    #table = load_table(Path(args.input))
    #repeats = json.loads(args.repeats)

    #out = build_janus(table, repeats_per_set=repeats, default_volume_uL=args.default_volume)
    #out.to_csv(args.output, index=False)
    #print(f"Wrote {args.output} with {len(out)} rows.")
if __name__ == "__main__":
    import json
    from pathlib import Path

    print("=== JANUS Worklist Generator ===")

    # ask for input file
    input_path = input("Enter path to your order file (.csv or .xlsx): ").strip()
    if not input_path:
        raise SystemExit("No file path provided.")
    table = load_table(Path(input_path))

    # ask for repeats mapping interactively
    print("\nEnter repeats per SetID (e.g., '1:3,2:2,3:1'):")
    raw = input("Repeats → ").strip()
    if not raw:
        raise SystemExit("No repeats provided.")
    repeats = {}
    for part in raw.split(","):
        if ":" in part:
            sid, val = part.split(":")
            repeats[sid.strip()] = int(val)

    # ask for optional volume and output path
    vol = input("Default volume in µL [default 5]: ").strip()
    default_vol = float(vol) if vol else 5.0
    output_path = input("Output filename [janus_generated.csv]: ").strip() or "janus_generated.csv"

    out = build_janus(table, repeats_per_set=repeats, default_volume_uL=default_vol)
    from pathlib import Path
output_path = str(Path(input_path).parent / (output_path or "janus_generated.csv"))
out.to_csv(output_path, index=False)

print(f"\n✅ Wrote {output_path} with {len(out)} rows.")
#triggered
