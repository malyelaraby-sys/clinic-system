from database.supabase_client import supabase

def add_patient(
    name,
    phone,
    gender,
    doctor_name,
    birth_date,
    national_id,
    address,
    emergency_contact,
    allergies,
    chronic_diseases
):
    supabase.table("patients").insert({
        "name": name,
        "phone": phone,
        "gender": gender,
        "doctor_name": doctor_name,
        "birth_date": birth_date,
        "national_id": national_id,
        "address": address,
        "emergency_contact": emergency_contact,
        "allergies": allergies,
        "chronic_diseases": chronic_diseases
    }).execute()


def get_all_patients(doctor_name):
    response = (
        supabase.table("patients")
        .select("*")
        .eq("doctor_name", doctor_name)
        .order("id")
        .execute()
    )

    patients = [
        (
            p["id"],
            p["name"],
            p.get("phone", ""),
            p.get("gender", ""),
            p.get("birth_date", ""),
            p.get("national_id", ""),
            p.get("address", ""),
            p.get("emergency_contact", ""),
            p.get("allergies", ""),
            p.get("chronic_diseases", ""),
            p.get("created_at", "")
        )
        for p in response.data
    ]

    return patients