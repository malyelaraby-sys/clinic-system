from datetime import datetime

def log_event(event_name, details=""):
    with open("usage_log.txt", "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} | {event_name} | {details}\n")