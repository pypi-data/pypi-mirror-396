from .base import SodecoBase
import pandas as pd


class Departments(SodecoBase):

    def __init__(self, sodeco):
        super().__init__(sodeco)

    def get(self) -> pd.DataFrame:
        url = f"{self.sodeco.base_url}department"
        data = self._make_request_with_polling(url)

        return pd.DataFrame(data)
