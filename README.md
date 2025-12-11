# Multimodal Personal Knowledge Base RAG

A Retrieval-Augmented Generation system that processes multimodal documents (PDFs, images, spreadsheets) and enables intelligent question-answering through semantic search and large language models. This system implements an end-to-end multimodal RAG pipeline with advanced document parsing, intelligent chunking strategies, and a web-based chat interface. It automatically extracts and processes text, images, and tables from diverse document formats, creating a queryable knowledge base with context-aware retrieval capabilities.

![WhatsApp Image 2025-12-11 at 12 48 34 AM](https://github.com/user-attachments/assets/ad90310f-317c-46e7-a29a-ad17e554ce99)


## Project Structure
```
multimodal-personal-knowledge-base-rag/
├── backend/
│   ├── app.py                    # FastAPI application and endpoints
│   ├── pipeline.py               # Main document processing pipeline
│   ├── docparser.py              # Document parsing with LlamaParse/PyMuPDF
│   ├── chunkers.py               # Semantic and agentic chunking strategies
│   ├── imageprocessing.py        # Image encoding and summarization
│   ├── doc_qa.py                 # Vector indexing and QA chain
│   ├── utils.py                  # File utilities and caching
│   └── backend_requirements.txt  # Python dependencies
├── rag-web-app/
│   ├── src/
│   │   ├── App.js                # Main React component
│   │   ├── App.css               # Styling
│   │   └── index.js              # React entry point
│   ├── public/                   # Static assets
│   └── package.json              # Node dependencies
├── requirements.txt              # Root Python dependencies
└── README.md
```

## System Architecture
### Backend Components
**Document Processing Pipeline**
- Multi-format document parsing with LlamaParse and PyMuPDF4LLM support
- Automated extraction of embedded images, tables, and text content
- OCR-based table detection and extraction using EasyOCR and img2table
- Support for PDFs, images (PNG/JPG), CSV, and Excel files

**Intelligent Chunking System**
- Semantic chunking using Google's text-embedding-004 model
- Agentic chunking with proposition-based document segmentation
- LLM-driven chunk summarization and title generation
- Automatic rate limiting and exponential backoff for API stability

**Multimodal Image Processing**
- Base64 image encoding for vision model input
- AI-powered image summarization using Gemini 1.5 Flash
- Automatic generation of retrieval-optimized image descriptions
- Batch processing with retry logic for reliability

**Vector Store and Retrieval**
- ChromaDB vector database for semantic similarity search
- Google Generative AI embeddings (text-embedding-004)
- Configurable top-k retrieval with similarity scoring
- Persistent storage with file-based caching system

**Question Answering Engine**
- Context-aware response generation using Gemini 1.5 Flash
- RAG-enhanced LLM chain with document context injection
- Structured prompt engineering for accurate, grounded responses
- Built-in fallback handling for out-of-context queries

### Frontend Application

**React-Based Web Interface**
- Real-time chat interface for knowledge base queries
- File upload system with automatic processing
- Sidebar display of uploaded documents
- Responsive design with loading states and error handling

### Caching and Performance Optimization

**Intelligent Caching System**
- MD5 hash-based file change detection
- JSON-based persistent cache for processed documents
- Skips reprocessing of unchanged files
- Stores chunked documents and image summaries

## Technical Stack

### Core Dependencies

**LLM and Embeddings**
- LangChain 0.3.13 (orchestration framework)
- Google Generative AI (Gemini 1.5 Flash, text-embedding-004)
- LlamaParse 0.5.19 (document parsing)

**Document Processing**
- PyMuPDF4LLM 0.0.17 (PDF extraction)
- img2table 1.4.0 (table detection)
- opencv-contrib-python 4.10.0 (image processing)

**Vector Storage**
- ChromaDB via langchain_chroma 0.1.4
- Weaviate Client 4.10.2

**Web Framework**
- FastAPI 0.115.6 (REST API)
- React 19.0.0 (frontend)
- Axios 1.7.9 (HTTP client)

**Utilities**
- python-dotenv 1.0.1 (environment management)
- Pydantic 2.10.4 (data validation)
- uuid6 2024.7.10 (unique identifiers)

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Cloud API credentials
- LlamaCloud API key (optional, for LlamaParse)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/ananya173147/multimodal-personal-knowledge-base-rag.git
cd multimodal-personal-knowledge-base-rag

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
# Create a var.env file in the backend directory
LLAMA_CLOUD_API_KEY=your_llama_cloud_key
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_key  # Optional
GOOGLE_CLOUD_PROJECT=your_project_id

# Start FastAPI server
cd backend
uvicorn app:app --reload --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd rag-web-app

# Install Node dependencies
npm install

# Start development server
npm start
```

The application will be available at `http://localhost:3000`

## Usage

### Document Upload and Processing

1. **Upload Files**: Use the web interface to upload documents (PDF, PNG, JPG, CSV, XLSX)
2. **Automatic Processing**: The system automatically:
   - Parses document structure
   - Extracts text, images, and tables
   - Generates semantic chunks
   - Creates image summaries
   - Indexes content in vector database
3. **Caching**: Processed documents are cached to avoid redundant processing

### Querying the Knowledge Base

1. **Submit Query**: Enter questions in the chat interface
2. **Semantic Search**: System retrieves top-k relevant documents using vector similarity
3. **Context-Aware Response**: LLM generates answers grounded in retrieved context
4. **Source Attribution**: Responses are based on indexed document content

## API Endpoints

### POST /upload/
Uploads and processes a document file.

**Request**: Multipart form data with file
**Response**: Processing confirmation message

### GET /query/
Queries the knowledge base with natural language.

**Parameters**: 
- `query` (string): Question to answer

**Response**:
```json
{
  "query": "What is the main topic?",
  "answer": "Based on the documents..."
}
```

### GET /files
Lists all uploaded files.

**Response**:
```json
{
  "files": ["document1.pdf", "image1.png", ...]
}
```

## Configuration Options

### Document Parsing
- `parser_name`: Choose between "LlamaParse" or "pymupdf4llm"
- LlamaParse offers higher accuracy for complex layouts
- PyMuPDF4LLM provides faster processing with built-in image extraction

### Chunking Strategy
- `semantic`: Uses sentence transformers for semantic boundary detection
- `agentic`: LLM-driven proposition extraction and intelligent clustering

### Retrieval Settings
- `top_k`: Number of documents to retrieve (default: 3)
- `similarity_threshold`: Minimum similarity score for retrieval

## Key Features

### Advanced Document Processing
- Handles encrypted PDFs with password authentication
- Extracts tables using OCR with borderless table detection
- Preserves document hierarchy and metadata
- Processes multi-sheet Excel files separately

### Intelligent Retrieval
- Semantic search using state-of-the-art embeddings
- Multimodal retrieval across text and image content
- Context-aware chunk ranking
- Efficient vector similarity computation

### Robust Error Handling
- Exponential backoff for API rate limiting
- Retry logic with configurable attempts
- Graceful degradation for processing failures
- Comprehensive logging for debugging

### Scalability
- Asynchronous document processing
- Batch image summarization
- Incremental indexing with cache invalidation
- CORS-enabled API for distributed deployment

## Performance Considerations
- File hashing prevents redundant processing of unchanged documents
- Concurrent processing pipelines for text and multimodal content
- Rate limiting prevents API quota exhaustion
- Persistent vector store enables fast startup times

## MIT License

