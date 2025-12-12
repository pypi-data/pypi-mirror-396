import pandas as pd
from .base import SodecoBase


class Parcom(SodecoBase):
    """Class to handle Paritair Committee (Joint Committee) data.
    
    This class provides access to Paritair Committee information, which represents
    Belgian collective agreement committees. These committees are established for various
    sectors of economic activity and set working conditions and wage standards for
    workers within their sector.
    """
    
    def get(self) -> pd.DataFrame:
        """
        Get Paritair Committee data.
        
        Returns:
            pd.DataFrame: The Paritair Committee data containing information about
                         different joint committees and their associated regulations
                         and standards.
        """
        url = f"{self.sodeco.base_url}/parcom"
        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)
