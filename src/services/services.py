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
    
    ###AI PERSISTANCE ORCHESTRATOR###
    def persist_ai_roadmap(self,user_id,ai_output):
        created_goal_ids=[]
        created_task_ids=[]
        roadmap=None
        try:
            roadmap=op.add_roadmap(user_id=user_id,
                    description=ai_output['goal'],
                    level=ai_output['level'],
                    duration_weeks=ai_output['duration_weeks'],
                    daily_hours=ai_output['daily_hours'],  
                    )
            if not roadmap:
                raise ValueError("Roadmap creation failed.")
            for week in ai_output['weeks']:
                goal=op.add_goal(roadmap_id=roadmap['roadmap_id'],
                                 description=week['weekly_goal'],
                                 metric='tasks',
                                 target=len(week['days']),
                    )
                if not goal:
                    raise ValueError("Goals creation failed.")
                created_goal_ids.append(goal['goal_id'])
                for day in week['days']:
                    for task in day['tasks']:
                        t=op.add_task(goal['goal_id'],task,priority=False)
                        if not t:
                            raise ValueError("Tasks creation failed.")
                        created_task_ids.append(t['task_id'])
            return roadmap
        except Exception as e:
            for t in created_task_ids:
                op.delete_task(t)
            for g in created_goal_ids:
                op.delete_goal(g)
            if roadmap:
                op.delete_roadmap(roadmap['roadmap_id'])
            raise ValueError(f"Could not persist AI output:{e}")
        #Added Transaction safety-Ensures that AI-generated roadmaps are either fully saved or completely rolled back if an error occurs.

    def generate_and_persist_roadmap(self,user_id,input_data):
        ai_output=generate_roadmap_ai(
            goal=input_data['goal'],
            duration_weeks=input_data['duration_weeks'],
            daily_hours=input_data['daily_hours'],
            level=input_data['level']
        )
        return self.persist_ai_roadmap(user_id,ai_output)