# Importing Dependencies
import os
import logging
import pandas as pd
from fastapi import APIRouter, HTTPException, status

from pipeline import run_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI router
router = APIRouter()

# Pipeline route
@router.post("/pipeline")
async def pipeline(data: dict):
    """
    Process the query and return structured results.
    """
    try:
        # Extract data from request
        query = data.get("query")
        column_name = data.get("column_name")
        df = data.get("df")

        # Convert df from list of dictionaries to DataFrame
        df = pd.DataFrame(df)

        # Run the entire pipeline
        results = await run_pipeline(query, column_name, df)
        if results:
            return {
                "filtered_results": results
            }
            # change here
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing the query. Please try again."
            )

    except Exception as e:
        logger.exception("An unexpected error occurred while processing the query.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the query. Please try again."
       )