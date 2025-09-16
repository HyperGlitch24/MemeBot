import json
from langchain_openai import OpenAIEmbeddings 
from langchain_chroma import Chroma
import os
from dotenv import load_dotenv

#load_dotenv()  # Load environment variables from .env file

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")


openai_api_key = openai_api_key.strip()




with open('memes.json', 'r') as f:
    meme_data = json.load(f)



descriptions = [item['description'] for item in meme_data]
metadatas = [{'name': item['name'], 'filename': item['filename']} for item in meme_data]


embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai_api_key)

vector_store = Chroma.from_texts(
    texts=descriptions,
    embedding=embeddings,
    metadatas=metadatas,
    persist_directory="./db_openai"
)

print(" Vector store created successfully!")