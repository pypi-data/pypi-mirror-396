import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, constr

from src.config.settings import settings
from src.db.base import AsyncSessionLocal
from src.db.models import LoginOTP, User
from sqlalchemy import select

from src.integrations.wecan_sms import wecan_sms_client


router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        extra = "forbid"


class OTPRequest(BaseModel):
    phone_number: constr(regex=r"^09\d{9}$")  # type: ignore[type-arg]
    full_name: Optional[str] = None


class OTPVerify(BaseModel):
    phone_number: constr(regex=r"^09\d{9}$")  # type: ignore[type-arg]
    code: constr(regex=r"^\d{4,6}$")  # type: ignore[type-arg]
    full_name: Optional[str] = None


class RoleInfo(BaseModel):
    """Role information with name (English identifier) and title (Persian display name)."""
    name: str
    title: str


class UserOut(BaseModel):
    id: int
    # بعضی از کاربران قدیمی ممکن است ایمیل با فرمت نامعتبر داشته باشند،
    # بنابراین اینجا فقط رشته بودن را چک می‌کنیم نه فرمت ایمیل RFC.
    email: str
    phone_number: Optional[str]
    full_name: Optional[str]
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    role: RoleInfo
    is_active: bool

    class Config:
        orm_mode = True


def get_role_info(role_name: str) -> RoleInfo:
    """Convert role name string to RoleInfo object with Persian title."""
    role_mapping = {
        "user": {"name": "user", "title": "کاربر"},
        "admin": {"name": "admin", "title": "ادمین"},
        "super_admin": {"name": "super_admin", "title": "سوپر ادمین"},
    }
    default_role = {"name": "user", "title": "کاربر"}
    return RoleInfo(**role_mapping.get(role_name, default_role))


def user_to_user_out(user: User) -> dict:
    """Convert User model to UserOut dict with role as object."""
    return {
        "id": user.id,
        "email": user.email,
        "phone_number": user.phone_number,
        "full_name": user.full_name,
        "username": user.username,
        "bio": user.bio,
        "avatar": user.avatar,
        "role": get_role_info(user.role),
        "is_active": user.is_active,
    }


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    # JWT استاندارداً انتظار دارد subject (sub) یک رشته باشد
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


async def get_user_by_email(email: str) -> Optional[User]:
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(User).where(User.email == email))
        return q.scalar_one_or_none()


async def get_user_by_phone(phone_number: str) -> Optional[User]:
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(User).where(User.phone_number == phone_number))
        return q.scalar_one_or_none()


async def get_user_by_id(user_id: int) -> Optional[User]:
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(User).where(User.id == user_id))
        return q.scalar_one_or_none()


async def authenticate_user(email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="حساب کاربری شما غیرفعال است.",
        )
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Resolve the current user from a Bearer JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except ExpiredSignatureError:
        # Token is structurally valid but has passed its exp time
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن منقضی شده است.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        # Any other JWT error (bad signature, bad claims, wrong algorithm, etc.)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"توکن معتبر نیست: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_raw = payload.get("sub")
    role: str | None = payload.get("role")
    if user_id_raw is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="شناسه کاربر در توکن یافت نشد.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # sub در توکن به صورت رشته ذخیره می‌شود؛ اینجا آن را به int تبدیل می‌کنیم
    try:
        user_id_int = int(user_id_raw)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="شناسه کاربر در توکن نامعتبر است.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = TokenData(user_id=user_id_int, role=role)

    user = await get_user_by_id(token_data.user_id)  # type: ignore[arg-type]
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="کاربر مربوط به این توکن یافت نشد.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="حساب کاربری شما غیرفعال است.",
        )
    return current_user


