from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# --- License Schemas ---

class LicenseBase(BaseModel):
    license_number: str
    issue_by: str


class LicenseCreate(LicenseBase):
    doctor_id: int


class LicenseResponse(LicenseBase):
    id: int
    doctor_id: int

    model_config = ConfigDict(from_attributes=True)


# --- Doctor Schemas ---

class DoctorBase(BaseModel):
    doctor_code: str
    salary: float


class DoctorCreate(DoctorBase):
    clinic_id: int


class DoctorUpdate(BaseModel):
    doctor_code: Optional[str] = None
    salary: Optional[float] = None
    clinic_id: Optional[int] = None


class DoctorResponse(DoctorBase):
    id: int
    clinic_id: int
    license: Optional[LicenseResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- Clinic Schemas ---

class ClinicBase(BaseModel):
    clinic_name: str
    specialty: str


class ClinicCreate(ClinicBase):
    pass


class ClinicResponse(ClinicBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ClinicDetailResponse(ClinicBase):
    id: int
    doctors: List[DoctorResponse] = []

    model_config = ConfigDict(from_attributes=True)
