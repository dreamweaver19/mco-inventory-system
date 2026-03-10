import datetime

def log_login(username, status):
    with open("logs/login_audit.log", "a") as file:
        file.write(f"{username} | {status} | {datetime.datetime.now()}\n")

def log_transition(component_id, old_state, new_state):
    with open("logs/lifecycle_audit.log", "a") as file:
        file.write(f"{component_id} | {old_state} -> {new_state} | {datetime.datetime.now()}\n")