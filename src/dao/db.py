import os
from supabase import Client,create_client
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime,timedelta,timezone
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

load_dotenv()

# Use environment variables if available, otherwise use config file
url = os.getenv('SUPABASE_URL') or SUPABASE_URL
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or SUPABASE_SERVICE_ROLE_KEY

if url == 'your_supabase_url_here' or key == 'your_supabase_anon_key_here':
    print("⚠️  WARNING: Please configure your Supabase credentials in config.py or set environment variables")
    print("   SUPABASE_URL and SUPABASE_KEY")

sb:Client=create_client(url,key)


class ops:
    ###GOALS###
    def add_goal(self,description,metric,target,deadline=None,roadmap_id=None):
        try:
            payload={'description':description,'metric':metric,'target_value':target,'deadline':deadline,'roadmap_id':roadmap_id}
            resp=sb.table('goals').insert(payload).execute()
            return resp.data[0] if resp.data else None
        except Exception as e:
            raise ValueError(f"An error occured! {e}")

    def update_goal(self, goal_id, description, metric, target_value,deadline=None,current_value=None):
        """Updates an existing goal's details."""
        try:
            payload = {
                'description': description,
                'metric': metric,
                'target_value': target_value,
                'deadline':deadline,
                'current_value':current_value
            }
            res = sb.table('goals').update(payload).eq('goal_id', goal_id).execute()
            return res.data
        except Exception as e:
            raise ValueError(f"Error! Could not update goal: {e}")

    def delete_goal(self, goal_id):
        """Deletes a goal by its ID."""
        try:
            res = sb.table('goals').delete().eq('goal_id', goal_id).execute()
            return res.data
        except Exception as e:
            raise ValueError(f"Error! Could not delete goal: {e}")
    
    def list_goals(self):
        try:
            res=sb.table('goals').select('*').execute()
            return res.data if res.data else None
        except Exception as e:
            raise ValueError(f"Error! Could not retrieve the data:{e}")
        
    def get_goal(self,goal_id):
        try:
            resp=sb.table('goals').select('*').eq('goal_id',goal_id).execute()
            return resp.data[0] if resp.data else None
        except Exception as e:
            raise ValueError(f"Error Occured! Could not retrieve the goal:{e}")
    
    def update_progress(self,goal_id,value):
        try:
            resp=sb.table('goals').select('*').eq('goal_id',goal_id).execute()
            if resp.data:
                n=resp.data[0]['current_value']+value
                res=sb.table('goals').update({'current_value':n}).eq('goal_id',goal_id).execute()
                return res.data if res.data else None
        except Exception as e:
            raise ValueError(f"Error! Could not update progress:{e}")
        
    def show_progress(self,goal_id):
        try:
            resp=sb.table('goals').select('*').eq('goal_id',goal_id).execute()
            if resp.data:
                if resp.data[0]['target_value']==0:
                    return 0.0
                progress=resp.data[0]['current_value']/resp.data[0]['target_value']
                return progress
        except Exception as e:
            raise ValueError(f"Error! Unable to show progress:{e}")
    
    ###TASKS###
    def add_task(self,goal_id,description,priority):
        try:
            payload={'goal_id':goal_id,'description':description,'is_prioritized':priority}
            resp=sb.table('tasks').insert(payload).execute()
            return resp.data[0] if resp.data else None
        except Exception as e:
            raise ValueError(f'Error Occured! Could not add the task:{e}')
        
    def get_task(self,task_id):
        try:
            resp=sb.table('tasks').select('*').eq('task_id',task_id).execute()
            return resp.data[0] if resp.data else None
        except Exception as e:
            raise ValueError(f"Error Occured! Could not retrieve the task:{e}")
    
    def list_tasks(self):
        try:
            resp=sb.table("tasks").select("*").execute()
            return resp.data if resp.data else None
        except Exception as e:
            raise ValueError(f"Error Occured! Could not retrieve the tasks table:{e}")      

    def update_task(self, task_id, description, goal_id):
        """Updates an existing task's details."""
        try:
            payload = {'description': description, 'goal_id': goal_id}
            res = sb.table('tasks').update(payload).eq('task_id', task_id).execute()
            return res.data
        except Exception as e:
            raise ValueError(f"Error! Could not update task: {e}")

    def delete_task(self, task_id):
        """Deletes a task by its ID."""
        try:
            res = sb.table('tasks').delete().eq('task_id', task_id).execute()
            return res.data
        except Exception as e:
            raise ValueError(f"Error! Could not delete task: {e}")
    def update_task_status(self,task_id,status):
        try:
            res=sb.table('tasks').update({'status':status}).eq('task_id',task_id).execute()
            return res.data if res.data else None
        except Exception as e:
            raise ValueError(f'Error! Could not update:{e}')
    
    def get_task_status(self,task_id):
        try:
            resp=sb.table('tasks').select('*').eq('task_id',task_id).execute()
            if resp.data:
                return resp.data[0]['status']
        except Exception as e:
            raise ValueError(f"Database error:{e}")
        
    def set_task_prioritized(self,task_id,val):
        try:
            resp=sb.table("tasks").update({'is_prioritized':val}).eq('task_id',task_id).execute()
            return resp.data if resp.data else None
        except Exception as e:
            raise ValueError(f"Error! Could not prioritize the task:{e}")
        
    def get_prioritized_tasks(self):
        try:
            resp=sb.table('tasks').select('*').eq('is_prioritized',True).execute()
            return resp.data if resp.data else None
        except Exception as e:
            raise ValueError(f"Error! Could not retrieve prioritized Tasks:{e}")
        
    ###ROADMAPS###
    def add_roadmap(self,user_id,description,level,daily_hours,duration_weeks):
        payload={
            'user_id':user_id,
            'description':description,
            'level':level,
            'daily_hours':daily_hours,
            'duration_weeks':duration_weeks
        }
        resp=sb.table('roadmaps').insert(payload).execute()
        return resp.data[0] if resp.data else None
    
    def list_roadmaps(self, user_id):
        try:
            resp = sb.table("roadmaps").select("*").eq("user_id", user_id).execute()
            return resp.data if resp.data else []
        except Exception as e:
            raise ValueError(f"Error! Could not retrieve data:{e}")

    def get_active_roadmap(self, user_id):
        """
        Returns the single active roadmap for a user (or None).
        """
        try:
            resp = (
                sb.table("roadmaps")
                .select("*")
                .eq("is_active", True)
                .eq("user_id", user_id)
                .execute()
            )
            return resp.data[0] if resp.data else None
        except Exception as e:
            raise ValueError(f"Could not retrieve active roadmap:{e}")
    
    def mark_roadmap_inactive(self, user_id, roadmap_id):
        try:
            resp = (
                sb.table("roadmaps")
                .update({"is_active": False})
                .eq("roadmap_id", roadmap_id)
                .eq("user_id", user_id)
                .execute()
            )
            return resp.data if resp.data else None
        except Exception as e:
            raise ValueError(f"Could not mark roadmap inactive:{e}")
        
    def delete_roadmap(self, roadmap_id: int, user_id: str):
        try:
            # Ensure user owns the roadmap
            resp = (
                sb
                .table("roadmaps")
                .delete()
                .eq("roadmap_id", roadmap_id)
                .eq("user_id", user_id)
                .execute()
            )

            if not resp.data:
                raise ValueError("Roadmap not found or unauthorized")

        except Exception as e:
            raise ValueError(f"Failed to delete roadmap: {e}")


        
    def get_roadmap(self, user_id, roadmap_id):
        try:
            resp = (
                sb.table("roadmaps")
                .select("*")
                .eq("roadmap_id", roadmap_id)
                .eq("user_id", user_id)
                .execute()
            )
            return resp.data[0] if resp.data else None
        except Exception as e:
            raise ValueError(f"Could not retrieve roadmap:{e}")

    def get_goals_for_roadmap(self, roadmap_id):
        try:
            resp = sb.table("goals").select("*").eq("roadmap_id", roadmap_id).execute()
            return resp.data if resp.data else None
        except Exception as e:
            raise ValueError(
                f"Could not retrieve goals for the given roadmap_id:{e}"
            )

    def get_tasks_for_roadmap(self, roadmap_id):
        """
        Returns all tasks that belong to goals under the given roadmap.
        Implemented without joins for better client compatibility.
        """
        try:
            goals_resp = (
                sb.table("goals")
                .select("goal_id")
                .eq("roadmap_id", roadmap_id)
                .execute()
            )
            if not goals_resp.data:
                return None

            goal_ids = [g["goal_id"] for g in goals_resp.data]

            tasks = []
            for gid in goal_ids:
                task_resp = (
                    sb.table("tasks")
                    .select("*")
                    .eq("goal_id", gid)
                    .execute()
                )
                if task_resp.data:
                    tasks.extend(task_resp.data)

            return tasks or None
        except Exception as e:
            raise ValueError(f"Could not retrieve tasks for roadmap:{e}")


    ###ROADMAPS_TASKS###
    def get_roadmap_tasks(self, roadmap_id: int):
        try:
            resp = (
                sb.table("roadmap_tasks")
                .select("*")
                .eq("roadmap_id", roadmap_id)
                .order("week_number,day_number")
                .execute()
            )
            return resp.data or []
        except Exception as e:
            raise ValueError(f"Error retrieving roadmap tasks: {e}")

    def get_roadmap_tasks_by_week(self, roadmap_id: int, week_number: int):
        try:
            resp = (
                sb.table("roadmap_tasks")
                .select("*")
                .eq("roadmap_id", roadmap_id)
                .eq("week_number", week_number)
                .order("day_number")
                .execute()
            )
            return resp.data or []
        except Exception as e:
            raise ValueError(f"Error retrieving roadmap tasks for week {week_number}: {e}")
     
    def add_roadmap_task(self, roadmap_id: int,week_number:int, day_number: int, task_text: str):
        try:
            resp = (
                sb.table("roadmap_tasks")
                .insert({
                    "roadmap_id": roadmap_id,
                    "week_number": week_number,
                    "day_number": day_number,
                    "task_text": task_text,
                    "completed": False
                })
                .execute()
            )
            return resp.data[0] if resp.data else None
        except Exception as e:
            raise ValueError(f"Error inserting roadmap task: {e}")

    def update_roadmap_task_status(self, task_id: str, completed: bool):
        """
        ✅ FIXED: Uses Supabase client correctly
        """
        try:
            resp = (
                sb.table("roadmap_tasks")
                .update({"completed": completed})
                .eq("id", task_id)
                .execute()
            )
            return resp.data[0] if resp.data else None
        except Exception as e:
            raise ValueError(f"Error updating roadmap task status: {e}")
        
    