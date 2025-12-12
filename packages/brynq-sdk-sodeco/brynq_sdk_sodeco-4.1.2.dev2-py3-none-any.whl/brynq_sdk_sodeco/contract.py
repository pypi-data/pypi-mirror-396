from typing import Dict, Any, Tuple, Optional, get_args, get_origin
import pandas as pd
import requests
from datetime import datetime
from .base import SodecoBase
from .schemas.contract import ContractCreate, ContractUpdate, ContractGet
from .schemas.salarycomposition import SalaryCompositionGet
from .schemas import DATEFORMAT
from brynq_sdk_functions import Functions
from pydantic import BaseModel
import re
import json


class Contracts(SodecoBase):
    """Handles all contract-related operations in Sodeco API."""

    def __init__(self, sodeco):
        """Initialize the Contracts class."""
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def get(self, worker_id: str, ref_date: Optional[datetime] = None, employer: str = None) -> Tuple[Tuple[pd.DataFrame, pd.DataFrame], Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Get contracts for a worker and split SalaryCompositions into a separate DataFrame.

        Args:
            worker_id (str): Worker ID
            ref_date (Optional[datetime]): Optional reference date

        Returns:
            Tuple[Tuple[pd.DataFrame, pd.DataFrame], Tuple[pd.DataFrame, pd.DataFrame]]:
                ((contracts_valid, contracts_invalid), (salary_compositions_valid, salary_compositions_invalid))
        """
        try:
            url = f"{self.url}/{worker_id}/contract"
            if ref_date is not None:
                url += f"/{ref_date.strftime(DATEFORMAT)}"

            data = self._make_request_with_polling(url, employer=employer)

            if not data:
                return (pd.DataFrame(), pd.DataFrame()), (pd.DataFrame(), pd.DataFrame())

            # Normalize nested data structure and flatten it
            df = pd.json_normalize(data, sep='__')

            if df.empty:
                return (pd.DataFrame(), pd.DataFrame()), (pd.DataFrame(), pd.DataFrame())

            # Validate data using schema
            # Extract SalaryCompositions from nested structure into a separate DataFrame
            # and add identifiers (WorkerNumber, ContractStartdate, ContractIdentifier)
            salary_rows: list[dict] = []
            for contract_item in data:
                compositions = contract_item.get('SalaryCompositions') or []
                if not compositions:
                    continue
                contract_startdate = contract_item.get('Startdate')
                worker_number = contract_item.get('WorkerNumber', worker_id)
                for item in compositions:
                    row = dict(item)
                    row['contract_startdate'] = contract_startdate
                    row['worker_number'] = worker_number
                    row['contract_identifier'] = f"{worker_number}_{contract_startdate}"
                    salary_rows.append(row)

            salary_df = pd.DataFrame(salary_rows) if len(salary_rows) > 0 else pd.DataFrame()

            # Drop nested SalaryCompositions from main contracts df to keep only contract-level fields
            df = df.drop(columns=['SalaryCompositions'], errors='ignore')

            contracts_valid, contracts_invalid = Functions.validate_data(df, ContractGet)
            salary_valid, salary_invalid = Functions.validate_data(salary_df, SalaryCompositionGet)
            return (contracts_valid, contracts_invalid), (salary_valid, salary_invalid)

        except Exception as e:
            raise Exception(f"Failed to retrieve contract data: {str(e)}") from e

    def create(self, worker_id: str, data: Dict[str, Any], employer: str = None) -> requests.Response:
        """
        Create a contract for a worker.

        Args:
            worker_id (str): Worker ID
            data (Dict[str, Any]): Contract data to create

        Returns:
            requests.Response: The API response
        """
        try:
            # Validate with Pydantic schema
            req_data = ContractCreate(**data)
            req_body = req_data.model_dump(by_alias=True, mode='json', exclude_none=True)

            url = f"{self.url}/{worker_id}/contract"

            # Send the POST request to create the contract (same style as Workers.create)
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

        except Exception as e:
            raise Exception(f"Failed to create contract: {str(e)}") from e

    def update(self, worker_id: str, contract_date: datetime, data: Dict[str, Any], employer: str = None) -> requests.Response:
        """
        Update a contract for a worker.

        Args:
            worker_id (str): Worker ID
            contract_date (datetime): Contract start date
            data (Dict[str, Any]): Contract data to update

        Returns:
            requests.Response: The API response
        """
        try:
            # Validate with Pydantic schema
            req_data = ContractUpdate(**data)
            req_body = req_data.model_dump(by_alias=True, mode='json', exclude_none=True)

            url = f"{self.url}/{worker_id}/contract/{contract_date.strftime(DATEFORMAT)}"

            # Send the PUT request to update the contract (same style as Workers.update)
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = json.dumps(req_body)
            resp_data = self._make_request_with_polling(
                url=url,
                method="PUT",
                headers=headers,
                data=data,
                employer=employer
            )
            return resp_data

        except Exception as e:
            raise Exception(f"Failed to update contract: {str(e)}") from e

    def delete(self, worker_id: str, contract_date: datetime, employer: str = None) -> requests.Response:
        """
        Delete a contract for a worker.

        Args:
            worker_id (str): Worker ID
            contract_date (datetime): Contract start date

        Returns:
            requests.Response: The API response
        """
        try:
            url = f"{self.url}/{worker_id}/contract/{contract_date.strftime(DATEFORMAT)}"

            resp_data = self._make_request_with_polling(
                url=url,
                method="DELETE",
                employer=employer
            )
            return resp_data

        except Exception as e:
            raise Exception(f"Failed to delete contract: {str(e)}") from e
