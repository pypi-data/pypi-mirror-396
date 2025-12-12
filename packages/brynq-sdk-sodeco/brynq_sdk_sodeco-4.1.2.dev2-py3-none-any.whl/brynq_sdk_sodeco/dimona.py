from typing import Optional
import pandas as pd
from datetime import datetime
from .base import SodecoBase
from .schemas.dimona import PostDimonaSchema, GetDimonaSchema, UsingDataSchema
from brynq_sdk_functions import Functions


class Dimonas(SodecoBase):
    """Class for managing Dimona declarations in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def get(self, worker_id: str) -> pd.DataFrame:
        """
        Get Dimona declarations for a worker.
        
        Args:
            worker_id: The worker ID to get Dimona declarations for
            
        Returns:
            pd.DataFrame: DataFrame containing the Dimona declarations
        """
        url = f"{self.url}/{worker_id}/dimona"
        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)

    def create(self, worker_id: str, payload: dict, debug: bool = False) -> dict:
        """
        Create a Dimona declaration for a worker.
        The payload must adhere to the structure defined by the PostDimonaSchema.
        If UsingData is provided, it must adhere to UsingDataSchema.
        
        Args:
            worker_id: The ID of the worker to create a Dimona declaration for
            payload: The Dimona data to create
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The created Dimona declaration
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/dimona"
        
        # First validate the main payload structure
        main_data = payload.copy()
        using_data = main_data.pop('UsingData', None)
        
        df = pd.DataFrame([main_data])
        valid_data, invalid_data = Functions.validate_data(df, PostDimonaSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid Dimona payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Then validate UsingData if present
        if using_data is not None:
            using_df = pd.DataFrame([using_data])
            valid_using, invalid_using = Functions.validate_data(using_df, UsingDataSchema, debug=debug)

            if len(invalid_using) > 0:
                error_msg = "Invalid UsingData in Dimona payload"
                if debug:
                    error_msg += f": {invalid_using.to_dict(orient='records')}"
                raise ValueError(error_msg)

        # Send the POST request to create the dimona
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='POST',
            headers=headers,
            data=data
        )
        return data
