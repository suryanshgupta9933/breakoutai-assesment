# Importing Dependencies
import pandas as pd
import streamlit as st

from src.sheets import authenticate_google_sheets, get_sheet_data, update_worksheet

# Initialize Google Sheets client in session state
if "gc" not in st.session_state:
    st.session_state["gc"] = authenticate_google_sheets()

# Page 2: Google Sheets Integration
def sheets_page():
    st.header("Google Sheets Integration")
    gc = st.session_state["gc"]
    if gc:
        st.success("Authenticated with Google Sheets")

        # List all spreadsheets shared with the service account
        spreadsheets = gc.list_spreadsheet_files()
        spreadsheet_names = [file["name"] for file in spreadsheets]

        if spreadsheet_names:
            selected_spreadsheet = st.selectbox("Select a Google Sheet to process:", spreadsheet_names)

            if selected_spreadsheet:
                selected_id = [file["id"] for file in spreadsheets if file["name"] == selected_spreadsheet][0]

                if st.button("Load Google Sheet"):
                    try:
                        sheet_data = get_sheet_data(gc, selected_id)
                        df = pd.DataFrame(sheet_data)
                        st.write("Google Sheet Data:")
                        st.dataframe(df.head(5))

                        # Pipeline processing
                        query = st.text_input(
                            "Enter your query with placeholders, e.g., 'Get me the email of {column_name}'"
                        )
                        selected_column = st.selectbox("Select the main column", df.columns.tolist())

                        if st.button("Run Query on Google Sheet"):
                            with st.spinner("Running query..."):
                                pipeline_data = {
                                    "query": query,
                                    "column_name": selected_column,
                                    "df": df.to_dict(orient="records"),
                                }
                                pipeline_result = requests.post(
                                    os.getenv("PIPELINE_ENDPOINT"), json=pipeline_data
                                )
                                if pipeline_result.status_code == 200:
                                    pipeline_result_data = pipeline_result.json()
                                    result_df = pd.DataFrame(pipeline_result_data["table"])
                                    st.write("Processed Data:")
                                    st.dataframe(result_df)

                                    # Download and Update buttons
                                    csv = result_df.to_csv(index=False)
                                    st.download_button(
                                        "Download Processed Data as CSV", csv, "processed_google_sheet_data.csv", "text/csv"
                                    )
                                    if st.button("Update Google Sheet"):
                                        if update_worksheet(gc, selected_id, result_df):
                                            st.success("Google Sheet updated successfully")
                                        else:
                                            st.error("Failed to update Google Sheet")
                    except Exception as e:
                        st.error(f"Failed to load the Google Sheet: {e}")
        else:
            st.warning("No Google Sheets are shared with the service account.")
    else:
        st.error("Google Sheets authentication failed. Check the service account configuration.")