from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

# ==================== AUTH SCHEMAS ====================
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


# ==================== SUPPLIER SCHEMAS ====================
class SupplierBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

class SupplierOut(SupplierBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


# ==================== MILK ENTRY SCHEMAS ====================
class MilkEntryBase(BaseModel):
    date: date
    shift: str = Field(..., pattern="^(Morning|Evening)$")
    quantity: float = Field(..., gt=0, description="Quantity in liters")
    fat: float = Field(..., ge=0, le=100, description="Fat percentage")
    rate: float = Field(..., ge=0, description="Rate per liter")

class MilkEntryCreate(MilkEntryBase):
    supplier_id: int

class MilkEntryOut(MilkEntryBase):
    id: int
    supplier_id: int
    total_amount: float
    supplier_name: Optional[str] = None  # Helper for display in UI

    class Config:
        from_attributes = True


# ==================== PAYMENT SCHEMAS ====================
class PaymentBase(BaseModel):
    date: date
    amount_paid: float = Field(..., gt=0)
    remarks: Optional[str] = Field(None, max_length=255)

class PaymentCreate(PaymentBase):
    supplier_id: int

class PaymentOut(PaymentBase):
    id: int
    supplier_id: int
    supplier_name: Optional[str] = None  # Helper for display in UI

    class Config:
        from_attributes = True


# ==================== AGGREGATED SCHEMAS ====================
class MonthlySummary(BaseModel):
    supplier_id: int
    supplier_name: str
    phone: Optional[str] = None
    total_milk: float
    total_due: float
    total_paid: float
    pending_payment: float

class DashboardStats(BaseModel):
    today_milk_liters: float
    today_entries_count: int
    active_suppliers_count: int
    total_pending_amount: float
