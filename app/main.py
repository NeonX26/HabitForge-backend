from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    activity,
    auth,
    bootstrap,
    expenses,
    habits,
    journal,
    me,
    mood,
    notes,
    pomodoro,
    priorities,
    progress,
    planner,
    tasks,
    weekly_goals,
    wellness,
)

app = FastAPI(title="HabitForge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api/v1")
api.include_router(auth.router)
api.include_router(habits.router)
api.include_router(tasks.router)
api.include_router(journal.router)
api.include_router(wellness.router)
api.include_router(priorities.router)
api.include_router(mood.router)
api.include_router(weekly_goals.router)
api.include_router(expenses.router)
api.include_router(notes.router)
api.include_router(pomodoro.router)
api.include_router(activity.router)
api.include_router(me.router)
api.include_router(progress.router)
api.include_router(bootstrap.router)
api.include_router(planner.router)
app.include_router(api)


@app.get("/health")
def health():
    return {"status": "ok"}
