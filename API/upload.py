# Importing Dependencies
import os
import logging
import pandas as pd
from io import BytesIO
from fastapi import APIRouter, UploadFile, HTTPException, status

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI router
router = APIRouter()

# Upload csv route
@router.post("/upload-csv")
async def upload_csv(file: UploadFile):
    """
    Read CSV file and return its contents and columns.
    """    
    try:
        # Read CSV file into a DataFrame
        df = pd.read_csv(BytesIO(await file.read()), encoding="utf-8")

        # Check if the DataFrame is empty
        if df.empty:
            logger.warning("Uploaded CSV is empty.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded CSV is empty."
            )

        # Convert DataFrame to JSON-friendly format
        data = df.to_dict(orient="records")  # Each row becomes a dictionary in a list

        # Return csv data
        return {"csv_data": data}

    except pd.errors.EmptyDataError:
        logger.error("Uploaded file is not a valid CSV or is empty.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid CSV or is empty."
        )

    except Exception as e:
        logger.exception("Unexpected error occurred while reading the CSV file.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the file. Please try again."
        )