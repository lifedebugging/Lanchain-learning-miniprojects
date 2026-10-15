# Standard library imports
import os
import sys
import logging
import asyncio

# Third-party imports
from dotenv import load_dotenv
from nltk.tokenize import word_tokenize

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.retrievers import BM25Retriever
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever

# Local imports
from error_handler import retry_with_backoff
from mcp.server.fastmcp import FastMCP

# CONFIGURATION & INITIALIZATION

logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
load_dotenv(override=True)

os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

mcp = FastMCP("rag_subagent")


# LLM CONFIGURATION

llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    temperature=0
)

# DOCUMENT INDEXING & RETRIEVAL

def Indexing():
    """Initialize document loader, splitter, embeddings, and vector store."""
    
    # Document loader
    loader = PyPDFLoader(
        file_path="D:/Downloads/eit-digital-artificial-intelligence-report.pdf",
        mode="single",
        extract_images=False,
        extraction_mode="layout",
    )
    documents = loader.load()

    # Text splitter
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-4",
        chunk_size=500,
        chunk_overlap=50,
    )
    splitted_documents = splitter.split_documents(documents)

    # Embeddings
    embeddings = HuggingFaceEmbeddings(model="all-MiniLM-L6-v2")

    # Vector store
    vector_store = Chroma(
        collection_name="example_collection",
        embedding_function=embeddings,
        persist_directory="D:/Downloads/",
    )

    if os.path.exists("D:/Downloads/chroma.sqlite3"):
        ensemble = build_retrievers(vector_store, splitted_documents)
        return ensemble
    else:
        vector_store.add_documents(documents=splitted_documents)
        ensemble = build_retrievers(vector_store, splitted_documents)
        return ensemble


def build_retrievers(vector_store, splitted_documents):
    """Build BM25 and Chroma retrievers and merge them using ensemble."""
    
    # BM25 retriever
    bm25_retriever = BM25Retriever.from_documents(
        splitted_documents,
        k=2,
        preprocess_func=word_tokenize,
    )

    # Chroma retriever
    chroma_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 2},
    )

    # Ensemble retriever
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, chroma_retriever],
        weights=[0.5, 0.5],
        c=60,
    )

    return ensemble_retriever

final_retriever = Indexing()
# TOOLS

@tool
async def search_docs(query: str) -> str:
    """
    Search documentation provided for specific information about AI.
    Use this when you need factual information from the material you've been provided.
    """
    global final_retriever
    try:
        result = await final_retriever.ainvoke(query)

        chunks = []
        for doc in result:
            chunks.append(doc.page_content)

        return "\n\n".join(chunks)
    except Exception as e:
        return f"an error occured: {e}"

# AGENT CONFIGURATION

agent = create_agent(
    model=llm,
    tools=[search_docs],
    system_prompt=
    """
    Role:You're an sub-agent with external knowledge base with context.
         You're intelligently capable to decide when to use your external knowledge base.

    Constraints: Use the following pieces of retrieved context to answer the question. 
                 If you don't know the answer, just say that you don't know.
                 Do not produce wrong answer with confidence.
                 For general questions answer without directly without using tools.

    Output_format: Accurate, Precise and Meaningful.
                   'strictly' Paraphrase, never quote directly
                   """
                   )

query =  " The example provided by Watcher et al "
# MAIN RESPONSE HANDLER
@mcp.tool()
async def rag() -> str:
    """
    High performing sub agent retrieval augmented generator.
    Provide clean response for main agent.
    Provide precise answer with no gibberish.
    Never ask questions.

    Args:
        query: The user query string

    Returns:
        The final response of agent.
    """
    @retry_with_backoff()
    async def response_func():
        response = await agent.ainvoke(
            {"messages": [HumanMessage(content=query)]}
        )

        final_response = response["messages"][-1]
        return final_response.content

    return await response_func()

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    
    


