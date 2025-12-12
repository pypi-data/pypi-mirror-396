from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from pydantic import BaseModel, Field


class SalaryCompositionGet(BrynQPanderaDataFrameModel):
    """Schema for validating SalaryCompositions extracted from Contract data."""

    # Required
    start_date: str = pa.Field(coerce=True, nullable=False, description="Start date in YYYYMMDD format", alias="Startdate")
    code: int = pa.Field(coerce=True, nullable=False, description="Salary composition code", alias="Code", ge=1, le=8999)
    employer: str = pa.Field(coerce=True, nullable=False, str_length={'min_value': 0, 'max_value': 40}, description="Employer name", alias="employer")

    # Optional fields
    end_date: Optional[str] = pa.Field(coerce=True, nullable=True, description="End date in YYYYMMDD format", alias="Enddate")
    days: Optional[int] = pa.Field(coerce=True, nullable=True, description="Days", alias="Days", ge=0, le=9999)
    hours: Optional[float] = pa.Field(coerce=True, nullable=True, description="Hours", alias="Hours", ge=0.0, le=9999.0)
    unity: Optional[float] = pa.Field(coerce=True, nullable=True, description="Unity", alias="Unity")
    percentage: Optional[float] = pa.Field(coerce=True, nullable=True, description="Percentage", alias="Percentage")
    amount: Optional[float] = pa.Field(coerce=True, nullable=True, description="Amount", alias="Amount")
    supplement: Optional[float] = pa.Field(coerce=True, nullable=True, description="Supplement", alias="Supplement")
    type_of_indexing: Optional[str] = pa.Field(coerce=True, nullable=True, description="Type of indexing", alias="TypeOfIndexing")
    contract_startdate: Optional[str] = pa.Field(coerce=True, nullable=True, description="Contract start date for identification", alias="contract_startdate")
    worker_number: Optional[str] = pa.Field(coerce=True, nullable=True, description="Worker number for identification", alias="worker_number")
    contract_identifier: Optional[str] = pa.Field(coerce=True, nullable=True, description="Derived identifier workerNumber_startdate", alias="contract_identifier")
    worker_number: Optional[int] = pa.Field(coerce=True, nullable=True, description="Worker number", alias="WorkerNumber")


    class _Annotation:
        primary_key = None
        # Foreign keys/identifiers added by processing layer

class SalaryCompositionCreate(BaseModel):
    """Schema for creating a salary composition entry."""

    # Required fields
    start_date: str = Field(..., alias="Startdate", description="Start date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    code: int = Field(..., alias="Code", description="Salary composition code", example=1001, ge=1, le=8999)

    # Optional fields
    end_date: Optional[str] = Field(None, alias="Enddate", description="End date in YYYYMMDD format", example="20251231", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    days: Optional[int] = Field(None, alias="Days", description="Days", example=22, ge=0, le=9999)
    hours: Optional[float] = Field(None, alias="Hours", description="Hours", example=176.0, ge=0, le=9999)
    unity: Optional[float] = Field(None, alias="Unity", description="Unity", example=1.0)
    percentage: Optional[float] = Field(None, alias="Percentage", description="Percentage", example=100.0)
    amount: Optional[float] = Field(None, alias="Amount", description="Amount", example=3000.0)
    supplement: Optional[float] = Field(None, alias="Supplement", description="Supplement", example=300.0)
    type_of_indexing: Optional[str] = Field(None, alias="TypeOfIndexing", description="Type of indexing", example="NoIndexation")
    contract_startdate: Optional[str] = Field(None, alias="contract_startdate", description="Contract start date for identification", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    worker_number: Optional[int] = Field(None, alias="WorkerNumber", description="Worker number", example=12345, ge=1, le=9999999)
    contract_identifier: Optional[str] = Field(None, alias="contract_identifier", description="Derived identifier workerNumber_startdate", example="12345_20250101", min_length=13, max_length=13, pattern=r'^[0-9]*$')

    class Config:
        populate_by_name = True

class SalaryCompositionUpdate(SalaryCompositionCreate):
    class Config:
        populate_by_name = True
