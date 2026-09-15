import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

def load_vector():
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    # embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")
    
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv('PG_VECTOR_COLLECTION_NAME'),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True
    )

    return store