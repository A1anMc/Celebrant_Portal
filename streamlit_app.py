import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import date, datetime, timedelta

# Configure Streamlit page
st.set_page_config(
    page_title="Melbourne Celebrant Portal",
    page_icon="💒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database setup
DATABASE_PATH = "celebrant_portal.db"

def init_database():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Couples table - simple version
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS couples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_1_name TEXT NOT NULL,
            partner_1_email TEXT,
            partner_2_name TEXT NOT NULL,
            partner_2_email TEXT,
            ceremony_date TEXT,
            ceremony_location TEXT,
            ceremony_time TEXT,
            fee REAL DEFAULT 0,
            travel_fee REAL DEFAULT 0,
            status TEXT DEFAULT 'Inquiry',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create admin user if it doesn't exist
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ("admin@celebrant.com",))
    if cursor.fetchone()[0] == 0:
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
            ("admin@celebrant.com", admin_password, "Admin User")
        )
    
    conn.commit()
    conn.close()

def authenticate_user(email, password):
    """Authenticate user login."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        "SELECT id, name FROM users WHERE email = ? AND password_hash = ?",
        (email, password_hash)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {"id": result[0], "name": result[1], "email": email}
    return None

def get_couples():
    """Get all couples from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM couples ORDER BY created_at DESC", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def add_couple(couple_data):
    """Add a new couple to the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO couples (
            partner_1_name, partner_1_email, partner_2_name, partner_2_email,
            ceremony_date, ceremony_location, ceremony_time, fee, travel_fee, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        couple_data['partner_1_name'], couple_data['partner_1_email'],
        couple_data['partner_2_name'], couple_data['partner_2_email'],
        couple_data['ceremony_date'], couple_data['ceremony_location'], 
        couple_data['ceremony_time'], couple_data['fee'], couple_data['travel_fee'],
        couple_data['status'], couple_data['notes']
    ))
    
    conn.commit()
    conn.close()

def login_page():
    """Display login form."""
    st.title("🌟 Melbourne Celebrant Portal")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 Login")
        
        email = st.text_input("Email", placeholder="admin@celebrant.com", key="email_input")
        password = st.text_input("Password", type="password", placeholder="admin123", key="password_input")
        
        if st.button("Login", use_container_width=True):
            if email and password:
                user = authenticate_user(email, password)
                if user:
                    st.session_state.user = user
                    st.success(f"Welcome, {user['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
            else:
                st.error("Please enter both email and password")
        
        st.info("💡 **Demo Login:**\n- Email: admin@celebrant.com\n- Password: admin123")

def dashboard_page():
    """Main dashboard with overview and statistics."""
    st.title("🏠 Dashboard")
    st.markdown("### Your celebrant portal overview")
    
    # Get statistics
    couples_df = get_couples()
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Couples", len(couples_df))
    
    with col2:
        confirmed = len(couples_df[couples_df['status'] == 'Confirmed']) if not couples_df.empty else 0
        st.metric("✅ Confirmed", confirmed)
    
    with col3:
        inquiries = len(couples_df[couples_df['status'] == 'Inquiry']) if not couples_df.empty else 0
        st.metric("📋 Inquiries", inquiries)
    
    with col4:
        total_revenue = couples_df['fee'].sum() + couples_df['travel_fee'].sum() if not couples_df.empty else 0
        st.metric("💰 Total Revenue", f"${total_revenue:.0f}")
    
    st.markdown("---")
    
    if not couples_df.empty:
        st.subheader("📅 Recent Couples")
        for _, couple in couples_df.head(5).iterrows():
            with st.expander(f"💑 {couple['partner_1_name']} & {couple['partner_2_name']} - {couple['status']}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**📅 Date:** {couple['ceremony_date'] or 'TBD'}")
                    st.write(f"**📍 Location:** {couple['ceremony_location'] or 'TBD'}")
                with col_b:
                    st.write(f"**💰 Fee:** ${couple['fee'] or 0}")
                    st.write(f"**🚗 Travel:** ${couple['travel_fee'] or 0}")
                if couple['notes']:
                    st.write(f"**📝 Notes:** {couple['notes']}")
    else:
        st.info("No couples added yet. Use the sidebar to add your first couple!")

def couples_page():
    """Couples management interface."""
    st.title("💑 Couples Management")
    
    tab1, tab2 = st.tabs(["📋 All Couples", "➕ Add New"])
    
    with tab1:
        couples_df = get_couples()
        
        if couples_df.empty:
            st.info("No couples found. Add your first couple using the 'Add New' tab!")
        else:
            st.subheader(f"👥 All Couples ({len(couples_df)})")
            
            for _, couple in couples_df.iterrows():
                with st.expander(f"💑 {couple['partner_1_name']} & {couple['partner_2_name']} - {couple['ceremony_date'] or 'TBD'}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**👫 Couple Details**")
                        st.write(f"**Partner 1:** {couple['partner_1_name']}")
                        if couple['partner_1_email']:
                            st.write(f"📧 {couple['partner_1_email']}")
                        st.write(f"**Partner 2:** {couple['partner_2_name']}")
                        if couple['partner_2_email']:
                            st.write(f"📧 {couple['partner_2_email']}")
                    
                    with col2:
                        st.markdown("**📅 Ceremony Details**")
                        st.write(f"**Date:** {couple['ceremony_date'] or 'TBD'}")
                        st.write(f"**Time:** {couple['ceremony_time'] or 'TBD'}")
                        st.write(f"**Location:** {couple['ceremony_location'] or 'TBD'}")
                        st.write(f"**Status:** {couple['status']}")
                    
                    st.markdown("**💰 Financial Details**")
                    col3, col4 = st.columns(2)
                    with col3:
                        st.write(f"**Ceremony Fee:** ${couple['fee'] or 0}")
                    with col4:
                        st.write(f"**Travel Fee:** ${couple['travel_fee'] or 0}")
                    
                    if couple['notes']:
                        st.markdown("**📝 Notes**")
                        st.write(couple['notes'])
    
    with tab2:
        st.subheader("➕ Add New Couple")
        
        with st.form("add_couple_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Partner 1**")
                partner_1_name = st.text_input("Name", key="p1_name")
                partner_1_email = st.text_input("Email", key="p1_email")
            
            with col2:
                st.markdown("**Partner 2**")
                partner_2_name = st.text_input("Name", key="p2_name")
                partner_2_email = st.text_input("Email", key="p2_email")
            
            st.markdown("**Ceremony Details**")
            col3, col4 = st.columns(2)
            
            with col3:
                ceremony_date = st.date_input("Ceremony Date", value=None)
                ceremony_location = st.text_input("Ceremony Location")
            
            with col4:
                ceremony_time = st.time_input("Ceremony Time", value=None)
                status = st.selectbox("Status", ["Inquiry", "Confirmed", "Completed", "Cancelled"])
            
            st.markdown("**Financial Details**")
            col5, col6 = st.columns(2)
            
            with col5:
                fee = st.number_input("Ceremony Fee ($)", min_value=0.0, value=0.0, step=50.0)
            
            with col6:
                travel_fee = st.number_input("Travel Fee ($)", min_value=0.0, value=0.0, step=25.0)
            
            notes = st.text_area("Notes", height=100)
            
            submit = st.form_submit_button("Add Couple", use_container_width=True)
            
            if submit:
                if partner_1_name and partner_2_name:
                    couple_data = {
                        'partner_1_name': partner_1_name,
                        'partner_1_email': partner_1_email,
                        'partner_2_name': partner_2_name,
                        'partner_2_email': partner_2_email,
                        'ceremony_date': ceremony_date.isoformat() if ceremony_date else "",
                        'ceremony_location': ceremony_location,
                        'ceremony_time': ceremony_time.strftime("%H:%M") if ceremony_time else "",
                        'fee': fee,
                        'travel_fee': travel_fee,
                        'status': status,
                        'notes': notes
                    }
                    
                    add_couple(couple_data)
                    st.success("✅ Couple added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter names for both partners")

def templates_page():
    """Templates management interface."""
    st.title("📝 Templates")
    st.markdown("### Manage ceremony templates and scripts")
    
    tab1, tab2 = st.tabs(["📋 All Templates", "➕ Create New"])
    
    with tab1:
        st.subheader("🎭 Available Templates")
        
        # Sample templates for demonstration
        templates = [
            {"name": "Traditional Wedding", "type": "Wedding", "description": "Classic wedding ceremony with traditional vows"},
            {"name": "Modern Casual", "type": "Wedding", "description": "Contemporary ceremony with personalized elements"},
            {"name": "Beach Wedding", "type": "Wedding", "description": "Relaxed outdoor ceremony perfect for beach settings"},
            {"name": "Elopement", "type": "Wedding", "description": "Intimate ceremony for small gatherings"},
        ]
        
        for template in templates:
            with st.expander(f"🎭 {template['name']} - {template['type']}"):
                st.write(f"**Description:** {template['description']}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button(f"✏️ Edit", key=f"edit_{template['name']}")
                with col2:
                    st.button(f"📋 Use", key=f"use_{template['name']}")
                with col3:
                    st.button(f"🗑️ Delete", key=f"delete_{template['name']}")
    
    with tab2:
        st.subheader("➕ Create New Template")
        
        with st.form("create_template"):
            template_name = st.text_input("Template Name")
            template_type = st.selectbox("Ceremony Type", ["Wedding", "Renewal", "Commitment", "Other"])
            template_description = st.text_area("Description")
            template_content = st.text_area("Template Content", height=300, 
                                          placeholder="Enter your ceremony script here...")
            
            if st.form_submit_button("Create Template"):
                if template_name and template_content:
                    st.success(f"✅ Template '{template_name}' created successfully!")
                else:
                    st.error("Please fill in template name and content")

def legal_forms_page():
    """Legal forms and compliance management."""
    st.title("⚖️ Legal Forms")
    st.markdown("### NOIM tracking and legal compliance")
    
    tab1, tab2, tab3 = st.tabs(["📋 NOIM Tracker", "📄 Form Upload", "⏰ Deadlines"])
    
    with tab1:
        st.subheader("📋 Notice of Intended Marriage (NOIM) Status")
        
        couples_df = get_couples()
        if not couples_df.empty:
            for _, couple in couples_df.iterrows():
                with st.expander(f"💑 {couple['partner_1_name']} & {couple['partner_2_name']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Ceremony Date:** {couple['ceremony_date'] or 'TBD'}")
                        if couple['ceremony_date']:
                            ceremony_date = datetime.strptime(couple['ceremony_date'], '%Y-%m-%d').date()
                            days_until = (ceremony_date - date.today()).days
                            if days_until > 0:
                                st.write(f"**Days until ceremony:** {days_until}")
                            else:
                                st.write("**Status:** Past ceremony date")
                    
                    with col2:
                        noim_status = st.selectbox(
                            "NOIM Status:",
                            ["Not Started", "In Progress", "Submitted", "Approved"],
                            key=f"noim_{couple['id']}"
                        )
                        
                        if noim_status == "Submitted":
                            st.success("✅ NOIM Submitted")
                        elif noim_status == "Approved":
                            st.success("🎉 NOIM Approved - Ready for ceremony!")
                        elif noim_status == "In Progress":
                            st.warning("⏳ NOIM In Progress")
                        else:
                            st.error("❌ NOIM Not Started")
        else:
            st.info("No couples found. Add couples to track their NOIM status.")
    
    with tab2:
        st.subheader("📄 Legal Form Upload")
        
        couples_df = get_couples()
        if not couples_df.empty:
            selected_couple = st.selectbox(
                "Select Couple:",
                options=couples_df.apply(lambda x: f"{x['partner_1_name']} & {x['partner_2_name']}", axis=1).tolist()
            )
            
            form_type = st.selectbox(
                "Form Type:",
                ["NOIM", "Marriage Certificate", "Divorce Certificate", "Other"]
            )
            
            uploaded_file = st.file_uploader(
                "Upload Legal Document",
                type=['pdf', 'jpg', 'jpeg', 'png'],
                help="Upload NOIM, certificates, or other legal documents"
            )
            
            if uploaded_file and st.button("Upload Document"):
                st.success(f"✅ {form_type} uploaded for {selected_couple}")
        else:
            st.info("No couples found. Add couples to upload their legal forms.")
    
    with tab3:
        st.subheader("⏰ Legal Deadlines")
        
        st.markdown("""
        **Important Legal Deadlines:**
        
        📅 **NOIM Submission:** Must be submitted at least 1 month before ceremony
        
        📋 **Required Documents:**
        - Birth Certificate or Passport
        - Divorce Certificate (if applicable)
        - Death Certificate of former spouse (if applicable)
        
        ⚠️ **Compliance Reminders:**
        - NOIM must be witnessed by an authorized person
        - All documents must be originals or certified copies
        - International documents may need translation
        """)

def invoices_page():
    """Invoice and payment management."""
    st.title("💰 Invoices")
    st.markdown("### Payment tracking and financial management")
    
    tab1, tab2, tab3 = st.tabs(["📋 All Invoices", "➕ Create Invoice", "📊 Financial Summary"])
    
    with tab1:
        st.subheader("💳 Invoice Management")
        
        # Sample invoice data
        invoices = [
            {"id": 1, "couple": "Emma & James", "amount": 1200, "status": "Paid", "due_date": "2024-07-01"},
            {"id": 2, "couple": "Sarah & Michael", "amount": 1000, "status": "Pending", "due_date": "2024-08-15"},
            {"id": 3, "couple": "Lisa & David", "amount": 1500, "status": "Overdue", "due_date": "2024-06-20"},
        ]
        
        for invoice in invoices:
            with st.expander(f"💰 Invoice #{invoice['id']} - {invoice['couple']} - ${invoice['amount']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Amount:** ${invoice['amount']}")
                    st.write(f"**Due Date:** {invoice['due_date']}")
                
                with col2:
                    status_color = {"Paid": "🟢", "Pending": "🟡", "Overdue": "🔴"}
                    st.write(f"**Status:** {status_color[invoice['status']]} {invoice['status']}")
                
                with col3:
                    if invoice['status'] != "Paid":
                        if st.button(f"Mark as Paid", key=f"pay_{invoice['id']}"):
                            st.success("✅ Invoice marked as paid!")
    
    with tab2:
        st.subheader("➕ Create New Invoice")
        
        couples_df = get_couples()
        if not couples_df.empty:
            with st.form("create_invoice"):
                selected_couple = st.selectbox(
                    "Select Couple:",
                    options=couples_df.apply(lambda x: f"{x['partner_1_name']} & {x['partner_2_name']}", axis=1).tolist()
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    ceremony_fee = st.number_input("Ceremony Fee ($)", min_value=0.0, value=1000.0, step=50.0)
                    travel_fee = st.number_input("Travel Fee ($)", min_value=0.0, value=0.0, step=25.0)
                
                with col2:
                    due_date = st.date_input("Due Date", value=date.today() + timedelta(days=30))
                    payment_terms = st.selectbox("Payment Terms", ["Net 30", "Net 15", "Due on Receipt"])
                
                description = st.text_area("Invoice Description", 
                                         value="Wedding ceremony services as discussed")
                
                total_amount = ceremony_fee + travel_fee
                st.write(f"**Total Amount: ${total_amount:.2f}**")
                
                if st.form_submit_button("Create Invoice"):
                    st.success(f"✅ Invoice created for {selected_couple} - ${total_amount:.2f}")
        else:
            st.info("No couples found. Add couples to create invoices.")
    
    with tab3:
        st.subheader("📊 Financial Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Total Revenue", "$3,700")
        
        with col2:
            st.metric("✅ Paid Invoices", "$1,200")
        
        with col3:
            st.metric("⏳ Pending", "$1,000")
        
        with col4:
            st.metric("🔴 Overdue", "$1,500")
        
        st.markdown("---")
        
        # Revenue chart placeholder
        st.subheader("📈 Revenue Trends")
        st.info("📊 Revenue analytics chart would appear here")

def travel_calculator_page():
    """Travel distance and cost calculator."""
    st.title("🗺️ Travel Calculator")
    st.markdown("### Calculate travel distances and costs")
    
    tab1, tab2 = st.tabs(["📍 Distance Calculator", "💰 Cost Estimator"])
    
    with tab1:
        st.subheader("📍 Calculate Travel Distance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📍 Your Location**")
            your_address = st.text_input("Your Address", value="Melbourne, VIC")
        
        with col2:
            st.markdown("**🎯 Ceremony Location**")
            ceremony_address = st.text_input("Ceremony Address")
        
        if st.button("Calculate Distance") and ceremony_address:
            # Simulated distance calculation
            distance = 25.5  # km
            drive_time = 35   # minutes
            
            st.success(f"📏 **Distance:** {distance} km")
            st.success(f"⏱️ **Estimated Drive Time:** {drive_time} minutes")
            
            # Map placeholder
            st.markdown("---")
            st.subheader("🗺️ Route Map")
            st.info("🗺️ Interactive map showing route would appear here")
    
    with tab2:
        st.subheader("💰 Travel Cost Calculator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            distance = st.number_input("Distance (km)", min_value=0.0, value=25.5, step=0.1)
            fuel_price = st.number_input("Fuel Price ($/L)", min_value=0.0, value=1.80, step=0.01)
            fuel_consumption = st.number_input("Fuel Consumption (L/100km)", min_value=0.0, value=8.5, step=0.1)
        
        with col2:
            time_cost = st.number_input("Time Cost ($/hour)", min_value=0.0, value=50.0, step=5.0)
            drive_time_hours = st.number_input("Drive Time (hours)", min_value=0.0, value=1.2, step=0.1)
            
            # Calculate costs
            fuel_cost = (distance * fuel_consumption / 100) * fuel_price * 2  # Return trip
            time_cost_total = drive_time_hours * time_cost * 2  # Return trip
            total_cost = fuel_cost + time_cost_total
        
        st.markdown("---")
        st.subheader("💰 Cost Breakdown")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.metric("⛽ Fuel Cost", f"${fuel_cost:.2f}")
        
        with col4:
            st.metric("⏰ Time Cost", f"${time_cost_total:.2f}")
        
        with col5:
            st.metric("💰 Total Cost", f"${total_cost:.2f}")
        
        st.info(f"💡 **Suggested Travel Fee:** ${total_cost * 1.3:.2f} (includes 30% markup)")

def reports_page():
    """Reports and analytics dashboard."""
    st.title("📊 Reports")
    st.markdown("### Business analytics and insights")
    
    tab1, tab2, tab3 = st.tabs(["📈 Revenue Analytics", "📅 Booking Trends", "📋 Couple Reports"])
    
    with tab1:
        st.subheader("📈 Revenue Analytics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Total Revenue", "$3,700", "↗️ +15%")
        
        with col2:
            st.metric("📊 Average Fee", "$1,233", "↗️ +8%")
        
        with col3:
            st.metric("🎯 Bookings", "3", "→ 0%")
        
        with col4:
            st.metric("💳 Payment Rate", "67%", "↘️ -10%")
        
        st.markdown("---")
        st.info("📊 Revenue charts and analytics would appear here")
    
    with tab2:
        st.subheader("📅 Booking Trends")
        
        st.markdown("**Popular Wedding Months:**")
        months = ["March", "April", "May", "October", "November"]
        for i, month in enumerate(months, 1):
            st.write(f"{i}. {month}")
        
        st.markdown("---")
        st.info("📊 Booking trend charts would appear here")
    
    with tab3:
        st.subheader("📋 Couple Management Reports")
        
        couples_df = get_couples()
        if not couples_df.empty:
            st.write(f"**Total Couples:** {len(couples_df)}")
            
            # Status breakdown
            status_counts = couples_df['status'].value_counts() if 'status' in couples_df.columns else {}
            
            for status, count in status_counts.items():
                st.write(f"- {status}: {count}")
        else:
            st.info("No couple data available for reporting")

def main():
    """Main application logic."""
    # Initialize database
    init_database()
    
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Check if user is logged in
    if st.session_state.user is None:
        login_page()
    else:
        # Sidebar with user info and navigation
        with st.sidebar:
            st.markdown(f"**👤 Welcome, {st.session_state.user['name']}**")
            st.markdown(f"📧 {st.session_state.user['email']}")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                st.rerun()
            
            st.markdown("---")
            
            # Navigation
            st.header("📋 Navigation")
            page = st.radio(
                "Choose a section:",
                [
                    "🏠 Dashboard", 
                    "💑 Couples Management",
                    "📝 Templates",
                    "⚖️ Legal Forms", 
                    "💰 Invoices",
                    "🗺️ Travel Calculator",
                    "📊 Reports"
                ],
                key="navigation"
            )
        
        # Route to appropriate page
        if page == "🏠 Dashboard":
            dashboard_page()
        elif page == "💑 Couples Management":
            couples_page()
        elif page == "📝 Templates":
            templates_page()
        elif page == "⚖️ Legal Forms":
            legal_forms_page()
        elif page == "💰 Invoices":
            invoices_page()
        elif page == "🗺️ Travel Calculator":
            travel_calculator_page()
        elif page == "📊 Reports":
            reports_page()

if __name__ == "__main__":
    main() 