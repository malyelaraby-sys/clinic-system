from database.supabase_client import supabase

def add_visit(patient_id, complaint, diagnosis, notes):
    supabase.table("visits").insert({
        "patient_id": patient_id,
        "complaint": complaint,
        "diagnosis": diagnosis,
        "notes": notes
    }).execute()


def get_visits_by_patient(patient_id):
    response = supabase.table("visits") \
        .select("*") \
        .eq("patient_id", patient_id) \
        .order("visit_date", desc=True) \
        .execute()

    # Convert to tuple format (same as before)
    visits = [
        (
            v["id"],
            v["patient_id"],
            v.get("visit_date", ""),
            v.get("complaint", ""),
            v.get("diagnosis", ""),
            v.get("notes", "")
        )
        for v in response.data
    ]

    return visits