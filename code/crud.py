from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
import models
from typing import Optional, List, Dict, Any


def create_address(db: Session, **data) -> models.Address:
    addr = models.Address(**data)
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return addr


def get_address(db: Session, address_id: int) -> Optional[models.Address]:
    return db.get(models.Address, address_id)


def update_address(db: Session, address_id: int, **changes) -> Optional[models.Address]:
    obj = db.get(models.Address, address_id)
    if not obj:
        return None
    for k, v in changes.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_address(db: Session, address_id: int) -> bool:
    obj = db.get(models.Address, address_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# Patients
def create_patient(db: Session, **data) -> models.Patient:
    p = models.Patient(**data)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def get_patient(db: Session, patient_id: int) -> Optional[models.Patient]:
    return db.get(models.Patient, patient_id)


def list_patients(db: Session, limit: int = 100) -> List[models.Patient]:
    return db.execute(select(models.Patient).limit(limit)).scalars().all()


def update_patient(db: Session, patient_id: int, **changes) -> Optional[models.Patient]:
    obj = db.get(models.Patient, patient_id)
    if not obj:
        return None
    for k, v in changes.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_patient(db: Session, patient_id: int) -> bool:
    obj = db.get(models.Patient, patient_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# Dentists
def create_dentist(db: Session, **data) -> models.Dentist:
    d = models.Dentist(**data)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def get_dentist(db: Session, dentist_id: int) -> Optional[models.Dentist]:
    return db.get(models.Dentist, dentist_id)


def list_dentists(db: Session, limit: int = 100) -> List[models.Dentist]:
    return db.execute(select(models.Dentist).limit(limit)).scalars().all()


def update_dentist(db: Session, dentist_id: int, **changes) -> Optional[models.Dentist]:
    obj = db.get(models.Dentist, dentist_id)
    if not obj:
        return None
    for k, v in changes.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_dentist(db: Session, dentist_id: int) -> bool:
    obj = db.get(models.Dentist, dentist_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# Surgeries
def create_surgery(db: Session, **data) -> models.Surgery:
    s = models.Surgery(**data)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def get_surgery(db: Session, surgery_id: int) -> Optional[models.Surgery]:
    return db.get(models.Surgery, surgery_id)


def update_surgery(db: Session, surgery_id: int, **changes) -> Optional[models.Surgery]:
    obj = db.get(models.Surgery, surgery_id)
    if not obj:
        return None
    for k, v in changes.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_surgery(db: Session, surgery_id: int) -> bool:
    obj = db.get(models.Surgery, surgery_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# Appointments
def create_appointment(db: Session, **data) -> models.Appointment:
    a = models.Appointment(**data)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def get_appointment(db: Session, appointment_id: int) -> Optional[models.Appointment]:
    return db.get(models.Appointment, appointment_id)


def list_appointments(db: Session, limit: int = 100) -> List[models.Appointment]:
    return db.execute(select(models.Appointment).limit(limit)).scalars().all()


def update_appointment(db: Session, appointment_id: int, **changes) -> Optional[models.Appointment]:
    obj = db.get(models.Appointment, appointment_id)
    if not obj:
        return None
    for k, v in changes.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_appointment(db: Session, appointment_id: int) -> bool:
    obj = db.get(models.Appointment, appointment_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# Users and Roles
def create_role(db: Session, **data) -> models.Role:
    r = models.Role(**data)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def create_user(db: Session, **data) -> models.User:
    # roles can be provided as list of Role objects or role ids
    roles = data.pop('roles', None)
    u = models.User(**data)
    if roles:
        for role in roles:
            if isinstance(role, models.Role):
                u.roles.append(role)
            else:
                r = db.get(models.Role, int(role))
                if r:
                    u.roles.append(r)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.get(models.User, user_id)


def update_user(db: Session, user_id: int, **changes) -> Optional[models.User]:
    obj = db.get(models.User, user_id)
    if not obj:
        return None
    roles = changes.pop('roles', None)
    for k, v in changes.items():
        setattr(obj, k, v)
    if roles is not None:
        obj.roles.clear()
        for role in roles:
            if isinstance(role, models.Role):
                obj.roles.append(role)
            else:
                r = db.get(models.Role, int(role))
                if r:
                    obj.roles.append(r)
    db.commit()
    db.refresh(obj)
    return obj


def delete_user(db: Session, user_id: int) -> bool:
    obj = db.get(models.User, user_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
