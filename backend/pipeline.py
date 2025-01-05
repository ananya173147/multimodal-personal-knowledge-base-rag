from docparser import DocParser
from chunkers import Chunker
from imageprocessing import ImageProcessor
from doc_qa import QA, indexing
from utils import list_supported_files, hash_file, load_cache, save_cache
from utils import dict_to_document, process_csv, process_xlsx, document_to_dict
from langchain_core.documents import Document
from pathlib import Path
import os


CACHE_FILE = "./cache.json"
cache = load_cache()

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


