import os
import pdfplumber
import pandas as pd
from docx import Document
import sqlite3

def convert_to_text(file_path):
    ext = file_path.lower().split('.')[-1]

    if ext == "pdf":
        return parse_pdf(file_path)
    elif ext in ["xls", "xlsx"]:
        return parse_excel(file_path)
    elif ext == "csv":
        return parse_csv(file_path)
    elif ext == "docx":
        return parse_docx(file_path)
    elif ext == "db":
        return parse_sqlite(file_path)
    else:
        return parse_plain_text(file_path)


def parse_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def parse_excel(file_path):
    text = ""
    xls = pd.ExcelFile(file_path)

    for sheet in xls.sheet_names:
        df = xls.parse(sheet)

        columns = df.columns.tolist()

        for _, row in df.iterrows():
            row_text = " | ".join(
                [f"{col}: {row[col]}" for col in columns if pd.notna(row[col])]
            )
            text += f"Sheet {sheet}: {row_text}\n"

    return text

def parse_csv(file_path):
    df = pd.read_csv(file_path)
    
    text = ""
    columns = df.columns.tolist()
    
    for _, row in df.iterrows():
        row_text = " | ".join(
            [f"{col}: {row[col]}" for col in columns if pd.notna(row[col])]
        )
        text += row_text + "\n"

    return df.to_string(index=False)


def parse_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def parse_sqlite(file_path):
    conn = sqlite3.connect(file_path)
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

def parse_plain_text(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def save_as_txt(text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def process_file(file_path):
    text = convert_to_text(file_path)

    parent_dir = os.path.dirname(os.path.dirname(file_path))
    output_folder = os.path.join(parent_dir, "extract")
    
    os.makedirs(output_folder, exist_ok=True)

    output_file = os.path.join(output_folder, os.path.basename(file_path) + ".txt")
    save_as_txt(text, output_file)

    print(f"✅ Converted: {output_file}")

def process_folder(folder_path):
    for file in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file)

        ext = os.path.splitext(file)[1].lower().replace('.', '')
        
        if ext == "txt": 
            continue

        if os.path.isfile(full_path):
            try:
                process_file(full_path)
            except Exception as e:
                print(f"❌ Error processing {file}: {e}")

process_folder("source")