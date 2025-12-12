from pandera import Field
from typing import Optional
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class AbsenceNoteSchema(BrynQPanderaDataFrameModel):
    """Schema for absence note entries"""
    # Required fields
    note_date: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Notedate")
    startdate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Startdate")
    enddate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Enddate")

    # Optional fields
    reason: Optional[str] = Field(nullable=True, isin=['Sickness', 'Accident', 'Extension'], alias="Reason")
    may_leave_house: Optional[str] = Field(nullable=True, isin=['N', 'Y'], alias="MayLeaveHouse")
    resumedate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Resumedate")
    resume: Optional[str] = Field(nullable=True, isin=['None', 'Full', 'Partial'], alias="Resume")
    salary_code: Optional[int] = Field(nullable=True, ge=800, le=899, alias="SalaryCode")
