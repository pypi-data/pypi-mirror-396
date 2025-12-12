from typing import Dict, Any, Tuple
import pandas as pd
import requests
from .base import SodecoBase
from .schemas.communication import CommunicationCreate, CommunicationUpdate, CommunicationGet, CommunicationDelete
from brynq_sdk_functions import Functions


class Communications(SodecoBase):
    """Handles all communication-related operations in Sodeco API."""

    def __init__(self, sodeco):
        """Initialize the Communications class."""
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def get(self, worker_id: str, employer: str = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get communication information for a worker.

        Args:
            worker_id (str): The worker ID to get communication for

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (valid_data, invalid_data)
        """
        try:
            url = f"{self.url}/{worker_id}/communication"
            data = self._make_request_with_polling(url, employer=employer)

            # Convert to DataFrame
            df = pd.DataFrame(data)

            if df.empty:
                return pd.DataFrame(), pd.DataFrame()

            # Validate data using schema
            valid_data, invalid_data = Functions.validate_data(df, CommunicationGet)
            return valid_data, invalid_data

        except Exception as e:
            raise Exception(f"Failed to retrieve communication data: {str(e)}") from e

    def create(self, worker_id: str, data: Dict[str, Any], employer: str = None) -> requests.Response:
        """
        Create a communication entry for a worker.

        Args:
            worker_id (str): The ID of the worker to create a communication for
            data (Dict[str, Any]): The communication data to create

        Returns:
            requests.Response: The API response
        """
        try:
            # Validate with Pydantic schema
            req_data = CommunicationCreate(**data)
            req_body = req_data.model_dump(by_alias=True, mode='json', exclude_none=True)

            url = f"{self.url}/{worker_id}/communication"

            # Send the POST request to create the communication
            headers, request_data = self._prepare_raw_request(req_body)
            resp_data = self._make_request_with_polling(
                url,
                method='POST',
                headers=headers,
                data=request_data,
                employer=employer
            )
            return resp_data

        except Exception as e:
            raise Exception(f"Failed to create communication: {str(e)}") from e

    def update(self, worker_id: str, data: Dict[str, Any], employer: str = None) -> requests.Response:
        """
        Update a communication entry for a worker.

        Args:
            worker_id (str): The ID of the worker
            data (Dict[str, Any]): The communication data to update

        Returns:
            requests.Response: The API response
        """
        try:
            # Validate with Pydantic schema
            req_data = CommunicationUpdate(**data)
            req_body = req_data.model_dump(by_alias=True, mode='json', exclude_none=True)

            url = f"{self.url}/{worker_id}/communication"

            # Send the PUT/PATCH request to update the communication
            headers, request_data = self._prepare_raw_request(req_body)
            resp_data = self._make_request_with_polling(
                url,
                method='PUT',
                headers=headers,
                data=request_data,
                employer=employer
            )
            return resp_data

        except Exception as e:
            raise Exception(f"Failed to update communication: {str(e)}") from e

    def delete(self, worker_id: str, payload: Dict[str, Any], employer: str = None) -> requests.Response:
        """
        Delete a communication entry for a worker.

        Args:
            worker_id (str): The ID of the worker who owns the communication
            payload (Dict[str, Any]): The communication data to delete

        Returns:
            requests.Response: The API response
        """
        try:
            url = f"{self.url}/{worker_id}/communication"

            validated_data = CommunicationDelete(**payload)
            delete_payload = validated_data.model_dump(by_alias=True, mode='json', exclude_none=True)

            # Send the PUT request to update the worker
            headers, data = self._prepare_raw_request(delete_payload)

            # Send the DELETE request
            resp_data = self._make_request_with_polling(
                url,
                headers=headers,
                method='DELETE',
                data=data,
                employer=employer
            )
            return resp_data

        except Exception as e:
            raise Exception(f"Failed to delete communication: {str(e)}") from e
