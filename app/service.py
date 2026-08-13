from typing import Optional, List
from sqlalchemy.orm import Session
from app import models, schemas

# --- Clinic Services ---

def create_clinic(db: Session, clinic_data: schemas.ClinicCreate) -> models.Clinic:
    """
    Tạo mới một Phòng khám/Chuyên khoa.
    Sử dụng toán tử giải nén dictionary **clinic_data.model_dump()
    Bọc trong khối try-except để đảm bảo an toàn Transaction.
    """
    db_clinic = models.Clinic(**clinic_data.model_dump())
    try:
        db.add(db_clinic)
        db.commit()
        db.refresh(db_clinic)
        return db_clinic
    except Exception as e:
        db.rollback()
        raise e


def get_clinic_detail(db: Session, clinic_id: int) -> Optional[models.Clinic]:
    """
    Lấy thông tin chi tiết phòng khám theo clinic_id.
    Tận dụng thuộc tính ORM relationship (doctors) để tự động trả về thông tin
    lồng ghép danh sách các bác sĩ liên kết.
    """
    return db.query(models.Clinic).filter(models.Clinic.id == clinic_id).first()


def get_all_clinics(db: Session) -> List[models.Clinic]:
    """
    Lấy danh sách tất cả phòng khám.
    """
    return db.query(models.Clinic).all()


# --- Doctor Services ---

def create_doctor(db: Session, doctor_data: schemas.DoctorCreate) -> models.Doctor:
    """
    Tạo mới một Bác sĩ.
    """
    db_doctor = models.Doctor(**doctor_data.model_dump())
    try:
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        db.rollback()
        raise e


def get_doctor(db: Session, doctor_id: int) -> Optional[models.Doctor]:
    """
    Lấy thông tin bác sĩ theo doctor_id.
    """
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()


def update_doctor(
    db: Session, doctor_id: int, doctor_update: schemas.DoctorUpdate
) -> Optional[models.Doctor]:
    """
    Cập nhật động thông tin Bác sĩ (PATCH).
    Sử dụng model_dump(exclude_unset=True) và setattr để chỉ cập nhật các trường được gửi lên.
    """
    db_doctor = get_doctor(db, doctor_id)
    if not db_doctor:
        return None

    update_data = doctor_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_doctor, key, value)

    try:
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        db.rollback()
        raise e


# --- License Services ---

def create_license(db: Session, license_data: schemas.LicenseCreate) -> models.License:
    """
    Tạo mới một Chứng chỉ hành nghề.
    """
    db_license = models.License(**license_data.model_dump())
    try:
        db.add(db_license)
        db.commit()
        db.refresh(db_license)
        return db_license
    except Exception as e:
        db.rollback()
        raise e


def get_license(db: Session, license_id: int) -> Optional[models.License]:
    """
    Lấy thông tin chứng chỉ hành nghề theo license_id.
    """
    return db.query(models.License).filter(models.License.id == license_id).first()


def delete_license(db: Session, license_id: int) -> bool:
    """
    Xóa vĩnh viễn (Hard Delete) Chứng chỉ hành nghề khỏi cơ sở dữ liệu.
    """
    db_license = get_license(db, license_id)
    if not db_license:
        return False

    try:
        db.delete(db_license)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
