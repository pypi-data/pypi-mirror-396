from typing import Optional, List
from pydantic import BaseModel, Field
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# ============================================================================
# PYDANTIC SCHEMAS (Request/Response Models)
# ============================================================================

class ScheduleWeekCreate(BaseModel):
    """Schema for creating schedule week entries."""
    week_number: int = Field(..., alias="WeekNumber", description="Week number", example=1, ge=1, le=15)
    day_1: Optional[float] = Field(None, alias="Day1", description="Hours for day 1", example=8.0, ge=0.0, le=24.0)
    day_2: Optional[float] = Field(None, alias="Day2", description="Hours for day 2", example=8.0, ge=0.0, le=24.0)
    day_3: Optional[float] = Field(None, alias="Day3", description="Hours for day 3", example=8.0, ge=0.0, le=24.0)
    day_4: Optional[float] = Field(None, alias="Day4", description="Hours for day 4", example=8.0, ge=0.0, le=24.0)
    day_5: Optional[float] = Field(None, alias="Day5", description="Hours for day 5", example=8.0, ge=0.0, le=24.0)
    day_6: Optional[float] = Field(None, alias="Day6", description="Hours for day 6", example=0.0, ge=0.0, le=24.0)
    day_7: Optional[float] = Field(None, alias="Day7", description="Hours for day 7", example=0.0, ge=0.0, le=24.0)

    class Config:
        populate_by_name = True


class ScheduleCreate(BaseModel):
    """Schema for creating a new schedule entry."""
    schedule_id: str = Field(..., alias="ScheduleID", description="Schedule identifier", example="SCH1", min_length=0, max_length=4)
    description: str = Field(..., alias="Description", description="Schedule description", example="Regular Schedule", min_length=0, max_length=50)
    start_date: str = Field(..., alias="StartDate", description="Schedule start date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    week: List[ScheduleWeekCreate] = Field(..., alias="Week", description="List of week schedules", min_items=1)

    class Config:
        populate_by_name = True


# ============================================================================
# PANDERA SCHEMAS (DataFrame Validation)
# ============================================================================

class ScheduleWeekGet(BrynQPanderaDataFrameModel):
    """Schema for validating schedule week data retrieved from Sodeco API."""
    week_number: int = pa.Field(coerce=True, nullable=False, description="Week number", alias="WeekNumber")
    day_1: Optional[float] = pa.Field(coerce=True, nullable=True, description="Hours for day 1", alias="Day1")
    day_2: Optional[float] = pa.Field(coerce=True, nullable=True, description="Hours for day 2", alias="Day2")
    day_3: Optional[float] = pa.Field(coerce=True, nullable=True, description="Hours for day 3", alias="Day3")
    day_4: Optional[float] = pa.Field(coerce=True, nullable=True, description="Hours for day 4", alias="Day4")
    day_5: Optional[float] = pa.Field(coerce=True, nullable=True, description="Hours for day 5", alias="Day5")
    day_6: Optional[float] = pa.Field(coerce=True, nullable=True, description="Hours for day 6", alias="Day6")
    day_7: Optional[float] = pa.Field(coerce=True, nullable=True, description="Hours for day 7", alias="Day7")

    class Config:
        strict = True
        coerce = True

    class _Annotation:
        primary_key = "week_number"


class ScheduleGet(BrynQPanderaDataFrameModel):
    """Schema for validating schedule data retrieved from Sodeco API."""
    schedule_id: str = pa.Field(coerce=True, nullable=False, description="Schedule identifier", alias="ScheduleID")
    description: str = pa.Field(coerce=True, nullable=False, description="Schedule description", alias="Description")
    start_date: str = pa.Field(coerce=True, nullable=False, description="Schedule start date in YYYYMMDD format", alias="StartDate")
    week: str = pa.Field(coerce=True, nullable=False, description="Week data as JSON string", alias="Week")
    employer: Optional[str] = pa.Field(coerce=True, nullable=True, description="Employer name", alias="employer")

    class Config:
        strict = True
        coerce = True

    class _Annotation:
        primary_key = "schedule_id"
