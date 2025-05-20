from src.db.models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload
from src.auth.schema import UserCreateModel
from src.auth.utils import generate_password_hash
from fastapi.exceptions import HTTPException
from fastapi import status 

class UserService:
    async def get_user_by_username(
            self, 
            username: str,
            session: AsyncSession
        ) -> User:
        statement = select(User).where(User.username == username).options(selectinload(User.code_reviews))
        result = await session.execute(statement)

        user = result.scalars().first()
        return user
    

    async def user_exists(
            self,
            username,
            session: AsyncSession
            )-> bool:
        user = await self.get_user_by_username(
            username,
            session
        )
        return user is not None
    
    async def create_user(
        self,
        user_data: UserCreateModel,
        session: AsyncSession
    ) -> User:
        user_data_dict = user_data.model_dump()

        new_user = User(
            **user_data_dict
        )

        user_exist = await self.user_exists(
            new_user.username,
            session
        )

        if not user_exist:
            new_user.password_hash = generate_password_hash(user_data_dict['password'])

            session.add(new_user)

            await session.commit()
            await session.refresh(new_user)
            return new_user
        
        else:
            raise HTTPException(
                status_code= status.HTTP_403_FORBIDDEN,
                detail= "User Already Exists"
            )
        
   
    async def update_user(
            self, 
            user: User,
            user_data: dict,
            session: AsyncSession
    ):
        for k, v in user_data.items():
            setattr(user, k, v)
        await session.commit()

        return user
