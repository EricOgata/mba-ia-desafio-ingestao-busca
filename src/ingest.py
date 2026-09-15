import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter # permite chuncking
from langchain_core.documents import Document

from load import load_vector

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")

def ingest_pdf():

    for k in ("GOOGLE_API_KEY", "DATABASE_URL", "PG_VECTOR_COLLECTION_NAME"):
        if not os.getenv(k):
            raise RuntimeError(f"Environment variable {k} is not set.")

    docs = PyPDFLoader(str(PDF_PATH)).load()

    splits = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=False
    ).split_documents(docs)

    if not splits:
        raise SystemExit(0)

    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)}
        )
        for d in splits
    ]

    ids = [f"doc-{i}" for i in range(len(enriched))]

    store = load_vector()
    if not store:
        raise RuntimeError("Failed to load PGVector store. Check your database connection and collection name.")
    # embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    # # embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")

    # store = PGVector(
    #     embeddings=embeddings,
    #     collection_name=os.getenv('PG_VECTOR_COLLECTION_NAME'),
    #     connection=os.getenv("DATABASE_URL"),
    #     use_jsonb=True
    # )

    store.add_documents(documents=enriched, ids=ids)

    pass


if __name__ == "__main__":
    ingest_pdf()