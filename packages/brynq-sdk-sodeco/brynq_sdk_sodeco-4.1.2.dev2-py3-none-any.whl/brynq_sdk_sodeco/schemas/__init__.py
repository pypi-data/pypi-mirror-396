"""Schema definitions for Sodeco package"""

DATEFORMAT = '%Y%m%d'

# Worker schemas
from .worker import (
    # GET schemas (Pandera - for DataFrame validation)
    EmployeeGet,
    FamilyGet,
    CommunicationGet,
    ContractGet,
    TaxGet,
    ReplacementGet,
    SalaryCompositionGet,
    # POST/PUT schemas (Pydantic - for request validation)
    WorkerCreate,
    WorkerUpdate,
)
from .address import (
    AddressGet,
    AddressCreate,
    AddressUpdate,
)
from .family import FamilyCreate, FamilyUpdate

# Other schemas
from .absence import AbsenceSchema, AbsencesSchema
from .absencenote import AbsenceNoteSchema
# AddressGet is provided by worker module; dedicated address Pandera schema is not exported separately
from .car import CarGet, CarCreate, CarUpdate
from .communication import CommunicationCreate, CommunicationUpdate, CommunicationGet
from .contract import ContractCreate, ContractUpdate, ContractGet
from .costcentre import CostCentreSchema
from .dimona import PostDimonaSchema, GetDimonaSchema, UsingDataSchema
from .divergentpayment import DivergentPaymentSchema
# Family GET schema is provided in worker module as FamilyGet; no separate FamilySchema export
from .replacement import ReplacementSchema
from .salarycomposition import SalaryCompositionGet
from .schedule import ScheduleGet, ScheduleCreate
from .tax import TaxSchema

__all__ = [
    'DATEFORMAT',
    # Worker schemas
    'EmployeeGet',
    'FamilyGet',
    'AddressGet',
    'CommunicationGet',
    'ContractGet',
    'TaxGet',
    'ReplacementGet',
    'SalaryCompositionGet',
    'WorkerCreate',
    'WorkerUpdate',
    'AddressCreate',
    'AddressUpdate',
    'AddressGet',
    # Other schemas
    'AbsenceSchema',
    'AbsencesSchema',
    'AbsenceNoteSchema',
    'CarGet',
    'CarCreate',
    'CarUpdate',
    'CommunicationCreate',
    'CommunicationUpdate',
    'CommunicationGet',
    'ContractCreate',
    'ContractUpdate',
    'ContractGet',
    'CostCentreSchema',
    'PostDimonaSchema',
    'GetDimonaSchema',
    'UsingDataSchema',
    'DivergentPaymentSchema',
    'ReplacementSchema',
    'SalaryCompositionGet',
    'ScheduleGet',
    'ScheduleCreate',
    'TaxSchema'
]
