from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
from config import Config
import uuid 
import logging
from itsdangerous import URLSafeTimedSerializer


passwrd_context = CryptContext(
    schemes= ['bcrypt']
)

ACCESS_TOKEN_EXPIRY = 3600

def generate_password_hash(
        password: str
    ) -> str:
    
    hash = passwrd_context.hash(password)
    
    return hash

def verify_password(
        password: str,
        hash : str
    ) -> bool:
    return passwrd_context.verify(password, hash)

def create_access_token(
        user_data: dict,
        expiry: float = None,
        refresh: bool = False
):
    payload = {}
    payload['user'] = user_data

    if expiry is not None:
        expiry_delta = timedelta(seconds= expiry)
    else:
        expiry_delta = timedelta(seconds= ACCESS_TOKEN_EXPIRY)

    payload['exp'] = datetime.now() + expiry_delta
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh


    token = jwt.encode(
        payload= payload,
        algorithm = Config.JWT_ALGORITHM,
        key = Config.JWT_SECRET
    )

    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt = token,
            key = Config.JWT_SECRET,
            algorithms = [Config.JWT_ALGORITHM]
        )
        return token_data
    
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None
    
serializer = URLSafeTimedSerializer(
    secret_key = Config.JWT_SECRET,
    salt= 'email-configuration'
)

def create_url_safe_token(data: dict):

    token = serializer.dumps(
        data,
        salt = 'email-configuration'
    )
    return token

def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)

        return token_data
    
    except Exception as e:
        logging.error(str(e))