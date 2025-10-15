
import pandas as pd
from pathlib import Path

def load_table(path: Path) -> pd.DataFrame:
    """Load Excel or CSV file."""
    if path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    # Normalize column names
    df.columns = [str(c).strip().capitalize() for c in df.columns]
    return df

def build_janus_v2(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Plate + Number → JANUS format."""
    required = {"Plate", "Number"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing columns: {required - set(df.columns)}")

    df = df.dropna(subset=["Plate", "Number"]).copy()
    df["Number"] = df["Number"].astype(int)

    n = len(df)
    dest_wells = list(range(1, n + 1))

    out = pd.DataFrame({
        "Source": df["Plate"],
        "Well_src": df["Number"],
        "Dest": ["384-1"] * n,
        "Well_dst": dest_wells,
        "Volume": [5] * n
    })

    return out

def write_janus_csv(df: pd.DataFrame, output_path: Path):
    """Write CSV with duplicate 'Well' headers."""
    df.to_csv(output_path, index=False, header=["Source", "Well", "Dest", "Well", "Volume"])

if __name__ == "__main__":
    print("=== JANUS Converter v2 ===")
    input_path = input("Path to order platemap (.csv or .xlsx): ").strip()
    if not input_path:
        raise SystemExit("No input file provided.")

    df = load_table(Path(input_path))
    out = build_janus_v2(df)
    output_path = Path(input_path).with_name(Path(input_path).stem + "_JANUS.csv")
    write_janus_csv(out, output_path)

    print(f"\n✅ Done: {len(out)} wells mapped → 384-1\nSaved as: {output_path}")
