from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from enum import Enum
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class ResetEnum(str, Enum):
    N = "N"
    Y = "Y"


class ContractTypeEnum(str, Enum):
    WORKMAN = "Workman"
    EMPLOYEE = "Employee"
    DIRECTOR = "Director"


class WorkingTimeEnum(str, Enum):
    FULLTIME = "Fulltime"
    PARTTIME = "PartTime"


class SpecWorkingTimeEnum(str, Enum):
    REGULAR = "Regular"
    INTERRUPTIONS = "Interruptions"
    SEASONAL_WORKER = "SeasonalWorker"


class AgricultureTypeEnum(str, Enum):
    NONE = None
    HORTICULTURE = "Horticulture"
    HORTICULTURE_CHICORY = "HorticultureChicory"
    AGRICULTURE = "Agriculture"
    HORTICULTURE_MUSHROOM = "HorticultureMushroom"
    HORTICULTURE_FRUIT = "HorticultureFruit"


class CareerBreakKindEnum(str, Enum):
    FULLTIME = "Fulltime"
    PARTTIME_ONE_FIFTH = "PartTimeOneFifth"
    PARTTIME_ONE_QUARTER = "PartTimeOneQuarter"
    PARTTIME_ONE_THIRD = "PartTimeOneThird"
    PARTTIME_HALF = "PartTimeHalf"
    PARTTIME_THREE_FIFTHS = "PartTimeThreeFifths"
    PARTTIME_ONE_TENTH = "PartTimeOneTenth"


class CareerBreakReasonEnum(str, Enum):
    PALLIATIVE_CARE = "PalliativeCare"
    SERIOUSLY_ILL = "SeriouslyIll"
    OTHER = "Other"
    PARENTAL_LEAVE = "ParentalLeave"
    CRISIS = "Crisis"
    FAMILY_CARE = "FamilyCare"
    END_OF_CAREER = "EndOfCareer"
    SICK_CHILD = "SickChild"
    FAMILY_CARE_CORONA = "FamilyCareCorona"
    CHILD_CARE_UNDER_8 = "ChildCareUnder8"
    CHILD_CARE_HANDICAP_UNDER_21 = "ChildCareHandicapUnder21"
    CERTIFIED_TRAINING = "CertifiedTraining"


class DocumentC78Enum(str, Enum):
    NIHIL = "Nihil"
    C783 = "C783"
    C784 = "C784"
    C78_ACTIVA = "C78Activa"
    C78_START = "C78Start"
    C78_SINE = "C78Sine"
    C78_SHORT_TERM = "C78ShortTerm"
    WALLONIA_LONGTERM_JOB_SEEKERS = "WalloniaLongtermJobSeekers"
    WALLONIA_YOUNG_JOB_SEEKERS = "WalloniaYoungJobSeekers"
    WALLONIA_IMPULSION_INSERTION = "WalloniaImpulsionInsertion"
    BRUSSELS_LONGTERM_JOB_SEEKERS = "BrusselsLongtermJobSeekers"
    BRUSSELS_REDUCED_ABILITY = "BrusselsReducedAbility"


class ReducingWorkingKindEnum(str, Enum):
    NIHIL = "Nihil"
    PAID = "Paid"
    UNPAID = "Unpaid"


class SocialBalanceJoblevelEnum(str, Enum):
    OPERATIONAL_STAFF = "OperationalStaff"
    EXECUTIVE_STAFF = "ExecutiveStaff"
    MANAGEMENT_STAFF = "ManagementStaff"
    BY_FUNCTION = "ByFunction"


class TypeOfIndexingEnum(str, Enum):
    NO_INDEXATION = "NoIndexation"
    INDEXATION = "Indexation"
    FROZEN_SALARY = "FrozenSalary"
    SALARY_ABOVE_SCALE = "SalaryAboveScale"


class DimonaStatusEnum(str, Enum):
    BLOCKED = "Blocked"
    IN_PROGRESS = "InProgress"
    OK = "OK"
    ERROR = "Error"


class ContractEnum(str, Enum):
    USUALLY = "Usually"
    FLEXI_VERBAL = "FlexiVerbal"
    FLEXI_WRITTEN = "FlexiWritten"
    FLEXI_LIABLE = "FlexiLiable"
    SPORTSPERSON = "Sportsperson"
    HOUSEKEEPER = "Housekeeper"
    SERVANT = "Servant"
    AGRICULTURE = "Agriculture"
    HOMEWORK = "Homework"
    HOMEWORK_CHILDCARE = "HomeworkChildcare"
    PHYSICIAN = "Physician"
    PHYSICIAN_TRAINING = "PhysicianTraining"
    PHYSICIAN_INDEPENDANT = "PhysicianIndependant"
    APPRENTICE_FLEMISCH = "ApprenticeFlemisch"
    APPRENTICE_FRENCH = "ApprenticeFrench"
    APPRENTICE_GERMAN = "ApprenticeGerman"
    APPRENTICE_MANAGER = "ApprenticeManager"
    APPRENTICE_INDUSTRIAL = "ApprenticeIndustrial"
    APPRENTICE_SOCIO = "ApprenticeSocio"
    APPRENTICE_BIO = "ApprenticeBio"
    APPRENTICE_ALTERNATING = "ApprenticeAlternating"
    EARLY_RETIREMENT = "EarlyRetirement"
    EARLY_RETIREMENT_PART_TIME = "EarlyRetirementPartTime"
    FREE_NOSS = "FreeNOSS"
    FREE_NOSS_MANAGER = "FreeNOSSManager"
    FREE_NOSS_OTHER = "FreeNOSSOther"
    FREE_NOSS_SPORTING_EVENT = "FreeNOSSSportingEvent"
    FREE_NOSS_HELPER = "FreeNOSSHelper"
    FREE_NOSS_SOCIO = "FreeNOSSSocio"
    FREE_NOSS_EDUCATION = "FreeNOSSEducation"
    FREE_NOSS_SPECIAL_CULTURES = "FreeNOSSSpecialCultures"
    FREE_NOSS_VOLUNTEER = "FreeNOSSVolunteer"
    HORECA = "Horeca"
    HORECA_EXTRA_HOUR_LIABLE = "HorecaExtraHourLiable"
    HORECA_EXTRA_DAY_LIABLE = "HorecaExtraDayLiable"
    HORECA_EXTRA_HOUR_FORFAIT = "HorecaExtraHourForfait"
    HORECA_EXTRA_DAY_FORFAIT = "HorecaExtraDayForfait"
    HORECA_FLEXI_VERBAL = "HorecaFlexiVerbal"
    HORECA_FLEXI_WRITTEN = "HorecaFlexiWritten"
    HORECA_FLEXI_LIABLE = "HorecaFlexiLiable"
    CONSTRUCTION = "Construction"
    CONSTRUCTION_ALTERNATING = "ConstructionAlternating"
    CONSTRUCTION_APPRENTICE_YOUNGER = "ConstructionApprenticeYounger"
    CONSTRUCTION_APPRENTICE = "ConstructionApprentice"
    CONSTRUCTION_GODFATHER = "ConstructionGodfather"
    JOB_TRAINING_IBO = "JobTrainingIBO"
    JOB_TRAINING_SCHOOL = "JobTrainingSchool"
    JOB_TRAINING_VDAB = "JobTrainingVDAB"
    JOB_TRAINING_LIBERAL_PROFESSION = "JobTrainingLiberalProfession"
    JOB_TRAINING_ENTRY = "JobTrainingEntry"
    JOB_TRAINING_PFI_WA = "JobTrainingPFIWa"
    JOB_TRAINING_ABO = "JobTrainingABO"
    JOB_TRAINING_PFI_BX = "JobTrainingPFIBx"
    JOB_TRAINING_BIO = "JobTrainingBIO"
    JOB_TRAINING_ALTERNATING = "JobTrainingAlternating"
    JOB_TRAINING_DISABILITY = "JobTrainingDisability"
    NON_PROFIT_RIZIV = "NonProfitRiziv"
    NON_PROFIT_GESCO = "NonProfitGesco"
    NON_PROFIT_DAC = "NonProfitDAC"
    NON_PROFIT_PRIME = "NonProfitPrime"
    NON_PROFIT_LOW_SKILLED = "NonProfitLowSkilled"
    ARTIST = "Artist"
    ARTIST_WITH_CONTRACT = "ArtistWithContract"
    ARTIST_WITHOUT_CONTRACT = "ArtistWithoutContract"
    TRANSPORT = "Transport"
    TRANSPORT_NON_MOBILE = "TransportNonMobile"
    TRANSPORT_GARAGE = "TransportGarage"
    AIRCREW = "Aircrew"
    AIRCREW_PILOT = "AircrewPilot"
    AIRCREW_CABIN_CREW = "AircrewCabinCrew"
    INTERIM = "Interim"
    INTERIM_TEMPORARY = "InterimTemporary"
    INTERIMS_PERMANENT = "InterimsPermanent"
    EXTERNAL = "External"
    EXTERNAL_APPLICANT = "ExternalApplicant"
    EXTERNAL_SUBCONTRACTOR = "ExternalSubcontractor"
    EXTERNAL_AGENT_INDEPENDANT = "ExternalAgentIndependant"
    EXTERNAL_EXTERN = "ExternalExtern"
    EXTERNAL_INTERN = "ExternalIntern"
    EXTERNAL_LEGAL_PERSON = "ExternalLegalPerson"
    SALES_REPRESENTATIVE = "SalesRepresentative"
    SPORTS_TRAINER = "SportsTrainer"


