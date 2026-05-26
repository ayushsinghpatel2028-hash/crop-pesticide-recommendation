import streamlit as st
import pandas as pd
from datetime import date, datetime
import io
import time
from api_client import APIClient

# Page configuration
st.set_page_config(
    page_title="Milk Dairy Management System",
    page_icon="🥛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API Client
if "api" not in st.session_state:
    st.session_state["api"] = APIClient()

api = st.session_state["api"]

# Inject custom CSS
def load_css():
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback if styling file is not found
        pass

load_css()

# Helper: local currency formatter
def format_currency(val):
    return f"₹{val:,.2f}"

# ==================== AUTHENTICATION SCREEN ====================
if "access_token" not in st.session_state or not st.session_state["access_token"]:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<h1 class='login-title'>🥛 Milk Dairy Admin</h1>", unsafe_allow_html=True)
    st.markdown("<p class='login-subtitle'>Enter credentials to access the dairy manager</p>", unsafe_allow_html=True)
    
    username_input = st.text_input("Username", placeholder="e.g. admin")
    password_input = st.text_input("Password", type="password", placeholder="e.g. admin123")
    
    if st.button("Log In", type="primary", use_container_width=True):
        if not username_input or not password_input:
            st.error("Please enter both username and password.")
        else:
            success = api.login(username_input, password_input)
            if success:
                st.success("Access Granted! Loading system...")
                time.sleep(1)
                st.rerun()
            else:
                st.error(st.session_state.get("login_error", "Incorrect username or password."))
                
    st.markdown("<p style='color:#94a3b8; font-size:0.8rem; margin-top:20px;'>Securely running SQLite database backplane</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==================== LOGGED IN APPLICATION ====================

# Sidebar navigation
with st.sidebar:
    st.markdown("<div style='text-align: center; padding: 15px 0;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1e3a8a; margin-bottom:5px;'>🥛 Dairy Manager</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#475569;'>Signed in: <b>{st.session_state.get('username', 'Admin')}</b></p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---", unsafe_allow_html=True)

    page = st.radio(
        "Navigation Menu",
        ["📊 Dashboard", "👥 Supplier Directory", "🥛 Milk Entry Log", "💸 Payment Ledger", "📅 Monthly Reports", "⚙️ Settings"],
        index=0
    )
    
    st.markdown("---", unsafe_allow_html=True)
    if st.button("🚪 Log Out", use_container_width=True):
        api.logout()
        st.rerun()

# ==================== 1. DASHBOARD PAGE ====================
if page == "📊 Dashboard":
    st.markdown("<h1 style='color:#1e3a8a; margin-bottom:5px;'>📊 Dairy Overview</h1>", unsafe_allow_html=True)
    st.write(f"Live overview for today: **{date.today().strftime('%A, %d %B %Y')}**")
    st.markdown("---", unsafe_allow_html=True)
    
    stats = api.get_dashboard_stats()
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='kpi-card kpi-blue'>
                <div class='kpi-value'>{stats.get('today_milk_liters', 0.0)} L</div>
                <div class='kpi-label'>Milk Collected Today</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class='kpi-card kpi-green'>
                <div class='kpi-value'>{stats.get('today_entries_count', 0)}</div>
                <div class='kpi-label'>Farmers Logged Today</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class='kpi-card kpi-orange'>
                <div class='kpi-value'>{stats.get('active_suppliers_count', 0)}</div>
                <div class='kpi-label'>Active Farmers</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class='kpi-card kpi-rose'>
                <div class='kpi-value'>{format_currency(stats.get('total_pending_amount', 0.0))}</div>
                <div class='kpi-label'>Total Owed Balance</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Could not load dashboard statistics. Ensure your FastAPI server is online.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3>🥛 Live Daily Entry Log</h3>", unsafe_allow_html=True)
    
    # Get today's entries
    today_entries = api.get_milk_entries(start_date=date.today(), end_date=date.today())
    if today_entries:
        df_today = pd.DataFrame(today_entries)
        df_today = df_today.rename(columns={
            "supplier_name": "Supplier Name",
            "shift": "Shift",
            "quantity": "Quantity (Ltrs)",
            "fat": "Fat %",
            "rate": "Rate (per L)",
            "total_amount": "Total Value (₹)"
        })
        st.dataframe(df_today[["Supplier Name", "Shift", "Quantity (Ltrs)", "Fat %", "Rate (per L)", "Total Value (₹)"]], use_container_width=True, hide_index=True)
    else:
        st.info("No milk entries logged for today yet. Use the 'Milk Entry Log' tab to record entries.")

# ==================== 2. SUPPLIER DIRECTORY ====================
elif page == "👥 Supplier Directory":
    st.markdown("<h1 style='color:#1e3a8a;'>👥 Supplier / Farmer Directory</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔍 View & Search Suppliers", "➕ Add New Supplier"])
    
    # Tab 1: List and Edit Suppliers
    with tab1:
        search_query = st.text_input("🔍 Search farmer by name", placeholder="Start typing name...")
        suppliers = api.get_suppliers(search=search_query)
        
        if suppliers:
            df_sup = pd.DataFrame(suppliers)
            df_sup_display = df_sup.rename(columns={
                "id": "Supplier ID",
                "name": "Supplier Name",
                "phone": "Phone Number",
                "address": "Address",
                "is_active": "Is Active"
            })
            
            st.write(f"Found **{len(suppliers)}** suppliers:")
            st.dataframe(df_sup_display[["Supplier ID", "Supplier Name", "Phone Number", "Address", "Is Active"]], use_container_width=True, hide_index=True)
            
            st.markdown("---", unsafe_allow_html=True)
            st.markdown("### ✏️ Edit or Delete Supplier")
            
            selected_supplier_id = st.selectbox(
                "Select a Supplier to Modify",
                options=[s["id"] for s in suppliers],
                format_func=lambda sid: next(s["name"] for s in suppliers if s["id"] == sid)
            )
            
            if selected_supplier_id:
                curr_sup = next(s for s in suppliers if s["id"] == selected_supplier_id)
                
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Name", value=curr_sup["name"], key="edit_name")
                    new_phone = st.text_input("Phone", value=curr_sup["phone"] or "", key="edit_phone")
                with col2:
                    new_address = st.text_input("Address", value=curr_sup["address"] or "", key="edit_addr")
                    new_status = st.toggle("Active Status", value=curr_sup["is_active"], key="edit_status")
                
                edit_col, delete_col = st.columns([1, 4])
                with edit_col:
                    if st.button("Save Changes", type="primary"):
                        res = api.update_supplier(selected_supplier_id, new_name, new_phone, new_address, new_status)
                        if res["status"] == 200:
                            st.success("Supplier updated successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(res["data"].get("detail", "Error updating supplier."))
                            
                with delete_col:
                    if "confirm_delete" not in st.session_state:
                        st.session_state["confirm_delete"] = False
                        
                    if not st.session_state["confirm_delete"]:
                        if st.button("🚨 Delete Supplier", key="trigger_del"):
                            st.session_state["confirm_delete"] = True
                            st.rerun()
                    else:
                        st.write("⚠️ **Are you sure?** Deleting this farmer will instantly delete all of their daily milk logs and payments records. This action **cannot** be undone.")
                        col_yes, col_no = st.columns([1, 12])
                        with col_yes:
                            if st.button("Yes, Delete", key="yes_del"):
                                success = api.delete_supplier(selected_supplier_id)
                                if success:
                                    st.success("Supplier and all related history deleted successfully!")
                                    st.session_state["confirm_delete"] = False
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Error deleting supplier.")
                        with col_no:
                            if st.button("Cancel", key="cancel_del"):
                                st.session_state["confirm_delete"] = False
                                st.rerun()
        else:
            st.info("No suppliers found in directory.")
            
    # Tab 2: Create Supplier
    with tab2:
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        st.write("### Register a new supplier")
        
        sup_name = st.text_input("Full Name *", placeholder="Enter farmer's full name")
        sup_phone = st.text_input("Phone Number", placeholder="e.g. 9876543210")
        sup_address = st.text_area("Home Address", placeholder="e.g. Village Rampur, District Patna")
        
        if st.button("Add Supplier", type="primary"):
            if not sup_name:
                st.error("Supplier Name is required.")
            else:
                res = api.create_supplier(sup_name, sup_phone, sup_address)
                if res["status"] in [200, 201]:
                    st.success(f"Farmer '{sup_name}' added successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(res["data"].get("detail", "Error creating supplier."))
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== 3. MILK ENTRY LOG ====================
elif page == "🥛 Milk Entry Log":
    st.markdown("<h1 style='color:#1e3a8a;'>🥛 Daily Milk Collection Entry</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 Add Daily Entry", "🔍 View & Filter Milk Logs"])
    
    suppliers = api.get_suppliers()
    
    # Tab 1: New Milk Entry
    with tab1:
        if not suppliers:
            st.warning("Please register at least one Supplier in the directory before adding milk entries.")
        else:
            st.markdown("<div class='form-container'>", unsafe_allow_html=True)
            st.write("### Record new milk yield")
            
            col1, col2 = st.columns(2)
            with col1:
                entry_date = st.date_input("Date", date.today())
                entry_shift = st.selectbox("Shift", ["Morning", "Evening"])
                
                supplier_options = {s["id"]: s["name"] for s in suppliers if s["is_active"]}
                selected_supplier = st.selectbox(
                    "Farmer Name *",
                    options=list(supplier_options.keys()),
                    format_func=lambda sid: supplier_options[sid]
                )
                
            with col2:
                quantity = st.number_input("Milk Quantity (Liters) *", min_value=0.1, max_value=500.0, value=10.0, step=0.5)
                fat_pct = st.number_input("Fat Percentage (%) *", min_value=0.0, max_value=15.0, value=4.0, step=0.1)
                
                # Estimate Rate or manual input
                # Simple dairy formula for beginners: standard base rate + fat bonus (e.g. fat * 6.5)
                est_rate = round(25.0 + (fat_pct * 5.0), 2)
                rate = st.number_input("Rate per Liter (₹) *", min_value=0.0, max_value=150.0, value=est_rate, step=0.5)
            
            # Interactive automatic preview
            total_est = round(quantity * rate, 2)
            st.markdown(f"**💰 Estimated Total Amount:** <span style='font-size:1.3rem; color:#10b981; font-weight:700;'>{format_currency(total_est)}</span>", unsafe_allow_html=True)
            
            if st.button("Log Entry", type="primary"):
                res = api.create_milk_entry(
                    supplier_id=selected_supplier,
                    date_val=entry_date,
                    shift=entry_shift,
                    quantity=quantity,
                    fat=fat_pct,
                    rate=rate
                )
                if res["status"] in [200, 201]:
                    st.success("Daily entry logged successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(res["data"].get("detail", "Error logging entry."))
            st.markdown("</div>", unsafe_allow_html=True)
            
    # Tab 2: Filter Milk Logs
    with tab2:
        st.write("### Filter & Search Milk Logs")
        col1, col2, col3 = st.columns(3)
        with col1:
            f_start = st.date_input("Start Date", date.today().replace(day=1))
        with col2:
            f_end = st.date_input("End Date", date.today())
        with col3:
            # Dropdown options with 'All'
            sup_filter_options = {0: "--- All Farmers ---"}
            for s in suppliers:
                sup_filter_options[s["id"]] = s["name"]
            f_supplier = st.selectbox("Filter by Farmer", options=list(sup_filter_options.keys()), format_func=lambda sid: sup_filter_options[sid])
            
        logs = api.get_milk_entries(start_date=f_start, end_date=f_end, supplier_id=f_supplier)
        
        if logs:
            df_logs = pd.DataFrame(logs)
            df_logs_display = df_logs.rename(columns={
                "id": "Entry ID",
                "date": "Date",
                "supplier_name": "Farmer Name",
                "shift": "Shift",
                "quantity": "Quantity (L)",
                "fat": "Fat %",
                "rate": "Rate (₹/L)",
                "total_amount": "Total Amount (₹)"
            })
            
            st.write(f"Showing **{len(logs)}** milk collection logs:")
            st.dataframe(df_logs_display[["Entry ID", "Date", "Farmer Name", "Shift", "Quantity (L)", "Fat %", "Rate (₹/L)", "Total Amount (₹)"]], use_container_width=True, hide_index=True)
            
            st.markdown("---", unsafe_allow_html=True)
            st.markdown("### 🚨 Delete Milk Entry Log")
            entry_to_del = st.selectbox("Select Entry ID to Delete", options=df_logs["id"].tolist())
            if entry_to_del:
                if st.button("Delete Selected Entry"):
                    success = api.delete_milk_entry(entry_to_del)
                    if success:
                        st.success("Milk log deleted successfully.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Error deleting log.")
        else:
            st.info("No logs found for the selected date range.")

# ==================== 4. PAYMENT LEDGER ====================
elif page == "💸 Payment Ledger":
    st.markdown("<h1 style='color:#1e3a8a;'>💸 Payment Voucher & Ledger</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["💳 Make Payment", "📜 Payment History Ledger"])
    
    suppliers = api.get_suppliers()
    
    # Tab 1: Make Payment
    with tab1:
        if not suppliers:
            st.warning("Please register at least one Supplier in the directory before logging payments.")
        else:
            st.markdown("<div class='form-container'>", unsafe_allow_html=True)
            st.write("### Issue payment to farmer")
            
            col1, col2 = st.columns(2)
            with col1:
                pay_date = st.date_input("Payment Date", date.today(), key="pay_date")
                
                supplier_options = {s["id"]: s["name"] for s in suppliers if s["is_active"]}
                pay_supplier = st.selectbox(
                    "Farmer Name *",
                    options=list(supplier_options.keys()),
                    format_func=lambda sid: supplier_options[sid],
                    key="pay_sup"
                )
                
            with col2:
                pay_amount = st.number_input("Amount Paid (₹) *", min_value=1.0, max_value=500000.0, value=1000.0, step=100.0)
                pay_remarks = st.text_input("Remarks", placeholder="e.g. Settle January milk bill", key="pay_rem")
            
            if st.button("Log Payment Voucher", type="primary"):
                res = api.create_payment(
                    supplier_id=pay_supplier,
                    date_val=pay_date,
                    amount_paid=pay_amount,
                    remarks=pay_remarks
                )
                if res["status"] in [200, 201]:
                    st.success("Payment recorded successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(res["data"].get("detail", "Error creating payment record."))
            st.markdown("</div>", unsafe_allow_html=True)
            
    # Tab 2: Payment History
    with tab2:
        st.write("### Payment History Log")
        col1, col2, col3 = st.columns(3)
        with col1:
            p_start = st.date_input("Start Date", date.today().replace(day=1), key="p_start")
        with col2:
            p_end = st.date_input("End Date", date.today(), key="p_end")
        with col3:
            p_sup_options = {0: "--- All Farmers ---"}
            for s in suppliers:
                p_sup_options[s["id"]] = s["name"]
            p_supplier = st.selectbox("Filter by Farmer", options=list(p_sup_options.keys()), format_func=lambda sid: p_sup_options[sid], key="p_sup_filt")
            
        payments = api.get_payments(start_date=p_start, end_date=p_end, supplier_id=p_supplier)
        
        if payments:
            df_pay = pd.DataFrame(payments)
            df_pay_display = df_pay.rename(columns={
                "id": "Voucher ID",
                "date": "Payment Date",
                "supplier_name": "Farmer Name",
                "amount_paid": "Amount Paid (₹)",
                "remarks": "Remarks"
            })
            
            st.write(f"Showing **{len(payments)}** payment entries:")
            st.dataframe(df_pay_display[["Voucher ID", "Payment Date", "Farmer Name", "Amount Paid (₹)", "Remarks"]], use_container_width=True, hide_index=True)
            
            st.markdown("---", unsafe_allow_html=True)
            st.markdown("### 🚨 Delete Payment Voucher")
            voucher_to_del = st.selectbox("Select Voucher ID to Delete", options=df_pay["id"].tolist())
            if voucher_to_del:
                if st.button("Delete Selected Voucher"):
                    success = api.delete_payment(voucher_to_del)
                    if success:
                        st.success("Payment voucher deleted successfully. Ledger re-balanced.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Error deleting payment voucher.")
        else:
            st.info("No payment vouchers found in selected date ranges.")

# ==================== 5. MONTHLY REPORTS ====================
elif page == "📅 Monthly Reports":
    st.markdown("<h1 style='color:#1e3a8a;'>📅 Monthly Farmers Summary Statements</h1>", unsafe_allow_html=True)
    st.write("Generates summary statements showing total milk, total money owed, total money paid, and remaining pending balances.")
    st.markdown("---", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        report_year = st.selectbox("Select Year", range(2025, 2030), index=date.today().year - 2025)
    with col2:
        report_month = st.selectbox("Select Month", range(1, 13), index=date.today().month - 1, format_func=lambda m: datetime(2000, m, 1).strftime('%B'))
        
    report_data = api.get_monthly_report(report_year, report_month)
    
    if report_data:
        df_rep = pd.DataFrame(report_data)
        
        # Display breakdown summary
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Total Milk Collected", f"{df_rep['total_milk'].sum():,.2f} Liters")
        with col_m2:
            st.metric("Total Bill Owed", format_currency(df_rep['total_due'].sum()))
        with col_m3:
            st.metric("Pending Balance Owed", format_currency(df_rep['pending_payment'].sum()))
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        df_rep_display = df_rep.rename(columns={
            "supplier_name": "Farmer Name",
            "phone": "Phone Number",
            "total_milk": "Total Milk (L)",
            "total_due": "Total Bill Due (₹)",
            "total_paid": "Total Paid in Month (₹)",
            "pending_payment": "Net Outstanding Balance (₹)"
        })
        
        st.dataframe(
            df_rep_display[["Farmer Name", "Phone Number", "Total Milk (L)", "Total Bill Due (₹)", "Total Paid in Month (₹)", "Net Outstanding Balance (₹)"]], 
            use_container_width=True, 
            hide_index=True
        )
        
        st.markdown("---", unsafe_allow_html=True)
        st.write("### 📥 Excel Report Downloader")
        
        # OpenPyXL in-memory excel generator
        buffer = io.BytesIO()
        
        # Clean dataframe for spreadsheet
        df_export = df_rep_display[["Farmer Name", "Phone Number", "Total Milk (L)", "Total Bill Due (₹)", "Total Paid in Month (₹)", "Net Outstanding Balance (₹)"]].copy()
        
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_export.to_excel(writer, index=False, sheet_name=f"Milk Report {report_month}-{report_year}")
            
        buffer.seek(0)
        
        st.download_button(
            label="📥 Download Excel File",
            data=buffer,
            file_name=f"Milk_Dairy_Report_{report_year}_{report_month:02d}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
    else:
        st.info("No records to summarize for this month.")

# ==================== 6. SETTINGS ====================
elif page == "⚙️ Settings":
    st.markdown("<h1 style='color:#1e3a8a;'>⚙️ System Settings</h1>", unsafe_allow_html=True)
    st.markdown("---", unsafe_allow_html=True)
    
    st.markdown("<div class='form-container'>", unsafe_allow_html=True)
    st.write("### 🔑 Change Account Password")
    st.write("To log in securely from your Android phone, change the default credentials below.")
    
    old_pw = st.text_input("Old Password", type="password", placeholder="Enter your current password")
    new_pw1 = st.text_input("New Password", type="password", placeholder="Minimum 6 characters")
    new_pw2 = st.text_input("Confirm New Password", type="password", placeholder="Retype new password")
    
    if st.button("Update Security Password", type="primary"):
        if not old_pw or not new_pw1 or not new_pw2:
            st.error("All password fields are required.")
        elif new_pw1 != new_pw2:
            st.error("New password and confirmation password do not match.")
        elif len(new_pw1) < 6:
            st.error("New password must be at least 6 characters.")
        else:
            res = api.change_password(old_pw, new_pw1)
            if res["status"] == 200:
                st.success("Password changed successfully! Please log in again using your new password.")
                time.sleep(2)
                api.logout()
                st.rerun()
            else:
                st.error(res["data"].get("detail", "Failed to update password. Check old password."))
    st.markdown("</div>", unsafe_allow_html=True)
