from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd
from .base import SodecoBase
from .schemas import DATEFORMAT
from .schemas.costcentre import CostCentreSchema
from brynq_sdk_functions import Functions


class CostCentres(SodecoBase):

    def __init__(self, sodeco):
        super().__init__(sodeco)

    def get(self, worker_id: Optional[str] = None, start_date: Optional[datetime] = None) -> pd.DataFrame:
        if worker_id is not None:
            url = f"{self.sodeco.base_url}worker/{worker_id}/costcentre"
            if start_date is not None:
                url += f"/{start_date.strftime(DATEFORMAT)}"
        else:
            if start_date is not None:
                raise ValueError("start_date can only be specified when worker_id is provided")
            url = f"{self.sodeco.base_url}costcentre"

        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)
        
    def create(self, worker_id: str, payload: Dict[str, Any], debug: bool = False) -> dict:
        """
        Create a cost centre entry for a worker.
        The payload must adhere to the structure defined by the CostCentreSchema.
        
        Args:
            worker_id: The ID of the worker to create a cost centre entry for
            payload: The cost centre data to create. Must include Startdate and CostCentres
                    (list of cost centre items with CostCentre and Percentage)
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The created cost centre data
            
        Raises:
            ValueError: If the payload is invalid or cost centres don't match schema
        """
        url = f"{self.sodeco.base_url}worker/{worker_id}/costcentre"
        
        # First validate the main cost centre data
        main_data = {
            'Startdate': payload.get('Startdate'),
            'Enddate': payload.get('Enddate')
        }
        df = pd.DataFrame([main_data])
        valid_data, invalid_data = Functions.validate_data(df, CostCentreSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid cost centre payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Then validate the cost centre items
        cost_centres = payload.get('CostCentres', [])
        if not CostCentreSchema.validate_cost_centres(cost_centres):
            error_msg = "Invalid cost centre items. Ensure all items are valid and percentages sum to 100%"
            if debug:
                error_msg += f": {cost_centres}"
            raise ValueError(error_msg)

        # Combine the validated data
        final_payload = valid_data.iloc[0].to_dict()
        final_payload['CostCentres'] = cost_centres

        # Send the POST request to create the cost centre
        headers, data = self._prepare_raw_request(final_payload)
        data = self._make_request_with_polling(
            url,
            method='POST',
            headers=headers,
            data=data
        )
        return data

    def update(self, worker_id: str, cost_centre_date: datetime, payload: dict, debug: bool = False) -> dict:
        """
        Update a cost centre entry for a worker.
        The payload must adhere to the structure defined by the CostCentreSchema.
        
        Args:
            worker_id: The ID of the worker who owns the cost centre
            cost_centre_date: The start date of the cost centre to update
            payload: The cost centre data to update. Must include Startdate and CostCentres
                    (list of cost centre items with CostCentre and Percentage)
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The updated cost centre data
            
        Raises:
            ValueError: If the payload is invalid or cost centres don't match schema
        """
        url = f"{self.sodeco.base_url}worker/{worker_id}/costcentre/{cost_centre_date.strftime(DATEFORMAT)}"
        
        # First validate the main cost centre data
        main_data = {
            'Startdate': payload.get('Startdate'),
            'Enddate': payload.get('Enddate')
        }
        df = pd.DataFrame([main_data])
        valid_data, invalid_data = Functions.validate_data(df, CostCentreSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid cost centre payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Then validate the cost centre items
        cost_centres = payload.get('CostCentres', [])
        if not CostCentreSchema.validate_cost_centres(cost_centres):
            error_msg = "Invalid cost centre items. Ensure all items are valid and percentages sum to 100%"
            if debug:
                error_msg += f": {cost_centres}"
            raise ValueError(error_msg)

        # Combine the validated data
        final_payload = valid_data.iloc[0].to_dict()
        final_payload['CostCentres'] = cost_centres

        # Send the PUT request to update the cost centre
        headers, data = self._prepare_raw_request(final_payload)
        data = self._make_request_with_polling(
            url,
            method='PUT',
            headers=headers,
            data=data
        )
        return data

    def delete(self, worker_id: str, cost_centre_date: datetime) -> dict:
        """
        Delete a cost centre entry for a worker.
        
        Args:
            worker_id: The ID of the worker who owns the cost centre
            cost_centre_date: The start date of the cost centre to delete
            
        Returns:
            dict: The response from the server
        """
        url = f"{self.sodeco.base_url}worker/{worker_id}/costcentre/{cost_centre_date.strftime(DATEFORMAT)}"
        
        # Send the DELETE request
        data = self._make_request_with_polling(
            url,
            method='DELETE'
        )
        return data
