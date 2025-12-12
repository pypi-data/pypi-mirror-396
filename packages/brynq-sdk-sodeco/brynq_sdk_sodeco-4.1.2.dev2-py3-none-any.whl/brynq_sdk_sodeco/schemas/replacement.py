from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime

class ReplacementSchema(DataFrameModel):
    """Schema defining validation rules for worker replacements.

    This model represents replacement information including both required
    and optional fields. All date fields follow the YYYYMMDD format.
    """
    # Required fields
    worker_number: int = Field(
        nullable=False,
        ge=1,
        le=9999999,
        description="Worker identification number (required, range: 1-9999999)",
        alias="WorkerNumber"
    )
    startdate: str = Field(
        nullable=False,
        str_length={'min_value': 8, 'max_value': 8},
        regex=r'^[0-9]*$',
        description="Start date of the replacement (required, format: YYYYMMDD)",
        alias="Startdate"
    )

    # Optional fields
    enddate: Optional[str] = Field(
        nullable=True,
        str_length={'min_value': 8, 'max_value': 8},
        regex=r'^[0-9]*$',
        description="End date of the replacement (optional, format: YYYYMMDD)",
        alias="Enddate"
    )
    percentage: Optional[float] = Field(
        nullable=True,
        ge=0.0,
        le=100.0,
        description="Replacement percentage (optional, range: 0-100)",
        alias="Percentage"
    )
