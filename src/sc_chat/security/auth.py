from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from src.sc_chat.core.config import settings
from src.sc_chat.database.conn import get_db
from src.sc_chat.models.user import User
from src.sc_chat.utils.common.exception import (InvalidCredentialsException,
                                                UserNotFoundException)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class JWTSecurity(object):
    """
    JWT Security handler for authentication and authorization.
    """

    def __init__(self):
        """Initialize JWT security with configuration from settings."""
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = settings.secret_key
        self.ALGORITHM = settings.algorithm
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
        self.REFRESH_TOKEN_TIME_IN_MINUTES = settings.refresh_token_time_in_minutes

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password (str): The plain text password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        """
        Hash a plain text password using bcrypt.

        Args:
            password (str): The plain text password to hash.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)

    def get_user(self, email: str, db: Session):
        """
        Retrieve a user by email from the database.

        Args:
            email (str): The email address of the user to retrieve.
            db (Session): The database session.

        Returns:
            User | None: The user object if found, None otherwise.
        """
        return db.query(User).filter(User.email == email).first()

    def authenticate_user(self, email: str, password: str, db: Session):
        """
        Authenticate a user with email and password.

        Args:
            email (str): The user's email address.
            password (str): The user's plain text password.
            db (Session): The database session.

        Returns:
            User: The authenticated user object.

        Raises:
            UserNotFoundException: If the user is not found.
            InvalidCredentialsException: If the password is incorrect.
        """
        user = self.get_user(email=email, db=db)

        if not user:
            raise UserNotFoundException(message="User not found")

        if not self.verify_password(password, str(user.hashed_password)):
            raise InvalidCredentialsException(message="Invalid credentials")

        return user

    def create_access_token(self, data: dict, expires_delta: timedelta = None):  # type: ignore
        """
        Create a JWT access token.

        Args:
            data (dict): The payload data to encode in the token (typically contains email and role).
            expires_delta (timedelta, optional): Custom expiration time. Defaults to 60 minutes.

        Returns:
            str: The encoded JWT access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=60)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)  # type: ignore
        return encoded_jwt

    def create_refresh_token(self, data: dict, expires_delta: timedelta = None):  # type: ignore
        """
        Create a JWT refresh token.

        Args:
            data (dict): The payload data to encode in the token (typically contains email and role).
            expires_delta (timedelta, optional): Custom expiration time. Defaults to 40 days.

        Returns:
            str: The encoded JWT refresh token.
        """
        to_encode = data.copy()
        to_encode.update({"token": "refresh"})
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=40)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)  # type: ignore
        return encoded_jwt

    def get_current_user(
        self, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
    ):
        """
        Get the current authenticated user from a JWT token.

        Args:
            db (Session): The database session dependency.
            token (str): The JWT token from the Authorization header.

        Returns:
            User: The authenticated user object.

        Raises:
            HTTPException: If the token is invalid or the user is not found.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            email: Optional[str] = self.decode_access_token_and_return_email(token)
            if email is None:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception from e
        user = self.get_user(email=email, db=db)
        if user is None:
            raise credentials_exception
        return user

    def decode_access_token_and_return_email(self, token: str):
        """
        Decode a JWT token and extract the email address.

        Args:
            token (str): The JWT token to decode.

        Returns:
            str | None: The email address from the token payload, or None if not found.
        """
        payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])  # type: ignore
        email: Optional[str] = payload.get("email")
        return email

    def decode_verification_token(self, token: str) -> dict[str, int]:
        """
        Decode a verification token and return its payload.

        Args:
            token (str): The JWT verification token to decode.

        Returns:
            dict[str, int]: The decoded token payload.

        Raises:
            ExpiredSignatureError: If the token is expired or invalid.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])  # type: ignore
            return payload
        except JWTError as e:
            raise ExpiredSignatureError("Token is expired") from e

    def validate_refresh_access_token(self, db: Session, refresh_token: str):
        """
        Validate a refresh token and return the associated user.

        Args:
            db (Session): The database session.
            refresh_token (str): The JWT refresh token to validate.

        Returns:
            User: The user associated with the refresh token.

        Raises:
            HTTPException: If the refresh token is invalid, expired, or the user is not found.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                refresh_token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM],  # type: ignore
            )
            email: str = payload.get("email")  # type: ignore
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        try:
            refresh_token = payload.get("token")  # type: ignore
            if not refresh_token:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = self.get_user(email=email, db=db)

        if user is None:
            raise credentials_exception

        return user


jwt_service = JWTSecurity()
