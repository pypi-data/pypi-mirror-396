from sys import intern
from typing import Optional, Literal
from enum import Enum
from pydantic import BaseModel, Field
from brynq_sdk_functions import BrynQPanderaDataFrameModel
import pandera as pa

# Family schemas: POST/PUT request models (GET validation via FamilyGet in schemas/worker.py)


class ExistEnum(str, Enum):
    NO = 'N'
    YES = 'Y'


class CivilStatusEnum(str, Enum):
    SINGLE = 'Single'
    MARRIED = 'Married'
    WIDOW = 'Widow'
    DIVORCED = 'Divorced'
    SEPARATED = 'Separated'
    COHABITATION = 'Cohabitation'
    LIVE_TOGETHER = 'LiveTogether'


class SpouseIncomeEnum(str, Enum):
    WITH_INCOME = 'WithIncome'
    WITHOUT_INCOME = 'WithoutIncome'
    PROFF_INCOME_LESS_THAN_235 = 'ProffIncomeLessThan235'
    PROFF_INCOME_LESS_THAN_141 = 'ProffIncomeLessThan141'
    PROFF_INCOME_LESS_THAN_469 = 'ProffIncomeLessThan469'


class SpouseProfessionEnum(str, Enum):
    HANDWORKER = 'Handworker'
    SERVANT = 'Servant'
    EMPLOYEE = 'Employee'
    SELF_EMPLOYED = 'SelfEmployed'
    MINER = 'Miner'
    SAILOR = 'Sailor'
    CIVIL_SERVANT = 'CivilServant'
    OTHER = 'Other'
    NIL = 'Nil'


class FamilyStatus(BaseModel):
    start_date: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    end_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Enddate")
    civil_status: Optional[CivilStatusEnum] = Field(None, alias="CivilStatus")
    worker_handicapped: Optional[ExistEnum] = Field(None, alias="WorkerHandicapped")
    worker_single_with_children: Optional[ExistEnum] = Field(None, alias="WorkerSingleWithChildren")
    spouse_with_income: Optional[SpouseIncomeEnum] = Field(None, alias="SpouseWithIncome")
    spouse_handicapped: Optional[ExistEnum] = Field(None, alias="SpouseHandicapped")
    spouse_name: Optional[str] = Field(None, min_length=0, max_length=40, alias="SpouseName")
    spouse_first_name: Optional[str] = Field(None, min_length=0, max_length=25, alias="SpouseFirstname")
    spouse_inss: Optional[float] = Field(None, ge=0.0, le=99999999999.0, alias="SpouseINSS")
    spouse_sex: Optional[Literal['M', 'F']] = Field(None, alias="SpouseSex")
    spouse_birth_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="SpouseBirthdate")
    spouse_profession: Optional[SpouseProfessionEnum] = Field(None, alias="SpouseProfession")
    spouse_birth_place: Optional[str] = Field(None, min_length=0, max_length=30, alias="SpouseBirthplace")
    children_at_charge: Optional[int] = Field(None, ge=0, le=99, alias="ChildrenAtCharge")
    children_handicapped: Optional[int] = Field(None, ge=0, le=99, alias="ChildrenHandicapped")
    others_at_charge: Optional[int] = Field(None, ge=0, le=99, alias="OthersAtCharge")
    others_handicapped: Optional[int] = Field(None, ge=0, le=99, alias="OthersHandicapped")
    others_65_at_charge: Optional[int] = Field(None, ge=0, le=99, alias="Others65AtCharge")
    others_65_handicapped: Optional[int] = Field(None, ge=0, le=99, alias="Others65Handicapped")
    child_benefit_institution: Optional[int] = Field(None, ge=0, le=9999, alias="ChildBenefitInstitution")
    child_benefit_reference: Optional[str] = Field(None, min_length=0, max_length=15, alias="ChildBenefitReference")
    wedding_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="WeddingDate")

    class Config:
        populate_by_name = True


class FamilyCreate(BaseModel):
    start_date: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    end_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Enddate")
    civil_status: Optional[str] = Field(None, alias="CivilStatus")
    worker_handicapped: Optional[str] = Field(None, alias="WorkerHandicapped")
    worker_single_with_children: Optional[str] = Field(None, alias="WorkerSingleWithChildren")
    spouse_with_income: Optional[str] = Field(None, alias="SpouseWithIncome")
    spouse_handicapped: Optional[str] = Field(None, alias="SpouseHandicapped")
    spouse_name: Optional[str] = Field(None, min_length=0, max_length=40, alias="SpouseName")
    spouse_first_name: Optional[str] = Field(None, min_length=0, max_length=25, alias="SpouseFirstname")
    spouse_inss: Optional[float] = Field(None, ge=0.0, le=99999999999.0, alias="SpouseINSS")
    spouse_sex: Optional[str] = Field(None, alias="SpouseSex")
    spouse_profession: Optional[str] = Field(None, alias="SpouseProfession")
    spouse_birth_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="SpouseBirthdate")
    spouse_birth_place: Optional[str] = Field(None, min_length=0, max_length=30, alias="SpouseBirthplace")
    children_at_charge: Optional[int] = Field(None, ge=0, le=99, alias="ChildrenAtCharge")
    children_handicapped: Optional[int] = Field(None, ge=0, le=99, alias="ChildrenHandicapped")
    others_at_charge: Optional[int] = Field(None, ge=0, le=99, alias="OthersAtCharge")
    others_handicapped: Optional[int] = Field(None, ge=0, le=99, alias="OthersHandicapped")
    others_65_at_charge: Optional[int] = Field(None, ge=0, le=99, alias="Others65AtCharge")
    wage_garnishment_children_at_charge: Optional[int] = Field(None, ge=0, le=99, alias="WageGarnishmentChildrenAtCharge")
    others_65_handicapped: Optional[int] = Field(None, ge=0, le=99, alias="Others65Handicapped")
    others_65_need_of_care: Optional[int] = Field(None, ge=0, le=99, alias="Others65NeedOfCare")
    child_benefit_institution: Optional[int] = Field(None, ge=0, le=9999, alias="ChildBenefitInstitution")
    child_benefit_reference: Optional[str] = Field(None, min_length=0, max_length=15, alias="ChildBenefitReference")
    wedding_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Weddingdate")

    class Config:
        populate_by_name = True


