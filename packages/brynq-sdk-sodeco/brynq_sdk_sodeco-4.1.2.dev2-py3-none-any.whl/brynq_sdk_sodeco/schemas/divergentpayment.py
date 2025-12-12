from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime

class DivergentPaymentSchema(DataFrameModel):
    """Schema for divergent payment entries"""
    # Required fields
    startdate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Startdate")
    enddate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Enddate")
    payout_type: str = Field(nullable=False, isin=['Salarycode', 'Amount', 'Percentage'], alias="PayoutType")
    amount: float = Field(nullable=False, ge=0.0, le=10000.0, alias="Amount")
    pay_way: str = Field(nullable=False, isin=['Cash', 'Transfer', 'Electronic', 'AssignmentList'], alias="PayWay")
    bank_account: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 45}, alias="BankAccount")
    bic_code: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 15}, alias="BICCode")

    # Optional fields
    salary_code: Optional[int] = Field(nullable=True, ge=1, le=8999, alias="SalaryCode")
    beneficiary: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30}, alias="Beneficiary")
    street: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30}, alias="Street")
    house_number: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 5}, alias="HouseNumber")
    post_box: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 5}, alias="PostBox")
    zip_code: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 12}, alias="ZIPCode")
    city: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30}, alias="City")
    reference: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30}, alias="Reference")
