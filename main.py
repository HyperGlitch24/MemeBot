from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv() 
try: 
    #OpenAI setup
    embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")
    llm = ChatOpenAI(model = "gpt-4o")

    #vector store loading
    Vector_store = Chroma(persist_directory = "./db_openai", embedding_function = embeddings)

    #retrieve function
    retriever = Vector_store.as_retriever(search_kwargs = {"k":1})

except Exception as e:
    print(f"Error during setup: {e}")

    retriever = None


# Define the RAG chain with prompt template
template = """
You are a helpful and witty meme expert. Your task is to identify a meme based on the user's description.
Use the following retrieved context to answer the question. If you don't know the answer, just say you don't know.

CONTEXT: {context}
QUESTION: {question}
ANSWER:
"""
prompt = ChatPromptTemplate.from_template(template)

RAG_chain =(
RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
.assign(Answer = (RunnablePassthrough() |prompt | llm | StrOutputParser() )))


def process_chain_output(chain_output):
    return {
        "answer": chain_output["Answer"],
        "filename": chain_output["context"][0].metadata["filename"],
    }

final_chain = RAG_chain | process_chain_output


print("--- Running the chain with a test query ---")
test_query = "Balakrishna"
result = final_chain.invoke(test_query)

# 3. Print the final dictionary output
print(result)

##Fast API setup

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)



app.mount("/static", StaticFiles(directory="meme_templates"), name="static")


class Query(BaseModel):
    text: str

@app.get("/")
async def read_root():
    return FileResponse('./frontend/index.html')

# 3. FIX: Attached the POST decorator to its function
@app.post("/find-meme")
async def find_meme_endpoint(query: Query):
    if not retriever:
        return {"error": "Server is not ready. Check logs."}
    response = final_chain.invoke(query.text)
    return {"response": response}

            