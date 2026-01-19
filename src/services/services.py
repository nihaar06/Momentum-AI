from src.dao.db import ops
import os
import json
from datetime import datetime
from .ai_generator import generate_roadmap_ai

op=ops()
class services:
    ###GOALS###
    def add_goal(self,des,m,t,deadline):
        res=op.add_goal(des,m,t,deadline)
        return res
    
    def get_goal(self,id):
        return op.get_goal(id)
    
    def update_goals(self,id,desc,metric,target_value,deadline,current_value=None):
        return op.update_goal(id,desc,metric,target_value,deadline,current_value)
    
    def delete_goal(self,id):
        return op.delete_goal(id)
    
    def list_goals(self):
        return op.list_goals()
    
    def update_progress(self,id,val):
        return op.update_progress(id,val)
    
    def show_progress(self,id):
        return op.show_progress(id)
    ###TASKS###
    def add_task(self,id,desc,p):
        return op.add_task(id,desc,p)

    def update_task(self, task_id, description, goal_id):
        return op.update_task(task_id, description, goal_id)
    
    def delete_task(self, task_id):
        return op.delete_task(task_id)
    
    def set_task_prioritized(self,tid,val):
        return op.set_task_prioritized(tid,val)
    
    def get_prioritized_tasks(self):
        return op.get_prioritized_tasks()

    def update_task_status(self,id,status):
        return op.update_task_status(id,status)
    
    def list_tasks(self):
        return op.list_tasks()
    
    ###ROADMAPS###
    def get_roadmap(self,user_id,roadmap_id):
        return op.get_roadmap(user_id,roadmap_id)
    
    def get_active_roadmap(self,user_id):
        return op.get_active_roadmap(user_id)
    
    def add_roadmap(self,user_id,description,level,daily_hours,duration_weeks):
        return op.add_roadmap(user_id,description,level,daily_hours,duration_weeks)
    
    def get_goals_for_roadmap(self,roadmap_id):
        return op.get_goals_for_roadmap(roadmap_id)
    
    def get_tasks_for_roadmap(self,roadmap_id):
        return op.get_tasks_for_roadmap(roadmap_id)
    
    def delete_roadmap(self, roadmap_id: int, user_id: str):
        return op.delete_roadmap(roadmap_id, user_id)

    
    def list_roadmaps(self,user_id):
        return op.list_roadmaps(user_id)
    
    ###ROADMAP TASKS###

    def get_roadmap_tasks(self,roadmap_id):
        return op.get_roadmap_tasks(roadmap_id)
    
    def add_roadmap_task(self,user_id,roadmap_id,day_number,task_description):
        return op.add_roadmap_task(user_id,roadmap_id,day_number,task_description)
    
    def update_roadmap_task_status(self,task_id,completed):
        return op.update_roadmap_task_status(task_id,completed)
    
    def get_roadmap_tasks_by_week(self,roadmap_id,week_number):
        return op.get_roadmap_tasks_by_week(roadmap_id,week_number)
    
    ###AI PERSISTANCE ORCHESTRATOR###
    def persist_ai_roadmap(self, user_id, ai_output):
        roadmap = None
        try:
            roadmap = op.add_roadmap(
                user_id=user_id,
                description=ai_output["goal"],
                level=ai_output["level"],
                duration_weeks=ai_output["duration_weeks"],
                daily_hours=ai_output["daily_hours"],
            )

            if not roadmap:
                raise ValueError("Roadmap creation failed.")

            roadmap_id = roadmap["roadmap_id"]

            for week in ai_output["weeks"]:
                for day in week["days"]:
                    for task in day["tasks"]:
                        op.add_roadmap_task(
                            roadmap_id,
                            week["week_number"],
                            day['day_number'],
                            task  
                        )

            return roadmap

        except Exception as e:
            if roadmap:
                op.delete_roadmap(roadmap["roadmap_id"],user_id)
            raise ValueError(f"Could not persist AI output: {e}")

        #Added Transaction safety-Ensures that AI-generated roadmaps are either fully saved or completely rolled back if an error occurs.

    def generate_and_persist_roadmap(self, user_id: str, input_data: dict):
        """
        1. Generate roadmap JSON from AI
        2. Persist roadmap
        3. Persist roadmap_tasks (day-wise)
        4. Return created roadmap
        """

        # 1️⃣ Generate roadmap from AI
        ai_output = generate_roadmap_ai(
            goal=input_data["goal"],
            duration_weeks=input_data["duration_weeks"],
            daily_hours=input_data["daily_hours"],
            level=input_data["level"],
        )

        roadmap = None

        try:
            # 2️⃣ Insert roadmap
            roadmap = op.add_roadmap(
                user_id=user_id,
                description=ai_output["goal"],
                level=ai_output["level"],
                daily_hours=ai_output["daily_hours"],
                duration_weeks=ai_output["duration_weeks"],
            )

            if not roadmap:
                raise ValueError("Roadmap creation failed")

            roadmap_id = roadmap["roadmap_id"]

            # 3️⃣ Insert roadmap tasks
            for week in ai_output["weeks"]:
                week_number = week["week_number"]
                for day in week["days"]:
                    day_number = day["day_number"]
                    for task_text in day["tasks"]:
                        op.add_roadmap_task(
                            roadmap_id=roadmap_id,
                            week_number=week_number,
                            day_number=day_number,
                            task_text=task_text,
                        )

            return roadmap

        except Exception as e:
            # 4️⃣ Rollback safety
            if roadmap:
                op.delete_roadmap(roadmap["roadmap_id"])
            raise ValueError(f"Failed to persist roadmap: {e}")