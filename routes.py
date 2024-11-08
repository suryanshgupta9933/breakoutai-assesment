# Importing Dependencies
import pandas as pd
from io import BytesIO
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware

# FastAPI app
app = FastAPI()

# CORS for Streamlit communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for FileColumn
class FileColumn(BaseModel):
    column_name: str

@app.post("/upload-csv/")
async def upload_csv(file: UploadFile):
    # Read CSV file and return columns
    df = pd.read_csv(BytesIO(await file.read()))
    return {"columns": df.columns.tolist()}

@app.post("/process-query/")
async def process_query(column_data: FileColumn, query: str):
    # Dummy response
    return {"message": f"Processing query '{query}' for column '{column_data.column_name}'"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)