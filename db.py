# -*- coding: utf-8 -*-
"""Database layer: SQLAlchemy engine, session, models, and seed data."""
import os
import secrets
import string
from datetime import datetime, date

from sqlalchemy import (create_engine, Column, Integer, String, Float, Boolean,
                         DateTime, Date, ForeignKey, UniqueConstraint, ForeignKeyConstraint)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
import bcrypt

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "camp.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
Base = declarative_base()

MAX_ROOMS = 5
MAX_CAPACITY = 10


# ---------------------------------------------------------------- Models ---
class Admin(Base):
    __tablename__ = "administrators"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(128), default="")
    role = Column(String(20), default="admin")  # super_admin | admin
    can_manage_payments = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)
    number = Column(Integer, unique=True, nullable=False)
    name = Column(String(128), default="")
    capacity = Column(Integer, default=MAX_CAPACITY)
    bed_label = Column(String(50), default="place")
    participants = relationship("Participant", back_populates="room")


class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True)
    reg_id = Column(String(30), unique=True, nullable=False)
    qr_token = Column(String(64), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    wilaya = Column(String(100), default="")
    phone = Column(String(30), default="")
    transport = Column(String(30), default="no_transport")
    entry_date = Column(String(30), default="")
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    place_number = Column(Integer, nullable=True)
    subscription_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    notes = Column(String(500), default="")
    show_roommates_override = Column(Boolean, default=None, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("Room", back_populates="participants")
    attendances = relationship("Attendance", back_populates="participant", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("room_id", "place_number", name="uq_room_place"),)

    @property
    def payment_status(self):
        if self.paid_amount <= 0:
            return "unpaid"
        if self.paid_amount >= self.subscription_amount and self.subscription_amount > 0:
            return "paid"
        if self.subscription_amount == 0:
            return "paid"
        return "partial"

    @property
    def remaining_amount(self):
        return max(0.0, self.subscription_amount - self.paid_amount)


class AttendanceDay(Base):
    __tablename__ = "attendance_days"
    id = Column(Integer, primary_key=True)
    label = Column(String(100), nullable=False)
    day_date = Column(Date, default=date.today)


class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    day_id = Column(Integer, ForeignKey("attendance_days.id"), nullable=False)
    status = Column(String(20), default="present")
    recorded_by = Column(String(100), default="")
    recorded_at = Column(DateTime, default=datetime.utcnow)

    participant = relationship("Participant", back_populates="attendances")
    day = relationship("AttendanceDay")

    __table_args__ = (UniqueConstraint("participant_id", "day_id", name="uq_participant_day"),)


class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(String(2000), default="")
    priority = Column(String(20), default="normal")  # normal | important | urgent
    created_at = Column(DateTime, default=datetime.utcnow)


class CampInfo(Base):
    __tablename__ = "camp_information"
    id = Column(Integer, primary_key=True)
    key = Column(String(64), unique=True, nullable=False)
    value = Column(String(2000), default="")


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True)
    admin_name = Column(String(100), default="")
    action = Column(String(255), default="")
    timestamp = Column(DateTime, default=datetime.utcnow)


# --------------------------------------------------------------- Helpers ---
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(pw: str, pw_hash: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode("utf-8"), pw_hash.encode("utf-8"))
    except Exception:
        return False


def gen_token(n=24):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


def gen_reg_id(session):
    year = datetime.now().year
    count = session.query(Participant).count() + 1
    return f"CAMP-{year}-{count:04d}"


CAMP_INFO_DEFAULTS = {
    "camp_program": "",
    "start_date": "",
    "end_date": "",
    "camp_location": "",
    "gather_time": "",
    "gather_place": "",
    "access_instructions": "",
    "required_items": "",
    "rules": "",
    "important_info": "",
    "contact_numbers": "",
    "app_url": "",
    "show_roommates_global": "true",
}


def init_db():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        # Seed rooms
        if session.query(Room).count() == 0:
            for i in range(1, MAX_ROOMS + 1):
                session.add(Room(number=i, name=f"الغرفة {i}", capacity=MAX_CAPACITY, bed_label="place"))
        # Seed super admin
        if session.query(Admin).count() == 0:
            session.add(Admin(
                username="admin",
                password_hash=hash_password("admin123"),
                full_name="المدير الرئيسي",
                role="super_admin",
                can_manage_payments=True,
            ))
        # Seed camp info
        existing_keys = {c.key for c in session.query(CampInfo).all()}
        for k, v in CAMP_INFO_DEFAULTS.items():
            if k not in existing_keys:
                session.add(CampInfo(key=k, value=v))
        session.commit()
    finally:
        session.close()


def get_session():
    return SessionLocal()


def log_activity(session, admin_name: str, action: str):
    session.add(ActivityLog(admin_name=admin_name, action=action, timestamp=datetime.utcnow()))
    session.commit()
