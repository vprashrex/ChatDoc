from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from api.chat.building_blocks.prompt import template
from dotenv import load_dotenv
import os

load_dotenv()

class LanguageModelProcess:
    def __init__(self):
        self.llm = ChatGroq(
            verbose=False,
            temperature=0,
            model_name="llama-3.1-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        
        prompt = ChatPromptTemplate.from_template(template)
        self.rag_chain = (
            prompt
            | self.llm
            | StrOutputParser()
        )

    def retrieve(self,user_id,query):
        self.presist_path = f"embedding_db/{user_id}_db"
        self.collection_name = f"{user_id}_collection"
        vectorstore = Chroma(collection_name=self.collection_name,persist_directory=self.presist_path,embedding_function=NVIDIAEmbeddings(
            model="nvidia/nv-embed-v1",
            api_key=os.getenv("NVIDIA_API_KEY"),
            truncate="NONE",
        ))

        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        documents = retriever.get_relevant_documents(query)
        return documents
    
    def generate(self,user_id,query):
        docs = self.retrieve(user_id,query)
        context = " ".join([doc.page_content for doc in docs])
        generation = self.rag_chain.invoke({"context": context, "question": query})
        return generation