def require_profile_fields(required_fields: list[str]):
    """
    Factory function to create a dependency that checks required profile fields.
    
    Usage:
        @router.post("/endpoint")
        async def my_endpoint(
            current_user: User = Depends(require_profile_fields(['username', 'full_name']))
        ):
            ...
    """
    async def check_required_profile_fields(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        """
        Dependency to check if user has completed required profile fields.
        
        Raises:
            HTTPException with status 428 (Precondition Required) if fields are missing
        """
        missing_fields = []
        field_labels = {
            'username': 'نام کاربری',
            'full_name': 'نام کامل',
            'bio': 'بیوگرافی',
            'avatar': 'آواتار',
            'phone_number': 'شماره موبایل',
        }
        
        for field in required_fields:
            value = getattr(current_user, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field_labels.get(field, field))
        
        if missing_fields:
            raise HTTPException(
                status_code=428,  # Precondition Required
                detail={
                    "message": "برای استفاده از این بخش، لطفاً ابتدا پروفایل خود را تکمیل کنید.",
                    "missing_fields": missing_fields,
                    "error_code": "PROFILE_INCOMPLETE"
                }
            )
        
        return current_user
    
    return check_required_profile_fields


def is_admin_or_super_admin(user: User) -> bool:
    """Check if user has admin or super_admin role."""
    return user.role in ("admin", "super_admin")


def is_super_admin(user: User) -> bool:
    """Check if user has super_admin role."""
    return user.role in ("super_admin")


async def get_current_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin or super_admin role."""
    if not is_admin_or_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی ادمین ندارید.",
        )
    return current_user


async def get_current_super_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require super_admin role (no limitations)."""
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی سوپر ادمین ندارید.",
        )
    return current_user


async def get_optional_user(token: Optional[str] = None) -> Optional[User]:
    """Optional user dependency - returns None if no token or invalid token."""
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            return None
        try:
            user_id_int = int(user_id_raw)
        except (TypeError, ValueError):
            return None
        user = await get_user_by_id(user_id_int)
        if user and not user.is_active:
            return None
        return user
    except (JWTError, ExpiredSignatureError):
        return None


async def get_optional_user_dependency(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> Optional[User]:
    """Dependency that extracts token from Authorization header optionally."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "")
    return await get_optional_user(token)


@router.post("/register", response_model=UserOut)
async def register_user(payload: UserCreate):
    existing = await get_user_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این ایمیل قبلاً ثبت شده است.",
        )
    if payload.phone_number:
        user_by_phone = await get_user_by_phone(payload.phone_number)
        if user_by_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="این شماره موبایل قبلاً ثبت شده است.",
            )

    async with AsyncSessionLocal() as session:
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            phone_number=payload.phone_number,
            hashed_password=get_password_hash(payload.password),
            role="user",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user_to_user_out(user)


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ایمیل یا رمز عبور اشتباه است.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.id, "role": user.role}  # type: ignore[arg-type]
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return user_to_user_out(current_user)


@router.patch("/me", response_model=UserOut)
async def update_users_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_active_user),
):
    async with AsyncSessionLocal() as session:
        db_user = await session.get(User, current_user.id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="کاربر یافت نشد.",
            )

        # موبایل قابل تغییر نیست
        # username فقط یکبار قابل ست کردن است و قابل تغییر نیست
        if payload.username is not None:
            if db_user.username is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="نام کاربری فقط یکبار قابل تنظیم است و قابل تغییر نیست.",
                )
            # بررسی یکتایی username
            from sqlalchemy import select
            existing = await session.execute(
                select(User).where(User.username == payload.username, User.id != db_user.id)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="این نام کاربری قبلاً استفاده شده است.",
                )
            db_user.username = payload.username

        if payload.full_name is not None:
            db_user.full_name = payload.full_name

        if payload.bio is not None:
            db_user.bio = payload.bio

        if payload.avatar is not None:
            db_user.avatar = payload.avatar

        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return user_to_user_out(db_user)


class PublicUserProfile(BaseModel):
    """Public user profile information (no sensitive data)."""
    id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True


@router.get("/users/{user_id}/public", response_model=PublicUserProfile)
async def get_public_user_profile(user_id: int):
    """Get public profile of a user (no authentication required)."""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="کاربر یافت نشد.",
            )
        
        return {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "bio": user.bio,
            "avatar": user.avatar,
            "created_at": user.created_at.isoformat() if user.created_at else "",
        }


@router.get("/users/username/{username}/public", response_model=PublicUserProfile)
async def get_public_user_profile_by_username(username: str):
    """Get public profile of a user by username (no authentication required)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == username, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="کاربر یافت نشد.",
            )
        
        return {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "bio": user.bio,
            "avatar": user.avatar,
            "created_at": user.created_at.isoformat() if user.created_at else "",
        }


class TelegramSettingsUpdate(BaseModel):
    """Telegram notification settings update."""
    telegram_enabled: Optional[bool] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None


class TelegramSettingsOut(BaseModel):
    """Telegram notification settings output."""
    telegram_enabled: bool
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    class Config:
        orm_mode = True


