from dados.database import SessionLocal
from security.encription import encrypt_text, decrypt_text
from dados.models import ClinicalRecord



def create_record(data):

    db = SessionLocal()

    record = ClinicalRecord(
        patient_id=data["patient_id"],
        user_id=data["user_id"],
        content=encrypt_text(
            data["content"]
        )
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    db.close()

    return record

def decrypt_records(records):

    for record in records:
        record.content = decrypt_text(
            record.content
        )

    return decrypt_records(records)

def get_patient_records(patient_id):

    db = SessionLocal()

    records = (

        db.query(
            ClinicalRecord
        )

        .filter(ClinicalRecord.patient_id==patient_id)

        .order_by(
            ClinicalRecord.created_at.desc()
        )

        .all()
    )

    db.close()

    return records



def delete_record(record_id):

    db = SessionLocal()

    record = (
        db.query(
            ClinicalRecord
        )

        .filter(

            ClinicalRecord.id == record_id
        )

        .first()
    )

    if record:
        db.delete(record)
        db.commit()


    db.close()