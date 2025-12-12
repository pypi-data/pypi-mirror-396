import pandas as pd
import requests
from datetime import datetime
import json
from typing import Optional, Dict, Any, Tuple
from .base import SodecoBase
from .schemas import DATEFORMAT
from .schemas import ScheduleGet, ScheduleCreate
from brynq_sdk_functions import Functions


class Schedules(SodecoBase):
    """Handles all schedule-related operations in Sodeco API."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}schedule"

    def get(self, worker_id: Optional[str] = None, start_date: Optional[datetime] = None, employers: list = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Retrieve schedule information from Sodeco API.

        This method fetches schedule data and validates it against the ScheduleGet schema.
        It can retrieve schedules for a specific worker or all schedules.

        Args:
            worker_id (Optional[str]): The ID of the worker to get schedule information for.
                If None, retrieves all schedules.
            start_date (Optional[datetime]): The start date for schedule filtering.
                If provided with worker_id, retrieves schedule for specific worker and date.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing:
                - valid_data: DataFrame with valid schedule records
                - invalid_data: DataFrame with invalid schedule records

        Raises:
            ValueError: If the API request fails or data validation fails

        Example:
            ```python
            # Get all schedules
            valid_schedules, invalid_schedules = client.schedules.get()

            # Get schedule for specific worker
            valid_schedules, invalid_schedules = client.schedules.get(worker_id="12345")

            # Get schedule for specific worker and date
            from datetime import datetime
            date = datetime(2024, 1, 1)
            valid_schedules, invalid_schedules = client.schedules.get(worker_id="12345", start_date=date)
            ```

        Note:
            - Schedule data includes ScheduleID, Description, StartDate, and Week information
            - Week data contains daily hour allocations (Day1-Day7)
            - All dates must be in YYYYMMDD format
        """
        try:
            # Build API URL based on parameters
            if worker_id and start_date:
                url = f"{self.url}/{worker_id}/{start_date.strftime(DATEFORMAT)}"
            elif worker_id:
                url = f"{self.url}/{worker_id}"
            else:
                url = self.url

            # Make API request
            data = self._make_request_with_polling_for_employers(url, employers=employers, use_pagination=False)

            # Convert to DataFrame
            df = pd.DataFrame(data)

            if df.empty:
                return pd.DataFrame(), pd.DataFrame()

            # Add worker_id if not present (for global schedule queries)
            if worker_id and 'WorkerId' not in df.columns:
                df['WorkerId'] = worker_id

            # Validate data using schema
            valid_data, invalid_data = Functions.validate_data(df, ScheduleGet)
            return valid_data, invalid_data

        except Exception as e:
            raise ValueError(f"Failed to retrieve schedule data: {str(e)}") from e

    def create(self, data: Dict[str, Any], employer: str = None) -> requests.Response:
        """
        Create a new schedule entry in Sodeco.

        This method validates the input data using Pydantic schema and creates
        a new schedule record in the Sodeco system.

        Args:
            data (Dict[str, Any]): Schedule data to create, including:
                - schedule_id (str): Required. Schedule identifier (0-4 characters)
                - description (str): Required. Schedule description (0-50 characters)
                - start_date (str): Required. Schedule start date in YYYYMMDD format
                - week (List[Dict]): Required. List of week schedules with:
                    - week_number (int): Week number (1-15)
                    - day_1 to day_7 (Optional[float]): Hours for each day (0.0-24.0)

        Returns:
            requests.Response: The API response containing created schedule data

        Raises:
            ValueError: If the API request fails or data validation fails

        Example:
            ```python
            schedule_data = {
                "schedule_id": "SCH1",
                "description": "Regular Schedule",
                "start_date": "20250101",
                "week": [
                    {
                        "week_number": 1,
                        "day_1": 8.0,
                        "day_2": 8.0,
                        "day_3": 8.0,
                        "day_4": 8.0,
                        "day_5": 8.0,
                        "day_6": 0.0,
                        "day_7": 0.0
                    }
                ]
            }
            response = client.schedules.create(data=schedule_data)
            ```

        Note:
            - All date fields must be in YYYYMMDD format
            - Schedule ID must be unique
            - Week data must include at least one week entry
        """
        try:
            # Validate with Pydantic schema
            validated_data = ScheduleCreate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode='json', exclude_none=True)

            # Send the POST request to create the schedule
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = json.dumps(request_body)

            response = self._make_request_with_polling(
                self.url,
                method='POST',
                headers=headers,
                data=data,
                employer=employer
            )
            return response

        except Exception as e:
            raise ValueError(f"Failed to create schedule: {str(e)}") from e