@router.get("/me/telegram", response_model=TelegramSettingsOut)
async def get_telegram_settings(current_user: User = Depends(get_current_active_user)):
    """Get current user's Telegram notification settings."""
    return {
        "telegram_enabled": current_user.telegram_enabled or False,
        "telegram_bot_token": current_user.telegram_bot_token,
        "telegram_chat_id": current_user.telegram_chat_id,
    }


@router.patch("/me/telegram", response_model=TelegramSettingsOut)
async def update_telegram_settings(
    payload: TelegramSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """Update current user's Telegram notification settings."""
    async with AsyncSessionLocal() as session:
        db_user = await session.get(User, current_user.id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="کاربر یافت نشد.",
            )

        if payload.telegram_enabled is not None:
            db_user.telegram_enabled = payload.telegram_enabled
        
        if payload.telegram_bot_token is not None:
            db_user.telegram_bot_token = payload.telegram_bot_token
        
        if payload.telegram_chat_id is not None:
            db_user.telegram_chat_id = payload.telegram_chat_id

        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        
        return {
            "telegram_enabled": db_user.telegram_enabled or False,
            "telegram_bot_token": db_user.telegram_bot_token,
            "telegram_chat_id": db_user.telegram_chat_id,
        }


def _hash_otp(phone_number: str, code: str) -> str:
    salted = f"{phone_number}:{code}:{settings.jwt_secret_key}"
    return hashlib.sha256(salted.encode()).hexdigest()


@router.post("/request-otp")
async def request_login_otp(payload: OTPRequest):
    now = datetime.now(timezone.utc)
    code = f"{secrets.randbelow(900000):06d}"
    hashed_code = _hash_otp(payload.phone_number, code)
    expires_at = now + timedelta(minutes=5)
    existing_user = await get_user_by_phone(payload.phone_number)

    async with AsyncSessionLocal() as session:
        otp = LoginOTP(
            phone_number=payload.phone_number,
            code_hash=hashed_code,
            expires_at=expires_at,
            verified=False,
        )
        session.add(otp)
        await session.commit()

    # sms_message = f"کد تایید: {code}\ است."
    sms_message = {
        "otp": code,
        "service": "WeTrade"
    }

    sent = await wecan_sms_client.send_sms(payload.phone_number, sms_message, template_id=settings.wecan_otp_template_id)
    if not sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ارسال پیامک با خطا مواجه شد. لطفاً دوباره تلاش کنید.",
        )

    return {"sent": True, "expires_in": 300, "is_new_user": existing_user is None}


@router.post("/login-otp", response_model=Token)
async def login_with_otp(payload: OTPVerify):
    now = datetime.now(timezone.utc)
    hashed_code = _hash_otp(payload.phone_number, payload.code)

    async with AsyncSessionLocal() as session:
        q = await session.execute(
            select(LoginOTP)
            .where(LoginOTP.phone_number == payload.phone_number)
            .order_by(LoginOTP.created_at.desc())
            .limit(1)
        )
        otp = q.scalar_one_or_none()
        if not otp or otp.verified:
            raise HTTPException(status_code=400, detail="کد معتبر نیست یا قبلاً مصرف شده است.")
        if otp.expires_at < now:
            raise HTTPException(status_code=400, detail="کد منقضی شده است.")
        if otp.code_hash != hashed_code:
            raise HTTPException(status_code=400, detail="کد وارد شده صحیح نیست.")

        otp.verified = True

        q_user = await session.execute(
            select(User).where(User.phone_number == payload.phone_number)
        )
        user = q_user.scalar_one_or_none()

        if not user:
            placeholder_email = f"user_{payload.phone_number}@mail.com"
            # Ensure uniqueness by appending random suffix if needed
            suffix = 1
            existing = await get_user_by_email(placeholder_email)
            while existing:
                # placeholder_email = f"user_{payload.phone_number}_{suffix}@mail.com"
                placeholder_email = f""
                existing = await get_user_by_email(payload.phone_number)
                suffix += 1

            user = User(
                email=placeholder_email,
                phone_number=payload.phone_number,
                full_name=payload.full_name,
                hashed_password=get_password_hash(secrets.token_urlsafe(8)),
                role="user",
            )
            session.add(user)
            await session.flush()
            otp.user_id = user.id
        else:
            if payload.full_name and not (user.full_name):
                user.full_name = payload.full_name

        session.add(otp)
        await session.commit()
        await session.refresh(user)

    access_token = create_access_token(data={"sub": user.id, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


