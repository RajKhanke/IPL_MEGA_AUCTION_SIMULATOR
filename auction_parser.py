import pdfplumber
import pandas as pd

pdf_path = r"auction.pdf"
csv_path = "ipl_auction.csv"

all_tables = []

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        if table:
            df = pd.DataFrame(table[1:], columns=table[0])
            all_tables.append(df)

# Merge all pages
final_df = pd.concat(all_tables, ignore_index=True)

# Save to CSV
final_df.to_csv(csv_path, index=False)

print("✅ Converted to CSV successfully!")