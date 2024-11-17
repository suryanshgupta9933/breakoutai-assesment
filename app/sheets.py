# Importing Dependencies
import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from typing import Optional, Dict, List

from src.sheets import authenticate_google_sheets, get_sheet_data, update_worksheet

# Load environment variables
load_dotenv()

PIPELINE_ENDPOINT = os.getenv("PIPELINE_ENDPOINT")

def initialize_session_state():
    """Initialize all session state variables with default values."""
    defaults = {
        "gc": None,
        "spreadsheets": None,
        "selected_spreadsheet": None,
        "loaded_data": None,
        "selected_column": None,
        "last_query": "",
        "processing_error": None,
        "authentication_attempted": False,
        "load_requested": False  # New state to track if load was requested
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def authenticate_sheets() -> bool:
    """Authenticate with Google Sheets and store client in session state."""
    try:
        if not st.session_state.authentication_attempted:
            st.session_state.gc = authenticate_google_sheets()
            st.session_state.authentication_attempted = True
        return st.session_state.gc is not None
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        return False

def load_spreadsheets() -> Optional[List[Dict]]:
    """Load and cache spreadsheet list in session state."""
    try:
        if st.session_state.spreadsheets is None:
            st.session_state.spreadsheets = st.session_state.gc.list_spreadsheet_files()
        return st.session_state.spreadsheets
    except Exception as e:
        st.error(f"Failed to load spreadsheets: {str(e)}")
        return None

def load_sheet_data(selected_id: str) -> bool:
    """Load and cache sheet data in session state."""
    try:
        sheet_data = get_sheet_data(st.session_state.gc, selected_id)
        st.session_state.loaded_data = pd.DataFrame(sheet_data)
        return True
    except Exception as e:
        st.error(f"Failed to load sheet data: {str(e)}")
        st.session_state.loaded_data = None
        return False

def process_pipeline_query(query: str, selected_column: str, df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Process the pipeline query and return results."""
    try:
        pipeline_data = {
            "query": query,
            "column_name": selected_column,
            "df": df.to_dict(orient="records"),
        }
        
        if not PIPELINE_ENDPOINT:
            raise ValueError("PIPELINE_ENDPOINT environment variable is not set")
            
        pipeline_result = requests.post(
            PIPELINE_ENDPOINT,
            json=pipeline_data
        )
        pipeline_result.raise_for_status()
        
        pipeline_result_data = pipeline_result.json()
        return pd.DataFrame(pipeline_result_data["table"])

    except Exception as e:
        st.error(f"Error processing pipeline query: {str(e)}")
    return None

def sheets_page():
    """Main function for Google Sheets integration page."""
    st.header("Google Sheets Integration")
    
    # Initialize session state
    initialize_session_state()
    
    # Authentication
    with st.status("Authenticating with Google Sheets...") as status:
        if not authenticate_sheets():
            status.update(label="Authentication failed. Check your service account configuration.", state="error")
            return
        status.update(label="Authenticated with Google Sheets.", state="complete")
        
        # Load spreadsheets
        spreadsheets = load_spreadsheets()
        if not spreadsheets:
            status.update(label="No Google Sheets are shared with the service account.", state="warning")
            return
    
    st.info("Share your Google Sheet with the service account email to access it here.")

    # Select spreadsheet
    spreadsheet_names = [file["name"] for file in spreadsheets]
    
    # Handle case when selected_spreadsheet is not in the list
    current_index = 0
    if st.session_state.selected_spreadsheet in spreadsheet_names:
        current_index = spreadsheet_names.index(st.session_state.selected_spreadsheet)
    
    selected_spreadsheet = st.selectbox(
        "Select a Google Sheet to process:",
        spreadsheet_names,
        index=current_index,
        key="spreadsheet_selector"
    )
    
    # Update selected spreadsheet in session state
    if selected_spreadsheet != st.session_state.selected_spreadsheet:
        st.session_state.selected_spreadsheet = selected_spreadsheet
        st.session_state.loaded_data = None  # Clear loaded data when spreadsheet changes
        st.session_state.load_requested = False  # Reset load request flag
    
    selected_id = next((file["id"] for file in spreadsheets if file["name"] == selected_spreadsheet), None)
    
    if not selected_id:
        st.error("Could not find selected spreadsheet ID")
        return
    
    # Load button
    if st.button("Load Google Sheet"):
        st.session_state.load_requested = True
    
    # Only load data if explicitly requested
    if st.session_state.load_requested:
        with st.spinner("Loading Google Sheet..."):
            if not load_sheet_data(selected_id):
                st.session_state.load_requested = False  # Reset on failure
                return

    
    # Display and process data only if it's loaded
    if st.session_state.loaded_data is not None:
        df = st.session_state.loaded_data
        
        st.write("Preview of Google Sheet Data:")
        st.dataframe(df.head(5))
        
        # Column selection with session state
        if st.session_state.selected_column not in df.columns:
            st.session_state.selected_column = df.columns[0]
            
        selected_column = st.selectbox(
            "Select the main column",
            df.columns.tolist(),
            index=df.columns.tolist().index(st.session_state.selected_column),
            key="column_selector"
        )
        st.session_state.selected_column = selected_column

        # Query input with session state
        query = st.text_input(
            "Enter your query. (Placeholders are allowed, e.g., 'Get me the email of {column_name}'",
            value=st.session_state.last_query,
            help="Example: 'Get me the email of {column_name}'"
        )
        st.session_state.last_query = query

        # Process query
        if st.button("Run Query on Google Sheet"):
            with st.status("Processing query...") as status:
                result_df = process_pipeline_query(query, selected_column, df)
                
                if result_df is not None:
                    status.update(label="Query processed successfully.", state="complete")
            
            st.write("Processed Data:")
            st.dataframe(result_df)
            
            # Download option
            csv = result_df.to_csv(index=False)
            st.download_button(
                "Download Processed Data as CSV",
                csv,
                "processed_google_sheet_data.csv",
                "text/csv",
                key="download_button"
            )
            
            # Update sheet option
            if st.button("Update Google Sheet", key="update_button"):
                with st.status("Updating Google Sheet...") as update_status:
                    try:
                        if update_worksheet(st.session_state.gc, selected_id, result_df):
                            update_status.update(label="Google Sheet updated successfully.", state="complete")
                        else:
                            update_status.update(label="Failed to update Google Sheet.", state="error")
                    except Exception as e:
                        update_status.update(label=f"Error updating Google Sheet: {str(e)}", state="error")