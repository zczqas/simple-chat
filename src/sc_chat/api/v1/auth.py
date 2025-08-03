from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login_user(username: str, password: str):
    return {"message": f"User {username} logged in successfully."}


@router.post("/signup")
def signup_user(username: str, password: str):
    return {"message": f"User {username} signed up successfully."}
