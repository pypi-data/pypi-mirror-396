from datetime import datetime
import requests
import pandas as pd
import warnings
import json
from typing import List, Dict, Union, Optional
import pandera as pa
from brynq_sdk_functions import Functions
from .schemas import AbsenceSchema, AbsencesSchema, DATEFORMAT
from .base import SodecoBase


class Absences(SodecoBase):

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}absences"  # Base URL for general absences
        self.worker_url = f"{self.sodeco.base_url}worker"  # Base URL for worker-specific absences

    def get(self, start_date: datetime, worker_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get absences for a specific date, optionally filtered by worker_id.
        
        Args:
            start_date: The date to get absences for
            worker_id: Optional worker ID to filter absences
            
        Returns:
            pd.DataFrame: DataFrame containing the absences
        """
        if worker_id is not None:
            url = f"{self.worker_url}/{worker_id}/absences/{start_date.strftime(DATEFORMAT)}"
        else:
            url = f"{self.url}/{start_date.strftime(DATEFORMAT)}"

        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)

    def validate_absences_list(self, absences_list: List[Dict], debug: bool = False) -> List[Dict]:
        """
        Validate individual absence entries within the absences list.
        
        Args:
            absences_list: List of absence dictionaries to validate
            debug: If True, prints detailed validation errors
            
        Returns:
            List[Dict]: List of validated absence dictionaries
        """
        if not absences_list:
            return []
            
        # Convert list of absences to DataFrame for validation
        absences_df = pd.DataFrame(absences_list)
        valid_data, invalid_data = Functions.validate_data(absences_df, AbsenceSchema, debug=debug)
        
        if len(invalid_data) > 0:
            error_msg = "Invalid absence entries found"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)
            
        return valid_data.to_dict(orient='records')

    def create(self, payload: Union[Dict, List[Dict]], debug: bool = False) -> Dict:
        """
        Create absences for one or multiple workers.
        
        Args:
            payload: Either a single worker's absences dict or a list of worker absences
            debug: If True, prints detailed validation errors
            
        Returns:
            Dict: API response containing created absences
            
        Raises:
            ValueError: If the payload is invalid
            Exception: If the create request fails
        """
        # Convert single dict to list for consistent processing
        if isinstance(payload, dict):
            payload = [payload]

        # Convert to DataFrame for initial validation
        df = pd.DataFrame(payload)
        valid_data, invalid_data = Functions.validate_data(df, AbsencesSchema, debug=debug)
        
        if len(invalid_data) > 0:
            error_msg = "Invalid absences payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Validate individual absence entries for each worker
        for idx, row in valid_data.iterrows():
            valid_data.at[idx, 'Absences'] = self.validate_absences_list(row['Absences'], debug=debug)

        # Send the POST request to create the absence
        headers, data = self._prepare_raw_request(valid_data.to_dict(orient='records'))
        data = self._make_request_with_polling(
            self.url,
            method='POST',
            headers=headers,
            data=data
        )
        return data

    def update(self, worker_number: int, payload: Dict, debug: bool = False) -> Dict:
        """
        Update absences for a specific worker.
        
        Args:
            worker_number: The worker number whose absences to update
            payload: Dict containing the worker's absences data
            debug: If True, prints detailed validation errors
            
        Returns:
            Dict: API response containing updated absences
            
        Raises:
            ValueError: If the payload is invalid or worker_number is not provided
            Exception: If the update request fails
        """
        if not worker_number:
            raise ValueError("worker_number must be provided for update operation")

        # Ensure worker_number in payload matches the parameter
        payload['WorkerNumber'] = worker_number

        # Convert to DataFrame for validation
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, AbsenceSchema, debug=debug)
        
        if len(invalid_data) > 0:
            error_msg = "Invalid absences payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Validate individual absence entries
        valid_data.at[0, 'Absences'] = self.validate_absences_list(valid_data.iloc[0]['Absences'], debug=debug)

        # Send the PUT request to update the absence
        url = f"{self.url}/{worker_number}"
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='PUT',
            headers=headers,
            data=data
        )
        return data
