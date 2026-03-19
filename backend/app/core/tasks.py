from typing import List

from app import schemas

# Basic stubs to keep the task pipeline from failing.
def auto_create_tasks(user_id: str, text: str):
    return None

def get_open_tasks(user_id: str) -> List[schemas.Task]:
    return []

def generate_plan_from_goal(payload, db=None, timeline=None) -> List[schemas.Task]:
    return []

def auto_extract_tasks_from_message(payload, db=None, timeline=None) -> List[schemas.Task]:
    return []

def get_open_tasks_for_user(db=None) -> List[schemas.Task]:
    return []
