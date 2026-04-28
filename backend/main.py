from fastapi import FastAPI

from app.api.routes.users import router as users_router
from app.api.routes.gmail_accounts import router as gmail_router
from app.api.routes.google_auth import router as google_auth_router
from app.api.routes.email_messages import router as email_router
from app.api.routes.gmail_sync import router as gmail_sync_router
from app.api.routes.classification import router as classification_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.classification_results import router as classification_results_router
from app.api.routes.review_queue import router as review_queue_router
from app.api.routes.dashboard import router as dashboard_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mail AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(gmail_router)
app.include_router(email_router)
app.include_router(google_auth_router)
app.include_router(gmail_sync_router)
app.include_router(classification_router)
app.include_router(notifications_router)
app.include_router(classification_results_router)
app.include_router(review_queue_router)
app.include_router(dashboard_router)

@app.get("/")
def root():
    return {"message": "Mail AI running"}