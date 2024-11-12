# Importing Dependencies
import os
import logging
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def retrieve_context(scrapped_data):
    """
    Retrieve relevant context from scrapped data.
    """
    retrieved_data = []
    try:
        # Initialize text splitter and vector store
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=200)
        vector_store = InMemoryVectorStore(OpenAIEmbeddings())

        for data in scrapped_data:
            # Extract and split text into chunks
            document = Document(page_content=data['scraped_text'])
            chunks = text_splitter.split_documents([document])  # Split document into chunks
            # Add chunks to vector store
            await vector_store.aadd_documents(documents=chunks)
            # Retrieve relevant chunks based on query
            relevant_chunks = vector_store.similarity_search(
                query=data['query'],
                k=2
            )
            # Join retrieved chunk content as context
            context = "\n".join([chunk.page_content for chunk in relevant_chunks])
            # Append result for the query
            retrieved_data.append({
                "query": data['query'],
                "context": context
            })
            logger.info(f"Retrieved relevant chunks for query: {data['query']}")    
    
    except Exception as e:
        logger.error(f"Failed to retrieve relevant chunks: {e}")
        # Append empty context on error for the failed query
        retrieved_data.append({
            "query": data['query'],
            "context": ""
        })

    return retrieved_data