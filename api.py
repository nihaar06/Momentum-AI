from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

# Updated imports to use absolute paths for better reliability in production
from src.services.ai_roadmap_assistant import ai_roadmap_assistant
from src.services.services import services

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://momentum-ai-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ss = services()

# --- Pydantic Models ---
class GenerateRoadmapRequest(BaseModel):
    user_id: str
    goal: str
    duration_weeks: int
    daily_hours: int
    level: str

class UpdateTaskRequest(BaseModel):
    task_id: str
    completed: bool

class AssistantRequest(BaseModel):
    user_id: str
    roadmap_id: int
    input_data: str  
    week_number: int | None = None
    day_number: int | None = None

# --- Endpoints ---

@app.post('/generate_roadmap')
def generate_roadmap(req: GenerateRoadmapRequest):
    return ss.generate_and_persist_roadmap(
        user_id=req.user_id,
        input_data=req.dict() # Using .dict() is cleaner
    )

@app.get('/roadmaps')
def list_roadmaps(user_id: str):
    return ss.list_roadmaps(user_id)

@app.delete("/roadmap/{roadmap_id}")
def delete_roadmap(roadmap_id: int, user_id: str):
    ss.delete_roadmap(roadmap_id, user_id)
    return {"success": True}

@app.get("/roadmap/{roadmap_id}/weeks")
def roadmap_weeks(roadmap_id: int):
    return ss.get_roadmap_weeks(roadmap_id)

@app.get("/roadmap/{roadmap_id}/week/{week_number}")
def roadmap_week_detail(roadmap_id: int, week_number: int):
    tasks = ss.get_roadmap_tasks_by_week(roadmap_id, week_number)
    if not tasks:
        return {"week_number": week_number, "progress": 0, "days": {}}
    
    days = {}
    completed = 0
    for t in tasks:
        days.setdefault(t["day_number"], []).append(t)
        if t["completed"]:
            completed += 1

    return {
        "week_number": week_number,
        "progress": round((completed / len(tasks)) * 100),
        "days": days,
    }

@app.get('/roadmap/{roadmap_id}')
def get_roadmap(roadmap_id: int): # Added :int type hint
    tasks = ss.get_roadmap_tasks(roadmap_id)
    return {'tasks': tasks}

@app.post('/task/update')
def update_task_status(req: UpdateTaskRequest):
    ss.update_roadmap_task_status(req.task_id, req.completed)
    return {"success": True}

@app.post('/ask-assistant')
def ask_assistant(req: AssistantRequest):
    resp = ai_roadmap_assistant(
        req.user_id, 
        req.roadmap_id, 
        req.input_data, 
        req.week_number, 
        req.day_number
    )
    return {'response': resp}

@app.get("/health")
def health():
    return {"status": "ok"}