from .services import services
from openai import OpenAI
import json
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
ss = services()
client = OpenAI(
    api_key=key,
    base_url="https://openrouter.ai/api/v1",
)

def validate_user_input(q: str) -> bool:
    return bool(q and len(q.strip()) >= 3)

def build_context(roadmap,tasks):
    return f"""
    Roadmap goal: {roadmap['description']}
    Level: {roadmap['level']}
    Duration: {roadmap['duration_weeks']} weeks
    Tasks:
    - {"\n- ".join(t["task_text"] for t in tasks)}
    """

def ai_assistant(user_id,roadmap_id, input_data):
    roadmap = ss.get_roadmap(user_id,roadmap_id)
    if not roadmap:
        return "Selected roadmap not found."
    if not validate_user_input(input_data):
        return (
            "I can help only with questions related to your roadmap, "
            "tasks, and learning progress."
        )
    tasks = ss.get_roadmap_tasks(roadmap_id)
    context = build_context(roadmap,tasks)
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


def ai_roadmap_assistant(user_id: str, roadmap_id: int, input_data: str) -> str:
    return ai_assistant(
        user_id=user_id,
        roadmap_id=roadmap_id,
        input_data=input_data
    )

