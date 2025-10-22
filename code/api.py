from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from .database import get_session
from . import models, crud
from . import auth
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict
from . import seed
from .database import Base, engine
from datetime import datetime, date

app = FastAPI(title='ADSWeb API', openapi_prefix='/adsweb/api/v1')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AddressOut(BaseModel):
    id: int
    street: str
    city: str
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]

    class Config:
        orm_mode = True


class AddressIn(BaseModel):
    street: str = Field(...)
    city: str = Field(...)
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None




class PatientIn(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: Optional[str] = None
    phone: Optional[str] = None
    address_id: Optional[int] = None


class PatientOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[AddressOut]

    class Config:
        orm_mode = True

class AppointmentIn(BaseModel):
    patient_id: int = Field(..., description="ID of the patient")
    dentist_id: int
    surgery_id: Optional[int] = None
    scheduled_at: datetime
    notes: Optional[str] = None

class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    dentist_id: int
    surgery_id: Optional[int] = None
    scheduled_at: datetime
    notes: Optional[str] = None

    class Config:
        orm_mode = True

# --- Dentist ---
class DentistIn(BaseModel):
    first_name: str
    last_name: str
    specialty: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address_id: Optional[int]

class DentistOut(BaseModel):
    id: int
    class Config:
        orm_mode = True
      
# --- Surgery ---
class SurgeryIn(BaseModel):
    title: str
    description: Optional[str]

class SurgeryOut(BaseModel):
    id: int
    class Config:
        orm_mode = str
    
def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@app.get('/patients', response_model=List[PatientOut])
def list_patients(db: Session = Depends(get_db)):
    patients = db.query(models.Patient).join(models.Address, isouter=True).order_by(models.Patient.last_name.asc()).all()
    return patients


@app.get('/patients/{patient_id}', response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    p = crud.get_patient(db, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail='Patient not found')
    return p


@app.post('/patients', response_model=PatientOut, status_code=201)
def create_patient(patient: PatientIn, db: Session = Depends(get_db), user: models.User = Depends(auth.require_roles(['admin','staff']))):
    p = crud.create_patient(db, **patient.dict())
    return p


@app.put('/patient/{patient_id}', response_model=PatientOut)
def update_patient(patient_id: int, patient: PatientIn, db: Session = Depends(get_db), user: models.User = Depends(auth.require_roles(['admin','staff']))):
    existing = crud.get_patient(db, patient_id)
    if not existing:
        raise HTTPException(status_code=404, detail='Patient not found')
    updated = crud.update_patient(db, patient_id, **patient.dict())
    return updated


@app.delete('/patient/{patient_id}', status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.require_roles(['admin']))):
    ok = crud.delete_patient(db, patient_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Patient not found')
    return None


@app.post('/auth/register', status_code=201)
def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    # create a role 'user' if not exists
    # store hashed password
    hashed = auth.get_password_hash(password)
    # ensure 'user' role exists and assign to the new user
    from . import models
    # create user
    user = crud.create_user(db, username=username, email=email, full_name=username, hashed_password=hashed)
    # find or create 'user' role and attach
    r = db.query(models.Role).filter_by(name='user').first()
    if not r:
        r = crud.create_role(db, name='user', description='Regular user')
    user.roles.append(r)
    db.commit()
    return {"id": user.id, "username": user.username}


@app.on_event('startup')
def startup_event():
    # create tables and seed roles/admin if configured
    try:
        Base.metadata.create_all(bind=engine)
        seed.seed_initial_data()
    except Exception as e:
        # don't fail startup; just log
        import logging
        logging.exception('Seeding initial data failed: %s', e)


@app.post('/auth/token')
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail='Incorrect username or password')
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get('/patient/search/{search_string}', response_model=List[PatientOut])
def search_patients(search_string: str, db: Session = Depends(get_db)):
    s = f"%{search_string}%"
    results = db.query(models.Patient).filter(
        (models.Patient.first_name.ilike(s)) |
        (models.Patient.last_name.ilike(s)) |
        (models.Patient.email.ilike(s)) |
        (models.Patient.phone.ilike(s))
    ).order_by(models.Patient.last_name.asc()).all()
    return results


@app.get('/addresses', response_model=List[AddressOut])
def list_addresses(db: Session = Depends(get_db)):
    addrs = db.query(models.Address).order_by(models.Address.city.asc()).all()
    return addrs


@app.post('/addresses', response_model=AddressOut, status_code=201)
def create_address(address: AddressIn, db: Session = Depends(get_db), user: models.User = Depends(auth.require_roles(['admin','staff']))):
    a = crud.create_address(db, **address.dict())
    return a

@app.post("/appointments", response_model=AppointmentOut, status_code=201)
def add_appointment(appointment: AppointmentIn, db: Session = Depends(get_db), user: models.User = Depends(auth.require_roles(['admin','staff']))):
    if not db.query(models.Patient).filter(models.Patient.id == appointment.patient_id).first():
        raise HTTPException(status_code=404, detail="Patient not found")
    if not db.query(models.Dentist).filter(models.Dentist.id == appointment.dentist_id).first():
        raise HTTPException(status_code=404, detail="Dentist not found")
    if appointment.surgery_id and not db.query(models.Surgery).filter(models.Surgery.id == appointment.surgery_id).first():
        raise HTTPException(status_code=404, detail="Surgery not found")

    new_appointment = models.Appointment(**appointment.dict())
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

@app.post('/surgeries', response_model=SurgeryOut, status_code=201)
def create_surgery(surgery: SurgeryIn, db: Session = Depends(get_db)):
    new_surgery = models.Surgery(**surgery.dict())
    db.add(new_surgery)
    db.commit()
    db.refresh(new_surgery)
    return new_surgery

@app.post('/dentists', response_model=DentistOut, status_code=201)
def create_dentist(dentist: DentistIn, db: Session = Depends(get_db)):
    new_dentist = models.Dentist(**dentist.dict())
    db.add(new_dentist)
    db.commit()
    db.refresh(new_dentist)
    return new_dentist