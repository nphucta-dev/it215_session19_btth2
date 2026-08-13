from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, service
from app.database import engine, get_db

# Tạo bảng dữ liệu nếu chưa tồn tại
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hệ thống Quản lý Y tế (Healthcare Management System)",
    description="API quản lý Phòng khám, Bác sĩ và Chứng chỉ hành nghề với SQLAlchemy và FastAPI",
    version="1.0.0",
)


# --- 1. API Tạo mới Phòng khám ---
@app.post(
    "/clinics",
    response_model=schemas.ClinicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới Phòng khám / Chuyên khoa",
)
def create_clinic_endpoint(
    clinic: schemas.ClinicCreate, db: Session = Depends(get_db)
):
    try:
        return service.create_clinic(db, clinic)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể tạo phòng khám: {str(e)}",
        )


# --- API Lấy danh sách Phòng khám ---
@app.get(
    "/clinics",
    response_model=List[schemas.ClinicResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách tất cả Phòng khám",
)
def get_clinics_endpoint(db: Session = Depends(get_db)):
    return service.get_all_clinics(db)


# --- 2. API Lấy chi tiết Phòng khám chứa liên kết 1-N ---
@app.get(
    "/clinics/{clinic_id}",
    response_model=schemas.ClinicDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy chi tiết Phòng khám kèm danh sách Bác sĩ",
)
def get_clinic_detail_endpoint(clinic_id: int, db: Session = Depends(get_db)):
    clinic = service.get_clinic_detail(db, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phòng khám với ID này",
        )
    return clinic


# --- Helper API: Tạo mới Bác sĩ ---
@app.post(
    "/doctors",
    response_model=schemas.DoctorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới Bác sĩ",
)
def create_doctor_endpoint(
    doctor: schemas.DoctorCreate, db: Session = Depends(get_db)
):
    # Kiểm tra clinic tồn tại
    clinic = service.get_clinic_detail(db, doctor.clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phòng khám chỉ định không tồn tại",
        )
    try:
        return service.create_doctor(db, doctor)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể tạo bác sĩ (mã bác sĩ có thể đã tồn tại): {str(e)}",
        )


# --- 3. API Cập nhật động thông tin Bác sĩ (PATCH) ---
@app.patch(
    "/doctors/{doctor_id}",
    response_model=schemas.DoctorResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật động thông tin Bác sĩ",
)
def update_doctor_endpoint(
    doctor_id: int,
    doctor_update: schemas.DoctorUpdate,
    db: Session = Depends(get_db),
):
    # If clinic_id is supplied in update, check if clinic exists
    if doctor_update.clinic_id is not None:
        clinic = service.get_clinic_detail(db, doctor_update.clinic_id)
        if not clinic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phòng khám chỉ định không tồn tại",
            )

    try:
        updated_doctor = service.update_doctor(db, doctor_id, doctor_update)
        if not updated_doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy bác sĩ với ID này",
            )
        return updated_doctor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lỗi khi cập nhật bác sĩ: {str(e)}",
        )


# --- Helper API: Tạo mới Chứng chỉ hành nghề ---
@app.post(
    "/licenses",
    response_model=schemas.LicenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới Chứng chỉ hành nghề",
)
def create_license_endpoint(
    license_data: schemas.LicenseCreate, db: Session = Depends(get_db)
):
    doctor = service.get_doctor(db, license_data.doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bác sĩ chỉ định không tồn tại",
        )
    try:
        return service.create_license(db, license_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể tạo chứng chỉ (bác sĩ đã có chứng chỉ hoặc số chứng chỉ trùng): {str(e)}",
        )


# --- 4. API Xóa vĩnh viễn Chứng chỉ hành nghề ---
@app.delete(
    "/licenses/{license_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa vĩnh viễn Chứng chỉ hành nghề",
)
def delete_license_endpoint(license_id: int, db: Session = Depends(get_db)):
    try:
        success = service.delete_license(db, license_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy chứng chỉ hành nghề với ID này",
            )
        return {"message": f"Đã xóa vĩnh viễn chứng chỉ hành nghề có ID {license_id}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lỗi khi xóa chứng chỉ hành nghề: {str(e)}",
        )
