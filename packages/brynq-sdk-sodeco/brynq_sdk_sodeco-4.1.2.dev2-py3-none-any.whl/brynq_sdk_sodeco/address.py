from typing import Tuple
import pandas as pd
from datetime import datetime
import json

from .base import SodecoBase
from .schemas import DATEFORMAT, AddressGet
from brynq_sdk_functions import Functions
from .schemas.address import AddressCreate, AddressUpdate


class Addresses(SodecoBase):
    """Class for managing addresses in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def get(self, worker_id: str, employer: str = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Retrieve address information for a worker.

        Returns a tuple of (valid_df, invalid_df) validated against AddressSchema.
        """
        url = f"{self.url}/{worker_id}/address"
        data = self._make_request_with_polling(url, employer=employer)
        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame(), pd.DataFrame()
        if 'WorkerNumber' not in df.columns:
            df['WorkerNumber'] = worker_id
        valid_df, invalid_df = Functions.validate_data(df, AddressGet)
        return valid_df, invalid_df

    def create(self, worker_id: str, payload: dict, employer: str = None, debug: bool = False) -> dict:
        """
        Create an address for a worker.
        The payload must adhere to the structure defined by the AddressSchema.

        Args:
            worker_id: The ID of the worker to create an address for
            payload: The address data to create
            debug: If True, prints detailed validation errors

        Returns:
            dict: The created address data

        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/address"

        # Validate with Pydantic Address schema
        try:
            validated = AddressCreate(**payload)
            request_body = validated.model_dump(mode="json", by_alias=True, exclude_none=True)
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = json.dumps(request_body)
            resp = self._make_request_with_polling(url, method='POST', headers=headers, data=data, employer=employer)
            return resp
        except Exception as e:
            error_msg = "Invalid address payload"
            if debug:
                error_details = str(e)
                error_msg = f"{error_msg}: {error_details}"
            raise ValueError(error_msg) from e

    def update(self, worker_id: str, address_date: datetime, payload: dict, employer: str = None, debug: bool = False) -> dict:
        """
        Update an address for a worker.
        The payload must adhere to the structure defined by the AddressSchema.

        Args:
            worker_id: The ID of the worker who owns the address
            address_date: The start date of the address to update
            payload: The address data to update
            debug: If True, prints detailed validation errors

        Returns:
            dict: The updated address data

        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/address/{address_date.strftime(DATEFORMAT)}"

        try:
            validated = AddressUpdate(**payload)
            update_payload = validated.model_dump(mode="json", by_alias=True, exclude_none=True)
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = json.dumps(update_payload)
            resp = self._make_request_with_polling(url, method='PUT', headers=headers, data=data, employer=employer)
            return resp
        except Exception as e:
            error_msg = "Invalid address payload"
            if debug:
                error_details = str(e)
                error_msg = f"{error_msg}: {error_details}"
            raise ValueError(error_msg) from e

    def delete(self, worker_id: str, address_date: datetime, employer: str = None) -> dict:
        """
        Delete an address entry for a worker.

        Args:
            worker_id: The ID of the worker who owns the address
            address_date: The start date of the address to delete

        Returns:
            dict: The response from the server
        """
        url = f"{self.url}/{worker_id}/address/{address_date.strftime(DATEFORMAT)}"

        # Send the DELETE request
        data = self._make_request_with_polling(
            url,
            method='DELETE',
            employer=employer
        )
        return data
