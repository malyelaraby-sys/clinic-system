from database.supabase_client import supabase

def add_patient(name, phone, gender):
    supabase.table("patients").insert({
        "name": name,
        "phone": phone,
        "gender": gender
    }).execute()


def get_all_patients():
    response = supabase.table("patients").select("*").order("id").execute()
    
    # Convert to same format your app expects (list of tuples)
    patients = [
        (
            p["id"],
            p["name"],
            p.get("phone", ""),
            p.get("gender", ""),
            p.get("created_at", "")
        )
        for p in response.data
    ]
    
    return patients