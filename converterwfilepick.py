import pandas as pd
import os
from tkinter import Tk, filedialog

def clean_order_platemap(input_path):
    """
    Cleans a Store Order Platemap Excel file:
    - Removes unnecessary columns
    - Adds 'Number' (1–N per plate)
    - Adds empty 'Set' column
    - Saves a cleaned Excel file next to the original
    """

    print(f"📂 Loading file: {input_path}")

    # Load Excel file
    df = pd.read_excel(input_path)

    # Columns to remove
    cols_to_remove = ["Order ID", "eLN", "User", "Description", "Note"]
    df = df.drop(columns=[col for col in cols_to_remove if col in df.columns], errors="ignore")

    # Add Number column (1–N per Plate)
    if "Plate" in df.columns:
        df["Number"] = df.groupby("Plate").cumcount() + 1
    else:
        print("⚠️ 'Plate' column not found — numbering globally instead.")
        df["Number"] = range(1, len(df) + 1)

    # Add empty Set column
    df["Set"] = ""

    # Build output filename
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_Cleaned{ext}"

    # Save to Excel
    df.to_excel(output_path, index=False)
    print(f"✅ Cleaned file saved to: {output_path}\n")


if __name__ == "__main__":
    print("=== ADME T2 Order Platemap Converter ===\n")

    # 🟢 OPTION 1: GUI file picker
    use_gui = True   # 👈 change to False to use text input instead

    if use_gui:
        # GUI file selection
        root = Tk()
        root.withdraw()  # Hide the main window

        file_path = filedialog.askopenfilename(
            title="Select Order Platemap Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )

        if file_path:
            clean_order_platemap(file_path)
        else:
            print("❌ No file selected. Exiting.")

    else:
        # 🧑‍💻 OPTION 2: Terminal text input
        file_path = input("📄 Enter or drag in the full path to your OrderPlatemap Excel file: ").strip()
        file_path = file_path.strip('"').strip("'")  # remove extra quotes if dragged in

        if os.path.exists(file_path):
            clean_order_platemap(file_path)
        else:
            print("❌ File not found. Please check your path and try again.")