class FamilyUpdate(FamilyCreate):
    class Config:
        populate_by_name = True


class FamilyGet(BrynQPanderaDataFrameModel):
    """Pandera schema for validating family status data retrieved from Sodeco API."""

    # Required fields
    start_date: str = pa.Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Family status start date in YYYYMMDD format", alias="Startdate")

    # Optional fields
    worker_number: Optional[int] = pa.Field(nullable=True, description="Worker number", alias="WorkerNumber")
    employer: Optional[str] = pa.Field(nullable=True, description="Employer identifier", alias="employer")
    end_date: Optional[str] = pa.Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Family status end date in YYYYMMDD format", alias="Enddate")
    civil_status: Optional[str] = pa.Field(nullable=True, isin=['Single', 'Married', 'Widow', 'Divorced', 'Separated', 'Cohabitation', 'LiveTogether'], description="Civil/marital status", alias="CivilStatus")
    worker_handicapped: Optional[str] = pa.Field(nullable=True, isin=['N', 'Y'], description="Worker has handicap (Y/N)", alias="WorkerHandicapped")
    worker_single_with_children: Optional[str] = pa.Field(nullable=True, isin=['N', 'Y'], description="Worker is single parent (Y/N)", alias="WorkerSingleWithChildren")

    # Spouse information
    spouse_with_income: Optional[str] = pa.Field(nullable=True, isin=['WithIncome', 'WithoutIncome', 'ProffIncomeLessThan235', 'ProffIncomeLessThan141', 'ProffIncomeLessThan469'], description="Spouse income status", alias="SpouseWithIncome")
    spouse_handicapped: Optional[str] = pa.Field(nullable=True, isin=['N', 'Y'], description="Spouse has handicap (Y/N)", alias="SpouseHandicapped")
    spouse_name: Optional[str] = pa.Field(nullable=True, str_length={'min_value': 0, 'max_value': 40}, description="Spouse last name", alias="SpouseName")
    spouse_first_name: Optional[str] = pa.Field(nullable=True, str_length={'min_value': 0, 'max_value': 25}, description="Spouse first name", alias="SpouseFirstname")
    spouse_inss: Optional[float] = pa.Field(nullable=True, ge=0, le=99999999999.0, description="Spouse national insurance number", alias="SpouseINSS")
    spouse_sex: Optional[str] = pa.Field(nullable=True, isin=['M', 'F'], description="Spouse gender (M/F)", alias="SpouseSex")
    spouse_profession: Optional[str] = pa.Field(nullable=True, isin=['Handworker', 'Servant', 'Employee', 'SelfEmployed', 'Miner', 'Sailor', 'CivilServant', 'Other', 'Nil'], description="Spouse profession category", alias="SpouseProfession")
    spouse_birth_date: Optional[str] = pa.Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Spouse birth date in YYYYMMDD format", alias="SpouseBirthdate")
    spouse_birth_place: Optional[str] = pa.Field(nullable=True, str_length={'min_value': 0, 'max_value': 30}, description="Spouse birthplace", alias="SpouseBirthplace")

    # Dependents information
    children_at_charge: Optional[int] = pa.Field(nullable=True, ge=0, le=99, description="Number of children at charge", alias="ChildrenAtCharge")
    children_handicapped: Optional[int] = pa.Field(nullable=True, ge=0, le=99, description="Number of handicapped children", alias="ChildrenHandicapped")
    others_at_charge: Optional[int] = pa.Field(nullable=True, ge=0, le=99, description="Number of other dependents", alias="OthersAtCharge")
    others_handicapped: Optional[int] = pa.Field(nullable=True, ge=0, le=99, description="Number of other handicapped dependents", alias="OthersHandicapped")
    others_65_at_charge: Optional[int] = pa.Field(nullable=True, ge=0, le=99, description="Number of dependents over 65", alias="Others65AtCharge")
    wage_garnishment_children_at_charge: Optional[int] = pa.Field(nullable=True, ge=0, le=99, description="Number of children for wage garnishment", alias="WageGarnishmentChildrenAtCharge")
    others_65_handicapped: Optional[int] = pa.Field(nullable=True, ge=0, le=99, description="Number of handicapped dependents over 65", alias="Others65Handicapped")
    others_65_need_of_care: Optional[int] = pa.Field(nullable=True, ge=0, le=99, description="Number of dependents over 65 needing care", alias="Others65NeedOfCare")

    # Child benefit information
    child_benefit_institution: Optional[int] = pa.Field(nullable=True, ge=0, le=9999, description="Child benefit institution code", alias="ChildBenefitInstitution")
    child_benefit_reference: Optional[str] = pa.Field(nullable=True, str_length={'min_value': 0, 'max_value': 15}, description="Child benefit reference number", alias="ChildBenefitReference")
    wedding_date: Optional[str] = pa.Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Wedding date in YYYYMMDD format", alias="Weddingdate")

    class Config:
        strict = True
        coerce = True
