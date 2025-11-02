from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request, Depends
from sqlalchemy.orm import Session
from orm import get_db, Patient, Doctor
import os
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = str(os.getenv("JWT_SECRET"))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


def verify_password(plain_password, hashed_password):
    # Use SHA-256 first to handle long passwords, then bcrypt
    sha256_password = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return pwd_context.verify(sha256_password, hashed_password)


def get_password_hash(password):
    # Use SHA-256 first to handle long passwords, then bcrypt
    sha256_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(sha256_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> str:
    token = (
        request.headers.get("Authorization").split(" ")[1]
        if request.headers.get("Authorization")
        else None
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided"
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("userId")
        user = db.query(Patient).filter(Patient.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user.id
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
        )


async def get_current_doctor(request: Request, db: Session = Depends(get_db)) -> str:
    token = (
        request.headers.get("Authorization").split(" ")[1]
        if request.headers.get("Authorization")
        else None
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided"
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        doctor_id = payload.get("doctorId")
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found"
            )

        return doctor.id
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
        )
