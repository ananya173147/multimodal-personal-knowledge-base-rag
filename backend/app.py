from dotenv import find_dotenv, load_dotenv
import os, shutil
from pipeline import pipeline
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from doc_qa import QA
from fastapi.middleware.cors import CORSMiddleware


load_dotenv(find_dotenv('var.env'), verbose=True)

LLAMA_CLOUD_API_KEY=os.getenv('LLAMA_CLOUD_API_KEY')
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
TAVILY_API_KEY=os.getenv('TAVILY_API_KEY')
GOOGLE_CLOUD_PROJECT=os.getenv('GOOGLE_CLOUD_PROJECT')


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploaded_files/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

latest_retriever = None

# Process uploaded files
@app.post("/upload/")
async def upload_file(file: UploadFile):
    global latest_retriever
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Run the pipeline on the uploaded file
        latest_retriever = pipeline(inputPath=UPLOAD_DIR)
        print(f"Retriever: {latest_retriever}")
        return {"message": f"Successfully processed {file.filename}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Query endpoint
@app.get("/query/")
async def query_document(query: str):
    global latest_retriever
    if not latest_retriever:
        raise HTTPException(status_code=400, detail="No retriever available. Please upload files first.")
    
    try:
        print(f"Using retriever: {latest_retriever}")
        qa = QA(latest_retriever)
        answer = qa.query(query)
        return {"query": query, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
@app.get("/files")
async def list_files():
    files = os.listdir("./uploaded_files")
    return {"files": files}

# input_path = "C:/Users/anany/Desktop/Work/Python/Multimodal PKB/multimodal-personal-knowledge-base/Documents"
# parser = "pymupdf4llm"
# chunking = "semantic"
        
# pipeline(inputPath=input_path, parser_name = parser, chunking_strategy = chunking)        
