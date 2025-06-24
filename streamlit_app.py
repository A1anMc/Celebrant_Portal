import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import os
from datetime import datetime, date
import json
from pathlib import Path

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
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Couples table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS couples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_1_name TEXT NOT NULL,
            partner_1_email TEXT,
            partner_1_phone TEXT,
            partner_2_name TEXT NOT NULL,
            partner_2_email TEXT,
            partner_2_phone TEXT,
            wedding_date DATE,
            venue TEXT,
            ceremony_time TEXT,
            status TEXT DEFAULT 'active',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create admin user if it doesn't exist
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ("admin@celebrant.com",))
    if cursor.fetchone()[0] == 0:
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (email, password_hash, name, is_admin) VALUES (?, ?, ?, ?)",
            ("admin@celebrant.com", admin_password, "Admin User", True)
        )
    
    conn.commit()
    conn.close()

def authenticate_user(email, password):
    """Authenticate user login."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        "SELECT id, name, is_admin FROM users WHERE email = ? AND password_hash = ?",
        (email, password_hash)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {"id": result[0], "name": result[1], "is_admin": bool(result[2]), "email": email}
    return None

def get_couples():
    """Get all couples from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM couples ORDER BY wedding_date DESC", conn)
    conn.close()
    return df

def add_couple(couple_data):
    """Add a new couple to the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO couples (
            partner_1_name, partner_1_email, partner_1_phone,
            partner_2_name, partner_2_email, partner_2_phone,
            wedding_date, venue, ceremony_time, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        couple_data['partner_1_name'], couple_data['partner_1_email'], couple_data['partner_1_phone'],
        couple_data['partner_2_name'], couple_data['partner_2_email'], couple_data['partner_2_phone'],
        couple_data['wedding_date'], couple_data['venue'], couple_data['ceremony_time'], couple_data['notes']
    ))
    
    conn.commit()
    conn.close()

def update_couple(couple_id, couple_data):
    """Update an existing couple."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE couples SET
            partner_1_name = ?, partner_1_email = ?, partner_1_phone = ?,
            partner_2_name = ?, partner_2_email = ?, partner_2_phone = ?,
            wedding_date = ?, venue = ?, ceremony_time = ?, notes = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (
        couple_data['partner_1_name'], couple_data['partner_1_email'], couple_data['partner_1_phone'],
        couple_data['partner_2_name'], couple_data['partner_2_email'], couple_data['partner_2_phone'],
        couple_data['wedding_date'], couple_data['venue'], couple_data['ceremony_time'], couple_data['notes'],
        couple_id
    ))
    
    conn.commit()
    conn.close()

