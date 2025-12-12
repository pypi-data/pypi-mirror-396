from typing import Dict, Any, Optional
import pandas as pd
from .base import SodecoBase
from .schemas.prestation import PrestationModel, DeletePrestationModel
import json

class Prestations(SodecoBase):
    """Class for managing prestations in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}prestations"

    def create(self, payload: Dict[str, Any], employer: str = None) -> dict:
        """
        Create a prestation entry.
        The payload must adhere to the structure defined by the PrestationModel.

        Args:
            payload: The prestation data to create
            debug: If True, only validate the payload without making the request

        Returns:
            dict: Response from the API

        Raises:
            ValueError: If the payload is invalid
        """
        # Validate with Pydantic schema
        req_data = PrestationModel(**payload)
        req_body = req_data.model_dump(by_alias=True, mode='json', exclude_none=True)

        # Send the POST request to create the contract (same style as Workers.create)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = json.dumps([req_body])
        resp_data = self._make_request_with_polling(
            url=self.url,
            method="POST",
            headers=headers,
            data=data,
            employer=employer
        )
        return resp_data

    def delete(self, payload: Dict[str, Any], employer: str = None) -> dict:
        """
        Delete prestations for a worker in a specific month and year.

        Args:
            payload: Dictionary containing:
                    - WorkerNumber: The worker number to delete prestations for
                    - Month: The month to delete prestations for (1-12)
                    - Year: The year to delete prestations for

        Returns:
            dict: Response from the API

        Raises:
            ValueError: If the payload is invalid
        """
        # Validate the payload
        req_data = DeletePrestationModel(**payload)
        req_body = req_data.model_dump(by_alias=True, mode='json', exclude_none=True)

        url = f"{self.url}/{payload['worker_number']}/{payload['year']}/{payload['month']:02d}"

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = json.dumps(req_body)
        resp_data = self._make_request_with_polling(
            url=url,
            method="DELETE",
            headers=headers,
            data=data,
            employer=employer
        )
        return resp_data

    def complete(self, payload: Dict[str, Any], employer: str = None) -> dict:
        """
        Mark prestations as completed for processing in the system.

        Args:
            payload: Dictionary containing:
                    - Month: The month to mark as completed (1-12)
                    - Year: The year to mark as completed
                    - Correction: Optional flag to indicate if this is a correction ('Y' or 'N')

        Returns:
            dict: Response from the API

        Raises:
            ValueError: If the payload is invalid
        """
        # Validate the payload
        req_data = PrestationCompletedModel(**payload)
        req_body = req_data.model_dump(by_alias=True, mode='json', exclude_none=True)

        url = f"{self.url}/completed"

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = json.dumps(req_body)
        resp_data = self._make_request_with_polling(
            url=url,
            method="POST",
            headers=headers,
            data=data,
            employer=employer
        )
        return resp_data
