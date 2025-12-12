from typing import Optional
import pandas as pd
from datetime import datetime

from .schemas import DATEFORMAT
from .base import SodecoBase
from .schemas.absencenote import AbsenceNoteSchema
from brynq_sdk_functions import Functions

class AbsenceNotes(SodecoBase):
    """Class for managing absence notes in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"
        self.schema = AbsenceNoteSchema

    def get(self, worker_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get absence note information for a worker.

        Args:
            worker_id: The worker ID to get absence note information for

        Returns:
            pd.DataFrame: DataFrame containing the absence note information
        """
        url = f"{self.url}/{worker_id}/absencenote"
        data = self._make_request_with_polling(url)
        df = pd.DataFrame(data)
        valid_timeoff, invalid_timeoff = Functions.validate_data(df=df, schema=self.schema, debug=True)
        return valid_timeoff, invalid_timeoff

    def create(self, worker_id: str, payload: dict, debug: bool = False) -> dict:
        """
        Create an absence note entry for a worker.
        The payload must adhere to the structure defined by the AbsenceNoteSchema.

        Args:
            worker_id: The ID of the worker to create an absence note entry for
            payload: The absence note data to create
            debug: If True, prints detailed validation errors

        Returns:
            dict: The created absence note data

        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/absencenote"

        # Convert payload to DataFrame and validate
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, self.schema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid absence note payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the POST request to create the absence note
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='POST',
            headers=headers,
            data=data
        )
        return data

    def update(self, worker_id: str, note_date: datetime, payload: dict, debug: bool = False) -> dict:
        """
        Update an absence note entry for a worker.
        The payload must adhere to the structure defined by the AbsenceNoteSchema.

        Args:
            worker_id: The ID of the worker who owns the absence note
            note_date: The start date of the absence note to update
            payload: The absence note data to update
            debug: If True, prints detailed validation errors

        Returns:
            dict: The updated absence note data

        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/absencenote/{note_date.strftime(DATEFORMAT)}"

        # Validate the payload
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, self.schema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid absence note payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the PUT request to update the absence note
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='PUT',
            headers=headers,
            data=data
        )
        return data

    def delete(self, worker_id: str, note_date: datetime) -> dict:
        """
        Delete an absence note entry for a worker.

        Args:
            worker_id: The ID of the worker who owns the absence note
            note_date: The start date of the absence note to delete

        Returns:
            dict: The response from the server
        """
        url = f"{self.url}/{worker_id}/absencenote/{note_date.strftime(DATEFORMAT)}"

        # Send the DELETE request
        data = self._make_request_with_polling(
            url,
            method='DELETE'
        )
        return data