def delete_couple(couple_id):
    """Delete a couple from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM couples WHERE id = ?", (couple_id,))
    conn.commit()
    conn.close()

def login_page():
    """Display login form."""
    st.title("🌟 Melbourne Celebrant Portal")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 Login")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="admin@celebrant.com")
            password = st.text_input("Password", type="password", placeholder="admin123")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
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

def couples_management_page():
    """Main couples management interface."""
    st.title("💒 Couples Management")
    
    # Sidebar for actions
    with st.sidebar:
        st.header("Actions")
        action = st.selectbox(
            "Choose an action:",
            ["View All Couples", "Add New Couple", "Search Couples"]
        )
    
    if action == "Add New Couple":
        add_couple_form()
    elif action == "Search Couples":
        search_couples()
    else:
        display_couples()

def add_couple_form():
    """Form to add a new couple."""
    st.subheader("➕ Add New Couple")
    
    with st.form("add_couple_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Partner 1**")
            partner_1_name = st.text_input("Name", key="p1_name")
            partner_1_email = st.text_input("Email", key="p1_email")
            partner_1_phone = st.text_input("Phone", key="p1_phone")
        
        with col2:
            st.markdown("**Partner 2**")
            partner_2_name = st.text_input("Name", key="p2_name")
            partner_2_email = st.text_input("Email", key="p2_email")
            partner_2_phone = st.text_input("Phone", key="p2_phone")
        
        st.markdown("**Wedding Details**")
        col3, col4 = st.columns(2)
        
        with col3:
            wedding_date = st.date_input("Wedding Date", min_value=date.today())
            venue = st.text_input("Venue")
        
        with col4:
            ceremony_time = st.time_input("Ceremony Time")
            
        notes = st.text_area("Notes", height=100)
        
        submit = st.form_submit_button("Add Couple", use_container_width=True)
        
        if submit:
            if partner_1_name and partner_2_name and wedding_date:
                couple_data = {
                    'partner_1_name': partner_1_name,
                    'partner_1_email': partner_1_email,
                    'partner_1_phone': partner_1_phone,
                    'partner_2_name': partner_2_name,
                    'partner_2_email': partner_2_email,
                    'partner_2_phone': partner_2_phone,
                    'wedding_date': wedding_date.isoformat(),
                    'venue': venue,
                    'ceremony_time': ceremony_time.strftime("%H:%M") if ceremony_time else "",
                    'notes': notes
                }
                
                add_couple(couple_data)
                st.success("✅ Couple added successfully!")
                st.rerun()
            else:
                st.error("Please fill in the required fields (Partner names and wedding date)")

def display_couples():
    """Display all couples in a table."""
    st.subheader("👥 All Couples")
    
    couples_df = get_couples()
    
    if couples_df.empty:
        st.info("No couples found. Add your first couple using the sidebar!")
        return
    
    # Display summary stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Couples", len(couples_df))
    
    with col2:
        upcoming = couples_df[couples_df['wedding_date'] >= date.today().isoformat()]
        st.metric("Upcoming Weddings", len(upcoming))
    
    with col3:
        this_month = couples_df[
            couples_df['wedding_date'].str.startswith(date.today().strftime("%Y-%m"))
        ]
        st.metric("This Month", len(this_month))
    
    with col4:
        active_couples = couples_df[couples_df['status'] == 'active']
        st.metric("Active Couples", len(active_couples))
    
    st.markdown("---")
    
    # Display couples table
    for idx, couple in couples_df.iterrows():
        with st.expander(f"💑 {couple['partner_1_name']} & {couple['partner_2_name']} - {couple['wedding_date']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**📅 Wedding Date:** {couple['wedding_date']}")
                st.markdown(f"**🕐 Time:** {couple['ceremony_time'] or 'Not set'}")
                st.markdown(f"**📍 Venue:** {couple['venue'] or 'Not set'}")
                st.markdown(f"**📝 Status:** {couple['status']}")
            
            with col2:
                st.markdown(f"**Partner 1:** {couple['partner_1_name']}")
                if couple['partner_1_email']:
                    st.markdown(f"📧 {couple['partner_1_email']}")
                if couple['partner_1_phone']:
                    st.markdown(f"📱 {couple['partner_1_phone']}")
                
                st.markdown(f"**Partner 2:** {couple['partner_2_name']}")
                if couple['partner_2_email']:
                    st.markdown(f"📧 {couple['partner_2_email']}")
                if couple['partner_2_phone']:
                    st.markdown(f"📱 {couple['partner_2_phone']}")
            
            if couple['notes']:
                st.markdown(f"**📋 Notes:** {couple['notes']}")
            
            # Action buttons
            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button(f"✏️ Edit", key=f"edit_{couple['id']}"):
                    st.session_state.editing_couple = couple['id']
                    st.rerun()
            
            with col_delete:
                if st.button(f"🗑️ Delete", key=f"delete_{couple['id']}", type="secondary"):
                    if st.session_state.get(f"confirm_delete_{couple['id']}", False):
                        delete_couple(couple['id'])
                        st.success("Couple deleted successfully!")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_{couple['id']}"] = True
                        st.warning("Click again to confirm deletion")

def search_couples():
    """Search functionality for couples."""
    st.subheader("🔍 Search Couples")
    
    search_term = st.text_input("Search by name, email, or venue:")
    
    if search_term:
        couples_df = get_couples()
        
        # Filter couples based on search term
        mask = (
            couples_df['partner_1_name'].str.contains(search_term, case=False, na=False) |
            couples_df['partner_2_name'].str.contains(search_term, case=False, na=False) |
            couples_df['partner_1_email'].str.contains(search_term, case=False, na=False) |
            couples_df['partner_2_email'].str.contains(search_term, case=False, na=False) |
            couples_df['venue'].str.contains(search_term, case=False, na=False)
        )
        
        filtered_couples = couples_df[mask]
        
        if not filtered_couples.empty:
            st.success(f"Found {len(filtered_couples)} matching couples:")
            
            for idx, couple in filtered_couples.iterrows():
                st.markdown(f"**{couple['partner_1_name']} & {couple['partner_2_name']}**")
                st.markdown(f"📅 {couple['wedding_date']} | 📍 {couple['venue']}")
                st.markdown("---")
        else:
            st.info("No couples found matching your search.")

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
        # Sidebar with user info and logout
        with st.sidebar:
            st.markdown(f"**👤 Logged in as:**")
            st.markdown(f"{st.session_state.user['name']}")
            st.markdown(f"📧 {st.session_state.user['email']}")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                st.rerun()
            
            st.markdown("---")
        
        # Main application
        couples_management_page()

if __name__ == "__main__":
    main() 