from .services import services
from openai import OpenAI
import json
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
BLOCKLIST = [
    "ignore previous instructions",
    "system prompt",
    "you are chatgpt",
    "write a poem",
    "tell me a joke",
    "hack",
    "bypass"
]
ss = services()
client = OpenAI(
    api_key=key,
    base_url="https://openrouter.ai/api/v1",
)

def validate_user_input(q: str) -> bool:
    if not q or len(q.strip()) < 3:
        return False
    q = q.lower()
    for p in BLOCKLIST:
        if p in q:
            return False
    return True

def build_context(roadmap, goals, tasks):
    return f"""
    Roadmap goal: {roadmap['description']}
    Level: {roadmap['level']}
    Duration: {roadmap['duration_weeks']} weeks
    Weekly goals:
    - {"\n- ".join(g["description"] for g in goals)}
    Tasks:
    - {"\n- ".join(t["description"] for t in tasks)}
    """

def ai_assistant(user_id, input_data):
    roadmap = ss.get_active_roadmap(user_id)
    if not roadmap:
        return "No active roadmaps found."
    if not validate_user_input(input_data):
        return (
            "I can help only with questions related to your roadmap, "
            "tasks, and learning progress."
        )
    goals = []
    roadmap_goals = ss.get_goals_for_roadmap(roadmap["roadmap_id"])
    if roadmap_goals:
        for g in roadmap_goals:
            goals.append(g)
    tasks = []
    roadmap_tasks = ss.get_tasks_for_roadmap(roadmap["roadmap_id"])
    if roadmap_tasks:
        for t in roadmap_tasks:
            tasks.append(t)
    context = build_context(roadmap, goals, tasks)
    prompt = f"""
    You are an assistant for a productivity roadmap system.

    Context:
    {context}

    Rules:
    - Only answer questions related to this roadmap
    - Do not modify tasks or goals
    - Suggest learning resources if relevant

    User question:
    {input_data}
    """
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": prompt,
        }],
        temperature=0,
    )
    return response.choices[0].message.content


def ai_roadmap_assistant(user_id: str, input_data: str) -> str:
    """
    Public wrapper used by external callers/tests.
    Keeps existing assistant behavior but exposes a clear callable.
    """
    return ai_assistant(user_id=user_id, input_data=input_data)

