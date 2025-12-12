from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import base64
import os
import pandas as pd

from .base import SodecoBase
from .schemas.document import DocumentModel, DocumentGet
from brynq_sdk_functions import Functions

# Date format YYYYMMDD
DATEFORMAT = "%Y%m%d"


class Documents(SodecoBase):
    """Document management in Sodeco Prisma"""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}document"

    def create(self, payload: dict, debug: bool = False) -> dict:
        """Create a document in Prisma.

        Args:
            payload: Complete document data dictionary
            debug: If True, only validate without sending request

        Returns:
            dict: Response from the API containing the document ID

        Raises:
            ValueError: If the document data is invalid
        """
        # Validate document data
        try:
            # Validate payload using Pydantic model
            validated_data = DocumentModel(**payload)
        except Exception as e:
            raise ValueError(f"Invalid document data: {str(e)}")

        # If debug mode, return without making request
        if debug:
            return validated_data.dict()

        # Send the POST request to upload the document
        headers, data = self._prepare_raw_request(validated_data.dict())
        response = self._make_request_with_polling(
            url=self.url,
            method="POST",
            headers=headers,
            data=data
        )
        return response

    def list(self, start_date: datetime, end_date: datetime, employers: list = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Get a list of available documents within the given period.

        The list includes both documents for the employer and documents
        for the employees of that employer. Each document has a unique ID
        that can be used to retrieve the document itself.

        Args:
            start_date: The start date of the period
            end_date: The end date of the period

        Returns:
            dict: List of available documents
        """
        url = f"{self.url}/listing/{start_date.strftime(DATEFORMAT)}/{end_date.strftime(DATEFORMAT)}"
        data = self._make_request_with_polling_for_employers(url, employers=employers, use_pagination=False)
        df = pd.DataFrame(data)

        df = df.drop(columns=['employer'])

        valid_df, invalid_df = Functions.validate_data(df, DocumentGet)
        return valid_df, invalid_df

    def get_withdrawn_documents(self, start_date: datetime) -> dict:
        """Get a list of withdrawn documents from the given start date.

        Withdrawn documents are documents that the social secretariat has
        recalled for some reason. This request is NOT per employer,
        the response contains the employer number along with the document ID.

        Args:
            start_date: The start date from which to get withdrawn documents

        Returns:
            dict: List of withdrawn documents
        """
        url = f"{self.url}/listing/withdrawals/{start_date.strftime(DATEFORMAT)}"
        data = self._make_request_with_polling(url)
        return data

    def get(self, document_id: str, file_path: Optional[str] = None, employer: str = None) -> dict:
        """Get a specific document by its ID.

        The document ID can be obtained via the list method.
        The result consists of a base64 converted byte array.

        If output_path is provided, the document will be saved to that location
        and the path to the saved file will be added to the returned document data.

        Args:
            document_id: The ID of the document to retrieve
            file_path: Optional filepath where to save the document (including filename)

        Returns:
            dict: The document data, with an additional 'saved_path' key if output_path was provided

        Raises:
            ValueError: If the output_path is provided but the document cannot be saved
        """
        # Get the document from the API
        url = f"{self.url}/{document_id}"
        document_data = self._make_request_with_polling(url, document=True, employer=employer)

        # If output_path is not provided, just return the document data
        if file_path is None:
            return document_data

        # Decode base64 content
        try:
            content = base64.b64decode(document_data)
        except Exception as e:
            raise ValueError(f"Failed to decode document content: {str(e)}")

        # Save to file
        with open(file_path, "wb") as file:
            file.write(content)
