"""Simple Firestore-based repository for selected entities.

This module provides minimal CRUD helpers to get started migrating data to Firestore.
It intentionally mirrors a subset of the SQLAlchemy models as dictionaries.
"""
from datetime import datetime
from typing import Optional, Dict, Any

from dados.firebase_client import get_firestore_client


def _now():
    return datetime.utcnow()


def create_patient(data: Dict[str, Any]) -> str:
    db = get_firestore_client()
    patients = db.collection("patients")
    doc_ref = patients.document()
    # enrich with timestamps
    payload = dict(data)
    payload.setdefault("created_at", _now())
    payload.setdefault("status", "Ativo")
    doc_ref.set(payload)
    return doc_ref.id


def get_patient(patient_id: str) -> Optional[Dict[str, Any]]:
    db = get_firestore_client()
    doc = db.collection("patients").document(patient_id).get()
    if not doc.exists:
        return None
    return {"id": doc.id, **doc.to_dict()}


def update_patient(patient_id: str, data: Dict[str, Any]) -> bool:
    db = get_firestore_client()
    doc_ref = db.collection("patients").document(patient_id)
    doc = doc_ref.get()
    if not doc.exists:
        return False
    data["updated_at"] = _now()
    doc_ref.update(data)
    return True


def list_patients(limit: int = 50):
    db = get_firestore_client()
    docs = db.collection("patients").limit(limit).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]


# Similar helpers can be added for consultations, users, clinical_records, etc.
