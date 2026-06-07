
import pandas as pd
from pathlib import Path

def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)

def build_janus_base(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic converter: Plate -> Source, Set -> Number -> Well, sequential dest wells.
    """
    if "Plate" not in df.columns or "Set" not in df.columns:
        raise ValueError("Expected columns: Plate, Set")

    df = df.dropna(subset=["Plate", "Set"]).copy()
    df["Set"] = df["Set"].astype(int)

    n = len(df)
    dest_wells = list(range(1, n + 1))

    out = pd.DataFrame({
        "Source": df["Plate"],
        "Well_src": df["Set"],
        "Dest": ["384-1"] * n,
        "Well_dst": dest_wells,
        "Volume": [5] * n
    })

    return out

def write_janus_csv(df: pd.DataFrame, output_path: Path):
    """Write CSV with duplicate Well headers."""
    df.to_csv(output_path, index=False, header=["Source", "Well", "Dest", "Well", "Volume"])

if __name__ == "__main__":
    print("=== JANUS Base Converter ===")
    input_path = input("Path to order platemap (.csv or .xlsx): ").strip()
    if not input_path:
        raise SystemExit("No input file provided.")

    df = load_table(Path(input_path))
    out = build_janus_base(df)
    output_path = Path(input_path).with_name(Path(input_path).stem + "_JANUS.csv")
    write_janus_csv(out, output_path)

    print(f"\n✅ Done. Wrote {len(out)} rows to: {output_path}")
