from pydantic import BaseModel, Field
from typing import Optional, List, Union
from enum import Enum
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class ResetEnum(str, Enum):
    NO = 'N'
    YES = 'Y'


class CostModel(BaseModel):
    """Model for cost entries in prestations"""
    code: int = Field(..., ge=1, le=8999, alias="Code")  # Required field
    cost_centre: Optional[str] = Field(None, min_length=0, max_length=15, alias="CostCentre")
    shift: Optional[int] = Field(None, ge=1, le=99, alias="Shift")
    days: Optional[int] = Field(None, ge=0, le=99, alias="Days")
    hours: Optional[float] = Field(None, ge=0, le=9999, alias="Hours")
    unity: Optional[float] = None
    percentage: Optional[float] = None
    amount: Optional[float] = None
    supplement: Optional[float] = None

    class Config:
        populate_by_name = True


class PrestationEntryModel(BaseModel):
    """Model for individual prestation entries"""
    day: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Day")  # Required field
    code: int = Field(..., ge=1, le=6999, alias="Code")  # Required field
    cost_centre: Optional[str] = Field(None, min_length=0, max_length=15, alias="CostCentre")
    shift: Optional[int] = Field(None, ge=1, le=99, alias="Shift")
    hours: Optional[float] = Field(None, ge=0, le=9999, alias="Hours")

    class Config:
        populate_by_name = True


class PrestationModel(BaseModel):
    """Model for prestation entries"""
    # Required fields
    worker_number: int = Field(..., ge=1, le=9999999, alias="WorkerNumber")
    month: int = Field(..., ge=1, le=12, alias="Month")
    year: int = Field(..., ge=1900, le=2075, alias="Year")
    end_of_period: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="EndOfPeriod")

    # Optional fields
    annotation: Optional[str] = None
    reset: Optional[ResetEnum] = None
    prestations: Optional[List[Union[PrestationEntryModel, None]]] = None
    costs: Optional[List[Union[CostModel, None]]] = None

    class Config:
        populate_by_name = True


class PrestationCompletedModel(BaseModel):
    """Model for marking prestations as completed"""
    month: int = Field(..., ge=1, le=12, alias="Month")
    year: int = Field(..., ge=1900, le=2075, alias="Year")
    correction: Optional[ResetEnum] = None

    class Config:
            populate_by_name = True

    @classmethod
    def validate_completed(cls, data: dict) -> bool:
        try:
            PrestationCompletedModel(**data)
            return True
        except Exception:
            return False


class DeletePrestationModel(BaseModel):
    """Model for deleting prestations"""
    worker_number: int = Field(..., ge=1, le=9999999, alias="WorkerNumber")
    month: int = Field(..., ge=1, le=12, alias="Month")
    year: int = Field(..., ge=1900, le=2075, alias="Year")

    class Config:
        populate_by_name = True

    @classmethod
    def validate_delete(cls, data: dict) -> bool:
        try:
            DeletePrestationModel(**data)
            return True
        except Exception:
            return False
