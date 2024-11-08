# Importing Dependencies
import os
import logging
import requests
import pandas as pd
import streamlit as st

# FastAPI backend URL
BACKEND_URL = "http://127.0.0.1:8000"

st.title("Dashboard")

st.sidebar.title("BreakoutAI.tech")
st.sidebar.markdown("---")
st.sidebar.write("Created by [Suryansh Gupta](https://github.com/suryanshgupta9933)")

# File upload section
uploaded_file = st.file_uploader("Upload CSV File", type="csv")
if uploaded_file:
    files = {"file": uploaded_file.getvalue()}
    response = requests.post(f"{BACKEND_URL}/upload-csv/", files=files)
    if response.status_code == 200:
        columns = response.json().get("columns", [])
        selected_column = st.selectbox("Select the main column", columns)
        
        # Query section
        query = st.text_input("Enter your query with placeholders, e.g., 'Get me the email of {company}'")
        
        if st.button("Run Query"):
            # Call FastAPI process-query endpoint
            data = {"column_name": selected_column}
            result = requests.post(f"{BACKEND_URL}/process-query/", json=data, params={"query": query})
            if result.status_code == 200:
                st.write("Query Processed!")
            else:
                st.error("Error in processing query")