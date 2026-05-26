from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
import calendar
from typing import List, Optional
from . import models, schemas

# ==================== SUPPLIER CRUD ====================
def get_supplier(db: Session, supplier_id: int) -> Optional[models.Supplier]:
    return db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()

def get_suppliers(db: Session, search: Optional[str] = None) -> List[models.Supplier]:
    query = db.query(models.Supplier)
    if search:
        query = query.filter(models.Supplier.name.contains(search))
    return query.order_by(models.Supplier.name).all()

def create_supplier(db: Session, supplier: schemas.SupplierCreate) -> models.Supplier:
    db_supplier = models.Supplier(
        name=supplier.name,
        phone=supplier.phone,
        address=supplier.address,
        is_active=True
    )
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

def update_supplier(db: Session, supplier_id: int, supplier_data: schemas.SupplierUpdate) -> Optional[models.Supplier]:
    db_supplier = get_supplier(db, supplier_id)
    if not db_supplier:
        return None
    
    update_data = supplier_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_supplier, key, value)
        
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

def delete_supplier(db: Session, supplier_id: int) -> bool:
    db_supplier = get_supplier(db, supplier_id)
    if not db_supplier:
        return False
    db.delete(db_supplier)
    db.commit()
    return True


# ==================== MILK ENTRY CRUD ====================
def get_milk_entry(db: Session, entry_id: int) -> Optional[models.MilkEntry]:
    return db.query(models.MilkEntry).filter(models.MilkEntry.id == entry_id).first()

def get_milk_entries(
    db: Session, 
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None, 
    supplier_id: Optional[int] = None
) -> List[models.MilkEntry]:
    query = db.query(
        models.MilkEntry, 
        models.Supplier.name.label("supplier_name")
    ).join(models.Supplier, models.MilkEntry.supplier_id == models.Supplier.id)
    
    if start_date:
        query = query.filter(models.MilkEntry.date >= start_date)
    if end_date:
        query = query.filter(models.MilkEntry.date <= end_date)
    if supplier_id:
        query = query.filter(models.MilkEntry.supplier_id == supplier_id)
        
    results = query.order_by(models.MilkEntry.date.desc(), models.MilkEntry.shift.desc()).all()
    
    # Map label to model instance
    output = []
    for entry, supplier_name in results:
        entry.supplier_name = supplier_name
        output.append(entry)
    return output

