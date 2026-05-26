from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..database import get_db
from .. import schemas, crud, auth, models

router = APIRouter(tags=["Payments & Analytics"])

# ==================== PAYMENT LEDGER ENDPOINTS ====================

@router.get("/payments", response_model=List[schemas.PaymentOut])
def read_payments(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    supplier_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Retrieves payment logs, with optional date and supplier filters."""
    return crud.get_payments(db, start_date=start_date, end_date=end_date, supplier_id=supplier_id)


@router.post("/payments", response_model=schemas.PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Logs a payment made to a supplier. Decreases their pending balance."""
    supplier = crud.get_supplier(db, payment.supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return crud.create_payment(db, payment=payment)


@router.delete("/payments/{payment_id}", status_code=status.HTTP_200_OK)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Deletes a payment record. Restores the pending balance owed to the supplier."""
    success = crud.delete_payment(db, payment_id=payment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Payment record not found")
    return {"message": "Payment record deleted successfully"}


# ==================== DASHBOARD & REPORT ENDPOINTS ====================

@router.get("/dashboard/stats", response_model=schemas.DashboardStats)
def read_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Retrieves live metrics for today's collection, active suppliers, and overall pending dues."""
    return crud.get_dashboard_stats(db)


@router.get("/reports/monthly", response_model=List[schemas.MonthlySummary])
def read_monthly_report(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Retrieves summary records for all active farmers for a specific month/year.
    Calculates total milk supplied, total amount due, payments made in month, and current pending dues.
    """
    return crud.get_monthly_summary(db, year=year, month=month)
