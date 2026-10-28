"""PDF indexing: chunk + embed + persist to Chroma.

Teaching goal: this is the SAME RAG indexing students did on Day 5. We're
just packaging it as a reusable module so the agent (Day 6) can call it as
a tool. The indexer is boring on purpose — the magic is in the agent.
"""
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION = "research_agent_pdf"


def _embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)


def build_index(pdf_path: str, persist_dir: str = "./chroma_db") -> int:
    """Load the PDF, chunk it, embed, and persist to Chroma. Returns chunk count."""
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(pages)

    vs = Chroma.from_documents(
        documents=chunks,
        embedding=_embeddings(),
        collection_name=COLLECTION,
        persist_directory=persist_dir,
    )
    # langchain-chroma persists automatically when persist_directory is set
    return len(chunks)


def get_vectorstore(persist_dir: str = "./chroma_db") -> Chroma:
    """Open an existing Chroma store for reuse by the agent."""
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=_embeddings(),
        persist_directory=persist_dir,
    )
