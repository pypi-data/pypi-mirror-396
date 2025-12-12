from typing import Optional
import pandas as pd
from datetime import datetime

from .schemas import DATEFORMAT
from .base import SodecoBase
from .schemas.tax import TaxSchema
from brynq_sdk_functions import Functions


class Taxes(SodecoBase):
    """Class for managing tax information in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def get(self, worker_id: str) -> pd.DataFrame:
        """
        Get tax information for a worker.
        
        Args:
            worker_id: The worker ID to get tax information for
            
        Returns:
            pd.DataFrame: DataFrame containing the tax information
        """
        url = f"{self.url}/{worker_id}/tax"
        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)

    def create(self, worker_id: str, payload: dict, debug: bool = False) -> dict:
        """
        Create a tax entry for a worker.
        The payload must adhere to the structure defined by the TaxSchema.
        
        Args:
            worker_id: The ID of the worker to create a tax entry for
            payload: The tax data to create
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The created tax data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/tax"
        
        # Convert payload to DataFrame and validate
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, TaxSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid tax payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the POST request to create the tax entry
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='POST',
            headers=headers,
            data=data
        )
        return data

    def update(self, worker_id: str, tax_date: datetime, payload: dict, debug: bool = False) -> dict:
        """
        Update a tax entry for a worker.
        The payload must adhere to the structure defined by the TaxSchema.
        
        Args:
            worker_id: The ID of the worker who owns the tax entry
            tax_date: The start date of the tax entry to update
            payload: The tax data to update
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The updated tax data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/tax/{tax_date.strftime(DATEFORMAT)}"
        
        # Validate the payload
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, TaxSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid tax payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the PUT request to update the tax entry
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='PUT',
            headers=headers,
            data=data
        )
        return data

    def delete(self, worker_id: str, tax_date: datetime) -> dict:
        """
        Delete a tax entry for a worker.
        
        Args:
            worker_id: The ID of the worker who owns the tax entry
            tax_date: The start date of the tax entry to delete
            
        Returns:
            dict: The response from the server
        """
        url = f"{self.url}/{worker_id}/tax/{tax_date.strftime(DATEFORMAT)}"
        
        # Send the DELETE request
        data = self._make_request_with_polling(
            url,
            method='DELETE'
        )
        return data
