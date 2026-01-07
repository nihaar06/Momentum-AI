from src.services import ai_roadmap_assistant
import json
from src.services import services

if __name__ == "__main__":
    ss = services()
    ss.generate_and_persist_roadmap(
    user_id="#SAMPLE_UID",
    input_data={
        "goal": "Learn Machine Learning",
        "duration_weeks": 8,
        "daily_hours": 2,
        "level": "beginner"
    }
)

    resp = ai_roadmap_assistant(
        user_id="#SAMPLE_UID",
        input_data="Summarize what the roadmap is about. And provide me some resources to learn from.",
    )
    print(resp)
