import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import auth_routes, questionnaire_routes
from app.routes import reference_routes
from app.routes import answer_routes
from dotenv import load_dotenv
load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Structured Questionnaire AI Tool")

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

# CORS (Next.js frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_routes.router)
app.include_router(questionnaire_routes.router)
app.include_router(reference_routes.router)
app.include_router(answer_routes.router)