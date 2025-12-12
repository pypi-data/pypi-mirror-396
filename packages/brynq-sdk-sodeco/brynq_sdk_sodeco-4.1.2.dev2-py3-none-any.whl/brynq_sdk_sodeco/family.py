from typing import Tuple
import pandas as pd
from datetime import datetime
import json

from .schemas import DATEFORMAT
from .base import SodecoBase
from .schemas import FamilyGet
from .schemas.family import FamilyCreate, FamilyUpdate
from brynq_sdk_functions import Functions


class Families(SodecoBase):
    """Class for managing family status in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def get(self, worker_id: str, employer: str = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get family status information for a worker.

        Args:
            worker_id: The worker ID to get family status for

        Returns:
            pd.DataFrame: DataFrame containing the family status information
        """
        url = f"{self.url}/{worker_id}/familystatus"
        data = self._make_request_with_polling(url, employer=employer)
        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame(), pd.DataFrame()
        valid_df, invalid_df = Functions.validate_data(df, FamilyGet)
        return valid_df, invalid_df

    def create(self, worker_id: str, payload: dict, employer: str = None, debug: bool = False) -> dict:
        """
        Create a family status entry for a worker.
        The payload must adhere to the structure defined by the FamilySchema.

        Args:
            worker_id: The ID of the worker to create a family status for
            payload: The family status data to create
            debug: If True, prints detailed validation errors

        Returns:
            dict: The created family status data

        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/familystatus"

        try:
            validated = FamilyCreate(**payload)
            request_body = validated.model_dump(mode="json", by_alias=True, exclude_none=True)
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = json.dumps(request_body)
            resp = self._make_request_with_polling(url, method='POST', headers=headers, data=data, employer=employer)
            return resp
        except Exception as e:
            error_msg = "Invalid family status payload"
            if debug:
                error_msg = f"{error_msg}: {str(e)}"
            raise ValueError(error_msg) from e

    def update(self, worker_id: str, family_date: datetime, payload: dict, employer: str = None, debug: bool = False) -> dict:
        """
        Update a family member for a worker.
        The payload must adhere to the structure defined by the FamilySchema.

        Args:
            worker_id: The ID of the worker who owns the family member
            family_date: The start date of the family status to update
            payload: The family member data to update
            debug: If True, prints detailed validation errors

        Returns:
            dict: The updated family member data

        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/familystatus/{family_date.strftime(DATEFORMAT)}"

        try:
            validated = FamilyUpdate(**payload)
            update_payload = validated.model_dump(mode="json", by_alias=True, exclude_none=True)
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = json.dumps(update_payload)
            resp = self._make_request_with_polling(url, method='PUT', headers=headers, data=data, employer=employer)
            return resp
        except Exception as e:
            error_msg = "Invalid family member payload"
            if debug:
                error_msg = f"{error_msg}: {str(e)}"
            raise ValueError(error_msg) from e

    def delete(self, worker_id: str, family_date: datetime, employer: str = None) -> dict:
        """
        Delete a family status entry for a worker.

        Args:
            worker_id: The ID of the worker who owns the family status
            family_date: The start date of the family status to delete

        Returns:
            dict: The response from the server
        """
        url = f"{self.url}/{worker_id}/familystatus/{family_date.strftime(DATEFORMAT)}"

        # Send the DELETE request
        data = self._make_request_with_polling(
            url,
            method='DELETE',
            employer=employer
        )
        return data
