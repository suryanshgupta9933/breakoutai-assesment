# Importing Dependencies
import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from .prompt import get_field_name_system_prompt, get_field_data_system_prompt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# User message for the field data
def create_user_message(field_name, query, context):
    return f"Field Name: {field_name}\n\nQuery: {query}\n\nContext: {context}"

# Generate a field name based on the user query
def generate_field_name(query):
    try:
        llm = ChatOpenAI(model="gpt-4o-mini")
        input = [
            SystemMessage(content=get_field_name_system_prompt()),
            HumanMessage(content="Query: " + query)
        ]
        response = llm.invoke(input)
        logger.info(f"Generated field name for query: {query}")
        return response.content
    except Exception as e:
        logger.error(f"Failed to generate field name: {e}")
        return None

# Generate field data based on the user query
async def generate_field_data(field_name, retrieved_data):
    try:
        batch_requests = []
        llm = ChatOpenAI(model="gpt-4o")
        for data in retrieved_data:
            batch_requests.append([
                SystemMessage(content=get_field_data_system_prompt()),
                HumanMessage(content=create_user_message(field_name, data['query'], data['context']))
            ])
        field_data = await llm.abatch(batch_requests)
        field_data = [response.content for response in field_data]
        logger.info(f"Generated field data for query: {query}")
        return field_data
    except Exception as e:
        logger.error(f"Failed to generate field data: {e}")
        return field_data