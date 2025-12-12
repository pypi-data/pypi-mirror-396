from typing import Optional
import pandas as pd
from datetime import datetime
from .base import SodecoBase
from .schemas.divergentpayment import DivergentPaymentSchema
from .schemas import DATEFORMAT
from brynq_sdk_functions import Functions


class DivergentPayments(SodecoBase):
    """Class for managing divergent payments in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def get(self, worker_id: str) -> pd.DataFrame:
        """
        Get divergent payment information for a worker.
        
        Args:
            worker_id: The worker ID to get divergent payment information for
            
        Returns:
            pd.DataFrame: DataFrame containing the divergent payment information
        """
        url = f"{self.url}/{worker_id}/divergentpayment"
        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)

    def create(self, worker_id: str, payload: dict, debug: bool = False) -> dict:
        """
        Create a divergent payment entry for a worker.
        The payload must adhere to the structure defined by the DivergentPaymentSchema.
        
        Args:
            worker_id: The ID of the worker to create a divergent payment entry for
            payload: The divergent payment data to create
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The created divergent payment data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/divergentpayment"
        
        # Convert payload to DataFrame and validate
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, DivergentPaymentSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid divergent payment payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the POST request to create the divergent payment
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='POST',
            headers=headers,
            data=data
        )
        return data

    def update(self, worker_id: str, payment_date: datetime, type_id: str, payload: dict, debug: bool = False) -> dict:
        """
        Update a divergent payment entry for a worker.
        The payload must adhere to the structure defined by the DivergentPaymentSchema.
        
        Args:
            worker_id: The ID of the worker who owns the divergent payment
            payment_date: The start date of the divergent payment to update
            type_id: The type ID of the divergent payment
            payload: The divergent payment data to update
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The updated divergent payment data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/divergentpayment/{payment_date.strftime(DATEFORMAT)}/{type_id}"
        
        # Validate the payload
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, DivergentPaymentSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid divergent payment payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the PUT request to update the divergent payment
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='PUT',
            headers=headers,
            data=data
        )
        return data

    def delete(self, worker_id: str, payment_date: datetime, type_id: str) -> dict:
        """
        Delete a divergent payment entry for a worker.
        
        Args:
            worker_id: The ID of the worker who owns the divergent payment
            payment_date: The start date of the divergent payment to delete
            type_id: The type ID of the divergent payment to delete
            
        Returns:
            dict: The response from the server
        """
        url = f"{self.url}/{worker_id}/divergentpayment/{payment_date.strftime(DATEFORMAT)}/{type_id}"
        
        # Send the DELETE request
        data = self._make_request_with_polling(
            url,
            method='DELETE'
        )
        return data
