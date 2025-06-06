from langchain_core.prompts import ChatPromptTemplate
from typing import List
# from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic import BaseModel, Field
from langchain import hub
import time, logging, uuid6
from langchain_core.documents import Document
from dotenv import find_dotenv, load_dotenv
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings, 
    ChatGoogleGenerativeAI)
from langchain_experimental.text_splitter import SemanticChunker
from threading import Semaphore

class RateLimiter:
    def __init__(self, max_requests, interval):
        self.semaphore = Semaphore(max_requests)
        self.interval = interval

    def acquire(self):
        if not self.semaphore.acquire(blocking=False):
            logger.info("Rate limit reached. Waiting...")
            time.sleep(self.interval)
            self.semaphore.acquire()

    def release(self):
        self.semaphore.release()

rate_limiter = RateLimiter(max_requests=15, interval=60)

load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chunker:
    def __init__(self, strategy):
        self.semantic_chunker= SemanticChunker_langchain()
        self.agentic_chunker= AgenticChunker()
        self.strategy_chunker_map= {
            "semantic": self.semantic_chunker,
            "agentic": self.agentic_chunker
        }
        self.chunker= self.strategy_chunker_map[strategy]

    def build_chunks(self, texts, source):
        return self.chunker.build_chunks(texts, source)
    # def build_chunks(self, texts_list, source_list):
    #     all_chunks = []
    #     for texts, source in zip(texts_list, source_list):
    #         chunks = self.chunker.build_chunks(texts, source)
    #         all_chunks.extend(chunks)
    #     return all_chunks


class SemanticChunker_langchain:
    #https://python.langchain.com/v0.2/docs/how_to/semantic-chunker/
    def __init__(self):
        self.embed_model_name= "models/text-embedding-004"
        
    def build_chunks(self, texts, source):
        text_splitter = SemanticChunker(
            GoogleGenerativeAIEmbeddings(
                model=self.embed_model_name))

        chunks= text_splitter.create_documents(
            texts=texts,
            metadatas= [{"source": source}]*len(texts)
            )
        return chunks

class ChunkMeta(BaseModel):
    title: str = Field(description="The title of the chunk.")
    summary: str = Field(description="The summary of the chunk.")

class ChunkID(BaseModel):
    chunk_id: int = Field(description="The chunk id.")

class Sentences(BaseModel):
    sentences: List[str]

class AgenticChunker:
    def __init__(self):
        """
        Initializes the AgenticChunker with:
        - An empty dictionary for storing chunks.
        - A large language model (LLM) for processing and summarizing text.
        - A placeholder for raw text input.
        """
        self.chunks = {}
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0
        )

    @staticmethod
    # def retry_with_delay(func, *args, delay=5, retries=2, **kwargs):
    #     for attempt in range(retries):
    #         try:
    #             return func(*args, **kwargs)
    #         except Exception as e:
    #             logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
    #             time.sleep(delay)
    #     raise RuntimeError("Exceeded maximum retries.")
    def retry_with_delay(func, *args, max_retries=5, initial_delay=2, **kwargs):
        delay = initial_delay
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "Resource has been exhausted" in str(e):
                    logger.warning(f"Quota exceeded. Waiting for {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
        raise RuntimeError("Exceeded maximum retries.")


    def extract_propositions_list(self, raw_text):
        """
        Extracts a list of propositions from the raw text using an LLM.
        """
        logger.info("Extracting propositions from raw text.")
        extraction_llm = self.llm.with_structured_output(Sentences)
        obj = hub.pull("wfh/proposal-indexing")
        extraction_chain = obj | extraction_llm
        self.propositions_list = self.retry_with_delay(extraction_chain.invoke, raw_text).sentences

    def build_chunks(self, raw_text, source=""):
        """
        Processes the list of propositions and organizes them into chunks.
        """
        chunks_as_documents=[]
        logger.info("Building chunks from propositions.")
        if len(raw_text) < 50:
            logger.warning("Text too short to chunk. Skipping.")
            return []
        self.extract_propositions_list(raw_text)
        for proposition in self.propositions_list:
            self.find_chunk_and_push_proposition(proposition)
        
        for chunk_id in self.chunks:
            chunk_content= " ".join(self.chunks[chunk_id]["propositions"])
            chunks_as_documents.append(Document(
                page_content=chunk_content,
                metadata={"source": f"{source}_{chunk_id}"},
                id= str(uuid6.uuid6()),
                ))

        return chunks_as_documents

    def create_prompt_template(self, messages):
        return ChatPromptTemplate.from_messages(messages)

    def upsert_chunk(self, chunk_id, propositions):
        """
        Creates or updates a chunk with the given propositions.
        """
        summary_llm = self.llm.with_structured_output(ChunkMeta)
        prompt = self.create_prompt_template([
            ("system", "Generate a new or updated summary and title based on the propositions."),
            ("user", "propositions:{propositions}")
        ])
        summary_chain = prompt | summary_llm

        chunk_meta = self.retry_with_delay(summary_chain.invoke, 
                                           {"propositions": propositions})
        self.chunks[chunk_id] = {
            "summary": chunk_meta.summary,
            "title": chunk_meta.title,
            "propositions": propositions
        }
    def find_chunk_and_push_proposition(self, propositions):
        
        if not propositions:
            return
        rate_limiter.acquire()
        try:
            logger.info(f"Finding chunks for {len(propositions)} propositions.")
            allocation_llm = self.llm.with_structured_output(ChunkID)
            allocation_prompt = self.create_prompt_template([
                ("system", "Using the chunk IDs and summaries, "
                 "determine the best chunk for each proposition. "
                "If no chunk matches, generate a new chunk ID. "
                "Return chunk IDs in order."),
                ("user", "propositions:{propositions}\nchunks_summaries:{chunks_summaries}")
            ])
            allocation_chain = allocation_prompt | allocation_llm
        
            chunks_summaries = {
                chunk_id: chunk["summary"] for chunk_id, chunk in self.chunks.items()
            }
        
            # Batch processing all propositions at once
            batch_result = self.retry_with_delay(
                allocation_chain.invoke, {
                    "propositions": propositions,
                    "chunks_summaries": chunks_summaries
                }
            )
        
            # Process each chunk assignment
            for proposition, chunk_id in zip(propositions, batch_result.chunk_id):
                if chunk_id not in self.chunks:
                    self.upsert_chunk(chunk_id, [proposition])
                else:
                    current_propositions = self.chunks[chunk_id]["propositions"]
                    self.upsert_chunk(chunk_id, current_propositions + [proposition])
        finally:
            rate_limiter.release()