from typing import Optional, Dict, Any, Tuple
import pandas as pd
import requests
from datetime import datetime
import json
from .schemas import DATEFORMAT
from .base import SodecoBase
from .schemas import CarGet, CarCreate, CarUpdate
from brynq_sdk_functions import Functions

class Cars(SodecoBase):
    """Handles all company car-related operations in Sodeco API."""

    def __init__(self, sodeco):
        """Initialize the Cars class."""
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def get(self, employers: list = None, worker_id: Optional[str] = None, start_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Retrieve company car information from Sodeco API with validation.

        This method fetches company car data and validates it against the CarGet schema.
        Returns both valid and invalid data separately for comprehensive data quality control.

        Args:
            worker_id (Optional[str]): Specific worker ID to retrieve car information for.
                If None, retrieves all company cars.
            start_date (Optional[datetime]): Filter cars by start date.
                Must be provided with worker_id for specific car retrieval.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing (valid_data, invalid_data) DataFrames:
                - valid_data: Company car records that passed validation
                - invalid_data: Company car records that failed validation

        Raises:
            ValueError: If start_date is provided without worker_id
            requests.exceptions.HTTPError: If API request fails
            Exception: If data retrieval or validation fails

        Example:
            ```python
            # Get all company cars
            valid_cars, invalid_cars = client.cars.get()

            # Get cars for specific worker
            valid_cars, invalid_cars = client.cars.get(worker_id="12345")

            # Get specific car for worker on date
            from datetime import datetime
            start_date = datetime(2024, 1, 1)
            valid_cars, invalid_cars = client.cars.get(worker_id="12345", start_date=start_date)

            # Check validation results
            print(f"Valid car records: {len(valid_cars)}")
            print(f"Invalid car records: {len(invalid_cars)}")
            ```

        Note:
            - All DataFrame column names are converted to snake_case
            - Empty DataFrames are returned if no data is found
            - Invalid data is captured separately and not included in valid DataFrame
        """
        try:
            # Build API URL based on parameters
            if worker_id and start_date:
                url = f"{self.url}/{worker_id}/companycar/{start_date.strftime(DATEFORMAT)}"
            elif worker_id:
                url = f"{self.url}/{worker_id}/companycar"
            else:
                url = f"{self.sodeco.base_url}companycar"

            # Make API request
            data = self._make_request_with_polling_for_employers(url, employers=employers, use_pagination=False)

            # Convert to DataFrame
            df = pd.DataFrame(data)

            if df.empty:
                return pd.DataFrame(), pd.DataFrame()

            # Add worker_id if not present (for global car queries)
            if worker_id and 'WorkerId' not in df.columns:
                df['WorkerId'] = worker_id

            # Validate data using schema
            valid_data, invalid_data = Functions.validate_data(df, CarGet)
            return valid_data, invalid_data

        except Exception as e:
            raise ValueError(f"Failed to retrieve company car data: {str(e)}") from e

    def create(self, worker_id: str, data: Dict[str, Any], employer: str = None) -> requests.Response:
        """
        Create a new company car entry for a worker.

        This method validates the input data using Pydantic schema and creates
        a new company car record in the Sodeco system.

        Args:
            worker_id (str): The ID of the worker to create a company car entry for
            data (Dict[str, Any]): Company car data to create, including:
                - starting_date (str): Required. Car start date in YYYYMMDD format
                - license_plate (str): Required. Car license plate number
                - ending_date (Optional[str]): Car end date in YYYYMMDD format
                - worker_id (Optional[int]): Worker ID associated with the car
                - cat_rsz (Optional[str]): Social security category code
                - motor_type (Optional[str]): Motor type (Gasoline, Diesel, LPG, Electric, CNG)
                - tax_horsepower (Optional[int]): Tax horsepower (0-99)
                - co2_emissions_hybride_wltp (Optional[int]): CO2 emissions hybrid WLTP (0-500)
                - co2_emissions_hybride (Optional[int]): CO2 emissions hybrid (0-500)
                - co2_emissions_wltp (Optional[int]): CO2 emissions WLTP (0-500)
                - co2_emissions (Optional[int]): CO2 emissions (0-500)
                - code (Optional[int]): Salary code (4000-8999)
                - fuel_card (Optional[str]): Fuel card number
                - brand (Optional[str]): Car brand
                - order_date (Optional[str]): Car order date in YYYYMMDD format
                - registration_date (Optional[str]): Car registration date in YYYYMMDD format
                - catalog_price (Optional[float]): Catalog price
                - informative (Optional[str]): Informative flag (N/Y)
                - light_truck (Optional[str]): Light truck flag (N/Y)
                - pool_car (Optional[str]): Pool car flag (N/Y)
                - pers_contribution_amount (Optional[float]): Personal contribution amount
                - pers_contribution_percentage (Optional[float]): Personal contribution percentage
                - pers_contribution_code (Optional[int]): Personal contribution salary code (4000-8999)
                - pers_contribution_startdate (Optional[str]): Personal contribution start date in YYYYMMDD format
                - pers_contribution_enddate (Optional[str]): Personal contribution end date in YYYYMMDD format

        Returns:
            requests.Response: The API response containing created car data

        Raises:
            ValueError: If the input data is invalid
            requests.exceptions.HTTPError: If the API request fails

        Example:
            ```python
            car_data = {
                "starting_date": "20250101",
                "license_plate": "ABC-123",
                "motor_type": "Gasoline",
                "tax_horsepower": 12,
                "co2_emissions": 120,
                "brand": "Toyota",
                "catalog_price": 25000.0
            }
            response = client.cars.create(worker_id="12345", data=car_data)
            ```

        Note:
            - All date fields must be in YYYYMMDD format
            - License plate is required and must be unique
            - Motor type must be one of the predefined values
        """
        try:
            url = f"{self.url}/{worker_id}/companycar"

            # Validate with Pydantic schema
            validated_data = CarCreate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode='json', exclude_none=True)

            # Send the POST request to create the car
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = json.dumps(request_body)

            response = self._make_request_with_polling(
                url,
                method='POST',
                headers=headers,
                data=data,
                employer=employer
            )
            return response

        except Exception as e:
            raise ValueError(f"Failed to create company car: {str(e)}") from e

    def update(self, worker_id: str, car_date: datetime, data: Dict[str, Any], employer: str = None) -> requests.Response:
        """
        Update an existing company car entry for a worker.

        This method validates the input data using Pydantic schema and updates
        an existing company car record in the Sodeco system.

        Args:
            worker_id (str): The ID of the worker who owns the car entry
            car_date (datetime): The start date of the car entry to update
            data (Dict[str, Any]): Company car data to update, including:
                - starting_date (Optional[str]): Car start date in YYYYMMDD format
                - license_plate (Optional[str]): Car license plate number
                - ending_date (Optional[str]): Car end date in YYYYMMDD format
                - worker_id (Optional[int]): Worker ID associated with the car
                - cat_rsz (Optional[str]): Social security category code
                - motor_type (Optional[str]): Motor type (Gasoline, Diesel, LPG, Electric, CNG)
                - tax_horsepower (Optional[int]): Tax horsepower (0-99)
                - co2_emissions_hybride_wltp (Optional[int]): CO2 emissions hybrid WLTP (0-500)
                - co2_emissions_hybride (Optional[int]): CO2 emissions hybrid (0-500)
                - co2_emissions_wltp (Optional[int]): CO2 emissions WLTP (0-500)
                - co2_emissions (Optional[int]): CO2 emissions (0-500)
                - code (Optional[int]): Salary code (4000-8999)
                - fuel_card (Optional[str]): Fuel card number
                - brand (Optional[str]): Car brand
                - order_date (Optional[str]): Car order date in YYYYMMDD format
                - registration_date (Optional[str]): Car registration date in YYYYMMDD format
                - catalog_price (Optional[float]): Catalog price
                - informative (Optional[str]): Informative flag (N/Y)
                - light_truck (Optional[str]): Light truck flag (N/Y)
                - pool_car (Optional[str]): Pool car flag (N/Y)
                - pers_contribution_amount (Optional[float]): Personal contribution amount
                - pers_contribution_percentage (Optional[float]): Personal contribution percentage
                - pers_contribution_code (Optional[int]): Personal contribution salary code (4000-8999)
                - pers_contribution_startdate (Optional[str]): Personal contribution start date in YYYYMMDD format
                - pers_contribution_enddate (Optional[str]): Personal contribution end date in YYYYMMDD format

        Returns:
            requests.Response: The API response containing updated car data

        Raises:
            ValueError: If the input data is invalid
            requests.exceptions.HTTPError: If the API request fails

        Example:
            ```python
            from datetime import datetime

            car_update_data = {
                "motor_type": "Electric",
                "co2_emissions": 0,
                "catalog_price": 35000.0,
                "fuel_card": "FC-789"
            }
            car_date = datetime(2024, 1, 1)
            response = client.cars.update(worker_id="12345", car_date=car_date, data=car_update_data)
            ```

        Note:
            - All date fields must be in YYYYMMDD format
            - Only provided fields will be updated
            - Motor type must be one of the predefined values if provided
        """
        try:
            url = f"{self.url}/{worker_id}/companycar/{car_date.strftime(DATEFORMAT)}"

            # Validate with Pydantic schema
            validated_data = CarUpdate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode='json', exclude_none=True)

            # Send the PUT request to update the car
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = json.dumps(request_body)

            response = self._make_request_with_polling(
                url,
                method='PUT',
                headers=headers,
                data=data,
                employer=employer
            )
            return response

        except Exception as e:
            raise ValueError(f"Failed to update company car: {str(e)}") from e

    def delete(self, worker_id: str, car_date: datetime, employer: str = None) -> requests.Response:
        """
        Delete a company car entry for a worker.

        This method removes an existing company car record from the Sodeco system.

        Args:
            worker_id (str): The ID of the worker who owns the car entry
            car_date (datetime): The start date of the car entry to delete

        Returns:
            requests.Response: The API response confirming deletion

        Raises:
            requests.exceptions.HTTPError: If the API request fails
            Exception: If the deletion operation fails

        Example:
            ```python
            from datetime import datetime

            car_date = datetime(2024, 1, 1)
            response = client.cars.delete(worker_id="12345", car_date=car_date)
            ```

        Note:
            - This operation is irreversible
            - The car_date must match the starting_date of the car entry
        """
        try:
            url = f"{self.url}/{worker_id}/companycar/{car_date.strftime(DATEFORMAT)}"

            # Send the DELETE request
            response = self._make_request_with_polling(
                url,
                method='DELETE',
                employer=employer
            )
            return response

        except Exception as e:
            raise ValueError(f"Failed to delete company car: {str(e)}") from e
