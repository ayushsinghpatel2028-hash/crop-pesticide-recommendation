import os
import requests
import streamlit as st
from typing import Optional, List, Dict, Any
from datetime import date

class APIClient:
    def __init__(self, base_url: Optional[str] = None):
        if base_url is None:
            self.base_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api")
        else:
            self.base_url = base_url

    def get_headers(self) -> Dict[str, str]:
        """Injects JWT auth token from session state if available."""
        headers = {}
        if "access_token" in st.session_state and st.session_state["access_token"]:
            headers["Authorization"] = f"Bearer {st.session_state['access_token']}"
        return headers

    def login(self, username: str, password: str) -> bool:
        """Sends credentials to exchange for token. Returns True on success."""
        try:
            response = requests.post(
                f"{self.base_url}/auth/token",
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state["access_token"] = data["access_token"]
                st.session_state["username"] = username
                return True
            else:
                st.session_state["login_error"] = response.json().get("detail", "Login failed.")
                return False
        except Exception as e:
            st.session_state["login_error"] = f"Could not connect to API server. ({e})"
            return False

    def logout(self):
        """Clears auth tokens from session state."""
        st.session_state["access_token"] = None
        st.session_state["username"] = None

    def change_password(self, old_password: str, new_password: str) -> Dict[str, Any]:
        """Requests backend to update password for current session user."""
        try:
            response = requests.put(
                f"{self.base_url}/auth/change-password",
                json={"old_password": old_password, "new_password": new_password},
                headers=self.get_headers()
            )
            return {"status": response.status_code, "data": response.json()}
        except Exception as e:
            return {"status": 500, "data": {"detail": str(e)}}

    # ==================== SUPPLIERS ====================
    def get_suppliers(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            params = {}
            if search:
                params["search"] = search
            response = requests.get(f"{self.base_url}/suppliers/", params=params, headers=self.get_headers())
            return response.json() if response.status_code == 200 else []
        except Exception:
            return []

    def create_supplier(self, name: str, phone: str, address: str) -> Dict[str, Any]:
        try:
            response = requests.post(
                f"{self.base_url}/suppliers/",
                json={"name": name, "phone": phone, "address": address},
                headers=self.get_headers()
            )
            return {"status": response.status_code, "data": response.json()}
        except Exception as e:
            return {"status": 500, "data": {"detail": str(e)}}

    def update_supplier(self, supplier_id: int, name: str, phone: str, address: str, is_active: bool) -> Dict[str, Any]:
        try:
            response = requests.put(
                f"{self.base_url}/suppliers/{supplier_id}",
                json={"name": name, "phone": phone, "address": address, "is_active": is_active},
                headers=self.get_headers()
            )
            return {"status": response.status_code, "data": response.json()}
        except Exception as e:
            return {"status": 500, "data": {"detail": str(e)}}

    def delete_supplier(self, supplier_id: int) -> bool:
        try:
            response = requests.delete(f"{self.base_url}/suppliers/{supplier_id}", headers=self.get_headers())
            return response.status_code == 200
        except Exception:
            return False

    # ==================== MILK ENTRIES ====================
    def get_milk_entries(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None, 
        supplier_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        try:
            params = {}
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
            if supplier_id and supplier_id > 0:
                params["supplier_id"] = supplier_id
                
            response = requests.get(f"{self.base_url}/milk/", params=params, headers=self.get_headers())
            return response.json() if response.status_code == 200 else []
        except Exception:
            return []

    def create_milk_entry(
        self, supplier_id: int, date_val: date, shift: str, quantity: float, fat: float, rate: float
    ) -> Dict[str, Any]:
        try:
            response = requests.post(
                f"{self.base_url}/milk/",
                json={
                    "supplier_id": supplier_id,
                    "date": date_val.isoformat(),
                    "shift": shift,
                    "quantity": quantity,
                    "fat": fat,
                    "rate": rate
                },
                headers=self.get_headers()
            )
            return {"status": response.status_code, "data": response.json()}
        except Exception as e:
            return {"status": 500, "data": {"detail": str(e)}}

    def update_milk_entry(
        self, entry_id: int, date_val: date, shift: str, quantity: float, fat: float, rate: float
    ) -> Dict[str, Any]:
        try:
            response = requests.put(
                f"{self.base_url}/milk/{entry_id}",
                json={
                    "date": date_val.isoformat(),
                    "shift": shift,
                    "quantity": quantity,
                    "fat": fat,
                    "rate": rate
                },
                headers=self.get_headers()
            )
            return {"status": response.status_code, "data": response.json()}
        except Exception as e:
            return {"status": 500, "data": {"detail": str(e)}}

    def delete_milk_entry(self, entry_id: int) -> bool:
        try:
            response = requests.delete(f"{self.base_url}/milk/{entry_id}", headers=self.get_headers())
            return response.status_code == 200
        except Exception:
            return False

    # ==================== PAYMENTS ====================
    def get_payments(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None, 
        supplier_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        try:
            params = {}
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
            if supplier_id and supplier_id > 0:
                params["supplier_id"] = supplier_id
                
            response = requests.get(f"{self.base_url}/payments", params=params, headers=self.get_headers())
            return response.json() if response.status_code == 200 else []
        except Exception:
            return []

    def create_payment(self, supplier_id: int, date_val: date, amount_paid: float, remarks: str) -> Dict[str, Any]:
        try:
            response = requests.post(
                f"{self.base_url}/payments",
                json={
                    "supplier_id": supplier_id,
                    "date": date_val.isoformat(),
                    "amount_paid": amount_paid,
                    "remarks": remarks
                },
                headers=self.get_headers()
            )
            return {"status": response.status_code, "data": response.json()}
        except Exception as e:
            return {"status": 500, "data": {"detail": str(e)}}

    def delete_payment(self, payment_id: int) -> bool:
        try:
            response = requests.delete(f"{self.base_url}/payments/{payment_id}", headers=self.get_headers())
            return response.status_code == 200
        except Exception:
            return False

    # ==================== ANALYTICS & REPORTS ====================
    def get_dashboard_stats(self) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(f"{self.base_url}/dashboard/stats", headers=self.get_headers())
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    def get_monthly_report(self, year: int, month: int) -> List[Dict[str, Any]]:
        try:
            params = {"year": year, "month": month}
            response = requests.get(f"{self.base_url}/reports/monthly", params=params, headers=self.get_headers())
            return response.json() if response.status_code == 200 else []
        except Exception:
            return []
