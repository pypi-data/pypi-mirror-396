from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum
from brynq_sdk_functions import BrynQPanderaDataFrameModel
import pandera as pa


class DocumentTypeEnum(str, Enum):
    """Document type codes defined in Prisma"""
    ASR_INFORMATION_SHEET = "ASR_informationSheet"
    ASR_REINSTATEMENT = "ASR_reinstatement"
    ASR_C32_EMPLOYER_CONTROL_CARD = "ASR_C32employerControlCard"
    ASR_C131B = "ASR_C131B"
    ASR_TEMPORARY_UNEMPLOYMENT = "ASR_TemporaryUnemployment"
    ASR_C32_EMPLOYER_BENEFIT_REQUEST = "ASR_C32employerBenefitRequest"
    ASR_C131A = "ASR_C131A"
    ASR_FIRST_DAY_OF_UNEMPLOYMENT = "ASR_FirstDayOfUnemployment"
    ASR_PROGRESSIVE_REINSTATEMENT = "ASR_progressiveReinstatement"
    SALARY_SLIP = "SalarySlip"
    ORDER_LIST_PAYMENTS = "OrderListPayments"
    SUMMARY_PAYMENT = "SummaryPayment"
    COINS_DISTRIBUTION = "CoinsDistribution"
    ELECTRONIC_PAYMENTS = "ElectronicPayments"
    INVOICE = "Invoice"
    PERFORMANCE_STATE = "Performancestate"
    ACCOUNTING_MOVEMENTS = "AccountingMovements"
    PAYROLL_STATEMENT_BY_COSTCENTRE = "PayrollStatementByCostcentre"
    WAGE_CHARGE = "WageCharge"
    VACATION_CERTIFICATE = "VacationCertificate"
    CERTIFICATE_FISCAL_EXEMPTION = "CertificateFiscalExemption"
    INDIVIDUAL_ACCOUNT = "IndividualAccount"
    SOCIAL_BALANCE = "SocialBalance"
    PERFORMANCE_STATE_TRANSPORT = "PerformanceStateTransport"
    TOTALS_PER_PAYCODE = "TotalsPerPaycode"
    OVERVIEW_MEAL_VOUCHERS = "OverviewMealVouchers"
    EMPLOYMENT_CERTIFICATE = "EmploymentCertificate"
    EMPLOYEE_SHEET = "EmployeeSheet"
    C103_YOUTH_VACATION = "C103YouthVacation"
    SALARY_SLIP_FISHERMAN = "SalarySlipFisherman"
    LIST_PRESTATIONS_TRANSPORT = "ListPrestationsTransport"
    LIST_NEGATIVE_SALARY_CALCULATIONS = "ListNegativeSalaryCalculations"
    CALCULATE_COST = "CalculateCost"
    LETTER_PAYMENT_EMPLOYER = "LetterPaymentEmployer"
    LIST_CALCULATED_WAGE_ATTACHMENTS = "ListCalculatedWageAttachments"
    C4 = "C4"
    DETAIL_FEES = "DetailFees"
    MISSING_VACATION_CERTIFICATES = "MissingVacationCertificates"
    LIST_OF_COMPANY_CARS = "ListOfCompanyCars"
    C103_SENIOR_VACATION = "C103SeniorVacation"
    C98 = "C98"
    BANKFILE = "Bankfile"
    BELCOTAX_SHEETS = "BelcotaxSheets"
    UNEMPLOYMENT_FUND = "UnemploymentFund"
    NOTICE_TEMP_UNEMPLOYMENT = "NoticeTempUnemployment"
    LETTER_HEADQUARTERS = "LetterHeadquarters"
    C106A_CORONA = "C106ACorona"
    LIST_OPEN_INVOICES = "ListOpenInvoices"
    PAYMENT_REMINDERS = "PaymentReminders"
    LETTER_DOMICILIATION = "LetterDomiciliation"
    REMINDERS_PT = "RemindersPT"
    REMINDERS_NSSO = "RemindersNSSO"
    EXTRA = "Extra"


class LanguageEnum(str, Enum):
    """Language codes supported in Prisma"""
    DUTCH = "N"     # Nederlands
    FRENCH = "F"    # Français
    GERMAN = "D"    # Deutsch
    ENGLISH = "E"   # English


class DocumentModel(BaseModel):
    """Model for document uploads"""
    filename: str = Field(..., description="The name of the file, with the extension", alias="Filename")
    publication_date: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', description="The date associated with the document in Prisma", alias="PublicationDate")
    document_type: str = Field(..., description="The document type code defined in Prisma", alias="DocumentType")
    worker: Optional[int] = Field(None, description="The worker ID as an integer", alias="Worker")
    month: int = Field(..., ge=1, le=12, description="The month the document relates to", alias="Month")
    year: int = Field(..., description="The year the document relates to", alias="Year")
    language: Optional[LanguageEnum] = Field(None, description="The language of the document (N=Dutch, F=French, D=German, E=English)", alias="Language")
    document: str = Field(..., description="Base64 representation of the document's bytestream", alias="Document")
    size: Optional[int] = Field(None, description="Size of the document in bytes", alias="Size")

    # For upload, DocumentID is not needed, but for retrieval it's included
    document_id: Optional[int] = Field(None, description="The unique identifier of the document in Prisma", alias="DocumentID")


class DocumentListing(BaseModel):
    """Model for document listing responses"""
    documents: List[DocumentModel] = Field(..., description="List of documents", alias="Documents")

class DocumentGet(BrynQPanderaDataFrameModel):
    """Model for document retrieval responses"""
    document_id: int = pa.Field(coerce=True, nullable=False, description="The unique identifier of the document in Prisma", alias="DocumentID")
    document_type: str = pa.Field(coerce=True, nullable=False, description="The document type code defined in Prisma", alias="DocumentType")
    document_name: str = pa.Field(coerce=True, nullable=False, description="The name of the document", alias="DocumentName")
    publication_date: str = pa.Field(coerce=True, nullable=False, description="The date associated with the document in Prisma", alias="PublicationDate")
    worker_number: int = pa.Field(coerce=True, nullable=False, description="The worker ID as an integer", alias="Worker")
    month: int = pa.Field(coerce=True, nullable=False, ge=1, le=12, description="The month the document relates to", alias="Month")
    year: int = pa.Field(coerce=True, nullable=False, description="The year the document relates to", alias="Year")
    language: str = pa.Field(coerce=True, nullable=False, description="The language of the document (N=Dutch, F=French, D=German, E=English)", alias="Language")
    size: Optional[int] = pa.Field(coerce=True, nullable=True, description="Size of the document in bytes", alias="Size")
    mime_type: Optional[str] = pa.Field(coerce=True, nullable=True, description="The MIME type of the document", alias="MIMEtype")
    employer: Optional[str] = pa.Field(coerce=True, nullable=True, description="The employer of the document", alias="Employer")
    type_description: Optional[str] = pa.Field(coerce=True, nullable=True, description="The description of the document type", alias="TypeDescription")

    class Config:
        strict = True
        coerce = True
