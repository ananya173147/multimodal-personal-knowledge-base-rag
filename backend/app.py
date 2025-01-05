from dotenv import find_dotenv, load_dotenv
import os
from pipeline import pipeline

load_dotenv(find_dotenv('var.env'), verbose=True)

LLAMA_CLOUD_API_KEY=os.getenv('LLAMA_CLOUD_API_KEY')
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
TAVILY_API_KEY=os.getenv('TAVILY_API_KEY')
GOOGLE_CLOUD_PROJECT=os.getenv('GOOGLE_CLOUD_PROJECT')

input_path = "C:/Users/anany/Desktop/Work/Python/Multimodal PKB/multimodal-personal-knowledge-base/Documents"
parser = "pymupdf4llm"
chunking = "semantic"
        
pipeline(inputPath=input_path, parser_name = parser, chunking_strategy = chunking)        
