from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)
    clinic_name = Column(String(255), nullable=False)
    specialty = Column(String(255), nullable=False)

    # 1-N relationship: One Clinic has Many Doctors
    doctors = relationship("Doctor", back_populates="clinic", cascade="all, delete-orphan")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    doctor_code = Column(String(50), nullable=False, unique=True, index=True)
    salary = Column(Float, nullable=False)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)

    # N-1 relationship: Doctor belongs to One Clinic
    clinic = relationship("Clinic", back_populates="doctors")

    # 1-1 relationship: Doctor owns One License (uselist=False enforces single object return)
    license = relationship("License", back_populates="doctor", uselist=False, cascade="all, delete-orphan")


class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    license_number = Column(String(100), nullable=False, unique=True, index=True)
    issue_by = Column(String(255), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False, unique=True)

    # 1-1 relationship: License belongs to One Doctor
    doctor = relationship("Doctor", back_populates="license")
