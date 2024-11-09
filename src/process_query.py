# Importing Dependencies
import pandas as pd

# Function to process the query
def process_query(query: str, column_name: str, df: pd.DataFrame):
    """
    Process the query by replacing placeholders with 
    row data from the specified column in quotes for
    exact match search on Google.
    """
    search_queries = []

    # Case 1: If "{column_name}" is in the query, replace placeholder with row data
    if "{column_name}".format(column_name=column_name) in query:
        for _, row in df.iterrows():
            formatted_query = query.replace("{" + "{column_name}".format(column_name=column_name) + "}", f"\"{row[column_name]}\"")
            search_queries.append(formatted_query)
    # Case 2: If "{column_name}" is not in the query, concatenate with each row data
    else:
        column_data = df[column_name].values
        for data in column_data:
            search_queries.append(f"{query} \"{data}\"")

    return search_queries