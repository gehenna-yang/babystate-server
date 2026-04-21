from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, babys, states 

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(babys.router)
app.include_router(states.router)

@app.get("/")
def root():
    return {"message": "BabyState API Server is running!"}