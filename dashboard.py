# Importing Dependencies
import streamlit as st
from app.csv import csv_page
from app.sheets import sheets_page

# Set up Streamlit app
st.set_page_config(page_title="AI Query Dashboard", layout="wide")
st.title("AI Query Dashboard")
st.write(
    "This dashboard allows you to upload your CSV data or use Google Sheets, "
    "define custom search queries, and let the AI retrieve relevant web data for each entity. "
    "View and download the results in a structured format with ease."
)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page:", ["Upload CSV", "Google Sheets"])

# Page 1: Upload CSV
if page == "Upload CSV":
    csv_page()
elif page == "Google Sheets":
    sheets_page()