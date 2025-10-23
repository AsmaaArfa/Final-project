from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Table,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Association table for many-to-many User <-> Role
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
)


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    street = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)

    # Backrefs
    patients = relationship('Patient', back_populates='address')
    dentists = relationship('Dentist', back_populates='address')

    def __repr__(self):
        return f"<Address(id={self.id}, street={self.street}, city={self.city})>"


class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=True, unique=True)
    phone = Column(String(50), nullable=True)
    address_id = Column(Integer, ForeignKey('addresses.id'), nullable=True)

    address = relationship('Address', back_populates='patients')
    appointments = relationship('Appointment', back_populates='patient', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Patient(id={self.id}, name={self.first_name} {self.last_name})>"


class Dentist(Base):
    __tablename__ = 'dentists'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialty = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True, unique=True)
    phone = Column(String(50), nullable=True)
    address_id = Column(Integer, ForeignKey('addresses.id'), nullable=True)

    address = relationship('Address', back_populates='dentists')
    appointments = relationship('Appointment', back_populates='dentist', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Dentist(id={self.id}, name={self.first_name} {self.last_name})>"


class Surgery(Base):
    __tablename__ = 'surgeries'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    appointments = relationship('Appointment', back_populates='surgery')

    def __repr__(self):
        return f"<Surgery(id={self.id}, title={self.title})>"


class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    dentist_id = Column(Integer, ForeignKey('dentists.id'), nullable=False)
    surgery_id = Column(Integer, ForeignKey('surgeries.id'), nullable=True)
    scheduled_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    patient = relationship('Patient', back_populates='appointments')
    dentist = relationship('Dentist', back_populates='appointments')
    surgery = relationship('Surgery', back_populates='appointments')

    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, dentist_id={self.dentist_id})>"


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    users = relationship('User', secondary=user_roles, back_populates='roles')

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    full_name = Column(String(200), nullable=True)
    hashed_password = Column(String(300), nullable=False)

    roles = relationship('Role', secondary=user_roles, back_populates='users')

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
