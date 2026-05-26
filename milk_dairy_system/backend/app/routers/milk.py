from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..database import get_db
from .. import schemas, crud, auth, models

router = APIRouter(prefix="/milk", tags=["Milk Entries"])

@router.get("/", response_model=List[schemas.MilkEntryOut])
def read_milk_entries(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    supplier_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Fetches list of daily milk entries, with optional date and supplier filters."""
    return crud.get_milk_entries(db, start_date=start_date, end_date=end_date, supplier_id=supplier_id)


@router.get("/{entry_id}", response_model=schemas.MilkEntryOut)
def read_milk_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Gets details for a specific milk entry."""
    db_entry = crud.get_milk_entry(db, entry_id=entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Milk entry not found")
    return db_entry


@router.post("/", response_model=schemas.MilkEntryOut, status_code=status.HTTP_201_CREATED)
def create_milk_entry(
    entry: schemas.MilkEntryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Records a new daily milk entry (Morning or Evening). Automatically calculates total payment due."""
    # Ensure supplier exists
    supplier = crud.get_supplier(db, entry.supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return crud.create_milk_entry(db, entry=entry)


@router.put("/{entry_id}", response_model=schemas.MilkEntryOut)
def update_milk_entry(
    entry_id: int,
    entry: schemas.MilkEntryBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Edits a previously recorded milk entry, automatically updating the total cost."""
    db_entry = crud.update_milk_entry(db, entry_id=entry_id, entry_data=entry)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Milk entry not found")
    return db_entry


@router.delete("/{entry_id}", status_code=status.HTTP_200_OK)
def delete_milk_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Removes a milk entry record."""
    success = crud.delete_milk_entry(db, entry_id=entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Milk entry not found")
    return {"message": "Milk entry deleted successfully"}
