from fastapi import FastAPI
from backend.database import Base, engine
from backend.auth.routes import router as auth_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure Data Sharing Backend")

app.include_router(auth_router)
