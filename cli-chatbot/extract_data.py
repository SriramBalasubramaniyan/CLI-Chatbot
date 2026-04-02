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
    cursor = conn.cursor()

    text = ""

    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    for table_name in tables:
        table = table_name[0]
        text += f"\n===== Table: {table} =====\n"
        
        columns_info = cursor.execute(f"PRAGMA table_info({table})").fetchall()
        columns = [col[1] for col in columns_info]  # col[1] = column name

        rows = cursor.execute(f"SELECT * FROM {table}").fetchall()

        for row in rows:
            text += " | ".join([f"{col}: {val}" for col, val in zip(columns, row)]) + "\n"

    conn.close()
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