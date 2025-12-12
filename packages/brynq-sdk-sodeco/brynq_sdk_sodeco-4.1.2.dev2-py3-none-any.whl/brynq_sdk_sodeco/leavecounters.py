from typing import Optional
import pandas as pd
from .base import SodecoBase


class LeaveCounters(SodecoBase):
    """Class to handle leave counters data.
    
    This class provides access to leave counter information, which tracks various types
    of leave balances. The data can be accessed either for all counters in a given year,
    for a specific worker's counters in a year, or for a specific counter in a year.
    """
    
    def get(self, year: int, worker_id: Optional[str] = None, counter_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get leave counters data.
        
        Args:
            year (int): The year to retrieve leave counters for (mandatory)
            worker_id (str, optional): The ID of the worker. If specified, returns leave
                                     counters for that specific worker
            counter_id (str, optional): The ID of the counter. Only used when worker_id
                                      is not specified. Returns data for a specific counter.
            
        Returns:
            pd.DataFrame: The leave counters data containing information about leave
                         balances for the specified year.
                         
        Raises:
            ValueError: If counter_id is specified but worker_id is also provided
        """
        if worker_id:
            if counter_id:
                raise ValueError("counter_id cannot be specified when worker_id is provided")
            url = f"{self.sodeco.base_url}/worker/{worker_id}/leavecounters/{year}"
        else:
            base_url = f"{self.sodeco.base_url}/leavecounter/{year}"
            url = f"{base_url}/{counter_id}" if counter_id else base_url
            
        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)
