from brynq_sdk_brynq import BrynQ
import os
from typing import List, Union, Literal, Optional
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import tempfile
from .address import Addresses
from .car import Cars
from .leavecounters import LeaveCounters
from .costcentres import CostCentres
from .department import Departments
from .dimona import Dimonas
from .family import Families
from .modifications import Modifications
from .parcom import Parcom
from .prestations import Prestations
from .schedule import Schedules
from .nssocat import NssoCat
from .profcat import ProfCat
from .tax import Taxes
from .worker import Workers
from .absences import Absences
from .absencenote import AbsenceNotes
from .contract import Contracts
from .communication import Communications
from .divergentpayment import DivergentPayments
from .salarycomposition import SalaryCompositions
from .documents import Documents


class Sodeco(BrynQ):
    """Class to handle all Sodeco API requests."""

    def __init__(self, employers: Union[str, List], system_type: Optional[Literal['source', 'target']] = None, debug: bool = False):
        super().__init__()
        self.debug = debug
        self.timeout = 3600
        credentials = self._get_credentials(system_type)
        self.base_url = credentials.get("base_url")
        self.user_certificate_header = credentials.get("certificate_header")

        # Get certificate and private key
        certificate = credentials.get("certificate")
        private_key = credentials.get("private_key")

        # Create temporary files for certificate and decrypted private key
        self.cert_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pem')
        self.key_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pem')

        # Write certificate to temporary file
        self.cert_file.write(certificate.encode())
        self.cert_file.close()

        # Decrypt and write private key to temporary file
        private_key_obj = serialization.load_pem_private_key(
            private_key.encode(),
            password=None,  # Empty string password
            backend=default_backend()
        )

        # Write decrypted private key to temporary file
        with open(self.key_file.name, 'wb') as f:
            f.write(private_key_obj.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Create session with certificate authentication
        self.session = requests.Session()
        self.session.cert = (self.cert_file.name, self.key_file.name)

        self.employers = employers if isinstance(employers, List) else [employers]
        self.workers = Workers(self)
        self.modifications = Modifications(self)
        self.absences = Absences(self)
        self.addresses = Addresses(self)
        self.cars = Cars(self)
        self.communications = Communications(self)
        self.costcentres = CostCentres(self)
        self.departments = Departments(self)
        self.dimonas = Dimonas(self)
        self.families = Families(self)
        self.leavecounters = LeaveCounters(self)
        self.parcom = Parcom(self)
        self.schedules = Schedules(self)
        self.nssocat = NssoCat(self)
        self.profcat = ProfCat(self)
        self.taxes = Taxes(self)
        self.contracts = Contracts(self)
        self.absencenotes = AbsenceNotes(self)
        self.divergentpayments = DivergentPayments(self)
        self.salarycompositions = SalaryCompositions(self)
        self.prestations = Prestations(self)
        self.documents = Documents(self)

    def __del__(self):
        """Cleanup temporary files when the object is destroyed"""
        try:
            if hasattr(self, 'cert_file'):
                os.unlink(self.cert_file.name)
            if hasattr(self, 'key_file'):
                os.unlink(self.key_file.name)
        except Exception:
            pass

    def _get_credentials(self, system_type):
        """
        Sets the credentials for the SuccessFactors API.
        :param label (str): The label for the system credentials.
        :returns: headers (dict): The headers for the API request, including the access token.
        """
        credentials = self.interfaces.credentials.get(system="prisma-sodeco", system_type=system_type)
        credentials = credentials.get('data')
        base_url = credentials.get("base_url")
        certificate = credentials.get("certificate")
        private_key = credentials.get("private_key")
        certificate_header = credentials.get("certificate_header")

        return {"base_url": base_url, "certificate": certificate, "private_key": private_key, "certificate_header": certificate_header}

    def update_headers(self, employer: str):
        self.session.headers.update({"Employer": employer})
        if self.user_certificate_header:
            self.session.headers.update({"User-Certificate-Subject": self.user_certificate_header})

    def send_request(self, request: requests.Request) -> requests.Response:
        """
        Send a request using the session with proper certificate authentication.

        Args:
            request: The request to send

        Returns:
            Response: The response from the server

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        # Prepare the request with session headers
        prepped = request.prepare()
        if hasattr(self.session, 'headers'):
            prepped.headers.update(self.session.headers)

        # Send the request and handle response
        response = self.session.send(prepped, timeout=self.timeout)
        response.raise_for_status()

        return response
