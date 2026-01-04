import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

key=os.getenv('OPENAI_API_KEY')
client=OpenAI(api_key=key,
    base_url="https://openrouter.ai/api/v1")

def generate_roadmap_ai(goal,duration_weeks,daily_hours,level):
    prompt = f"""
You are an AI planning engine.

Generate a structured productivity roadmap strictly in VALID JSON format.

Rules:
- Output ONLY valid JSON
- Do NOT include explanations or markdown
- Do NOT include comments
- Do NOT invent IDs
- Follow the schema exactly

Input:
Goal: {goal}
Duration (weeks): {duration_weeks}
Daily hours available: {daily_hours}
Difficulty level: {level}

JSON schema:
{{
  "goal": string,
  "duration_weeks": number,
  "daily_hours": number,
  "level": string,
  "weeks": [
    {{
      "week_number": number,
      "weekly_goal": string,
      "days": [
        {{
          "day_number": number,
          "tasks": [string]
        }}
      ]
    }}
  ]
}}

Generate a realistic and evenly distributed roadmap.
"""

    resp=client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{
            "role":"user",
            "content":prompt
        }],
        temperature=0
    )
    content=resp.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError("AI returned invalid json:",e)