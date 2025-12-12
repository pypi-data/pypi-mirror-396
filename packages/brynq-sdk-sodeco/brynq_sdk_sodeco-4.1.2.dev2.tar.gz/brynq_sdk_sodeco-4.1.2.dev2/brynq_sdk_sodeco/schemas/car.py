from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# ============================================================================
# ENUMS
# ============================================================================

class MotorTypeEnum(str, Enum):
    """Enumeration for motor types."""
    GASOLINE = "Gasoline"
    DIESEL = "Diesel"
    LPG = "LPG"
    ELECTRIC = "Electric"
    CNG = "CNG"


class YesNoEnum(str, Enum):
    """Enumeration for Yes/No values."""
    NO = "N"
    YES = "Y"


# ============================================================================
# PYDANTIC SCHEMAS (Request/Response Models)
# ============================================================================

class CarCreate(BaseModel):
    """Schema for creating a new company car entry."""

    # Required fields
    starting_date: str = Field(..., alias="StartingDate", description="Car start date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    license_plate: str = Field(..., alias="LicensePlate", description="Car license plate number", example="ABC-123", min_length=0, max_length=15)

    # Optional fields
    ending_date: Optional[str] = Field(None, alias="EndingDate", description="Car end date in YYYYMMDD format", example="20251231", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    worker_number: Optional[int] = Field(None, alias="WorkerId", description="Worker ID associated with the car", example=12345)
    cat_rsz: Optional[str] = Field(None, alias="CatRSZ", description="Social security category code", example="123", min_length=3, max_length=3, pattern=r'^[0-9]*$')
    motor_type: Optional[MotorTypeEnum] = Field(None, alias="MotorType", description="Type of motor/engine", example="Gasoline")
    tax_horsepower: Optional[int] = Field(None, alias="TaxHorsepower", description="Tax horsepower rating", example=12, ge=0, le=99)
    co2_emissions_hybride_wltp: Optional[int] = Field(None, alias="Co2EmissionsHybrideWLTP", description="CO2 emissions hybrid WLTP", example=120, ge=0, le=500)
    co2_emissions_hybride: Optional[int] = Field(None, alias="Co2EmissionsHybride", description="CO2 emissions hybrid", example=110, ge=0, le=500)
    co2_emissions_wltp: Optional[int] = Field(None, alias="Co2EmissionsWLTP", description="CO2 emissions WLTP", example=130, ge=0, le=500)
    co2_emissions: Optional[int] = Field(None, alias="Co2Emissions", description="CO2 emissions", example=125, ge=0, le=500)
    code: Optional[int] = Field(None, alias="Code", description="Salary code for car benefits", example=4001, ge=4000, le=8999)
    fuel_card: Optional[str] = Field(None, alias="FuelCard", description="Fuel card number", example="FC-123456", min_length=0, max_length=20)
    brand: Optional[str] = Field(None, alias="Brand", description="Car brand/manufacturer", example="Toyota", min_length=0, max_length=50)
    order_date: Optional[str] = Field(None, alias="OrderDate", description="Car order date in YYYYMMDD format", example="20241201", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    registration_date: Optional[str] = Field(None, alias="RegistrationDate", description="Car registration date in YYYYMMDD format", example="20250115", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    catalog_price: Optional[float] = Field(None, alias="CatalogPrice", description="Car catalog price", example=25000.0)
    informative: Optional[YesNoEnum] = Field(None, alias="Informative", description="Is this entry informative only", example="N")
    light_truck: Optional[YesNoEnum] = Field(None, alias="LightTruck", description="Is this a light truck", example="N")
    pool_car: Optional[YesNoEnum] = Field(None, alias="PoolCar", description="Is this a pool car", example="N")
    pers_contribution_amount: Optional[float] = Field(None, alias="PersContributionAmount", description="Personal contribution amount", example=100.0)
    pers_contribution_percentage: Optional[float] = Field(None, alias="PersContributionPercentage", description="Personal contribution percentage", example=5.0)
    pers_contribution_code: Optional[int] = Field(None, alias="PersContributionCode", description="Personal contribution salary code", example=4002, ge=4000, le=8999)
    pers_contribution_startdate: Optional[str] = Field(None, alias="PersContributionStartdate", description="Personal contribution start date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    pers_contribution_enddate: Optional[str] = Field(None, alias="PersContributionEnddate", description="Personal contribution end date in YYYYMMDD format", example="20251231", min_length=8, max_length=8, pattern=r'^[0-9]*$')


    class Config:
        populate_by_name = True


class CarUpdate(CarCreate):
    """Schema for updating a company car entry. All fields are optional for partial updates."""

    # Make required fields optional for updates
    starting_date: Optional[str] = Field(None, alias="StartingDate", description="Car start date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    license_plate: Optional[str] = Field(None, alias="LicensePlate", description="Car license plate number", example="ABC-123", min_length=0, max_length=15)

    class Config:
        populate_by_name = True


# ============================================================================
# PANDERA SCHEMAS (DataFrame Validation)
# ============================================================================

class CarGet(BrynQPanderaDataFrameModel):
    """Schema for validating company car data retrieved from Sodeco API."""

    # Required fields
    starting_date: str = pa.Field(coerce=True, nullable=False, description="Car start date in YYYYMMDD format", alias="StartingDate")
    license_plate: str = pa.Field(coerce=True, nullable=False, description="Car license plate number", alias="LicensePlate")

    # Optional fields
    ending_date: Optional[str] = pa.Field(coerce=True, nullable=True, description="Car end date in YYYYMMDD format", alias="EndingDate")
    worker_number: Optional[int] = pa.Field(coerce=True, nullable=True, description="Worker ID associated with the car", alias="WorkerId")
    cat_rsz: Optional[str] = pa.Field(coerce=True, nullable=True, description="Social security category code", alias="CatRSZ")
    motor_type: Optional[str] = pa.Field(coerce=True, nullable=True, description="Type of motor/engine", alias="MotorType")
    tax_horsepower: Optional[int] = pa.Field(coerce=True, nullable=True, description="Tax horsepower rating", alias="TaxHorsepower")
    co2_emissions_hybride_wltp: Optional[int] = pa.Field(coerce=True, nullable=True, description="CO2 emissions hybrid WLTP", alias="Co2EmissionsHybrideWLTP")
    co2_emissions_hybride: Optional[int] = pa.Field(coerce=True, nullable=True, description="CO2 emissions hybrid", alias="Co2EmissionsHybride")
    co2_emissions_wltp: Optional[int] = pa.Field(coerce=True, nullable=True, description="CO2 emissions WLTP", alias="Co2EmissionsWLTP")
    co2_emissions: Optional[int] = pa.Field(coerce=True, nullable=True, description="CO2 emissions", alias="Co2Emissions")
    code: Optional[int] = pa.Field(coerce=True, nullable=True, description="Salary code for car benefits", alias="Code")
    fuel_card: Optional[str] = pa.Field(coerce=True, nullable=True, description="Fuel card number", alias="FuelCard")
    brand: Optional[str] = pa.Field(coerce=True, nullable=True, description="Car brand/manufacturer", alias="Brand")
    order_date: Optional[str] = pa.Field(coerce=True, nullable=True, description="Car order date in YYYYMMDD format", alias="OrderDate")
    registration_date: Optional[str] = pa.Field(coerce=True, nullable=True, description="Car registration date in YYYYMMDD format", alias="RegistrationDate")
    catalog_price: Optional[float] = pa.Field(coerce=True, nullable=True, description="Car catalog price", alias="CatalogPrice")
    informative: Optional[str] = pa.Field(coerce=True, nullable=True, description="Is this entry informative only", alias="Informative")
    light_truck: Optional[str] = pa.Field(coerce=True, nullable=True, description="Is this a light truck", alias="LightTruck")
    pool_car: Optional[str] = pa.Field(coerce=True, nullable=True, description="Is this a pool car", alias="PoolCar")
    pers_contribution_amount: Optional[float] = pa.Field(coerce=True, nullable=True, description="Personal contribution amount", alias="PersContributionAmount")
    pers_contribution_percentage: Optional[float] = pa.Field(coerce=True, nullable=True, description="Personal contribution percentage", alias="PersContributionPercentage")
    pers_contribution_code: Optional[int] = pa.Field(coerce=True, nullable=True, description="Personal contribution salary code", alias="PersContributionCode")
    pers_contribution_startdate: Optional[str] = pa.Field(coerce=True, nullable=True, description="Personal contribution start date in YYYYMMDD format", alias="PersContributionStartdate")
    pers_contribution_enddate: Optional[str] = pa.Field(coerce=True, nullable=True, description="Personal contribution end date in YYYYMMDD format", alias="PersContributionEnddate")
    employer: Optional[str] = pa.Field(nullable=True, str_length={'min_value': 0, 'max_value': 40}, description="Employer name", alias="employer")

    class Config:
        strict = True
        coerce = True

    class _Annotation:
        primary_key = "license_plate"
