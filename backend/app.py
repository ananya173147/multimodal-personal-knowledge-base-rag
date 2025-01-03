from fastapi import FastAPI, UploadFile, Form
from docparser import DocParser
from chunkers import Chunker
from imageprocessing import ImageProcessor
from doc_qa import QA, indexing
from glob import glob
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import os
from utils import *


CACHE_FILE = "./cache.json"
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

def list_supported_files(inputPath, supported_extensions=[".pdf", ".png", ".jpg", ".csv", ".xlsx"]):
    file_list = glob(f"{inputPath}/**", recursive=True)
    return [f for f in file_list if Path(f).suffix in supported_extensions]


def pipeline(inputPath="/multimodal-personal-knowledge-base/Documents/", 
             parser_name="LlamaParse", 
             chunking_strategy="semantic"):
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
            # Handle PDF documents
            if file_path.endswith(".pdf"):
                text_docs = parser.parsing_function(file_path)
                
                # Extract tables (if not cached)
                if not cache.get(file_hash, {}).get("tables_extracted", False):
                    parser.extract_tables(file_path)
                
                # Chunking
                file_chunks = chunker.build_chunks(text_docs, file_path)
                chunks.extend(file_chunks)
            
            # Handle PNG/JPG images
            elif file_path.endswith(('.png', '.jpg')):
                img_base64 = image_processor.encode_image(file_path)
                summary = image_processor.image_summarize(img_base64)
                
                image_doc = Document(
                    page_content=summary,
                    metadata={"source": Path(file_path).name}
                )
                image_documents.append(image_doc)
            
            elif file_path.endswith(".csv"):
                doc = process_csv(file_path)
                chunks.append(doc)
            
            elif file_path.endswith(".xlsx"):
                docs = process_xlsx(file_path)
                chunks.extend(docs)
            
            # Cache results
            cache[file_hash] = {
                "file_path": file_path,
                "timestamp": os.path.getmtime(file_path),
                "chunks": [document_to_dict(doc) for doc in chunks],
                "image_docs": [document_to_dict(doc) for doc in image_documents],
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
