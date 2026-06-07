import pandas as pd
import os

def clean_order_platemap(input_path):
    # Load the Excel file
    df = pd.read_excel(input_path)

    # Columns to remove
    cols_to_remove = ["Order ID", "eLN", "User", "Description", "Note"]
    df = df.drop(columns=[col for col in cols_to_remove if col in df.columns], errors="ignore")

    # Add Number column (1–N per unique Plate)
    if "Plate" in df.columns:
        df["Number"] = df.groupby("Plate").cumcount() + 1
    else:
        print("⚠️ Warning: 'Plate' column not found. Numbering globally instead.")
        df["Number"] = range(1, len(df) + 1)

    # Add empty Set column
    df["Set"] = ""

    # Create output path
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_Cleaned{ext}"

    # Save to Excel
    df.to_excel(output_path, index=False)
    print(f"✅ Cleaned file saved to: {output_path}")

# === Example Usage ===
# clean_order_platemap("C:/path/to/OrderPlatemap.xlsx")
