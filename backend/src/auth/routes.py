from fastapi import APIRouter, status, Depends
from src.auth.schema import UserCreateModel, UserModel, UserLoginModel, UsernameModel, PasswordResetConfirmModel, PasswordResetConfirmModel
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import create_access_token, decode_token, verify_password, create_url_safe_token, decode_url_safe_token
from datetime import timedelta, date, datetime
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.config import Config
from auth.service import UserService
from fastapi.responses import JSONResponse
from src.db.redis import add_jti_to_blacklist
from src.mail import create_message, mail

auth_router = APIRouter()
user_service = UserService()
REFRESH_TOKEN_EXPIRY = 2



@auth_router.post("/send_mail")
async def send_mail(
    username: UsernameModel
):
    user = await user_service.get_user_by_username(username.username)
    
    if not user:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail = 'User Not Found'
        )
    
    email = user.email

    html = '<h1>Welcome to Code Reviewer</h1>'

    message = create_message(
        receipients=email,
        subject= 'Welcome to Code Reviewer',
        body = html
    )
    await mail.send_message(message)

    return {"message" : "Email sent successfully"}

@auth_router.post('/signup', status_code= status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreateModel, 
    session: AsyncSession = Depends(get_session)
):
    username = user_data.username
    email = user_data.email

    user_exists = await user_service.user_exists(
        username, 
        session
    )

    if user_exists:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail = 'User Already Exists'
        )
    
    new_user = await user_service.create_user(
        user_data,
        session
    )

    token = create_url_safe_token({'email': email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message = f"""
    <h1>Verify Your Email</h1>
    <p>Please click this <a href = "{link}">link</a> to verify your email</p>
    """

    message = create_message(
        receipients=[email],
        subject= 'Welcome',
        body = html_message
    )

    await mail.send_message(message)
    
    return {
        "message" : "Account Creaed!! Check email to verify your account",
        "user" : new_user
    } 


@auth_router.post('/login')
async def login_users(
    login_data: UserLoginModel,
    session: AsyncSession = Depends(get_session)
):
    username = login_data.username
    password = login_data.password

    user = await user_service.get_user_by_username(username, session)

    if user is not None:
        password_valid = verify_password(
            password, user.password_hash
        )

        if password_valid:
            access_token = create_access_token(
                user_data = {
                    'username': user.username,
                    'user_uid': str(user.uid),
                    'role' : user.role
                }
            )

            refresh_token = create_access_token(
                user_data = {
                    'username': user.username,
                    'user_uid' : str(user.uid)
                }, 
                refresh = True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY).total_seconds()
            )

            return JSONResponse(
                content = {
                    "message" : "Login Successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user" : {
                        "email": user.email,
                        "uid": str(user.uid)
                    }
                }
            )
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail = "Invalid Credentials"
        )


@auth_router.get('/me', response_model= UserModel)
async def get_current_user(
    user= Depends(get_current_user)
):
    return user


@auth_router.get('/logout', status_code = status.HTTP_200_OK)
async def revoke_token(
    token_details: dict = Depends(AccessTokenBearer())
):
    jti = token_details['jti']

    await add_jti_to_blacklist(jti)

    return JSONResponse(
        content = {
            "message" : "Logged Out Successfully"
        }, 
        status_code= status.HTTP_200_OK
    )