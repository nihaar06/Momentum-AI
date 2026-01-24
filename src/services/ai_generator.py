from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

def generate_roadmap_ai(goal, duration_weeks, daily_hours, level):
    """
    Generates an adaptive roadmap.
    Task count, effort, and structure are decided by AI.
    """

    prompt = f"""
You are an expert learning roadmap planner.

Create a JSON roadmap with the following rules:

GOAL:
- {goal}

USER CONTEXT:
- Level: {level}
- Duration: {duration_weeks} weeks
- Daily available time: {daily_hours} hours

TASK GENERATION RULES (VERY IMPORTANT):
1. Task count per day MUST be adaptive:
   - Beginner: 2–3 tasks/day
   - Intermediate: 3–5 tasks/day
   - Advanced: 4–6 tasks/day

2. More daily hours → more tasks or deeper tasks.
3. Tasks must vary in effort (light / medium / deep).
4. Avoid repetitive or generic tasks.
5. Each week must have a clear weekly_goal.
6. Tasks must be practical and progressive.

OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "goal": "...",
  "level": "{level}",
  "daily_hours": {daily_hours},
  "duration_weeks": {duration_weeks},
  "weeks": [
    {{
      "week_number": 1,
      "weekly_goal": "Short clear objective for the week",
      "days": [
        {{
          "day_number": 1,
          "tasks": [
            {{
              "text": "Task description",
              "effort": "light | medium | deep",
              "category": "reading | coding | revision | practice"
            }}
          ]
        }}
      ]
    }}
  ]
}}

IMPORTANT:
- Return ONLY valid JSON.
- Do NOT add explanations or markdown.
"""

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )

    raw = response.choices[0].message.content.strip()

    try:
        return json.loads(raw)
    except Exception as e:
        raise ValueError(f"AI output is not valid JSON: {e}")
