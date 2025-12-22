from src.dao.db import ops
import os
import json
from datetime import datetime

op=ops()
class services:
    STATE_FILE_PATH=os.path.expanduser('~/.momentum_state.json')
    def get_status(self):
        if os.path.exists(self.STATE_FILE_PATH):
            try:
                with open(self.STATE_FILE_PATH,'r') as f:
                    state_data=json.load(f)
                tid=state_data['task_id']
                status=op.get_task_status(tid)
                return status
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error: Could not read state file: {e}")
                return None
        else :
            print("No timer is running")
            return None
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
                for day in week['days']:
                    for task in day['tasks']:
                        op.add_task(goal['goal_id'],task,priority=False)
            return roadmap
        except Exception as e:
            raise ValueError(f"Could not persist AI output:{e}")