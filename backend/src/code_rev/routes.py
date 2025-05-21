from .utils import generate_title_from_code
from fastapi import APIRouter, status, Depends
from .ai_model import generate_response
from fastapi.exceptions import HTTPException
from db.main import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from auth.dependencies import AccessTokenBearer
from .schemas import  CodeReviewSubmitModel
from auth.schema import UserModel
from auth.dependencies import get_current_user
from db.models import CodeReview
from typing import List, Optional
from sqlmodel import select
from sqlalchemy.orm import selectinload
import uuid
from datetime import datetime
from sqlalchemy import or_
from fastapi import Query

code_router = APIRouter()
access_token_bearer = AccessTokenBearer()


@code_router.post("/submit")
async def submit_code_for_review(
    review_data: CodeReviewSubmitModel,
    token_details: dict = Depends(access_token_bearer),
    session :AsyncSession = Depends(get_session)
):
   user = await get_current_user(token_details=token_details, session = session)
   review =  generate_response(review_data.code_snippet, review_data.language)
   new_review = CodeReview(
      title=review_data.title,
      code_snippet=review_data.code_snippet,
      review=review,   
      user_id= user.uid
   )

   session.add(new_review)
   await session.commit()
   return new_review


@code_router.get("/my-reviews", response_model= List[CodeReview])
async def get_my_review(
   token_details: dict = Depends(access_token_bearer),
   session: AsyncSession = Depends(get_session)
):
   user = await get_current_user(
      token_details=token_details,
      session= session
   )


   result = await session.execute(
      select(CodeReview).where(
         CodeReview.user_id == user.uid
      )
   )

   reviews = result.scalars().all()
   return reviews

@code_router.get("/{uid}", response_model=CodeReview)
async def get_review_by_id(
   uid: uuid.UUID,
   session: AsyncSession = Depends(get_session),
   token_details: dict = Depends(access_token_bearer)
):
   result = await session.execute(
      select(CodeReview).where(CodeReview.uid == uid)
   )

   review = result.scalar_one_or_none()
   if not review:
      raise HTTPException(
         status_code=404,
         details= "Review Not Found"
      )
   return review


@code_router.put("/{review_id}")
async def update_review(
   review_id: uuid.UUID,
   review_data: CodeReviewSubmitModel,
   session: AsyncSession = Depends(get_session),
   token_details: dict = Depends(access_token_bearer)
):
   user = await get_current_user(
      token_details=token_details,
      session=session
   )
   result = await session.execute(
      select(CodeReview).where(CodeReview.uid == review_id) 
   )

   review = result.scalar_one_or_none()

   if not review:
      raise HTTPException(
         status_code = status.HTTP_404_NOT_FOUND,
         detail = "Review Not Found"
      )
   
   if review.user_id != user.uid:
      raise HTTPException(
         status_code= status.HTTP_401_UNAUTHORIZED,
         detail= "This User is not authorised for updating this."
      )
   
   review.title = review_data.title
   review.code_snippet = review_data.code_snippet
   review.review = generate_response(
      review_data.code_snippet,
      review_data.language
   )
   review.updated_at = datetime.now()

   session.add(review)
   await session.commit()
   return review

@code_router.delete('/{review_id}', status_code= status.HTTP_204_NO_CONTENT)
async def delete_review(
   review_id: uuid.UUID,
   session: AsyncSession = Depends(get_session),
   token_details: dict = Depends(access_token_bearer)
):
   user = await get_current_user(
      token_details= token_details,
      session= session
   )

   result= await session.execute(
      select(CodeReview).where(CodeReview.uid == review_id)
   )

   review = result.scalar_one_or_none()

   if not review or review.user_id != user.uid:
      raise HTTPException(
         status_code=status.HTTP_404_NOT_FOUND,
         detail ="Review Not Found Or Access Denied"
      )
   
   await session.delete(review)

   await session.commit()

@code_router.get("/search", response_model=List[CodeReview])
async def search_my_reviews(
    query: str = Query(...),
    token_details: dict = Depends(access_token_bearer),
    session: AsyncSession = Depends(get_session)
):
    user = await get_current_user(
        token_details=token_details,
        session=session
    )

    result = await session.execute(
        select(CodeReview).where(
            CodeReview.user_id == user.uid,
            or_(
                CodeReview.title.ilike(f"%{query}%"),
                CodeReview.code_snippet.ilike(f"%{query}%"),
                CodeReview.review.ilike(f"%{query}%")
            )
        )
    )

    reviews = result.scalars().all()
    return reviews
