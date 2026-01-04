from src.services import services
import json

if __name__ == "__main__":
    service_instance = services()
    service_instance.generate_and_persist_roadmap(
    user_id="20f86aff-6a5e-4aba-922c-13a2d46443b5",
    input_data={
        "goal": "Learn Data Science",
        "duration_weeks": 4,
        "daily_hours": 2,
        "level": "beginner"
    }
)
