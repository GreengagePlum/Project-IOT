"""Database table definitions

This file describes the models used and the Python mappings. These descriptions are used to create matching database
tables eventually and to access them from Python.
"""

from typing import List
from typing import Optional
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import CheckConstraint
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

PAYLOAD_separator = ";"


class Base(DeclarativeBase):
    pass


class Sensor(Base):
    __tablename__ = "sensor"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(30), unique=True)

    status: Mapped[bool]  # whether the ESP32 is currently online
    mac_address: Mapped[str] = mapped_column(String(17), unique=True)
    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(server_default=func.now())
    session_id: Mapped[str] = mapped_column(String(17))

    led_status: Mapped[List["LedStatus"]] = relationship(
        back_populates="sensor", cascade="all, delete-orphan"
    )
    button_status: Mapped[List["ButtonStatus"]] = relationship(
        back_populates="sensor", cascade="all, delete-orphan"
    )
    pres_status: Mapped[List["PhotoresistorStatus"]] = relationship(
        back_populates="sensor", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("joined_at <= last_seen"),
        CheckConstraint(
            "mac_address GLOB '[0-9A-Fa-f][0-9A-Fa-f]:[0-9A-Fa-f][0-9A-Fa-f]:[0-9A-Fa-f][0-9A-Fa-f]:[0-9A-Fa-f][0-9A-Fa-f]:[0-9A-Fa-f][0-9A-Fa-f]:[0-9A-Fa-f][0-9A-Fa-f]'"
        ),
        CheckConstraint("instr(name, '%s') = 0" % PAYLOAD_separator),
        CheckConstraint("instr(session_id, '%s') = 0" % PAYLOAD_separator),
    )

    def __repr__(self) -> str:
        return f"""
            Sensor(
                id={self.id!r},
                name={self.name!r},
                isActive={self.status!r},
                @MAC={self.mac_address!r},
                joined_at={self.joined_at!r},
                last_seen={self.last_seen!r},
                session_id={self.session_id!r}
            )"""


class BasicStatus:
    id: Mapped[int] = mapped_column(primary_key=True)
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensor.id"))
    date: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())
    status: Mapped[bool]

    def __repr__(self) -> str:
        return f"Status(id={self.id!r}, sensor_id={self.sensor_id!r}, status={self.status!r}, date={self.date!r})"


class PercentageStatus(BasicStatus):
    status: Mapped[int]

    __table_args__ = (CheckConstraint("0 <= status AND status <= 100"),)


class LedStatus(Base, BasicStatus):
    __tablename__ = "led_status"
    sensor: Mapped["Sensor"] = relationship(back_populates="led_status")

    def __repr__(self) -> str:
        return "Led" + super().__repr__()


class ButtonStatus(Base, BasicStatus):
    __tablename__ = "button_status"
    sensor: Mapped["Sensor"] = relationship(back_populates="button_status")

    def __repr__(self) -> str:
        return "Button" + super().__repr__()


class PhotoresistorStatus(Base, PercentageStatus):
    __tablename__ = "pres_status"
    sensor: Mapped["Sensor"] = relationship(back_populates="pres_status")

    def __repr__(self) -> str:
        return "Photoresistor" + super().__repr__()
