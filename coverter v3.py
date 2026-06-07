import pandas as pd
import os

def clean_order_platemap(input_path):
    """
    Cleans a Store Order Platemap Excel file:
    - Removes unnecessary columns
    - Adds 'Number' (1–N per plate)
    - Adds empty 'Set' column
    - Saves a cleaned Excel file next to the original
    """

    print(f"\n📂 Loading file: {input_path}")

    # Load the Excel file
    df = pd.read_excel(input_path)

    # Columns to remove
    cols_to_remove = ["Order ID", "eLN", "User", "Description", "Note"]
    df = df.drop(columns=[col for col in cols_to_remove if col in df.columns], errors="ignore")

    # Add 'Number' column (1–N per Plate)
    if "Plate" in df.columns:
        df["Number"] = df.groupby("Plate").cumcount() + 1
    else:
        print("⚠️ 'Plate' column not found — numbering globally instead.")
        df["Number"] = range(1, len(df) + 1)

    # Add empty 'Set' column
    df["Set"] = ""

    # Save cleaned Excel
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_Cleaned{ext}"
    df.to_excel(output_path, index=False)

    print(f"✅ Cleaned file saved to: {output_path}\n")


if __name__ == "__main__":
    print("=== ADME T2 Order Platemap Converter ===\n")

    # Prompt user for file path
    file_path = input("📄 Please type the full path to your Order Platemap Excel file: ").strip()

    # Check that the file exists
    if os.path.exists(file_path):
        clean_order_platemap(file_path)
    else:
        print(f"❌ File not found at:\n{file_path}\nPlease check your path and try again.")
