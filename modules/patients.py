from database.supabase_client import supabase

def add_patient(name, phone, gender, doctor_name):
    supabase.table("patients").insert({
        "name": name,
        "phone": phone,
        "gender": gender,
        "doctor_name": doctor_name
    }).execute()


def get_all_patients(doctor_name):
    response = supabase.table("patients") \
        .select("*") \
        .eq("doctor_name", doctor_name) \
        .order("id") \
        .execute()

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