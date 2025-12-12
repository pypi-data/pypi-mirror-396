import pandas as pd
from .base import SodecoBase


class ProfCat(SodecoBase):
    """Class to handle professional categories.
    
    This class provides access to professional category information, which classifies
    workers based on their professional roles and qualifications. These categories
    are used to determine appropriate wage scales, benefits, and other employment
    conditions.
    """
    
    def get(self) -> pd.DataFrame:
        """
        Get professional category data.
        
        Returns:
            pd.DataFrame: The professional category data containing information about
                         different job classifications and their associated
                         requirements and standards.
        """
        url = f"{self.sodeco.base_url}/profcat"
        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)
