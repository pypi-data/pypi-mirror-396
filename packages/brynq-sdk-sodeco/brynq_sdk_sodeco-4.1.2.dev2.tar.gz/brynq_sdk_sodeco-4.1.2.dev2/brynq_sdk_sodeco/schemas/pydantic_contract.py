from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, constr

class CareerBreakDefinition(BaseModel):
    """Details about a career break period."""
    reason: str = Field(
        ...,
        max_length=50,
        description="The reason for taking a career break (max length: 50 characters)",
        alias="Reason"
    )
    start_date: str = Field(
        ...,
        pattern=r'^[0-9]{8}$',
        description="Start date of the career break (required, format: YYYYMMDD)",
        alias="StartDate"
    )
    end_date: Optional[str] = Field(
        None,
        pattern=r'^[0-9]{8}$',
        description="End date of the career break (optional, format: YYYYMMDD)",
        alias="EndDate"
    )

class CertainWorkDefinition(BaseModel):
    """Details about a certain work period."""
    start_date: str = Field(
        ...,
        pattern=r'^[0-9]{8}$',
        description="Start date of the certain work period (required, format: YYYYMMDD)",
        alias="StartDate"
    )
    end_date: str = Field(
        ...,
        pattern=r'^[0-9]{8}$',
        description="End date of the certain work period (required, format: YYYYMMDD)",
        alias="EndDate"
    )

class StudentDefinition(BaseModel):
    """Details about a student work period."""
    start_date: str = Field(
        ...,
        pattern=r'^[0-9]{8}$',
        description="Start date of the student work period (required, format: YYYYMMDD)",
        alias="StartDate"
    )
    end_date: str = Field(
        ...,
        pattern=r'^[0-9]{8}$',
        description="End date of the student work period (required, format: YYYYMMDD)",
        alias="EndDate"
    )

class Contract(BaseModel):
    """
    Contract schema defining all fields and validation rules for a worker contract.

    This model represents the complete contract information including both required
    and optional fields. All date fields follow the YYYYMMDD format.
    """
    # Required fields
    start_date: str = Field(
        ...,
        pattern=r'^[0-9]{8}$',
        description="Contract start date (required, format: YYYYMMDD)",
        alias="StartDate"
    )
    employment_status: str = Field(
        ...,
        description="Type of employment (required). Valid values: Employee, Interim, Student",
        alias="EmploymentStatus",
        enum=['Employee', 'Interim', 'Student']
    )
    working_time: str = Field(
        ...,
        description="Working time type (required). Valid values: Fulltime, Parttime",
        alias="WorkingTime",
        enum=['Fulltime', 'Parttime']
    )
    wekhours_worker: float = Field(
        ...,
        ge=0.0,
        le=168.0,
        description="Weekly hours for worker (required, range: 0-168)",
        alias="WekhoursWorker"
    )
    wekhours_employer: float = Field(
        ...,
        ge=0.0,
        le=168.0,
        description="Weekly hours for employer (required, range: 0-168)",
        alias="WekhoursEmployer"
    )

    # Optional fields
    end_date: str = Field(
        None,
        pattern=r'^[0-9]{8}$',
        description="Contract end date (optional, format: YYYYMMDD)",
        alias="EndDate"
    )
    contract_type: Optional[str] = Field(
        None,
        description="Type of contract (optional). Valid values: Determined, Undetermined, Replacement, Student",
        enum=['Determined', 'Undetermined', 'Replacement', 'Student'],
        alias="ContractType"
    )
    function: Optional[str] = Field(
        None,
        max_length=50,
        description="Job function (optional, max length: 50 characters)",
        alias="Function"
    )
    schedule_code: Optional[str] = Field(
        None,
        max_length=20,
        description="Schedule identifier (optional, max length: 20 characters)",
        alias="ScheduleCode"
    )
    shift_code: Optional[str] = Field(
        None,
        max_length=20,
        description="Shift identifier (optional, max length: 20 characters)",
        alias="ShiftCode"
    )
    workplace_code: Optional[str] = Field(
        None,
        max_length=20,
        description="Workplace identifier (optional, max length: 20 characters)",
        alias="WorkplaceCode"
    )
    department_code: Optional[str] = Field(
        None,
        max_length=20,
        description="Department identifier (optional, max length: 20 characters)",
        alias="DepartmentCode"
    )
    job_classification_code: Optional[str] = Field(
        None,
        max_length=20,
        description="Job classification code (optional, max length: 20 characters)",
        alias="JobClassificationCode"
    )
    salary_scale_code: Optional[str] = Field(
        None,
        max_length=20,
        description="Salary scale identifier (optional, max length: 20 characters)",
        alias="SalaryScaleCode"
    )
    salary_scale_step: Optional[int] = Field(
        None,
        ge=0,
        description="Step in salary scale (optional, must be >= 0)",
        alias="SalaryScaleStep"
    )
    comments: Optional[str] = Field(
        None,
        max_length=255,
        description="Additional comments (optional, max length: 255 characters)",
        alias="Comments"
    )
    career_break: Optional[CareerBreakDefinition] = Field(
        None,
        description="Career break information (optional). See CareerBreakDefinition schema",
        alias="CareerBreak"
    )
    certain_work: Optional[CertainWorkDefinition] = Field(
        None,
        description="Certain work period information (optional). See CertainWorkDefinition schema",
        alias="CertainWork"
    )
    student: Optional[StudentDefinition] = Field(
        None,
        description="Student period information (optional). See StudentDefinition schema",
        alias="Student"
    )
    cost_centers: Optional[List[str]] = Field(
        None,
        description="List of cost center codes (optional)",
        alias="CostCenters"
    )
    benefit_codes: Optional[List[str]] = Field(
        None,
        description="List of benefit codes (optional)",
        alias="BenefitCodes"
    )
