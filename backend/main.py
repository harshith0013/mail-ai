from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

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
from app.api.routes.review import router as review_router
from app.api.routes.email_details import router as email_details_router
from app.api.routes.email_actions import router as email_actions_router
from app.api.routes.email_summary import router as email_summary_router
from app.api.routes.email_reply import router as email_reply_router
from app.api.routes.semantic_search import router as semantic_search_router
from app.services.scheduler_service import start_scheduler, stop_scheduler
from app.services.websocket_manager import manager

app = FastAPI(title="Mail AI")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
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
app.include_router(review_router)
app.include_router(email_details_router)
app.include_router(email_actions_router)
app.include_router(email_summary_router)
app.include_router(email_reply_router)
app.include_router(semantic_search_router)


@app.get("/")
def root():
    return {"message": "Mail AI running"}


@app.on_event("startup")
def startup_event():
    start_scheduler()


@app.on_event("shutdown")
def shutdown_event():
    stop_scheduler()


@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        print("WebSocket disconnected")
        manager.disconnect(websocket)

    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)