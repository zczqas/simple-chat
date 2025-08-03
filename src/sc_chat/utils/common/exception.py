from fastapi import HTTPException, status


class InvalidCredentialsException(HTTPException):
    """Exception raised for invalid credentials in the application."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=self.message)


class CredentialsValidationException(HTTPException):
    """Exception raised when credentials could not be validated."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=self.message)


class UserNotFoundException(HTTPException):
    """Exception raised when a user is not found in the application."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=self.message)
