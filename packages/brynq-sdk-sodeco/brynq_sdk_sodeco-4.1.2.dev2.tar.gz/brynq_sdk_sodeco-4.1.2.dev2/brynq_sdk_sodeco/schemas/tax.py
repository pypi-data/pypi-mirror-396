from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime

class TaxSchema(DataFrameModel):
    # Required fields
    startdate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Startdate")
    tax_calculation: str = Field(nullable=False, isin=[
        'Normal', 'Conversion PT', 'FiscVolAmount', 'FiscVolPercent',
        'Amount', 'Percent', 'PercentNormal', 'NonResident', 'NoCity',
        'NoTax', 'Younger', 'NormalPlus', 'Trainer', 'NormalMinPerc',
        'NormalMinAmount'
    ], alias="TaxCalculation")
    value: float = Field(nullable=False, ge=0.0, le=9999999999.0, alias="Value")
