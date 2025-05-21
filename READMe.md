#  Codereviewer

Codereviewer is a full-stack web application that takes your code, analyzes it using a powerful LLM (LLaMA via Groq API), and returns a detailed review — highlighting bugs, potential improvements, and coding best practices.


## Features 
- User Authentication: Signup, Login, Logout with JWT-based access control
- Email verification using itsdangerous
- Password reset option
- AI Powered code review using Groq's LLaMa
- Backend powered by FastAPI, PostgreSQL, and Alembic for DB Migrations
- Redis-based token blacklisting for secure logut and session management

## Tech Stack


| Layer        | Stack                                         |
|--------------|-----------------------------------------------|
| Frontend     | Streamlit                                     |
| Backend      | FastAPI, JWT, Redis, Alembic, itsdangerous    |
| AI Model     | LLaMA via Groq API                            |
| Database     | PostgreSQL                                    |
| Auth Tokens  | JWT with Redis Blacklist                      |

## Setup Instruction

1. Clone Repo
```bash
git clone https://github.com/yourusername/codereviewer.git
cd codereviewer
```
2. Create and Activate venv
```bash
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
```
3. Install Dependencies
```bash
pip install -r requirements.txt
```
4. Set Up Environment Variables
```bash
DATABASE_URL= Enter_your_database_url
SECRET_KEY= Enter_your_secret_key
GROQ_API_KEY= Enter_your_groq_api_key
EMAIL_HOST= Enter_host_name
EMAIL_PORT= Enter_port_name
EMAIL_USER= Enter_username
EMAIL_PASSWORD= Enter_email_password
REDIS_URL= Enter_redis_url
```
5. Alembic Commands

```bash
alembic init -t async migrations
alembic revision --autogenerate -m "your_comments"
alembic upgrade head
```

6. Start Redis Server
```bash
redis-server
# or with Docker
docker run -p 6379:6379 redis
```
7. Run FastAPI Backend
```bash
cd backend\src
uvicorn main:app --reload
```
8. Run Streamlit Frontend
```bash
cd frontend
streamlit run main.py
```