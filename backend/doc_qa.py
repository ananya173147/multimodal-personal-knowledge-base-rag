from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import uuid6

class indexing:
   def __init__(self):
      self.embedding_function= GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
      pass
   
   def index_documents(self, documents, 
                       collection_name="Agentic_retrieval", 
                       top_k= 3):
      vector_store = Chroma(
         collection_name= collection_name,
         embedding_function=self.embedding_function)
      
     
      vector_store.add_documents(
          documents=documents, 
          ids=[str(uuid6.uuid6()) for _ in documents])

      retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},)
      
      return retriever
  

class QA:
  def __init__(self, retriever) -> None:
    self.system_template = """
      Answer the user's questions based on the below context. 
      If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

      <context>
      {context}
      </context>
      """

    self.question_answering_prompt = ChatPromptTemplate.from_messages(
    [("system", self.system_template),
     MessagesPlaceholder(variable_name="messages"),]
    )
    self.retriever= retriever
    self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    self.qa_chain = create_stuff_documents_chain(self.llm, 
                                                 self.question_answering_prompt
                                                 )

  def query(self, query_text:str) -> str:
    # while True:
    #   query = input("You: ")
    #   if query.lower() == "exit":
    #       break
    #   # docs = self.retriever.invoke(query)
    docs = self.retriever.get_relevant_documents(query_text)
  
    response = self.qa_chain.invoke(
            {"context": docs,
             "messages": [HumanMessage(content=query_text)]
             }
            )
    # print(f"AI: {response}")
    return response