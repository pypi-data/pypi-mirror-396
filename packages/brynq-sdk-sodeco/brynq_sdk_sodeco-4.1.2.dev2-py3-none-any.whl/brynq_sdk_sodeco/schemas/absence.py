from pandera import Field
from typing import Optional, List
from datetime import datetime
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class AbsenceSchema(BrynQPanderaDataFrameModel):
    """Schema for individual absence entries"""
    # Required fields
    day: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Day")
    code: int = Field(nullable=False, ge=1, le=6999, alias="Code")

    # Optional fields
    shift: Optional[pd.Int64Dtype] = Field(nullable=True, ge=1, le=99, alias="Shift")
    hours: Optional[float] = Field(nullable=True, ge=0.0, le=23.99, alias="Hours")

    class Config:
        strict = True
        coerce = True

class AbsencesSchema(BrynQPanderaDataFrameModel):
    """Schema for worker absences list"""
    # Required fields
    worker_number: int = Field(nullable=False, ge=1, le=9999999, alias="WorkerNumber")
    absences: List[dict] = Field(nullable=False, alias="Absences")  # Will be validated separately using AbsenceSchema

    class Config:
        strict = True
        coerce = True
