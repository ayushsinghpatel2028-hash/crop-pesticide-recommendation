from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships - cascade delete removes all milk logs/payments if a supplier is deleted
    milk_entries = relationship("MilkEntry", back_populates="supplier", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="supplier", cascade="all, delete-orphan")


class MilkEntry(Base):
    __tablename__ = "milk_entries"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, index=True, nullable=False)
    shift = Column(String, nullable=False)  # "Morning" or "Evening"
    quantity = Column(Float, nullable=False)  # in Liters
    fat = Column(Float, nullable=False)       # Fat percentage
    rate = Column(Float, nullable=False)      # Price per liter
    total_amount = Column(Float, nullable=False) # Automatically calculated: quantity * rate

    # Relationship
    supplier = relationship("Supplier", back_populates="milk_entries")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    amount_paid = Column(Float, nullable=False)
    remarks = Column(String, nullable=True)

    # Relationship
    supplier = relationship("Supplier", back_populates="payments")
