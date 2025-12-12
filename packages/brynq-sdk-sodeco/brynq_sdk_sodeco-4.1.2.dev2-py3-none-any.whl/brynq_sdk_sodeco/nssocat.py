import pandas as pd
from .base import SodecoBase


class NssoCat(SodecoBase):
    """Class to handle NSSO (National Social Security Office) employer categories.
    
    This class provides access to NSSO employer category information. These categories
    are used by the Belgian social security system to classify employers based on
    various criteria, which can affect their social security contributions and
    obligations.
    """
    
    def get(self) -> pd.DataFrame:
        """
        Get NSSO employer category data.
        
        Returns:
            pd.DataFrame: The NSSO employer category data containing information about
                         different employer classifications and their associated
                         social security requirements.
        """
        url = f"{self.sodeco.base_url}/nssocat"
        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)
