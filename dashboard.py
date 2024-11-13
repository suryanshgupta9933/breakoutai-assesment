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

# Set up Streamlit app title
st.title("AI Query Dashboard")
st.write("This dashboard allows you to upload your csv data, define custom search queries, and let the AI retrieve relevant web data for each entity. View and download the results in a structured format with ease.")

# Sidebar
with st.sidebar:
    st.title("BreakoutAI.tech")
    st.markdown("---")
    st.header("Upload CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file to get started", type="csv")
    st.markdown("##### Note: Remove the csv file to start over.")
    st.markdown("---")
    st.write("Created by [Suryansh Gupta](https://github.com/suryanshgupta9933)")

# Main content
if uploaded_file:
    files = {"file": uploaded_file.getvalue()}
    result = requests.post(UPLOAD_ENDPOINT, files=files)
    data = result.json()  
    if result.status_code == 200:
        df = pd.DataFrame(data["csv_data"])
        selected_column = st.selectbox("Select the main column", df.columns.tolist())
        st.write("Data Preview:")
        st.write(df.head(5))

        # Query section
        query = st.text_input("Enter your query with placeholders, e.g., 'Get me the email of {column_name}'")
        if st.button("Run Query"):
            with st.spinner("Generating Table..."):
                data = {"query": query,
                        "column_name": selected_column,
                        "df": df.to_dict(orient="records")}
                result = requests.post(PIPELINE_ENDPOINT, json=data, params={"query": query})
                data = result.json()
                df = pd.DataFrame(data["table"])
                if result.status_code == 200:
                    st.markdown("## Response")
                    st.write(df)
                    # Convert the DataFrame to CSV for download
                    csv = df.to_csv(index=False)
                    # Download button
                    st.download_button(
                        label="Download Table as CSV",
                        data=csv,
                        file_name="query_results.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Error in processing query")