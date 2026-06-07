
import pandas as pd
from pathlib import Path

BLOCK = 96  # Each 384-well plate has 4 x 96-well blocks

def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)

def parse_repeats(text: str):
    """Parse repeats mapping like '1:3,2:2,3:1' into dict {'1': 3, '2': 2, '3': 1}"""
    result = {}
    for part in text.split(","):
        if ":" not in part:
            continue
        key, val = part.split(":", 1)
        key = key.strip()
        val = val.strip()
        result[key] = int(val)
    return result

def build_janus_v2(df: pd.DataFrame, repeats_per_set: dict) -> pd.DataFrame:
    """Build JANUS output file based on Set, Plate, and Number columns."""
    required = {"Set", "Plate", "Number"}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        raise ValueError(f"Missing columns: {missing}. Expected columns: {required}")

    df = df.dropna(subset=["Plate", "Number"]).copy()
    df["Number"] = df["Number"].astype(int)

    sets = df["Set"].unique().tolist()
    rows = []
    prior_blocks = 0

    for set_id in sets:
        subset = df[df["Set"] == set_id].copy()
        subset = subset.sort_values(by="Number", kind="mergesort")
        wells_src = subset["Number"].tolist()
        plates = subset["Plate"].tolist()

        repeats = int(repeats_per_set.get(str(set_id), 1))
        M = len(wells_src)

        for j in range(repeats):
            start = 1 + BLOCK * (prior_blocks + j)
            dest_wells = list(range(start, start + M))

            for i in range(M):
                rows.append({
                    "Source": plates[i],
                    "Well_src": wells_src[i],
                    "Dest": "384-1",
                    "Well_dst": dest_wells[i],
                    "Volume": 5
                })
        prior_blocks += repeats

    out = pd.DataFrame(rows, columns=["Source", "Well_src", "Dest", "Well_dst", "Volume"])
    return out

def write_janus_csv(df: pd.DataFrame, output_path: Path):
    """Write output CSV with duplicate 'Well' headers."""
    df = df[["Source", "Well_src", "Dest", "Well_dst", "Volume"]].copy()
    df.to_csv(output_path, index=False, header=["Source", "Well", "Dest", "Well", "Volume"])

if __name__ == "__main__":
    print("=== JANUS Generator v2 ===")
    input_path = input("Path to order platemap (.csv or .xlsx): ").strip()
    if not input_path:
        raise SystemExit("No input file provided.")

    df = load_table(Path(input_path))

    print("Detected Sets:", sorted(df["Set"].unique().tolist()))
    repeats_text = input("Repeats per Set (e.g., '1:3,2:2,3:1'): ").strip()
    repeats = parse_repeats(repeats_text)

    out = build_janus_v2(df, repeats_per_set=repeats)
    output_path = Path(input_path).with_name(Path(input_path).stem + "_JANUS.csv")
    write_janus_csv(out, output_path)

    print(f"\n✅ Done. Wrote {len(out)} rows to: {output_path}")
