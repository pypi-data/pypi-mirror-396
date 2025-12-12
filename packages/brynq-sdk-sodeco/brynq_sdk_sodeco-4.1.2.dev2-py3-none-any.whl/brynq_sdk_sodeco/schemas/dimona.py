from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime
import pandas as pd


class UsingDataSchema(DataFrameModel):
    """Schema for using data in Dimona"""
    # All fields are optional
    using_joint_commission_nbr: Optional[str] = Field(nullable=True, str_length={'min_value': 3, 'max_value': 3}, regex=r'^[0-9,.]*$', alias="UsingJointCommissionNbr")
    using_employer_name: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 40}, alias="UsingEmployerName")
    using_employer_company_id: Optional[float] = Field(nullable=True, ge=0.0, le=9999999999.0, alias="UsingEmployerCompanyID")
    using_street: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 100}, alias="UsingStreet")
    using_house_number: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 10}, alias="UsingHouseNumber")
    using_post_box: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 5}, alias="UsingPostBox")
    using_zip_code: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 12}, alias="UsingZIPCode")
    using_city: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30}, alias="UsingCity")
    using_country: Optional[str] = Field(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default="00150", alias="UsingCountry")

    class Config:
        strict = True
        coerce = True

class GetDimonaSchema(DataFrameModel):
    """Schema for GET Dimona entries"""
    # Required fields
    starting_date: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="StartingDate")

    # Optional fields
    dimona_period_id: Optional[float] = Field(nullable=True, ge=0.0, le=999999999999.0, alias="DimonaPeriodId")
    ending_date: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="EndingDate")
    starting_hour: Optional[str] = Field(nullable=True, str_length={'min_value': 12, 'max_value': 12}, regex=r'^[0-9]*$', alias="StartingHour")
    ending_hour: Optional[str] = Field(nullable=True, str_length={'min_value': 12, 'max_value': 12}, regex=r'^[0-9]*$', alias="EndingHour")
    first_month_c32a_nbr: Optional[float] = Field(nullable=True, ge=0.0, le=999999999999.0, alias="FirstMonthC32ANbr")
    next_month_c32a_nbr: Optional[float] = Field(nullable=True, ge=0.0, le=999999999999.0, alias="NextMonthC32ANbr")
    planned_hours_nbr: Optional[pd.Int64Dtype] = Field(nullable=True, ge=0, le=999, alias="PlannedHoursNbr")
    UsingData: Optional[dict] = Field(nullable=True)  # Will be validated separately using UsingDataSchema
    receipt: Optional[float] = Field(nullable=True, ge=0.0, le=999999999999.0, alias="Receipt")
    joint_commission_nbr: Optional[str] = Field(nullable=True, str_length={'min_value': 3, 'max_value': 6}, regex=r'^[0-9,.]*$', alias="JointCommissionNbr")
    worker_type: Optional[str] = Field(nullable=True, str_length={'min_value': 3, 'max_value': 3}, alias="WorkerType")
    last_action: Optional[str] = Field(nullable=True, str_length={'min_value': 1, 'max_value': 1}, alias="LastAction")
    exceeding_hours_nbr: Optional[pd.Int64Dtype] = Field(nullable=True, ge=0, le=999, alias="ExceedingHoursNbr")
    quota_exceeded: Optional[str] = Field(nullable=True, isin=['N', 'Y'], alias="QuotaExceeded")
    belated: Optional[str] = Field(nullable=True, isin=['N', 'Y'], alias="Belated")
    status: Optional[str] = Field(nullable=True, isin=['Blocked', 'InProgress', 'OK', 'Error'], alias="Status")
    error: Optional[str] = Field(nullable=True, alias="Error")

    class Config:
        strict = True
        coerce = True

class PostDimonaSchema(GetDimonaSchema):
    """Schema for POST Dimona entries, extends GetDimonaSchema with additional required fields"""
    # Additional required fields for POST
    nature_declaration: str = Field(nullable=False, isin=['DimonaIn', 'DimonaOut', 'DimonaModification', 'DimonaCancel'], alias="NatureDeclaration")
    email: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 100}, alias="Email")

    # Additional optional fields for POST
    contract_type: str = Field(nullable=True, isin=['Normal', 'Extra', 'Apprentice', 'IBO', 'TRI', 'DWD', 'A17', 'Flex', 'STG', 'S17', 'O17'], alias="ContractType")
    name: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 40}, alias="Name")
    firstname: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 25}, alias="Firstname")
    initial: Optional[str] = Field(nullable=True, str_length={'min_value': 1, 'max_value': 1}, alias="Initial")
    inss: Optional[float] = Field(nullable=True, ge=0.0, le=99999999999.0, alias="INSS")
    sex: Optional[str] = Field(nullable=True, isin=['M', 'F'], alias="Sex")
    birthdate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Birthdate")
    birthplace: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30}, alias="Birthplace")
    birthplace_country: Optional[str] = Field(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default="00150", alias="BirthplaceCountry")
    nationality: Optional[str] = Field(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default="00150", alias="Nationality")
    street: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 100}, alias="Street")
    house_number: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 10}, alias="HouseNumber")
    post_box: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 5}, alias="PostBox")
    zip_code: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 12}, alias="ZIPCode")
    city: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30}, alias="City")
    country: Optional[str] = Field(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default="00150", alias="Country")
    cat_rsz: Optional[str] = Field(nullable=True, str_length={'min_value': 3, 'max_value': 3}, regex=r'^[0-9]*$', alias="CatRSZ")
    student: Optional[str] = Field(nullable=True, isin=['N', 'Y'], alias="Student")
    activity_with_risk: Optional[pd.Int64Dtype] = Field(nullable=True, alias="ActivityWithRisk")
    worker_status: Optional[str] = Field(nullable=True, isin=['F1', 'F2'], alias="WorkerStatus")
    employment_nature: Optional[str] = Field(nullable=True, isin=['Employee', 'Worker'], alias="EmploymentNature")
    starting_hour2: Optional[str] = Field(nullable=True, str_length={'min_value': 12, 'max_value': 12}, regex=r'^[0-9]*$', alias="StartingHour2")
    ending_hour2: Optional[str] = Field(nullable=True, str_length={'min_value': 12, 'max_value': 12}, regex=r'^[0-9]*$', alias="EndingHour2")

    class Config:
        strict = True
        coerce = True
