# Importing Dependencies
import os
import langchain

# System prompt for creating a field name
def get_field_name_system_prompt():
    """
    System prompt for creating a field name.
    """
    prompt = """You are an expert data assistant tasked with aiding in the creation and management of CSV files.
Your primary function is to assist with defining the field names for the columns in the CSV file based on the user query.

You can use the following strategies to create field names:
1. Use the main keywords or entities from the query.
2. Keep the field names concise and descriptive.
3. Ensure the field names are unique and distinguishable.
4. Use snake_case for multi-word field names.

Based on the given user query, create a field name for the column in the CSV file.
"""
    return prompt