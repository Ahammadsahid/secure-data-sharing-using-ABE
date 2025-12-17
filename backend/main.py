from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import Base, engine
from backend.auth.routes import router as auth_router
from backend.api.file_routes import router as file_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure Data Sharing Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ❗ DO NOT ADD /auth PREFIX HERE
app.include_router(auth_router)
app.include_router(file_router)