# Nested Models
class CareerBreakDefinition(BaseModel):
    exist: ResetEnum = Field(alias="Exist", description="Career break exists", example="N")
    kind: Optional[CareerBreakKindEnum] = Field(None, alias="Kind", description="Career break kind", example="Fulltime")
    reason: Optional[CareerBreakReasonEnum] = Field(None, alias="Reason", description="Career break reason", example="ParentalLeave")
    originally_contract_type: Optional[str] = Field(None, alias="OriginallyContractType", description="Originally contract type", example="Fulltime")
    weekhours_worker_before: Optional[float] = Field(None, alias="WeekhoursWorkerBefore", description="Weekly hours worker before", example=40.0)
    weekhours_employer_before: Optional[float] = Field(None, alias="WeekhoursEmployerBefore", description="Weekly hours employer before", example=40.0)

    class Config:
        populate_by_name = True


class RetiredDefinition(BaseModel):
    exist: str = Field(alias="Exist", description="Indicates if the person is retired", example="Y", min_length=1, max_length=1)
    kind: Optional[str] = Field(None, alias="Kind", description="Type of retirement", example="PensionPrivateSector", enum=["PensionPrivateSector", "SurvivalPension", "PensionSelfEmployed", "pensionPublicSector"])
    date_retired: Optional[str] = Field(None, alias="DateRetired", description="Retirement date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    apply_collecting_2nd_pension_pillar: Optional[str] = Field(None, alias="ApplyCollecting2ndPensionPillar", description="Indicates if collecting the 2nd pension pillar applies", example="N", enum=["N", "Y"])
    retired_type: Optional[str] = Field(None, alias="RetiredType", description="Type of pension", example="EarlyPension", enum=["EarlyPension", "LegalPension"])

    class Config:
        populate_by_name = True


class ProtectedEmployeeDefinition(BaseModel):
    exist: str = Field(alias="Exist", description="Indicates if the employee is protected", example="Y", min_length=1, max_length=1, enum=["N", "Y"])
    reason: Optional[str] = Field(None, alias="Reason", description="Reason code for protection", example="0001", min_length=4, max_length=4, pattern=r'^[0-9]*$')
    startdate: Optional[str] = Field(None, alias="Startdate", description="Protection start date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    enddate: Optional[str] = Field(None, alias="Enddate", description="Protection end date in YYYYMMDD format", example="20251231", min_length=8, max_length=8, pattern=r'^[0-9]*$')

    class Config:
        populate_by_name = True


class SportsPersonDefinition(BaseModel):
    exist: str = Field(alias="Exist", description="Indicates if the person is a sportsperson", example="Y", min_length=1, max_length=1, enum=["N", "Y"])
    recognized_foreign_sportsperson: Optional[str] = Field(None, alias="RecognizedForeignSportsperson", description="Indicates if the sportsperson is recognized as a foreign sportsperson", example="N", enum=["N", "Y"])
    opportunity_contract: Optional[str] = Field(None, alias="OpportunityContract", description="Indicates if the sportsperson has an opportunity contract", example="N", enum=["N", "Y"])

    class Config:
        populate_by_name = True


class CertainWorkDefinition(BaseModel):
    exist: ResetEnum = Field(alias="Exist", description="Certain work exists", example="N")
    description: Optional[str] = Field(None, alias="Description", description="Certain work description", example="Special project work", max_length=250)

    class Config:
        populate_by_name = True


class StudentDefinition(BaseModel):
    exist: str = Field(alias="Exist", description="Indicates if the person is a student", example="Y", min_length=1, max_length=1, enum=["N", "Y"])
    solidarity_contribution: str = Field(alias="SolidarityContribution", description="Indicates if the student pays solidarity contribution", example="N", enum=["N", "Y"])

    class Config:
        populate_by_name = True


class ProgressiveWorkResumptionDefinition(BaseModel):
    exist: str = Field(alias="Exist", description="Indicates if progressive work resumption applies", example="Y", min_length=1, max_length=1, enum=["N", "Y"])
    risk: Optional[str] = Field(None, alias="Risk", description="Type of risk for work resumption", example="IncapacityForWork", enum=["IncapacityForWork", "MaternityProtection"])
    hours: Optional[int] = Field(None, alias="Hours", description="Number of hours resumed", example=20, ge=0, le=40)
    minutes: Optional[int] = Field(None, alias="Minutes", description="Number of minutes resumed", example=30, ge=0, le=60)
    days: Optional[float] = Field(None, alias="Days", description="Number of days resumed", example=3.0, ge=0, le=5)
    startdate_illness: Optional[str] = Field(None, alias="StartdateIllness", description="Start date of illness in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    comment: Optional[str] = Field(None, alias="Comment", description="Comment related to progressive work resumption", example="Partial return to work approved", min_length=0, max_length=200)

    class Config:
        populate_by_name = True


class MethodOfRemunerationDefinition(BaseModel):
    exist: str = Field(alias="Exist", description="Indicates if a specific method of remuneration applies", example="Y", min_length=1, max_length=1, enum=["N", "Y"])
    remuneration: Optional[str] = Field(None, alias="Remuneration", description="Type of remuneration method", example="Commission", enum=["Commission", "Piece", "ServiceVouchers"])
    payment: Optional[str] = Field(None, alias="Payment", description="Type of payment", example="Fixed", enum=["Fixed", "Variable", "Mixed"])

    class Config:
        populate_by_name = True


class InternationalEmploymentDefinition(BaseModel):
    exist: str = Field(alias="Exist", description="Indicates if international employment applies", example="Y", min_length=1, max_length=1, enum=["N", "Y"])
    kind: Optional[str] = Field(None, alias="Kind", description="Type of international employment", example="SecondmentFrom", enum=["SecondmentFrom", "SalarySplit", "FrontierWorker", "SecondmentTo"])
    border_country: Optional[str] = Field(None, alias="BorderCountry", description="Border country code", example="00111", min_length=5, max_length=5, pattern=r'^[0-9]*$')

    class Config:
        populate_by_name = True


class UsingData(BaseModel):
    using_joint_commission_nbr: Optional[str] = Field(None, alias="UsingJointCommissionNbr", description="Using joint commission number", example="123", min_length=3, max_length=3, pattern=r'^[0-9,.]*$')
    using_employer_name: Optional[str] = Field(None, alias="UsingEmployerName", description="Using employer name", example="Acme Corp", max_length=40)
    using_employer_company_id: Optional[float] = Field(None, alias="UsingEmployerCompanyID", description="Using employer company ID", example=1234567890.0, ge=0, le=9999999999)
    using_street: Optional[str] = Field(None, alias="UsingStreet", description="Using street", example="Main Street", max_length=100)
    using_house_number: Optional[str] = Field(None, alias="UsingHouseNumber", description="Using house number", example="123", max_length=10)
    using_post_box: Optional[str] = Field(None, alias="UsingPostBox", description="Using post box", example="12345", max_length=5)
    using_zip_code: Optional[str] = Field(None, alias="UsingZIPCode", description="Using ZIP code", example="1000", max_length=12)
    using_city: Optional[str] = Field(None, alias="UsingCity", description="Using city", example="Brussels", max_length=30)
    using_country: Optional[str] = Field("00150", alias="UsingCountry", description="Using country code", example="00150", min_length=5, max_length=5, pattern=r'^[0-9]*$')

    class Config:
        populate_by_name = True


class ClsDimona(BaseModel):
    dimona_period_id: Optional[float] = Field(None, alias="DimonaPeriodId", description="DIMONA period ID", example=123456789.0, ge=0, le=999999999999)
    starting_date: str = Field(alias="StartingDate", description="Starting date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    ending_date: Optional[str] = Field(None, alias="EndingDate", description="Ending date in YYYYMMDD format", example="20251231", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    starting_hour: Optional[str] = Field(None, alias="StartingHour", description="Starting hour", example="080000000000", min_length=12, max_length=12, pattern=r'^[0-9]*$')
    ending_hour: Optional[str] = Field(None, alias="EndingHour", description="Ending hour", example="170000000000", min_length=12, max_length=12, pattern=r'^[0-9]*$')
    starting_hour2: Optional[str] = Field(None, alias="StartingHour2", description="Starting hour 2", example="080000000000", min_length=12, max_length=12, pattern=r'^[0-9]*$')
    ending_hour2: Optional[str] = Field(None, alias="EndingHour2", description="Ending hour 2", example="170000000000", min_length=12, max_length=12, pattern=r'^[0-9]*$')
    first_month_c32a_nbr: Optional[float] = Field(None, alias="FirstMonthC32ANbr", description="First month C32A number", example=123456789.0, ge=0, le=999999999999)
    next_month_c32a_nbr: Optional[float] = Field(None, alias="NextMonthC32ANbr", description="Next month C32A number", example=123456789.0, ge=0, le=999999999999)
    planned_hours_nbr: Optional[int] = Field(None, alias="PlannedHoursNbr", description="Planned hours number", example=40, ge=0, le=999)
    receipt: Optional[float] = Field(None, alias="Receipt", description="Receipt", example=123456789.0, ge=0, le=999999999999)
    joint_commission_nbr: Optional[str] = Field(None, alias="JointCommissionNbr", description="Joint commission number", example="123456", min_length=3, max_length=6, pattern=r'^[0-9,.]*$')
    worker_type: Optional[str] = Field(None, alias="WorkerType", description="Worker type", example="EMP", min_length=3, max_length=3)
    last_action: Optional[str] = Field(None, alias="LastAction", description="Last action", example="A", min_length=1, max_length=1)
    exceeding_hours_nbr: Optional[int] = Field(None, alias="ExceedingHoursNbr", description="Exceeding hours number", example=5, ge=0, le=999)
    quota_exceeded: Optional[ResetEnum] = Field(None, alias="QuotaExceeded", description="Quota exceeded", example="N")
    belated: Optional[ResetEnum] = Field(None, alias="Belated", description="Belated", example="N")
    status: Optional[DimonaStatusEnum] = Field(None, alias="Status", description="DIMONA status", example="OK")
    error: Optional[str] = Field(None, alias="Error", description="Error message", example="")

    using_data: Optional[UsingData] = Field(None, alias="UsingData", description="Using data")

    class Config:
        populate_by_name = True



# Pydantic schemas for API requests
class ContractCreate(BaseModel):
    """Schema for creating a new contract entry."""

    start_date: str = Field(alias="Startdate", description="Contract start date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    end_date: Optional[str] = Field(None, alias="Enddate", description="Contract end date in YYYYMMDD format", example="20251231", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    employment_status: Optional[ContractTypeEnum] = Field(None, alias="EmploymentStatus", description="Employment status type", example="Employee")
    contract: Optional[ContractEnum] = Field(None, alias="Contract", description="Contract type code", example="Usually")
    cat_rsz: Optional[str] = Field(None, alias="CatRSZ", description="Social security category code", example="123", min_length=3, max_length=3, pattern=r'^[0-9]*$')
    par_com: Optional[str] = Field(None, alias="ParCom", description="Parity committee code", example="123.45", min_length=3, max_length=10, pattern=r'^[0-9. ]*$')
    document_c78: Optional[DocumentC78Enum] = Field(None, alias="DocumentC78", description="Document C78 status", example="Nihil")
    code_c98: Optional[ResetEnum] = Field(None, alias="CodeC98", description="Code C98 flag", example="N")
    code_c131a: Optional[ResetEnum] = Field(None, alias="CodeC131A", description="Code C131A flag", example="N")
    code_c131a_request_ft: Optional[ResetEnum] = Field(None, alias="CodeC131ARequestFT", description="Code C131A request full-time flag", example="N")
    code_c131: Optional[ResetEnum] = Field(None, alias="CodeC131", description="Code C131 flag", example="N")
    risk: Optional[str] = Field(None, alias="Risk", description="Risk code", example="RISK001", max_length=10)
    social_security_card: Optional[str] = Field(None, alias="SocialSecurityCard", description="Social security card number", example="123456789012345", max_length=15)
    work_permit: Optional[str] = Field(None, alias="WorkPermit", description="Work permit number", example="WP123456789", max_length=15)
    date_in_service: Optional[str] = Field(None, alias="DateInService", description="Date in service in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    seniority: Optional[str] = Field(None, alias="Seniority", description="Seniority date in YYYYMMDD format", example="20200101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    date_professional_experience: Optional[str] = Field(None, alias="DateProfessionalExperience", description="Date professional experience in YYYYMMDD format", example="20200101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    scale_salary_seniority: Optional[str] = Field(None, alias="ScaleSalarySeniority", description="Scale salary seniority date in YYYYMMDD format", example="20200101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    start_probation_period: Optional[str] = Field(None, alias="StartProbationPeriod", description="Start probation period in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    end_probation_period: Optional[str] = Field(None, alias="EndProbationPeriod", description="End probation period in YYYYMMDD format", example="20250401", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    fixed_term: Optional[ResetEnum] = Field(None, alias="FixedTerm", description="Fixed term flag", example="N")
    end_fixed_term: Optional[str] = Field(None, alias="EndFixedTerm", description="End fixed term in YYYYMMDD format", example="20251231", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    date_out_service: Optional[str] = Field(None, alias="DateOutService", description="Date out service in YYYYMMDD format", example="20251231", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    reason_out: Optional[str] = Field(None, alias="ReasonOut", description="Reason out", example="Resignation")
    working_time: Optional[WorkingTimeEnum] = Field(None, alias="WorkingTime", description="Working time type", example="Fulltime")
    spec_working_time: Optional[SpecWorkingTimeEnum] = Field(None, alias="SpecWorkingTime", description="Special working time type", example="Regular")
    schedule: Optional[str] = Field(None, alias="Schedule", description="Schedule code", example="SCH1", max_length=4)
    weekhours_worker: Optional[float] = Field(None, alias="WeekhoursWorker", description="Weekly hours for worker", example=40.0, ge=1, le=50)
    weekhours_employer: Optional[float] = Field(None, alias="WeekhoursEmployer", description="Weekly hours for employer", example=40.0, ge=1, le=50)
    weekhours_worker_average: Optional[float] = Field(None, alias="WeekhoursWorkerAverage", description="Weekly hours worker average", example=40.0, ge=1, le=50)
    weekhours_employer_average: Optional[float] = Field(None, alias="WeekhoursEmployerAverage", description="Weekly hours employer average", example=40.0, ge=1, le=50)
    weekhours_worker_effective: Optional[float] = Field(None, alias="WeekhoursWorkerEffective", description="Weekly hours worker effective", example=40.0, ge=1, le=50)
    weekhours_employer_effective: Optional[float] = Field(None, alias="WeekhoursEmployerEffective", description="Weekly hours employer effective", example=40.0, ge=1, le=50)
    days_week: Optional[float] = Field(None, alias="DaysWeek", description="Days per week", example=5.0)
    days_week_ft: Optional[float] = Field(None, alias="DaysWeekFT", description="Days per week full time", example=5.0)
    reducing_working_kind: Optional[ReducingWorkingKindEnum] = Field(None, alias="ReducingWorkingKind", description="Reducing working kind", example="Nihil")
    reducing_working_kind_days: Optional[float] = Field(None, alias="ReducingWorkingKindDays", description="Reducing working kind days", example=0.0)
    reducing_working_kind_hours: Optional[float] = Field(None, alias="ReducingWorkingKindHours", description="Reducing working kind hours", example=0.0)
    part_time_return_towork: Optional[str] = Field(None, alias="PartTimeReturnTowork", description="Part time return to work", example="PT01", max_length=4)
    asr_schedule: Optional[str] = Field(None, alias="ASRSchedule", description="ASR schedule", example="AS", max_length=2)
    proff_cat: Optional[str] = Field(None, alias="ProffCat", description="Professional category", example="PROF001", max_length=10)
    function: Optional[str] = Field(None, alias="Function", description="Function code", example="FUNC001", max_length=10)
    function_description: Optional[str] = Field(None, alias="FunctionDescription", description="Function description", example="Software Developer", max_length=50)
    social_balance_joblevel: Optional[SocialBalanceJoblevelEnum] = Field(None, alias="SocialBalanceJoblevel", description="Social balance job level", example="ExecutiveStaff")
    office: Optional[int] = Field(None, alias="Office", description="Office code", example=1)
    division: Optional[str] = Field(None, alias="Division", description="Division code", example="DIV001", max_length=10)
    invoicing_division: Optional[str] = Field(None, alias="InvoicingDivision", description="Invoicing division code", example="INV001", max_length=10)
    cost_centre: Optional[str] = Field(None, alias="CostCentre", description="Cost centre code", example="CC001", max_length=15)
    scale_salary_prisma: Optional[ResetEnum] = Field(None, alias="ScaleSalaryPrisma", description="Scale salary prisma", example="N")
    scale_salary_use: Optional[ResetEnum] = Field(None, alias="ScaleSalaryUse", description="Scale salary use", example="N")
    scale_salary_definition: Optional[str] = Field(None, alias="ScaleSalaryDefinition", description="Scale salary definition", example="SCALE001", max_length=10)
    scale_salary_category: Optional[str] = Field(None, alias="ScaleSalaryCategory", description="Scale salary category", example="CAT001", max_length=10)
    scale_salary_scale: Optional[str] = Field(None, alias="ScaleSalaryScale", description="Scale salary scale", example="SCALE_DEFINITION", max_length=100)
    exclude_for_dmfa_declaration: Optional[ResetEnum] = Field(None, alias="ExcludeForDmfaDeclaration", description="Exclude for DMFA declaration", example="N")
    agriculture_type: Optional[AgricultureTypeEnum] = Field(None, alias="AgricultureType", description="Agriculture type", example="Agriculture")
    no_dimona: Optional[ResetEnum] = Field(None, alias="NoDimona", description="No DIMONA flag", example="N")
    no_dmfa: Optional[ResetEnum] = Field(None, alias="NoDmfa", description="No DMFA flag", example="N")
    no_asrdrs: Optional[ResetEnum] = Field(None, alias="NoAsrdrs", description="No ASRDRS flag", example="N")
    security: Optional[str] = Field(None, alias="Security", description="Security code", example="SEC001", max_length=10)

    # Nested models
    career_break: Optional[CareerBreakDefinition] = Field(None, alias="CareerBreak", description="Career break definition")
    retired: Optional[RetiredDefinition] = Field(None, alias="Retired", description="Retired definition")
    protected_employee: Optional[ProtectedEmployeeDefinition] = Field(None, alias="ProtectedEmployee", description="Protected employee definition")
    sports_person: Optional[SportsPersonDefinition] = Field(None, alias="SportsPerson", description="Sports person definition")
    certain_work: Optional[CertainWorkDefinition] = Field(None, alias="CertainWork", description="Certain work definition")
    student: Optional[StudentDefinition] = Field(None, alias="Student", description="Student definition")
    progressive_work_resumption: Optional[ProgressiveWorkResumptionDefinition] = Field(None, alias="ProgressiveWorkResumption", description="Progressive work resumption definition")
    method_of_remuneration: Optional[MethodOfRemunerationDefinition] = Field(None, alias="MethodOfRemuneration", description="Method of remuneration definition")
    international_employment: Optional[InternationalEmploymentDefinition] = Field(None, alias="InternationalEmployment", description="International employment definition")
    dimona: Optional[ClsDimona] = Field(None, alias="Dimona", description="DIMONA definition")


    class Config:
        populate_by_name = True


class ContractUpdate(ContractCreate):
    """Schema for updating a contract entry."""
    # Make Startdate optional for updates
    start_date: Optional[str] = Field(None, alias="Startdate", description="Contract start date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    class Config:
        populate_by_name = True


# Pandera schema for DataFrame validation
class ContractGet(BrynQPanderaDataFrameModel):
    """Schema for validating contract data from API."""

    # Required fields
    start_date: str = pa.Field(coerce=True, nullable=False, description="Contract start date in YYYYMMDD format", alias="Startdate")

    # Optional fields - contract basic info
    worker_number: Optional[int] = pa.Field(coerce=True, nullable=False, description="Worker number reference", alias="WorkerNumber")
    end_date: Optional[str] = pa.Field(coerce=True, nullable=True, description="Contract end date in YYYYMMDD format", alias="Enddate")
    employment_status: Optional[str] = pa.Field(coerce=True, nullable=True, description="Employment status type", alias="EmploymentStatus")
    contract: Optional[str] = pa.Field(coerce=True, nullable=True, description="Contract type code", alias="Contract")
    employer: Optional[str] = pa.Field(coerce=True, nullable=True, str_length={'min_value': 0, 'max_value': 40}, description="Employer name", alias="employer")

    # Social security fields
    cat_rsz: Optional[str] = pa.Field(coerce=True, nullable=True, description="Social security category code", alias="CatRSZ")
    par_com: Optional[str] = pa.Field(coerce=True, nullable=True, description="Parity committee code", alias="ParCom")
    document_c78: Optional[str] = pa.Field(coerce=True, nullable=True, description="Document C78 status", alias="DocumentC78")
    code_c98: Optional[str] = pa.Field(coerce=True, nullable=True, description="Code C98 flag", alias="CodeC98")
    code_c131a: Optional[str] = pa.Field(coerce=True, nullable=True, description="Code C131A flag", alias="CodeC131A")
    code_c131a_request_ft: Optional[str] = pa.Field(coerce=True, nullable=True, description="Code C131A request full-time flag", alias="CodeC131ARequestFT")
    code_c131: Optional[str] = pa.Field(coerce=True, nullable=True, description="Code C131 flag", alias="CodeC131")
    risk: Optional[str] = pa.Field(coerce=True, nullable=True, description="Risk code", alias="Risk")
    social_security_card: Optional[str] = pa.Field(coerce=True, nullable=True, description="Social security card number", alias="SocialSecurityCard")
    work_permit: Optional[str] = pa.Field(coerce=True, nullable=True, description="Work permit number", alias="WorkPermit")

    # Date fields
    date_in_service: Optional[str] = pa.Field(coerce=True, nullable=True, description="Date in service in YYYYMMDD format", alias="DateInService")
    seniority: Optional[str] = pa.Field(coerce=True, nullable=True, description="Seniority date in YYYYMMDD format", alias="Seniority")
    date_professional_experience: Optional[str] = pa.Field(coerce=True, nullable=True, description="Date professional experience in YYYYMMDD format", alias="DateProfessionalExperience")
    scale_salary_seniority: Optional[str] = pa.Field(coerce=True, nullable=True, description="Scale salary seniority date in YYYYMMDD format", alias="ScaleSalarySeniority")
    start_probation_period: Optional[str] = pa.Field(coerce=True, nullable=True, description="Start probation period in YYYYMMDD format", alias="StartProbationPeriod")
    end_probation_period: Optional[str] = pa.Field(coerce=True, nullable=True, description="End probation period in YYYYMMDD format", alias="EndProbationPeriod")
    fixed_term: Optional[str] = pa.Field(coerce=True, nullable=True, description="Fixed term flag", alias="FixedTerm")
    end_fixed_term: Optional[str] = pa.Field(coerce=True, nullable=True, description="End fixed term in YYYYMMDD format", alias="EndFixedTerm")
    date_out_service: Optional[str] = pa.Field(coerce=True, nullable=True, description="Date out service in YYYYMMDD format", alias="DateOutService")
    reason_out: Optional[str] = pa.Field(coerce=True, nullable=True, description="Reason out", alias="ReasonOut")

    # Working time fields
    working_time: Optional[str] = pa.Field(coerce=True, nullable=True, description="Working time type", alias="WorkingTime")
    spec_working_time: Optional[str] = pa.Field(coerce=True, nullable=True, description="Special working time type", alias="SpecWorkingTime")
    schedule: Optional[str] = pa.Field(coerce=True, nullable=True, description="Schedule code", alias="Schedule")
    weekhours_worker: Optional[float] = pa.Field(coerce=True, nullable=True, description="Weekly hours for worker", alias="WeekhoursWorker")
    weekhours_employer: Optional[float] = pa.Field(coerce=True, nullable=True, description="Weekly hours for employer", alias="WeekhoursEmployer")
    weekhours_worker_average: Optional[float] = pa.Field(coerce=True, nullable=True, description="Weekly hours worker average", alias="WeekhoursWorkerAverage")
    weekhours_employer_average: Optional[float] = pa.Field(coerce=True, nullable=True, description="Weekly hours employer average", alias="WeekhoursEmployerAverage")
    weekhours_worker_effective: Optional[float] = pa.Field(coerce=True, nullable=True, description="Weekly hours worker effective", alias="WeekhoursWorkerEffective")
    weekhours_employer_effective: Optional[float] = pa.Field(coerce=True, nullable=True, description="Weekly hours employer effective", alias="WeekhoursEmployerEffective")
    days_week: Optional[float] = pa.Field(coerce=True, nullable=True, description="Days per week", alias="DaysWeek")
    days_week_ft: Optional[float] = pa.Field(coerce=True, nullable=True, description="Days per week full time", alias="DaysWeekFT")
    reducing_working_kind: Optional[str] = pa.Field(coerce=True, nullable=True, description="Reducing working kind", alias="ReducingWorkingKind")
    reducing_working_kind_days: Optional[float] = pa.Field(coerce=True, nullable=True, description="Reducing working kind days", alias="ReducingWorkingKindDays")
    reducing_working_kind_hours: Optional[float] = pa.Field(coerce=True, nullable=True, description="Reducing working kind hours", alias="ReducingWorkingKindHours")
    part_time_return_towork: Optional[str] = pa.Field(coerce=True, nullable=True, description="Part time return to work", alias="PartTimeReturnTowork")
    asr_schedule: Optional[str] = pa.Field(coerce=True, nullable=True, description="ASR schedule", alias="ASRSchedule")

    # Job and function fields
    proff_cat: Optional[str] = pa.Field(coerce=True, nullable=True, description="Professional category", alias="ProffCat")
    function: Optional[str] = pa.Field(coerce=True, nullable=True, description="Function code", alias="Function")
    function_description: Optional[str] = pa.Field(coerce=True, nullable=True, description="Function description", alias="FunctionDescription")
    social_balance_joblevel: Optional[str] = pa.Field(coerce=True, nullable=True, description="Social balance job level", alias="SocialBalanceJoblevel")
    office: Optional[int] = pa.Field(coerce=True, nullable=True, description="Office code", alias="Office")
    division: Optional[str] = pa.Field(coerce=True, nullable=True, description="Division code", alias="Division")
    invoicing_division: Optional[str] = pa.Field(coerce=True, nullable=True, description="Invoicing division code", alias="InvoicingDivision")
    cost_centre: Optional[str] = pa.Field(coerce=True, nullable=True, description="Cost centre code", alias="CostCentre")

    # Salary scale fields
    scale_salary_prisma: Optional[str] = pa.Field(coerce=True, nullable=True, description="Scale salary prisma", alias="ScaleSalaryPrisma")
    scale_salary_use: Optional[str] = pa.Field(coerce=True, nullable=True, description="Scale salary use", alias="ScaleSalaryUse")
    scale_salary_definition: Optional[str] = pa.Field(coerce=True, nullable=True, description="Scale salary definition", alias="ScaleSalaryDefinition")
    scale_salary_category: Optional[str] = pa.Field(coerce=True, nullable=True, description="Scale salary category", alias="ScaleSalaryCategory")
    scale_salary_scale: Optional[str] = pa.Field(coerce=True, nullable=True, description="Scale salary scale", alias="ScaleSalaryScale")

    # Other fields
    agriculture_type: Optional[str] = pa.Field(coerce=True, nullable=True, description="Agriculture type", alias="AgricultureType")
    no_dimona: Optional[ResetEnum] = pa.Field(coerce=True, nullable=True, description="No DIMONA flag", alias="NoDimona")
    no_dmfa: Optional[str] = pa.Field(coerce=True, nullable=True, description="No DMFA flag", alias="NoDMFA")
    no_asrdrs: Optional[str] = pa.Field(coerce=True, nullable=True, description="No ASRDRS flag", alias="NoASRDRS")
    security: Optional[str] = pa.Field(coerce=True, nullable=True, description="Security code", alias="Security")
    exclude_for_dmfa_declaration: Optional[str] = pa.Field(coerce=True, nullable=True, description="Exclude for DMFA declaration", alias="ExcludeForDmfaDeclaration")

    # Nested fields - SectorSeniority (normalized)
    sector_seniority: Optional[str] = pa.Field(coerce=True, nullable=True, description="Sector seniority", alias="SectorSeniority")

    # Nested fields - Student (normalized)
    student_exist: Optional[str] = pa.Field(coerce=True, nullable=True, description="Student exist", alias="Student__Exist")
    student_solidarity_contribution: Optional[str] = pa.Field(coerce=True, nullable=True, description="Student solidarity contribution", alias="Student__SolidarityContribution")

    # Nested fields - SalaryCompositions (keep as single field)
    salary_compositions: Optional[str] = pa.Field(coerce=True, nullable=True, description="Salary compositions data", alias="SalaryCompositions")

    # Nested fields - SubstituteContract (normalized)
    substitute_contract: Optional[str] = pa.Field(coerce=True, nullable=True, description="Substitute contract", alias="SubstituteContract")

    # Nested fields - CareerBreak (normalized)
    career_break_exist: Optional[str] = pa.Field(coerce=True, nullable=True, description="Career break exist", alias="CareerBreak__Exist")
    career_break_kind: Optional[str] = pa.Field(coerce=True, nullable=True, description="Career break kind", alias="CareerBreak__Kind")
    career_break_reason: Optional[str] = pa.Field(coerce=True, nullable=True, description="Career break reason", alias="CareerBreak__Reason")
    career_break_originally_contract_type: Optional[str] = pa.Field(coerce=True, nullable=True, description="Career break originally contract type", alias="CareerBreak__OriginallyContractType")
    career_break_weekhours_worker_before: Optional[float] = pa.Field(coerce=True, nullable=True, description="Career break weekhours worker before", alias="CareerBreak__WeekhoursWorkerBefore")
    career_break_weekhours_employer_before: Optional[float] = pa.Field(coerce=True, nullable=True, description="Career break weekhours employer before", alias="CareerBreak__WeekhoursEmployerBefore")

    # Nested fields - Retired (normalized)
    retired_exist: Optional[str] = pa.Field(coerce=True, nullable=True, description="Retired exist", alias="Retired__Exist")
    retired_kind: Optional[str] = pa.Field(coerce=True, nullable=True, description="Retired kind", alias="Retired__Kind")
    retired_date_retired: Optional[str] = pa.Field(coerce=True, nullable=True, description="Retired date retired", alias="Retired__DateRetired")
    retired_apply_collecting_2nd_pension_pillar: Optional[str] = pa.Field(coerce=True, nullable=True, description="Retired apply collecting 2nd pension pillar", alias="Retired__ApplyCollecting2ndPensionPillar")
    retired_retired_type: Optional[str] = pa.Field(coerce=True, nullable=True, description="Retired retired type", alias="Retired__RetiredType")

    # Nested fields - ProtectedEmployee (normalized)
    protected_employee_exist: Optional[str] = pa.Field(coerce=True, nullable=True, description="Protected employee exist", alias="ProtectedEmployee__Exist")
    protected_employee_reason: Optional[str] = pa.Field(coerce=True, nullable=True, description="Protected employee reason", alias="ProtectedEmployee__Reason")
    protected_employee_start_date: Optional[str] = pa.Field(coerce=True, nullable=True, description="Protected employee start date", alias="ProtectedEmployee__Startdate")
    protected_employee_end_date: Optional[str] = pa.Field(coerce=True, nullable=True, description="Protected employee end date", alias="ProtectedEmployee__Enddate")

    # Nested fields - Sportsperson (normalized)
    sportsperson_exist: Optional[str] = pa.Field(coerce=True, nullable=True, description="Sportsperson exist", alias="Sportsperson__Exist")
    sportsperson_recognized_foreign_sportsperson: Optional[str] = pa.Field(coerce=True, nullable=True, description="Sportsperson recognized foreign sportsperson", alias="Sportsperson__RecognizedForeignSportsperson")
    sportsperson_opportunity_contract: Optional[str] = pa.Field(coerce=True, nullable=True, description="Sportsperson opportunity contract", alias="Sportsperson__OpportunityContract")

    # Nested fields - CertainWork (normalized)
    certain_work_exist: Optional[str] = pa.Field(coerce=True, nullable=True, description="Certain work exist", alias="CertainWork__Exist")
    certain_work_description: Optional[str] = pa.Field(coerce=True, nullable=True, description="Certain work description", alias="CertainWork__Description")

    # Nested fields - MethodOfRemuneration (normalized)
    method_of_remuneration_exist: Optional[str] = pa.Field(coerce=True, nullable=True, description="Method of remuneration exist", alias="MethodOfRemuneration__Exist")
    method_of_remuneration_remuneration: Optional[str] = pa.Field(coerce=True, nullable=True, description="Method of remuneration remuneration", alias="MethodOfRemuneration__Remuneration")
    method_of_remuneration_payment: Optional[str] = pa.Field(coerce=True, nullable=True, description="Method of remuneration payment", alias="MethodOfRemuneration__Payment")

    # Nested fields - InternationalEmployment (normalized)
    international_employment_exist: Optional[str] = pa.Field(coerce=True, nullable=True, description="International employment exist", alias="InternationalEmployment__Exist")
    international_employment_kind: Optional[str] = pa.Field(coerce=True, nullable=True, description="International employment kind", alias="InternationalEmployment__Kind")
    international_employment_border_country: Optional[str] = pa.Field(coerce=True, nullable=True, description="International employment border country", alias="InternationalEmployment__BorderCountry")

    # Nested fields - Dimona (normalized)
    dimona_dimona_period_id: Optional[float] = pa.Field(coerce=True, nullable=True, description="Dimona period ID", alias="Dimona__DimonaPeriodId")
    dimona_starting_date: Optional[str] = pa.Field(coerce=True, nullable=True, description="Dimona starting date", alias="Dimona__StartingDate")
    dimona_ending_date: Optional[str] = pa.Field(coerce=True, nullable=True, description="Dimona ending date", alias="Dimona__EndingDate")
    dimona_starting_hour: Optional[str] = pa.Field(coerce=True, nullable=True, description="Dimona starting hour", alias="Dimona__StartingHour")
    dimona_ending_hour: Optional[str] = pa.Field(coerce=True, nullable=True, description="Dimona ending hour", alias="Dimona__EndingHour")
    dimona_starting_hour2: Optional[str] = pa.Field(coerce=True, nullable=True, description="Dimona starting hour 2", alias="Dimona__StartingHour2")
    dimona_ending_hour2: Optional[str] = pa.Field(coerce=True, nullable=True, description="Dimona ending hour 2", alias="Dimona__EndingHour2")
    dimona_first_month_c32a_nbr: Optional[float] = pa.Field(coerce=True, nullable=True, description="Dimona first month C32A number", alias="Dimona__FirstMonthC32ANbr")
    dimona_next_month_c32a_nbr: Optional[float] = pa.Field(coerce=True, nullable=True, description="Dimona next month C32A number", alias="Dimona__NextMonthC32ANbr")
    dimona_planned_hours_nbr: Optional[int] = pa.Field(coerce=True, nullable=True, description="Dimona planned hours number", alias="Dimona__PlannedHoursNbr")
    dimona_receipt: Optional[float] = pa.Field(coerce=True, nullable=True, description="Dimona receipt", alias="Dimona__Receipt")
    dimona_joint_commission_nbr: Optional[str] = pa.Field(coerce=True, nullable=True, description="Dimona joint commission number", alias="Dimona__JointCommissionNbr")
    dimona_worker_type: Optional[str] = pa.Field(coerce=True, nullable=True, description="Dimona worker type", alias="Dimona__WorkerType")
    dimona_last_action: Optional[str] = pa.Field(coerce=True, nullable=True, description="Dimona last action", alias="Dimona__LastAction")
    dimona_exceeding_hours_nbr: Optional[int] = pa.Field(coerce=True, nullable=True, description="Dimona exceeding hours number", alias="Dimona__ExceedingHoursNbr")
    dimona_quota_exceeded: Optional[str] = pa.Field(coerce=True, nullable=True, description="Dimona quota exceeded", alias="Dimona__QuotaExceeded")
    dimona_belated: Optional[str] = pa.Field(coerce=True, nullable=True, description="Dimona belated", alias="Dimona__Belated")
    dimona_status: Optional[str] = pa.Field(coerce=True, nullable=True, description="Dimona status", alias="Dimona__Status")
    dimona_error: Optional[str] = pa.Field(coerce=True, nullable=True, description="Dimona error", alias="Dimona__Error")

    # Nested fields - ProgressiveWorkResumption (normalized)
    progressive_work_resumption_progressive_work_resumption: Optional[str] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption", alias="ProgressiveWorkResumption__ProgressiveWorkResumption")
    progressive_work_resumption_exist: Optional[str] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption exist", alias="ProgressiveWorkResumption__Exist")
    progressive_work_resumption_risk: Optional[str] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption risk", alias="ProgressiveWorkResumption__Risk")
    progressive_work_resumption_hours: Optional[float] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption hours", alias="ProgressiveWorkResumption__Hours")
    progressive_work_resumption_minutes: Optional[float] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption minutes", alias="ProgressiveWorkResumption__Minutes")
    progressive_work_resumption_days: Optional[float] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption days", alias="ProgressiveWorkResumption__Days")
    progressive_work_resumption_start_date_illness: Optional[str] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption start date illness", alias="ProgressiveWorkResumption__StartdateIllness")
    progressive_work_resumption_comment: Optional[str] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption comment", alias="ProgressiveWorkResumption__Comment")
    progressive_work_resumption_start_date: Optional[str] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption start date", alias="ProgressiveWorkResumption__StartDate")
    progressive_work_resumption_end_date: Optional[str] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption end date", alias="ProgressiveWorkResumption__EndDate")
    progressive_work_resumption_percentage: Optional[float] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption percentage", alias="ProgressiveWorkResumption__Percentage")

    # Social security
    cat_rsz: Optional[str] = pa.Field(coerce=True, nullable=True, description="Social security category code", alias="CatRSZ")
    par_com: Optional[str] = pa.Field(coerce=True, nullable=True, description="Parity committee code", alias="ParCom")
    document_c78: Optional[str] = pa.Field(coerce=True, nullable=True, description="Document C78 status", alias="DocumentC78")
    code_c98: Optional[str] = pa.Field(coerce=True, nullable=True, description="Code C98 flag", alias="CodeC98")
    code_c131a: Optional[str] = pa.Field(coerce=True, nullable=True, description="Code C131A flag", alias="CodeC131A")
    code_c131a_request_ft: Optional[str] = pa.Field(coerce=True, nullable=True, description="Code C131A request full-time flag", alias="CodeC131ARequestFT")
    code_c131: Optional[str] = pa.Field(coerce=True, nullable=True, description="Code C131 flag", alias="CodeC131")
    risk: Optional[str] = pa.Field(coerce=True, nullable=True, description="Risk code", alias="Risk")
    social_security_card: Optional[str] = pa.Field(coerce=True, nullable=True, description="Social security card number", alias="SocialSecurityCard")
    work_permit: Optional[str] = pa.Field(coerce=True, nullable=True, description="Work permit number", alias="WorkPermit")

    # Dates
    date_in_service: Optional[str] = pa.Field(coerce=True, nullable=True, description="Date in service in YYYYMMDD format", alias="DateInService")
    seniority: Optional[str] = pa.Field(coerce=True, nullable=True, description="Seniority date in YYYYMMDD format", alias="Seniority")
    date_professional_experience: Optional[str] = pa.Field(coerce=True, nullable=True, description="Date professional experience in YYYYMMDD format", alias="DateProfessionalExperience")
    scale_salary_seniority: Optional[str] = pa.Field(coerce=True, nullable=True, description="Scale salary seniority date in YYYYMMDD format", alias="ScaleSalarySeniority")
    start_probation_period: Optional[str] = pa.Field(coerce=True, nullable=True, description="Start probation period in YYYYMMDD format", alias="StartProbationPeriod")
    end_probation_period: Optional[str] = pa.Field(coerce=True, nullable=True, description="End probation period in YYYYMMDD format", alias="EndProbationPeriod")
    end_fixed_term: Optional[str] = pa.Field(coerce=True, nullable=True, description="End fixed term in YYYYMMDD format", alias="EndFixedTerm")
    date_out_service: Optional[str] = pa.Field(coerce=True, nullable=True, description="Date out service in YYYYMMDD format", alias="DateOutService")
    reason_out: Optional[str] = pa.Field(coerce=True, nullable=True, description="Reason out", alias="ReasonOut")

    # Working time
    working_time: Optional[str] = pa.Field(coerce=True, nullable=True, description="Working time type", alias="WorkingTime")
    spec_working_time: Optional[str] = pa.Field(coerce=True, nullable=True, description="Special working time type", alias="SpecWorkingTime")
    schedule: Optional[str] = pa.Field(coerce=True, nullable=True, description="Schedule code", alias="Schedule")
    weekhours_worker: Optional[float] = pa.Field(coerce=True, nullable=True, description="Weekly hours for worker", alias="WeekhoursWorker")
    weekhours_employer: Optional[float] = pa.Field(coerce=True, nullable=True, description="Weekly hours for employer", alias="WeekhoursEmployer")
    weekhours_worker_average: Optional[float] = pa.Field(coerce=True, nullable=True, description="Weekly hours worker average", alias="WeekhoursWorkerAverage")
    weekhours_employer_average: Optional[float] = pa.Field(coerce=True, nullable=True, description="Weekly hours employer average", alias="WeekhoursEmployerAverage")
    weekhours_worker_effective: Optional[float] = pa.Field(coerce=True, nullable=True, description="Weekly hours worker effective", alias="WeekhoursWorkerEffective")
    weekhours_employer_effective: Optional[float] = pa.Field(coerce=True, nullable=True, description="Weekly hours employer effective", alias="WeekhoursEmployerEffective")
    days_week: Optional[float] = pa.Field(coerce=True, nullable=True, description="Days per week", alias="DaysWeek")
    days_week_ft: Optional[float] = pa.Field(coerce=True, nullable=True, description="Days per week full time", alias="DaysWeekFT")
    reducing_working_kind: Optional[str] = pa.Field(coerce=True, nullable=True, description="Reducing working kind", alias="ReducingWorkingKind")
    reducing_working_kind_days: Optional[float] = pa.Field(coerce=True, nullable=True, description="Reducing working kind days", alias="ReducingWorkingKindDays")
    reducing_working_kind_hours: Optional[float] = pa.Field(coerce=True, nullable=True, description="Reducing working kind hours", alias="ReducingWorkingKindHours")
    part_time_return_towork: Optional[str] = pa.Field(coerce=True, nullable=True, description="Part time return to work", alias="PartTimeReturnTowork")
    asr_schedule: Optional[str] = pa.Field(coerce=True, nullable=True, description="ASR schedule", alias="ASRSchedule")

    # Function and organization
    proff_cat: Optional[str] = pa.Field(coerce=True, nullable=True, description="Professional category", alias="ProffCat")
    function: Optional[str] = pa.Field(coerce=True, nullable=True, description="Function code", alias="Function")
    function_description: Optional[str] = pa.Field(coerce=True, nullable=True, description="Function description", alias="FunctionDescription")
    social_balance_joblevel: Optional[str] = pa.Field(coerce=True, nullable=True, description="Social balance job level", alias="SocialBalanceJoblevel")
    office: Optional[int] = pa.Field(coerce=True, nullable=True, description="Office code", alias="Office")
    division: Optional[str] = pa.Field(coerce=True, nullable=True, description="Division code", alias="Division")
    invoicing_division: Optional[str] = pa.Field(coerce=True, nullable=True, description="Invoicing division code", alias="InvoicingDivision")
    cost_centre: Optional[str] = pa.Field(coerce=True, nullable=True, description="Cost centre code", alias="CostCentre")

    # Salary and scales
    scale_salary_prisma: Optional[str] = pa.Field(coerce=True, nullable=True, description="Scale salary prisma", alias="ScaleSalaryPrisma")
    scale_salary_use: Optional[str] = pa.Field(coerce=True, nullable=True, description="Scale salary use", alias="ScaleSalaryUse")
    scale_salary_definition: Optional[str] = pa.Field(coerce=True, nullable=True, description="Scale salary definition", alias="ScaleSalaryDefinition")
    scale_salary_category: Optional[str] = pa.Field(coerce=True, nullable=True, description="Scale salary category", alias="ScaleSalaryCategory")
    scale_salary_scale: Optional[str] = pa.Field(coerce=True, nullable=True, description="Scale salary scale", alias="ScaleSalaryScale")

    # Flags
    fixed_term: Optional[str] = pa.Field(coerce=True, nullable=True, description="Fixed term flag", alias="FixedTerm")
    exclude_for_dmfa_declaration: Optional[str] = pa.Field(coerce=True, nullable=True, description="Exclude for DMFA declaration", alias="ExcludeForDmfaDeclaration")
    agriculture_type: Optional[str] = pa.Field(coerce=True, nullable=True, description="Agriculture type", alias="AgricultureType")
    no_dimona: Optional[str] = pa.Field(coerce=True, nullable=True, description="No DIMONA flag", alias="NoDimona")
    no_dmfa: Optional[str] = pa.Field(coerce=True, nullable=True, description="No DMFA flag", alias="NoDmfa")
    no_asrdrs: Optional[str] = pa.Field(coerce=True, nullable=True, description="No ASRDRS flag", alias="NoAsrdrs")
    security: Optional[str] = pa.Field(coerce=True, nullable=True, description="Security code", alias="Security")

    class _Annotation:
        primary_key = "worker_number"
