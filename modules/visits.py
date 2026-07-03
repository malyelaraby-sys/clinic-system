from database.supabase_client import supabase


def add_visit(
    patient_id,
    doctor_name,
    chief_complaint="",
    history_present_illness="",
    examination="",
    assessment="",
    plan="",
    complaint="",
    diagnosis="",
    notes=""
):
    supabase.table("visits").insert({
        "patient_id": patient_id,
        "doctor_name": doctor_name,

        # New structure
        "chief_complaint": chief_complaint,
        "history_present_illness": history_present_illness,
        "examination": examination,
        "assessment": assessment,
        "plan": plan,

        # Legacy fields
        "complaint": complaint,
        "diagnosis": diagnosis,
        "notes": notes
    }).execute()


def get_visits_by_patient(patient_id, doctor_name):
    response = (
        supabase.table("visits")
        .select("*")
        .eq("patient_id", patient_id)
        .eq("doctor_name", doctor_name)
        .order("visit_date", desc=True)
        .execute()
    )

    visits = [
        (
            v["id"],
            v["patient_id"],
            v.get("visit_date", ""),

            # legacy
            v.get("complaint", ""),
            v.get("diagnosis", ""),
            v.get("notes", ""),

            # new structure
            v.get("chief_complaint", ""),
            v.get("history_present_illness", ""),
            v.get("examination", ""),
            v.get("assessment", ""),
            v.get("plan", "")
        )
        for v in response.data
    ]

    return visits