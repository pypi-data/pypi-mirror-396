from datetime import datetime
from typing import Optional
import pandas as pd
from .base import SodecoBase
from .schemas import DATEFORMAT


class Modifications(SodecoBase):

    def __init__(self, sodeco):
        super().__init__(sodeco)

    def get(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Get modifications between start_date and end_date.
        
        Args:
            start_date: Start date for modifications
            end_date: End date for modifications
            
        Returns:
            pd.DataFrame: DataFrame containing the modifications
        """
        url = f"{self.sodeco.base_url}modifications/{start_date.strftime(DATEFORMAT)}/{end_date.strftime(DATEFORMAT)}"

        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)
