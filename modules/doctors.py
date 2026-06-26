from database.supabase_client import supabase

def add_doctor(name):
    if not name:
        return
    
    supabase.table("doctors").insert({
        "name": name
    }).execute()


def get_doctors():
    response = supabase.table("doctors") \
        .select("*") \
        .order("name") \
        .execute()

    return [d["name"] for d in response.data]