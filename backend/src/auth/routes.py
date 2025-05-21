from fastapi import APIRouter, status, Depends
from .schema import UserCreateModel, UserModel, UserLoginModel, UsernameModel, PasswordResetConfirmModel, PasswordResetRequestModel
from db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import create_access_token, decode_token, generate_password_hash, verify_password, create_url_safe_token, decode_url_safe_token
from datetime import timedelta, date, datetime
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user
from config import Config
from auth.service import UserService
from fastapi.responses import JSONResponse
from db.redis import add_jti_to_blacklist
from mail import create_message, mail

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


@auth_router.get('/verify/{token}')
async def verify_user_account(
    token: str,
    session: AsyncSession = Depends(get_session)
):
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(email=user_email, session=session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= "User Not Found"
            )
        
        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content = {
                "message" : "Account is successfully verified"
            },
            status_code= status.HTTP_200_OK
        )
    return JSONResponse(
        content = {
            "message": "Account is successfully verified!!!"
        },
        status_code= status.HTTP_500_INTERNAL_SERVER_ERROR
    )


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


@auth_router.post('/password-reset-request')
async def password_reset_request(
    email_data : PasswordResetRequestModel
):
    email = email_data.email

    token = create_url_safe_token(
        {
            'email': email
        }
    )

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"


    html_message = f"""
    <h1>Reset your password</h1>
    <p>Please click this <a href = "{link}">link</a> to reset your password</p>
    """
    message = create_message(
        receipients=[email],
        subject= 'Reset your password - from code reviwer',
        body = html_message
    )

    await mail.send_message(message)
    
    return JSONResponse(
        content = {
            "message": "Please check your inbox to reset yur password"
        },
        status_code = status.HTTP_200_OK
    )


@auth_router.post('/password-reset-confirm/{token}')
async def reset_account_password(
    token: str,
    password: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_password = password.new_password
    confirm_password = password.confirm_password
    if new_password != confirm_password:
        raise HTTPException(
            detail = "Passwords do not match",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    token_data = decode_url_safe_token(token)

    passwordh = generate_password_hash(new_password)

    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail= "User Not Found"
            )
        
        await user_service.update_user(user, {"password_hash": passwordh}, session)

        return JSONResponse(
            content = {
                "message" : "Password changed successfully"
            },
            status_code= status.HTTP_200_OK
        )
    return JSONResponse(
        content = {
            "message": "Oops! Error occurred in changing the password"
        },
        status_code= status.HTTP_500_INTERNAL_SERVER_ERROR
    )



