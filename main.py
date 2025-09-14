from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
#from langchain_core.runnables import RunnablePassthrough
#from langchain_core.output_parsers import StrOutputParser
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
import os

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

def load_chain():
    try:
        llm = ChatOpenAI(model = "gpt-4o")
        embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")

        if not os.path.exists("./db_openai"):
            raise Exception("Vector store directory not found. Please run database.py to create the vector store.")
        vector_store = Chroma(persist_directory = "./db_openai", embedding_function=embeddings) 
        retriever  = vector_store.as_retriever (search_kwargs = {"k":1})


        condenser_prompt = ChatPromptTemplate.from_messages([
            ("system","Given a chat history and the latest user question, formulate a standalone question that can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is." ),
            ("human", "{chat_history}\n\n {input}")
        ])

        history_aware_retriever = create_history_aware_retriever(
            llm = llm, 
            retriever = retriever,
            prompt = condenser_prompt
        )


        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful and witty meme expert. Answer the user's question based only on the following context:\n\n{context}"),
            ("human", "{input}")
        ])

        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        return rag_chain
    
    except Exception as e:
        print(f"Error during chain setup: {e}")
        return None 
    

final_chain = load_chain()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models for Request Body
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatQuery(BaseModel):
    question: str
    chat_history: List[ChatMessage]

# API Endpoint
@app.post("/chat")
async def chat_endpoint(query: ChatQuery):
    if not final_chain:
        raise HTTPException(status_code=500, detail="Chat chain is not initialized.")

    # Format history for LangChain
    chat_history_messages = []
    for msg in query.chat_history:
        chat_history_messages.append((msg.role, msg.content))

    # Invoke the modern chain
    response = final_chain.invoke({
        "input": query.question,
        "chat_history": chat_history_messages
    })
    
    answer = response["answer"]
    # The retrieved documents are now in the 'context' key
    source_document = response["context"][0]
    filename = source_document.metadata["filename"]
    
    return {
        "answer": answer,
        "filename": filename
    }


    





