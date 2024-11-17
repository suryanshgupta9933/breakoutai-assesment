# Importing Dependencies
import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from pipeline import run_pipeline

# Load environment variables
load_dotenv()

UPLOAD_ENDPOINT = os.getenv("UPLOAD_ENDPOINT")
PIPELINE_ENDPOINT = os.getenv("PIPELINE_ENDPOINT")

# Page 1: Upload CSV
def csv_page():
    st.header("Upload CSV File")

    uploaded_file = st.file_uploader("Choose a CSV file to get started", type="csv")
    if uploaded_file:
        files = {"file": uploaded_file.getvalue()}
        result = requests.post(UPLOAD_ENDPOINT, files=files)
        data = result.json()
        if result.status_code == 200:
            df = pd.DataFrame(data["csv_data"])
            st.write("Data Preview:")
            st.dataframe(df.head(5))

            # Query section
            query = st.text_input("Enter your query with placeholders, e.g., 'Get me the email of {column_name}'")
            selected_column = st.selectbox("Select the main column", df.columns.tolist())

            if st.button("Run Query"):
                with st.spinner("Running query..."):
                    pipeline_data = {
                        "query": query,
                        "column_name": selected_column,
                        "df": df.to_dict(orient="records"),
                    }
                    pipeline_result = requests.post(PIPELINE_ENDPOINT, json=pipeline_data, params={"query": query})
                    if pipeline_result.status_code == 200:
                        pipeline_result_data = pipeline_result.json()
                        result_df = pd.DataFrame(pipeline_result_data["table"])
                        st.write("Query Results:")
                        st.dataframe(result_df)

                        if st.button("Download Results"):
                            result_df.to_csv("query_results.csv", index=False)
                            st.success("Results downloaded successfully!")
                    else:
                        st.error("Failed to run query. Please try again.")