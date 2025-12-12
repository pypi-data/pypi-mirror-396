from typing import Optional, Literal
from pydantic import BaseModel, Field
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# Pydantic schemas for API requests
class CommunicationCreate(BaseModel):
    """Schema for creating a new communication entry."""

    communication_type: Literal['None', 'Phone', 'GSM', 'Email', 'PrivatePhone', 'Fax', 'InternalPhone', 'PrivateEmail', 'GSMEntreprise', 'Website'] = Field(alias="CommunicationType", description="Type of communication method", example="Email")
    value: str = Field(alias="Value", description="Communication value (phone number, email, etc.)", example="john.doe@example.com", min_length=0, max_length=100)
    id: Optional[str] = Field(None, alias="ID", description="Communication ID", example="COMM001", max_length=100)
    contact_person: Optional[str] = Field(None, alias="ContactPerson", description="Contact person name", example="John Doe", max_length=100)
    contact_person_firstname: Optional[str] = Field(None, alias="ContactPersonFirstname", description="Contact person first name", example="John", max_length=50)

    class Config:
        populate_by_name = True


class CommunicationUpdate(CommunicationCreate):
    """Schema for updating a communication entry."""
    class Config:
        populate_by_name = True



# Pandera schema for DataFrame validation
class CommunicationGet(BrynQPanderaDataFrameModel):
    """Schema for validating communication data from API."""

    # Required fields
    communication_type: str = pa.Field(coerce=True, nullable=False, description="Type of communication method", alias="CommunicationType")
    value: str = pa.Field(coerce=True, nullable=False, description="Communication value (phone number, email, etc.)", alias="Value")

    # Optional fields
    id: Optional[str] = pa.Field(coerce=True, nullable=True, description="Communication ID", alias="ID")
    contact_person: Optional[str] = pa.Field(coerce=True, nullable=True, description="Contact person name", alias="ContactPerson")
    contact_person_firstname: Optional[str] = pa.Field(coerce=True, nullable=True, description="Contact person first name", alias="ContactPersonFirstname")
    worker_number: Optional[int] = pa.Field(coerce=True, nullable=True, description="Worker number", alias="WorkerNumber")
    employer: Optional[str] = pa.Field(coerce=True, nullable=True, str_length={'min_value': 0, 'max_value': 40}, description="Employer name", alias="employer")

    class _Annotation:
        primary_key = "id"

class CommunicationDelete(BaseModel):
    """Schema for deleting a communication entry."""
    communication_type: Literal['None', 'Phone', 'GSM', 'Email', 'PrivatePhone', 'Fax', 'InternalPhone', 'PrivateEmail', 'GSMEntreprise', 'Website'] = Field(alias="CommunicationType", description="Type of communication method", example="Email")
    value: str = Field(alias="Value", description="Communication value (phone number, email, etc.)", example="john.doe@example.com", min_length=0, max_length=100)

    id: Optional[str] = Field(None, alias="ID", description="Communication ID", example="COMM001", max_length=100)
    worker_number: Optional[int] = Field(None, alias="WorkerNumber", description="Worker number", example=12345)
    contact_person: Optional[str] = Field(None, alias="ContactPerson", description="Contact person name", example="John Doe", max_length=100)
    contact_person_firstname: Optional[str] = Field(None, alias="ContactPersonFirstname", description="Contact person first name", example="John", max_length=50)
    worker_id: Optional[int] = Field(None, alias="WorkerId", description="Worker ID", example=12345)
    class Config:
        populate_by_name = True
