from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import random  # <--- THIS WAS MISSING
from core.database import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse, UserLogin, UserPasswordUpdate, OTPRequest, OTPVerify, PasswordResetFinal
from core.email_utils import send_verification_email, send_otp_email

router = APIRouter(tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/signup", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.login_id == user.login_id).first():
        raise HTTPException(status_code=400, detail="Login ID already taken")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Import secrets only if needed, or rely on random/uuid
    import secrets 
    token = secrets.token_urlsafe(32)

    new_user = User(
        login_id=user.login_id,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        is_verified=False,
        verification_token=token
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    send_verification_email(user.email, token)

    return new_user

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login_id == user_data.login_id).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid Login ID or Password")
    
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Account not verified. Please check your email.")

    return {
        "message": "Login Successful", 
        "user_id": user.id, 
        "username": user.login_id,
        "email": user.email
    }

@router.post("/update-password")
def update_password(data: UserPasswordUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login_id == data.login_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

# --- OTP ROUTES ---

@router.post("/forgot-password/request-otp")
def request_otp(data: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    
    otp_code = str(random.randint(100000, 999999))
    
    user.otp = otp_code
    db.commit()
    
    send_otp_email(user.email, otp_code)
    
    return {"message": "OTP sent to email"}

@router.post("/forgot-password/verify-otp")
def verify_otp_check(data: OTPVerify, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or user.otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    return {"message": "OTP Verified"}

@router.post("/forgot-password/reset")
def reset_password_final(data: PasswordResetFinal, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user or user.otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP or Email")
    
    user.hashed_password = get_password_hash(data.new_password)
    user.otp = None
    db.commit()
    
    return {"message": "Password reset successfully"}