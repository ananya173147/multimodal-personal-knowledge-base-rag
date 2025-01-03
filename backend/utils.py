import pandas as pd
import os, json, hashlib
from langchain_core.documents import Document
from pathlib import Path

CACHE_FILE = "./cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def hash_file(file_path):
    """Generate MD5 hash for a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def document_to_dict(doc):
    return {
        "metadata": doc.metadata,
        "page_content": doc.page_content
    }

def dict_to_document(doc_dict):
    return Document(metadata=doc_dict["metadata"], page_content=doc_dict["page_content"])

def process_csv(file_path):
    df = pd.read_csv(file_path)
    content = df.to_string(index=False)
    return Document(page_content=content, metadata={"source": Path(file_path).name})

def process_xlsx(file_path):
    dfs = pd.read_excel(file_path, sheet_name=None)
    documents = []
    for sheet, df in dfs.items():
        content = df.to_string(index=False)
        documents.append(Document(page_content=content, metadata={"source": f"{Path(file_path).name} - {sheet}"}))
    return documents