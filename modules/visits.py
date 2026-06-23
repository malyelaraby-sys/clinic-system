from database.db import connect_db

# ✅ Add a new visit
def add_visit(patient_id, complaint, diagnosis, notes):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO visits (patient_id, complaint, diagnosis, notes)
    VALUES (?, ?, ?, ?)
    """, (patient_id, complaint, diagnosis, notes))

    conn.commit()
    conn.close()


# ✅ Get all visits for a specific patient
def get_visits_by_patient(patient_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM visits
    WHERE patient_id = ?
    ORDER BY visit_date DESC
    """, (patient_id,))

    visits = cursor.fetchall()

    conn.close()
    return visits