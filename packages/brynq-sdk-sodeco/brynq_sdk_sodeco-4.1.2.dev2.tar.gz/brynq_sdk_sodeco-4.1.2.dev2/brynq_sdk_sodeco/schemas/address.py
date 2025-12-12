from typing import Optional
from pydantic import BaseModel, Field
from brynq_sdk_functions import BrynQPanderaDataFrameModel
import pandera as pa
import pandas as pd
from pandera.typing import Series


class AddressGet(BrynQPanderaDataFrameModel):
    """Pandera schema for validating address data retrieved from Sodeco API (address endpoint)."""

    # Required fields
    worker_number: int = pa.Field(coerce=True, nullable=False, ge=1, le=9999999, description="Worker number reference", alias="WorkerNumber")
    employer: str = pa.Field(coerce=True, nullable=False, description="Employer identifier", alias="employer")
    start_date: str = pa.Field(coerce=True, nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Address valid from date in YYYYMMDD format", alias="Startdate")
    street: str = pa.Field(coerce=True, nullable=False, str_length={'min_value': 0, 'max_value': 100}, description="Street name", alias="Street")
    house_number: str = pa.Field(coerce=True, nullable=False, str_length={'min_value': 0, 'max_value': 10}, description="House number", alias="HouseNumber")
    zip_code: str = pa.Field(coerce=True, nullable=False, str_length={'min_value': 0, 'max_value': 12}, description="Postal/ZIP code", alias="ZIPCode")
    city: str = pa.Field(coerce=True, nullable=False, str_length={'min_value': 0, 'max_value': 30}, description="City name", alias="City")
    country: str = pa.Field(coerce=True, nullable=False, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', description="Country code (5 digits, default 00150 for Belgium)", alias="Country")

    # Optional fields
    end_date: Optional[str] = pa.Field(coerce=True, nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Address valid until date in YYYYMMDD format", alias="Enddate")
    post_box: Optional[str] = pa.Field(coerce=True, nullable=True, str_length={'min_value': 0, 'max_value': 5}, description="Post office box number", alias="PostBox")
    distance: Optional[float] = pa.Field(coerce=True, nullable=True, ge=0.0, le=99999.9, description="Distance from workplace in kilometers", alias="Distance")
    employer: Optional[str] = pa.Field(nullable=True, str_length={'min_value': 0, 'max_value': 40}, description="Employer name", alias="employer")

    class Config:
        strict = True
        coerce = True


class AddressCreate(BaseModel):
    start_date: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    end_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Enddate")
    street: str = Field(..., min_length=0, max_length=100, alias="Street")
    house_number: str = Field(..., min_length=0, max_length=10, alias="HouseNumber")
    post_box: Optional[str] = Field(None, min_length=0, max_length=5, alias="PostBox")
    zip_code: str = Field(..., min_length=0, max_length=12, alias="ZIPCode")
    city: str = Field(..., min_length=0, max_length=30, alias="City")
    country: str = Field(default='00150', min_length=5, max_length=5, pattern=r'^[0-9]*$', alias="Country")
    distance: Optional[float] = Field(None, ge=0.0, le=99999.9, alias="Distance")

    class Config:
        populate_by_name = True


class AddressUpdate(AddressCreate):
    class Config:
        populate_by_name = True
