from typing import Union
from pathlib import Path
from io import BytesIO
import os

from docx import Document
import pandas as pd
import pdfplumber

def extract_text_from_file(file: Union[BytesIO, Path], filename: str = "") -> str:
    if isinstance(file, Path):
        filename = file.name
        with open(file, 'rb') as f:
            stream = BytesIO(f.read())
    elif isinstance(file, BytesIO):
        stream = file
    else:
        raise ValueError("Неподдерживаемый тип входного файла")

    ext = os.path.splitext(filename)[-1].lower()

    try:
        if ext == ".docx":
            doc = Document(stream)
            return "\n".join([para.text for para in doc.paragraphs])

        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(stream, engine="openpyxl")
            return df.to_csv(index=False)

        elif ext == ".csv":
            df = pd.read_csv(stream)
            return df.to_csv(index=False)

        elif ext == ".pdf":
            text = ""
            with pdfplumber.open(stream) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text.strip()

        elif ext == ".txt":
            return stream.read().decode("utf-8")

        else:
            return f"[❌ Неподдерживаемый формат файла: {ext}]"

    except Exception as e:
        return f"[⚠️ Ошибка при обработке файла: {str(e)}]"


test_file = Path("docs/test.docx")  # или .pdf, .xlsx и т.д.

text = extract_text_from_file(test_file)
print("Извлечённый текст:")
print(text)
