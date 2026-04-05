import os
import shutil
import pdfplumber
import pandas as pd
from docx import Document
import sqlite3

def convert_to_text(source_file_path):
    ext = source_file_path.lower().split('.')[-1]

    if ext == "pdf":
        return parse_pdf(source_file_path)
    elif ext in ["xls", "xlsx"]:
        return parse_excel(source_file_path)
    elif ext == "csv":
        return parse_csv(source_file_path)
    elif ext == "docx":
        return parse_docx(source_file_path)
    elif ext == "db":
        return parse_sqlite(source_file_path)
    else:
        return parse_plain_text(source_file_path)


def parse_pdf(source_file_path):
    text = ""
    with pdfplumber.open(source_file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def parse_excel(source_file_path):
    text = ""
    xls = pd.ExcelFile(source_file_path)

    for sheet in xls.sheet_names:
        df = xls.parse(sheet)

        columns = df.columns.tolist()

        for _, row in df.iterrows():
            row_text = " | ".join(
                [f"{col}: {row[col]}" for col in columns if pd.notna(row[col])]
            )
            text += f"Sheet {sheet}: {row_text}\n"

    return text

def parse_csv(source_file_path):
    df = pd.read_csv(source_file_path)
    
    text = ""
    columns = df.columns.tolist()
    
    for _, row in df.iterrows():
        row_text = " | ".join(
            [f"{col}: {row[col]}" for col in columns if pd.notna(row[col])]
        )
        text += row_text + "\n"

    return df.to_string(index=False)


def parse_docx(source_file_path):
    doc = Document(source_file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def parse_sqlite(source_file_path):
    conn = sqlite3.connect(source_file_path)
    conn.row_factory = sqlite3.Row  # Allows column name access
    cursor = conn.cursor()

    # ── Step 1: Load ALL tables into memory first (needed for FK resolution) ──
    all_data = {}
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    for (table,) in tables:
        columns_info = cursor.execute(f"PRAGMA table_info({table})").fetchall()
        columns = [col[1] for col in columns_info]
        rows = cursor.execute(f"SELECT * FROM {table}").fetchall()
        all_data[table] = {
            "columns": columns,
            "rows": [dict(zip(columns, row)) for row in rows]
        }

    # ── Step 2: Build FK map  {table: [(fk_col, ref_table, ref_col)]} ──
    fk_map = {}
    for table in all_data:
        fk_info = cursor.execute(f"PRAGMA foreign_key_list({table})").fetchall()
        fk_map[table] = [
            (fk[3], fk[2], fk[4])   # (from_col, to_table, to_col)
            for fk in fk_info
        ]

    conn.close()

    # ── Step 3: Helper — resolve a FK code to a human-readable name ──
    def resolve_fk(ref_table, ref_col, ref_val):
        if ref_table not in all_data:
            return None

        ref_columns = all_data[ref_table]["columns"]

        # Auto-detect: any column whose name contains "name" (case-insensitive)
        name_cols = [c for c in ref_columns if "name" in c.lower()]

        for row in all_data[ref_table]["rows"]:
            if str(row.get(ref_col)) == str(ref_val):
                # Try auto-detected name columns first
                for col in name_cols:
                    if row.get(col):
                        return row[col]
                # Final fallback: first non-empty, non-id column
                for col, val in row.items():
                    if col != ref_col and val:
                        return str(val)
        return None

    # ── Step 4: Render each table into clean readable text ──
    text = ""

    for table, data in all_data.items():
        if not data["rows"]:
            continue  # Skip empty tables

        text += f"\n{'='*50}\n"
        text += f"  {table.upper()}\n"
        text += f"{'='*50}\n"

        fks = fk_map.get(table, [])
        fk_cols = {fk[0]: (fk[1], fk[2]) for fk in fks}  # {col: (ref_table, ref_col)}

        for row in data["rows"]:
            fields = []
            for col, val in row.items():
                # ── Skip empty / None values ──
                if val is None or str(val).strip() == "":
                    continue

                # ── Resolve FK to human-readable name ──
                if col in fk_cols:
                    ref_table, ref_col = fk_cols[col]
                    resolved = resolve_fk(ref_table, ref_col, val)
                    if resolved:
                        fields.append(f"{col}: {resolved} (id: {val})")
                        continue

                fields.append(f"{col}: {val}")

            if fields:
                text += "• " + " | ".join(fields) + "\n"

        text += "\n"

    return text

def parse_plain_text(source_file_path):
    with open(source_file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def save_as_txt(text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def process_file(source_file_path, extract_folder_path):
    text = convert_to_text(source_file_path)

    parent_dir = os.path.dirname(os.path.dirname(source_file_path))
    output_folder = os.path.join(parent_dir, extract_folder_path)
    
    os.makedirs(output_folder, exist_ok=True)

    output_file = os.path.join(output_folder, os.path.basename(source_file_path) + ".txt")
    save_as_txt(text, output_file)

    print(f"✅ Converted: {output_file}")

def process_folder(source_folder_path, extract_folder_path):
    parent_dir = os.path.dirname(source_folder_path)
    output_folder = os.path.join(parent_dir, extract_folder_path)
    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(source_folder_path):
        full_path = os.path.join(source_folder_path, file)

        if not os.path.isfile(full_path):
            continue

        ext = os.path.splitext(file)[1].lower().replace('.', '')
        output_text_path = os.path.join(output_folder, file + ".txt")

        if ext == "txt":
            dest_path = os.path.join(output_folder, file)
            if os.path.exists(dest_path):
                print(f"⏭️ Skipped existing txt: {dest_path}")
                continue
            try:
                shutil.copy2(full_path, dest_path)
                print(f"✅ Copied txt: {dest_path}")
            except Exception as e:
                print(f"❌ Error copying txt {file}: {e}")
            continue

        if os.path.exists(output_text_path):
            print(f"⏭️ Skipped already processed: {output_text_path}")
            continue

        try:
            process_file(full_path, extract_folder_path)
            print(f"✅ Processed file: {full_path}")
        except Exception as e:
            print(f"❌ Error processing {file}: {e}")

if __name__ == "__main__":
    process_folder(source_folder_path="source", extract_folder_path="extract")