# Importing Dependencies
import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

UPLOAD_ENDPOINT = os.getenv("UPLOAD_ENDPOINT")
PIPELINE_ENDPOINT = os.getenv("PIPELINE_ENDPOINT")


def initialize_csv_session_state():
    """Initialize session state variables for the CSV page."""
    defaults = {
        "uploaded_file": None,
        "uploaded_data": None,
        "selected_column": None,
        "last_query": "",
        "query_results": None,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def csv_page():
    """Render the Upload CSV page."""
    st.header("Upload CSV File")

    # Initialize session state
    initialize_csv_session_state()

    # Upload CSV
    uploaded_file = st.file_uploader("Choose a CSV file to get started", type="csv")
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file

        # Process the uploaded file
        if st.session_state.uploaded_file is not None:
            with st.status("Uploading file...") as status:
                try:
                    files = {"file": st.session_state.uploaded_file.getvalue()}
                    result = requests.post(UPLOAD_ENDPOINT, files=files)
                    result.raise_for_status()

                    data = result.json()
                    st.session_state.uploaded_data = pd.DataFrame(data["csv_data"])
                    status.update(label="File uploaded successfully!", state="complete")
                except requests.RequestException as e:
                    status.update(label="Failed to upload file: {str(e)}", state="error")
                    return

    # Display uploaded data
    if st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        st.write("Data Preview:")
        st.dataframe(df.head(5))

        # Column selection with session state
        if st.session_state.selected_column not in df.columns:
            st.session_state.selected_column = df.columns[0]

        selected_column = st.selectbox(
            "Select the main column",
            df.columns.tolist(),
            index=df.columns.tolist().index(st.session_state.selected_column),
            key="csv_column_selector",
        )
        st.session_state.selected_column = selected_column

        # Query input with session state
        query = st.text_input(
            "Enter your query. (Placeholders are allowed, e.g., 'Get me the email of {column_name}'",
            value=st.session_state.last_query,
        )
        st.session_state.last_query = query

        # Run query
        if st.button("Run Query"):
            with st.status("Processing query...") as status:
                try:
                    pipeline_data = {
                        "query": query,
                        "column_name": selected_column,
                        "df": df.to_dict(orient="records"),
                    }
                    pipeline_result = requests.post(PIPELINE_ENDPOINT, json=pipeline_data)
                    pipeline_result.raise_for_status()

                    pipeline_result_data = pipeline_result.json()
                    st.session_state.query_results = pd.DataFrame(pipeline_result_data["table"])
                    status.update(label="Query processed successfully!", state="complete")
                except requests.RequestException as e:
                    status.update(label="Failed to process query: {str(e)}", state="error")
                    st.session_state.query_results = None

        # Display query results
        if st.session_state.query_results is not None:
            result_df = st.session_state.query_results
            st.write("Query Results:")
            st.dataframe(result_df)

            # Download option
            csv = result_df.to_csv(index=False)
            st.download_button(
                "Download Results as CSV",
                csv,
                "query_results.csv",
                "text/csv",
                key="csv_download_button",
            )