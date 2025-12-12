from typing import Optional
import pandas as pd
from datetime import datetime

from .schemas import DATEFORMAT
from .base import SodecoBase
from .schemas.replacement import ReplacementSchema
from brynq_sdk_functions import Functions


class Replacements(SodecoBase):
    """Class for managing worker replacements in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def get(self, worker_id: str) -> pd.DataFrame:
        """
        Get replacement information for a worker.
        
        Args:
            worker_id: The worker ID to get replacement information for
            
        Returns:
            pd.DataFrame: DataFrame containing the replacement information
        """
        url = f"{self.url}/{worker_id}/replacement"
        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)

    def create(self, worker_id: str, payload: dict, debug: bool = False) -> dict:
        """
        Create a replacement entry for a worker.
        The payload must adhere to the structure defined by the ReplacementSchema.
        
        Args:
            worker_id: The ID of the worker to create a replacement entry for
            payload: The replacement data to create
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The created replacement data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/replacement"
        
        # Convert payload to DataFrame and validate
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, ReplacementSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid replacement payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the POST request to create the replacement entry
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='POST',
            headers=headers,
            data=data
        )
        return data

    def update(self, worker_id: str, replacement_date: datetime, payload: dict, debug: bool = False) -> dict:
        """
        Update a replacement entry for a worker.
        The payload must adhere to the structure defined by the ReplacementSchema.
        
        Args:
            worker_id: The ID of the worker who owns the replacement entry
            replacement_date: The start date of the replacement to update
            payload: The replacement data to update
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The updated replacement data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/replacement/{replacement_date.strftime(DATEFORMAT)}"
        
        # Validate the payload
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, ReplacementSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid replacement payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the PUT request to update the replacement entry
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='PUT',
            headers=headers,
            data=data
        )
        return data

    def delete(self, worker_id: str, replacement_date: datetime) -> dict:
        """
        Delete a replacement entry for a worker.
        
        Args:
            worker_id: The ID of the worker who owns the replacement
            replacement_date: The start date of the replacement to delete
            
        Returns:
            dict: The response from the server
        """
        url = f"{self.url}/{worker_id}/replacement/{replacement_date.strftime(DATEFORMAT)}"
        
        # Send the DELETE request
        data = self._make_request_with_polling(
            url,
            method='DELETE'
        )
        return data
