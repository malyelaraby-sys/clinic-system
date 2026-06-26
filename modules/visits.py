from database.supabase_client import supabase

def add_visit(patient_id, complaint, diagnosis, notes, doctor_name):
    supabase.table("visits").insert({
        "patient_id": patient_id,
        "complaint": complaint,
        "diagnosis": diagnosis,
        "notes": notes,
        "doctor_name": doctor_name
    }).execute()


def get_visits_by_patient(patient_id, doctor_name):
    response = supabase.table("visits") \
        .select("*") \
        .eq("patient_id", patient_id) \
        .eq("doctor_name", doctor_name) \
        .order("visit_date", desc=True) \
        .execute()

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