def create_milk_entry(db: Session, entry: schemas.MilkEntryCreate) -> models.MilkEntry:
    # Auto-calculate total amount
    total_amount = round(entry.quantity * entry.rate, 2)
    db_entry = models.MilkEntry(
        supplier_id=entry.supplier_id,
        date=entry.date,
        shift=entry.shift,
        quantity=entry.quantity,
        fat=entry.fat,
        rate=entry.rate,
        total_amount=total_amount
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def update_milk_entry(db: Session, entry_id: int, entry_data: schemas.MilkEntryBase) -> Optional[models.MilkEntry]:
    db_entry = get_milk_entry(db, entry_id)
    if not db_entry:
        return None
        
    for key, value in entry_data.model_dump().items():
        setattr(db_entry, key, value)
    
    # Recalculate total
    db_entry.total_amount = round(db_entry.quantity * db_entry.rate, 2)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def delete_milk_entry(db: Session, entry_id: int) -> bool:
    db_entry = get_milk_entry(db, entry_id)
    if not db_entry:
        return False
    db.delete(db_entry)
    db.commit()
    return True


# ==================== PAYMENT CRUD ====================
def get_payments(
    db: Session, 
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None, 
    supplier_id: Optional[int] = None
) -> List[models.Payment]:
    query = db.query(
        models.Payment, 
        models.Supplier.name.label("supplier_name")
    ).join(models.Supplier, models.Payment.supplier_id == models.Supplier.id)
    
    if start_date:
        query = query.filter(models.Payment.date >= start_date)
    if end_date:
        query = query.filter(models.Payment.date <= end_date)
    if supplier_id:
        query = query.filter(models.Payment.supplier_id == supplier_id)
        
    results = query.order_by(models.Payment.date.desc()).all()
    
    output = []
    for payment, supplier_name in results:
        payment.supplier_name = supplier_name
        output.append(payment)
    return output

def create_payment(db: Session, payment: schemas.PaymentCreate) -> models.Payment:
    db_payment = models.Payment(
        supplier_id=payment.supplier_id,
        date=payment.date,
        amount_paid=payment.amount_paid,
        remarks=payment.remarks
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def delete_payment(db: Session, payment_id: int) -> bool:
    db_payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not db_payment:
        return False
    db.delete(db_payment)
    db.commit()
    return True


# ==================== COMPLEX REPORTING & CALCULATION ====================
def get_monthly_summary(db: Session, year: int, month: int) -> List[schemas.MonthlySummary]:
    """
    Returns monthly statistics (total milk, total dues, total paid) for the requested month,
    along with overall running pending balance (all-time due - all-time paid) for each supplier.
    """
    suppliers = db.query(models.Supplier).filter(models.Supplier.is_active == True).all()
    summary_list = []
    
    # Calculate start and end date of the target month
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    for s in suppliers:
        # 1. Milk supplied in the specified month
        month_milk_stats = db.query(
            func.sum(models.MilkEntry.quantity).label("total_milk"),
            func.sum(models.MilkEntry.total_amount).label("total_due")
        ).filter(
            models.MilkEntry.supplier_id == s.id,
            models.MilkEntry.date >= start_date,
            models.MilkEntry.date <= end_date
        ).first()
        
        total_milk = month_milk_stats.total_milk or 0.0
        total_due = month_milk_stats.total_due or 0.0
        
        # 2. Payments made in the specified month
        month_payments = db.query(
            func.sum(models.Payment.amount_paid).label("total_paid")
        ).filter(
            models.Payment.supplier_id == s.id,
            models.Payment.date >= start_date,
            models.Payment.date <= end_date
        ).first()
        
        total_paid = month_payments.total_paid or 0.0
        
        # 3. Overall / Running pending payment (All-time due - All-time paid)
        all_time_due = db.query(
            func.sum(models.MilkEntry.total_amount)
        ).filter(models.MilkEntry.supplier_id == s.id).scalar() or 0.0
        
        all_time_paid = db.query(
            func.sum(models.Payment.amount_paid)
        ).filter(models.Payment.supplier_id == s.id).scalar() or 0.0
        
        pending_payment = round(all_time_due - all_time_paid, 2)
        
        summary_list.append(
            schemas.MonthlySummary(
                supplier_id=s.id,
                supplier_name=s.name,
                phone=s.phone,
                total_milk=round(total_milk, 2),
                total_due=round(total_due, 2),
                total_paid=round(total_paid, 2),
                pending_payment=pending_payment
            )
        )
        
    return summary_list

def get_dashboard_stats(db: Session) -> schemas.DashboardStats:
    """Computes high-level KPIs to display on the dashboard."""
    today = date.today()
    
    # 1. Today's milk collected
    today_milk = db.query(func.sum(models.MilkEntry.quantity)).filter(models.MilkEntry.date == today).scalar() or 0.0
    
    # 2. Today's entries count
    today_count = db.query(models.MilkEntry).filter(models.MilkEntry.date == today).count()
    
    # 3. Active suppliers count
    active_count = db.query(models.Supplier).filter(models.Supplier.is_active == True).count()
    
    # 4. Total pending payment across all suppliers (all time)
    all_time_due = db.query(func.sum(models.MilkEntry.total_amount)).scalar() or 0.0
    all_time_paid = db.query(func.sum(models.Payment.amount_paid)).scalar() or 0.0
    total_pending = round(all_time_due - all_time_paid, 2)
    
    return schemas.DashboardStats(
        today_milk_liters=round(today_milk, 2),
        today_entries_count=today_count,
        active_suppliers_count=active_count,
        total_pending_amount=total_pending
    )
