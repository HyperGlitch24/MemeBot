import json
from langchain_openai import OpenAIEmbeddings 
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# 1. Load your meme data from the JSON file
with open('memes.json', 'r') as f:
    meme_data = json.load(f)

# 2. Prepare documents for LangChain
# We create a list of descriptions and their corresponding metadata
descriptions = [item['description'] for item in meme_data]
metadatas = [{'name': item['name'], 'filename': item['filename']} for item in meme_data]

# 3. Initialize the embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 4. Create a Chroma vector store and ingest the data
# This will create a 'db' folder for persistence
vector_store = Chroma.from_texts(
    texts=descriptions,
    embedding=embeddings,
    metadatas=metadatas,
    persist_directory="./db_openai"
)

print(" Vector store created successfully!")