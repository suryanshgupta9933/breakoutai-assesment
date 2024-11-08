# Importing Dependencies
import os
import logging
import pandas as pd
from io import BytesIO
from fastapi import APIRouter, UploadFile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI router
router = APIRouter()

# Upload csv route
@router.post("/upload-csv")
async def upload_csv(file: UploadFile):
    """
    Read CSV file and return columns.
    """
    df = pd.read_csv(BytesIO(await file.read()))
    return {"columns": df.columns.tolist()}