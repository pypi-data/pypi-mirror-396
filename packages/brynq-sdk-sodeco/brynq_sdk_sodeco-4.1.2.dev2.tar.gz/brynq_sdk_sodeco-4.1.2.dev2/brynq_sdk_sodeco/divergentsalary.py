from datetime import datetime
from typing import Optional
import pandas as pd
from .base import SodecoBase
from .schemas import DATEFORMAT


class DivergentSalaryScale(SodecoBase):
    """Class to handle divergent salary scale information.
    
    This class provides access to divergent salary scale data for workers. A divergent
    salary scale represents variations or exceptions from standard salary scales,
    which may be applied based on specific circumstances or agreements.
    """

    def __init__(self, sodeco):
        super().__init__(sodeco)

    def get(self, worker_id: str) -> pd.DataFrame:
        """
        Get divergent salary scale data for a worker.
        
        Args:
            worker_id (str): The ID of the worker
            
        Returns:
            pd.DataFrame: The divergent salary scale data containing information about
                         any special or non-standard salary arrangements for the worker.
        """
        url = f"{self.sodeco.base_url}/worker/{worker_id}/divergentsalaryscale"
        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)
