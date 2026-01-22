from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from src.services import ai_roadmap_assistant
from src.services.services import services

app=FastAPI()
ss=services()

# ---- CORS CONFIG (CRITICAL) ----
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class GenerateRoadmapRequest(BaseModel):
    user_id:str
    goal:str
    duration_weeks:int
    daily_hours:int
    level:str

@app.post('/generate_roadmap')
def generate_roadmap(req:GenerateRoadmapRequest):
    roadmap=ss.generate_and_persist_roadmap(
        user_id=req.user_id,
        input_data={
            'goal':req.goal,
            'duration_weeks':req.duration_weeks,
            'daily_hours':req.daily_hours,
            'level':req.level
        },
    )
    return roadmap

@app.get('/roadmaps')
def list_roadmaps(user_id:str):
    return ss.list_roadmaps(user_id)

@app.delete("/roadmap/{roadmap_id}")
def delete_roadmap(roadmap_id: int, user_id: str):
    ss.delete_roadmap(roadmap_id, user_id)
    return {"success": True}

@app.get("/roadmap/{roadmap_id}/weeks")
def roadmap_weeks(roadmap_id: int):
    tasks = ss.get_roadmap_tasks(roadmap_id)

    weeks = {}

    for t in tasks:
        w = t["week_number"]

        if w not in weeks:
            weeks[w] = {
                "week_number": w,
                "total_tasks": 0,
                "completed_tasks": 0,
            }

        weeks[w]["total_tasks"] += 1
        if t["completed"]:
            weeks[w]["completed_tasks"] += 1

    result = []
    for w in sorted(weeks.keys()):
        data = weeks[w]
        progress = (
            round((data["completed_tasks"] / data["total_tasks"]) * 100)
            if data["total_tasks"] > 0
            else 0
        )

        result.append({
            "week_number": w,
            "total_tasks": data["total_tasks"],
            "completed_tasks": data["completed_tasks"],
            "progress": progress,
        })

    return result

@app.get("/roadmap/{roadmap_id}/week/{week_number}")
def roadmap_week_detail(roadmap_id: int, week_number: int):
    tasks = ss.get_roadmap_tasks_by_week(roadmap_id, week_number)

    days = {}
    completed = 0
    for t in tasks:
        days.setdefault(t["day_number"], []).append(t)
        if t["completed"]:
            completed += 1

    total = len(tasks)

    return {
        "week_number": week_number,
        "progress": round((completed / total) * 100) if total else 0,
        "days": days,
    }


@app.get('/roadmap/{roadmap_id}')
def get_roadmap(roadmap_id):
    tasks=ss.get_roadmap_tasks(roadmap_id)
    return {'tasks':tasks}

class UpdateTaskRequest(BaseModel):
    task_id:str
    completed:bool

@app.post('/task/update')
def update_task(req:UpdateTaskRequest):
    ss.update_roadmap_task_status(req.task_id,req.completed)
    return {"success":True}

class AssistantRequest(BaseModel):
    user_id:str
    roadmap_id:int
    input_data:str  
    week_number:int|None
    day_number:int|None

@app.post('/ask-assistant')
def ask_assistant(req:AssistantRequest):
    resp=ai_roadmap_assistant(req.user_id,req.roadmap_id,req.input_data,req.week_number,req.day_number)
    return {'response':resp}

@app.get("/health")
def health():
    return {"status": "ok"}
