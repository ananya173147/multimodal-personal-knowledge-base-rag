from fastapi import FastAPI, UploadFile, Form
from docparser import DocParser
from chunkers import Chunker
from imageprocessing import ImageProcessor
from doc_qa import QA, indexing
from glob import glob
from pathlib import Path
import os, json, hashlib
from dotenv import find_dotenv, load_dotenv
from langchain_core.documents import Document

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
    # Convert Document object to a dictionary
    return {
        "metadata": doc.metadata,
        "page_content": doc.page_content
    }

def dict_to_document(doc_dict):
    # Assuming you have a Document constructor or factory method
    return Document(metadata=doc_dict["metadata"], page_content=doc_dict["page_content"])

cache = load_cache()

# app = FastAPI()
# client = Weaviate.embedded()
# embed_model = OpenAIEmbedding("text-embedding-ada-002")
# vector_store = Weaviate(client)


# @app.post("/upload")
# async def upload_file(file: UploadFile):
#     with open(file.filename, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     pipeline(file.filename, "pdf_parser", "semantic", "agentic")
#     return {"message": f"{file.filename} processed and indexed!"}

# @app.post("/upload")
# async def upload_file(files: list[UploadFile]):
#     for file in files:
#         with open(file.filename, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#         pipeline(file.filename, "pdf_parser", "semantic", "agentic")
#     return {"message": "All files processed and indexed!"}



load_dotenv(find_dotenv('var.env'), verbose=True)

LLAMA_CLOUD_API_KEY=os.getenv('LLAMA_CLOUD_API_KEY')
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
TAVILY_API_KEY=os.getenv('TAVILY_API_KEY')
GOOGLE_CLOUD_PROJECT=os.getenv('GOOGLE_CLOUD_PROJECT')

def list_supported_files(inputPath, supported_extensions=[".pdf"]):
    # file_list = glob(inputPath)
    file_list = glob(f"{inputPath}/**", recursive=True)
    # print(glob(inputPath))
    return [f for f in file_list if Path(f).suffix in supported_extensions]


def pipeline(inputPath = "/multimodal-personal-knowledge-base/Documents/", parser_name = "LlamaParse", chunking_strategy = "semantic"):
    parser = DocParser(parser_name)
    chunker = Chunker(chunking_strategy)
    image_processor = ImageProcessor()

    files_list = list_supported_files(inputPath)
    print(f"Found {len(files_list)} files.")
    chunks, image_documents = [], []

    for file_path in files_list:
        file_hash = hash_file(file_path)
    
        if file_hash in cache:
            cached_data = cache[file_hash]
            print(f"Skipping {file_path} (Already processed)")
            
            c_chunks = [dict_to_document(doc_dict) for doc_dict in cached_data["chunks"]]
            c_image_docs = [dict_to_document(doc_dict) for doc_dict in cached_data["image_docs"]]
    
            chunks.extend(c_chunks)
            image_documents.extend(c_image_docs)
            continue
    
        print(f"\nProcessing {file_path}...")
        try:
            # Parse the document
            text_docs = parser.parsing_function(file_path)
    
            # Extract tables (only if not cached)
            if not cache.get(file_hash, {}).get("tables_extracted", False):
                parser.extract_tables(file_path)
    
            # Chunking
            file_chunks = chunker.build_chunks(text_docs, file_path)
            
            chunks.extend(file_chunks)
            
            # Process images
            file_images = image_processor.get_image_documents()
            image_documents.extend(file_images)
    
            # Cache results
            cache[file_hash] = {
                "file_path": file_path,
                "timestamp": os.path.getmtime(file_path),
                "chunks": [document_to_dict(doc) for doc in file_chunks],
                "image_docs": [document_to_dict(doc) for doc in file_images],
                "tables_extracted": True,
            }
            save_cache(cache)
            
        except Exception as e:
            print(f"Failed to process {file_path}: {e}")


    doc_indexing = indexing()
    retriever = doc_indexing.index_documents(chunks + image_documents)

    qa = QA(retriever)
    qa.query()
        
pipeline(inputPath="C:/Users/anany/Desktop/Work/Python/Multimodal PKB/multimodal-personal-knowledge-base/Documents", parser_name = "pymupdf4llm", chunking_strategy = "semantic")        
