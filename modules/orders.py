from database.supabase_client import supabase


def add_order(
    visit_id,
    patient_id,
    doctor_name,
    order_type,
    order_text
):
    supabase.table("orders").insert({
        "visit_id": visit_id,
        "patient_id": patient_id,
        "doctor_name": doctor_name,
        "order_type": order_type,
        "order_text": order_text
    }).execute()


def get_orders_by_patient(patient_id, doctor_name):
    response = (
        supabase.table("orders")
        .select("*")
        .eq("patient_id", patient_id)
        .eq("doctor_name", doctor_name)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data


def get_orders_by_visit(visit_id):
    response = (
        supabase.table("orders")
        .select("*")
        .eq("visit_id", visit_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data