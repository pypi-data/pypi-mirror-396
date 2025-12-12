from datetime import datetime
import json
import pandas as pd
import logging
from typing import Optional, Dict, Any, Tuple
from brynq_sdk_functions import Functions

from .costcentres import CostCentres
from .dimona import Dimonas
from .replacement import Replacements
from .car import Cars
from .schemas.worker import WorkerCreate, WorkerUpdate
from .schemas import (
    DATEFORMAT,
    EmployeeGet,
    FamilyGet,
    AddressGet,
    CommunicationGet,
    ContractGet,
    TaxGet,
    ReplacementGet,
    SalaryCompositionGet
)
from .absences import Absences
from .absencenote import AbsenceNotes
from .communication import Communications
from .contract import Contracts
from .family import Families
from .tax import Taxes
from .salarycomposition import SalaryCompositions
from .base import SodecoBase
from .divergentsalary import DivergentSalaryScale
from .divergentpayment import DivergentPayments
from .leavecounters import LeaveCounters
from .address import Addresses
from .schedule import Schedules


class Workers(SodecoBase):
    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"
        self.addresses = Addresses(sodeco)
        self.communications = Communications(sodeco)
        self.contracts = Contracts(sodeco)
        self.costcentres = CostCentres(sodeco)
        self.families = Families(sodeco)
        self.taxes = Taxes(sodeco)
        self.replacements = Replacements(sodeco)
        self.absences = Absences(sodeco)
        self.absencenotes = AbsenceNotes(sodeco)
        self.cars = Cars(sodeco)
        self.dimonas = Dimonas(sodeco)
        self.divergentsalaries = DivergentSalaryScale(sodeco)
        self.divergentpayments = DivergentPayments(sodeco)
        self.leavecounters = LeaveCounters(sodeco)
        self.salarycompositions = SalaryCompositions(sodeco)
        self.schedules = Schedules(sodeco)

    def get(
        self,
        worker_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        employers: list = None
    ) -> Tuple[
        Tuple[pd.DataFrame, pd.DataFrame],  # employee (valid, invalid)
        Tuple[pd.DataFrame, pd.DataFrame],  # family (valid, invalid)
        Tuple[pd.DataFrame, pd.DataFrame],  # addresses (valid, invalid)
        Tuple[pd.DataFrame, pd.DataFrame],  # communication (valid, invalid)
        Tuple[pd.DataFrame, pd.DataFrame],  # contract (valid, invalid)
        Tuple[pd.DataFrame, pd.DataFrame],  # tax (valid, invalid)
        Tuple[pd.DataFrame, pd.DataFrame],  # replacement (valid, invalid)
        Tuple[pd.DataFrame, pd.DataFrame],  # salary_compositions (valid, invalid)
    ]:
        """
        Retrieve worker information from Sodeco API with comprehensive validation.

        This method fetches worker data and normalizes it into 8 separate DataFrames,
        each validated against its respective Pandera schema. The method handles
        pagination automatically and validates all returned data.

        Args:
            worker_id (Optional[str]): Specific worker ID to retrieve. If None, retrieves all workers.
            start_date (Optional[datetime]): Filter workers by start date. Must be provided with end_date.
            end_date (Optional[datetime]): Filter workers by end date. Required if start_date is provided.

        Returns:
            Tuple containing 8 tuples, each with (valid_data, invalid_data) DataFrames:
                - employee: Main worker/employee information
                - family: Family status and dependent information
                - addresses: Worker address history
                - communication: Contact information (phone, email, etc.)
                - contract: Employment contract details
                - tax: Tax calculation configuration
                - replacement: Replacement worker assignments
                - salary_compositions: Salary component breakdown

        Raises:
            ValueError: If start_date is provided without end_date
            requests.exceptions.HTTPError: If API request fails
            Exception: If data retrieval or validation fails

        Example:
            ```python
            # Get all workers
            (emp_valid, emp_invalid), (fam_valid, fam_invalid), ... = client.workers.get()

            # Get specific worker
            (emp_valid, emp_invalid), ... = client.workers.get(worker_id="12345")

            # Get workers for date range
            from datetime import datetime
            start = datetime(2024, 1, 1)
            end = datetime(2024, 12, 31)
            (emp_valid, emp_invalid), ... = client.workers.get(start_date=start, end_date=end)

            # Check validation results
            print(f"Valid employees: {len(emp_valid)}")
            print(f"Invalid employees: {len(emp_invalid)}")
            ```

        Note:
            - All DataFrame column names are converted to snake_case
            - Each DataFrame includes 'worker_number' and 'employer' columns for reference
            - Empty DataFrames are returned if no data is found
            - Invalid data is captured separately and not included in valid DataFrames
        """
        # Build API URL with optional filters
        url = self.url
        if worker_id is not None:
            url += f"/{worker_id}"
        if start_date is not None:
            if end_date is not None:
                url += f"/{start_date.strftime(DATEFORMAT)}/{end_date.strftime(DATEFORMAT)}"
            else:
                raise ValueError("if start_date is specified, end_date must be specified as well")

        all_data = self._make_request_with_polling_for_employers(url, method='GET', employers=employers)

        # If no data found, return empty DataFrames for all
        if not all_data:
            empty_df = pd.DataFrame()
            return (
                (empty_df, empty_df),  # employee
                (empty_df, empty_df),  # family
                (empty_df, empty_df),  # addresses
                (empty_df, empty_df),  # communication
                (empty_df, empty_df),  # contract
                (empty_df, empty_df),  # tax
                (empty_df, empty_df),  # replacement
                (empty_df, empty_df),  # salary_compositions
            )

        # 1. EMPLOYEE DATA - Main worker information
        employee = pd.DataFrame(all_data)
        employee = employee.drop(columns=['FamilyStatus', 'address', 'Communication', 'contract', 'Tax', 'Replacement'], errors='ignore')
        employee_valid, employee_invalid = Functions.validate_data(employee, EmployeeGet)

        # 2. FAMILY DATA - Family status and dependents
        try:
            family = pd.json_normalize(
                all_data,
                record_path='FamilyStatus',
                meta=['WorkerNumber', 'employer'],
                errors='ignore'
            )
            family_valid, family_invalid = Functions.validate_data(family, FamilyGet)

        except (KeyError, ValueError):
            family_valid, family_invalid = pd.DataFrame(), pd.DataFrame()

        # 3. ADDRESS DATA - Worker addresses
        try:
            addresses = pd.json_normalize(
                all_data,
                record_path='address',
                meta=['WorkerNumber', 'employer'],
                errors='ignore'
            )
            addresses_valid, addresses_invalid = Functions.validate_data(addresses, AddressGet)
        except (KeyError, ValueError):
            addresses_valid, addresses_invalid = pd.DataFrame(), pd.DataFrame()

        # 4. COMMUNICATION DATA - Contact information
        try:
            communication = pd.json_normalize(
                all_data,
                record_path='Communication',
                meta=['WorkerNumber', 'employer'],
                errors='ignore'
            )
            communication_valid, communication_invalid = Functions.validate_data(communication, CommunicationGet)
        except (KeyError, ValueError):
            communication_valid, communication_invalid = pd.DataFrame(), pd.DataFrame()

        # 5. CONTRACT DATA - Employment contracts
        try:
            contract = pd.json_normalize(
                all_data,
                record_path='contract',
                meta=['WorkerNumber', 'employer'],
                sep='__',
                errors='ignore'
            )
            # Drop nested SalaryCompositions as it's handled separately
            contract = contract.drop(columns=['SalaryCompositions'], errors='ignore')
            contract_valid, contract_invalid = Functions.validate_data(contract, ContractGet)
        except (KeyError, ValueError):
            contract_valid, contract_invalid = pd.DataFrame(), pd.DataFrame()

        # 6. TAX DATA - Tax calculation configuration
        try:
            tax = pd.json_normalize(
                all_data,
                record_path='Tax',
                meta=['WorkerNumber', 'employer'],
                errors='ignore'
            )
            tax_valid, tax_invalid = Functions.validate_data(tax, TaxGet)
        except (KeyError, ValueError):
            tax_valid, tax_invalid = pd.DataFrame(), pd.DataFrame()

        # 7. REPLACEMENT DATA - Replacement worker assignments
        try:
            replacement = pd.json_normalize(
                all_data,
                record_path='Replacement',
                meta=['WorkerNumber', 'employer'],
                errors='ignore'
            )
            replacement_valid, replacement_invalid = Functions.validate_data(replacement, ReplacementGet)
        except (KeyError, ValueError):
            replacement_valid, replacement_invalid = pd.DataFrame(), pd.DataFrame()

        # 8. SALARY COMPOSITION DATA - Salary component breakdown
        try:
            salary_compositions = pd.json_normalize(
                all_data,
                record_path=['contract', 'SalaryCompositions'],
                meta=['WorkerNumber', 'employer'],
                errors='ignore'
            )
            salary_compositions_valid, salary_compositions_invalid = Functions.validate_data(
                salary_compositions,
                SalaryCompositionGet
            )
        except (KeyError, ValueError):
            salary_compositions_valid, salary_compositions_invalid = pd.DataFrame(), pd.DataFrame()

        return (
            (employee_valid, employee_invalid),
            (family_valid, family_invalid),
            (addresses_valid, addresses_invalid),
            (communication_valid, communication_invalid),
            (contract_valid, contract_invalid),
            (tax_valid, tax_invalid),
            (replacement_valid, replacement_invalid),
            (salary_compositions_valid, salary_compositions_invalid),
        )

    def create(self, payload: Dict[str, Any], employer: str = None) -> dict:
        """
        Create a new worker with flat parameters that are automatically structured into nested objects.

        This method accepts flat parameters with prefixes (address_, family_, contract_) and automatically
        groups them into the required nested structure for the API.

        Args:
            payload (Dict[str, Any]): Flat dictionary with prefixed keys for nested objects, including:
                - worker_number (int): Required. Worker identifier
                - name (str): Required. Last name
                - first_name (str): Required. First name
                - address_* : Address fields (e.g. address_street, address_city, address_start_date)
                - family_* : Family status fields (e.g. family_civil_status, family_start_date)
                - contract_* : Contract fields (e.g. contract_employment_status, contract_start_date)
                - communication_* : Optional communication fields
                - tax_* : Optional tax fields
                - replacement_* : Optional replacement fields
                - Other worker fields: inss, sex, birth_date, bank_account, etc.

        Returns:
            dict: The created worker data from API

        Raises:
            ValueError: If the parameters are invalid or required nested objects are missing

        Example:
            ```python
            worker_data = {
                "worker_number": 12345,
                "name": "Doe",
                "first_name": "John",
                "inss": 12345678901,
                "sex": "M",
                # Address fields
                "address_street": "Main Street",
                "address_house_number": "123",
                "address_zip_code": "1000",
                "address_city": "Brussels",
                "address_start_date": "20250101",
                "address_country": "00150",
                # Family fields
                "family_start_date": "20250101",
                "family_civil_status": "Single",
                # Contract fields
                "contract_start_date": "20250101",
                "contract_employment_status": "Employee"
            }
            worker = client.workers.create(worker_data)
            ```
        """
        try:
            # Validate the payload using WorkerCreate
            validated_data = WorkerCreate(**payload)
            data = validated_data.model_dump(mode="json", by_alias=True, exclude_none=True)

            # Send the POST request to create the worker
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            data = json.dumps(data)

            resp_data = self._make_request_with_polling(
                self.url,
                method='POST',
                headers=headers,
                data=data,
                employer=employer
            )
            return resp_data

        except Exception as e:
            error_msg = "Invalid worker payload"
            raise ValueError(error_msg) from e

    def update(self, worker_id: str, payload: Dict[str, Any], employer: str = None) -> dict:
        """
        Update a worker's main information (personal fields only).

        This endpoint updates only the main worker fields. Nested objects like Address, Contract,
        FamilyStatus cannot be updated through this endpoint; they have separate PUT endpoints.

        Args:
            worker_id (str): The ID of the worker to update
            payload (Dict[str, Any]): Flat dictionary with snake_case keys containing only main worker fields:
                - worker_number (int): Worker identifier
                - name (str): Last name
                - first_name (str): First name
                - sex (str): Gender ('M' or 'F')
                - birth_date (str): Birth date in YYYYMMDD format
                - language (str): Language code ('N', 'F', 'D', 'E')
                - pay_way (str): Payment method
                - bank_account (str): Bank account number
                - bic_code (str): BIC code
                - education (str): Education level
                - profession (str): Profession
                - travel_expenses (str): Travel expense type
                - Other main worker fields (no nested objects like address_, family_, contract_)

        Returns:
            dict: The API response containing updated worker data

        Raises:
            ValueError: If the update operation fails
            requests.exceptions.HTTPError: If the API request fails

        Example:
            ```python
            worker_update = {
                "worker_number": 12345,
                "name": "Doe",
                "first_name": "Jane",
                "bank_account": "BE68 5390 0754 7034",
                "language": "F",
                "profession": "Senior Analyst"
            }
            response = client.workers.update(worker_id="12345", payload=worker_update)
            ```

        Note:
            To update Address, use: sodeco.workers.addresses.update()
            To update Contract, use: sodeco.workers.contracts.update()
            To update Family Status, use: sodeco.workers.families.update()
        """
        try:
            url = f"{self.url}/{worker_id}"

            # Validate and convert using WorkerUpdate schema
            # populate_by_name=True allows snake_case input
            # by_alias=True converts to CamelCase for API
            validated_data = WorkerUpdate(**payload)
            update_payload = validated_data.model_dump(mode="json", by_alias=True, exclude_none=True)

            # Send the PUT request to update the worker
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = json.dumps(update_payload)

            resp_data = self._make_request_with_polling(
                url,
                method='PUT',
                headers=headers,
                data=data,
                employer=employer
            )
            return resp_data
        except Exception as e:
            error_msg = f"Failed to update worker {worker_id}: {str(e)}"
            raise ValueError(error_msg) from e

    def get_new_worker_number(self, employer: str = None):
        url = f"{self.sodeco.base_url}newworkernumber"
        resp = self._make_request_with_polling(url, employer=employer)
        return resp
