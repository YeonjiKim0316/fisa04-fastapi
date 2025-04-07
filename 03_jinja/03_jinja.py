from fastapi import FastAPI
from routers import welcome, user

app = FastAPI()

app.include_router(welcome.welcome_router, prefix="/welcome")
app.include_router(user.user_router, prefix="/user")

