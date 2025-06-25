# 🚀 Melbourne Celebrant Portal - Stack & Blueprint

## 📊 Technology Stack Overview

### **Frontend Stack**
```yaml
Framework: Streamlit 1.28+
Language: Python 3.8+
UI Components: Native Streamlit widgets
Styling: Streamlit theming + custom CSS
Charts: Streamlit built-in charting
Forms: Streamlit forms with validation
```

### **Backend Stack**
```yaml
Runtime: Python 3.8+
Framework: Streamlit (full-stack)
Database: SQLite 3
ORM: Raw SQL with sqlite3
Data Processing: Pandas 2.0+
Authentication: SHA256 + Session State
```

### **Development Stack**
```yaml
IDE: VS Code / PyCharm
Version Control: Git + GitHub
Package Manager: pip
Virtual Environment: venv
Testing: Manual + Custom scripts
Linting: Built-in Python standards
```

### **Deployment Stack**
```yaml
Platform: Streamlit Cloud
CI/CD: GitHub integration
Domain: Custom domain support
SSL: Automatic HTTPS
CDN: Global content delivery
Monitoring: Streamlit Cloud analytics
```

## 🏗️ Application Blueprint

### **1. Core Application Structure**

```python
# streamlit_app.py - Main Application
├── Configuration & Setup
│   ├── Page config
│   ├── Database path
│   └── Global constants
│
├── Database Layer
│   ├── init_database()
│   ├── CRUD operations
│   └── Connection management
│
├── Authentication System
│   ├── authenticate_user()
│   ├── login_page()
│   └── Session management
│
├── Business Logic Controllers
│   ├── dashboard_page()
│   ├── couples_page()
│   ├── templates_page()
│   ├── legal_forms_page()
│   ├── invoices_page()
│   ├── travel_calculator_page()
│   └── reports_page()
│
├── Navigation System
│   ├── main_navigation()
│   ├── Sidebar menu
│   └── Page routing
│
└── Main Application Entry
    ├── Session initialization
    ├── User authentication check
    └── Page rendering
```

### **2. Database Blueprint**

```sql
-- Core Tables Schema
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE couples (
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
);

-- Extended Tables (Future Implementation)
CREATE TABLE ceremony_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE legal_forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    couple_id INTEGER,
    form_type TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    deadline_date TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (couple_id) REFERENCES couples (id)
);

CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    couple_id INTEGER,
    amount REAL NOT NULL,
    status TEXT DEFAULT 'Draft',
    due_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (couple_id) REFERENCES couples (id)
);
```

### **3. Feature Implementation Blueprint**

#### **Dashboard Module**
```python
def dashboard_page():
    """Main dashboard implementation"""
    # Metrics calculation
    couples_df = get_couples()
    total_couples = len(couples_df)
    confirmed_bookings = len(couples_df[couples_df['status'] == 'Confirmed'])
    total_revenue = couples_df['fee'].sum() + couples_df['travel_fee'].sum()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Couples", total_couples)
    with col2: st.metric("Confirmed", confirmed_bookings)
    with col3: st.metric("Inquiries", total_couples - confirmed_bookings)
    with col4: st.metric("Revenue", f"${total_revenue:.0f}")
    
    # Recent activity
    display_recent_couples(couples_df.head(5))
```

#### **Couples Management Module**
```python
def couples_page():
    """Couples management implementation"""
    tab1, tab2 = st.tabs(["All Couples", "Add New"])
    
    with tab1:
        # Display all couples
        couples_df = get_couples()
        for _, couple in couples_df.iterrows():
            display_couple_card(couple)
    
    with tab2:
        # Add new couple form
        with st.form("add_couple"):
            partner_1_name = st.text_input("Partner 1 Name")
            partner_2_name = st.text_input("Partner 2 Name")
            # ... additional fields
            
            if st.form_submit_button("Add Couple"):
                add_couple(form_data)
                st.success("Couple added successfully!")
```

#### **Templates Module**
```python
def templates_page():
    """Template management implementation"""
    templates = [
        {"name": "Traditional Ceremony", "type": "Traditional"},
        {"name": "Modern Ceremony", "type": "Contemporary"},
        {"name": "Beach Ceremony", "type": "Outdoor"},
        {"name": "Elopement", "type": "Intimate"}
    ]
    
    for template in templates:
        with st.expander(f"📝 {template['name']}"):
            st.write(f"Type: {template['type']}")
            st.text_area("Content", key=f"template_{template['name']}")
```

#### **Legal Forms Module**
```python
def legal_forms_page():
    """Legal compliance implementation"""
    st.subheader("NOIM Tracker")
    
    couples_df = get_couples()
    for _, couple in couples_df.iterrows():
        if couple['ceremony_date']:
            days_until = calculate_days_until_ceremony(couple['ceremony_date'])
            if days_until <= 30:
                st.warning(f"NOIM due for {couple['partner_1_name']} & {couple['partner_2_name']}")
```

#### **Invoice Module**
```python
def invoices_page():
    """Invoice management implementation"""
    tab1, tab2 = st.tabs(["All Invoices", "Create New"])
    
    with tab1:
        # Display invoices
        display_invoice_summary()
    
    with tab2:
        # Create new invoice
        couples_df = get_couples()
        couple_options = [f"{row['partner_1_name']} & {row['partner_2_name']}" 
                         for _, row in couples_df.iterrows()]
        
        selected_couple = st.selectbox("Select Couple", couple_options)
        amount = st.number_input("Amount", min_value=0.0)
        
        if st.button("Create Invoice"):
            create_invoice(selected_couple, amount)
```

## 🔧 Development Blueprint

### **1. Setup & Installation**
```bash
# Environment Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Dependencies
pip install streamlit>=1.28.0 pandas>=2.0.0

# Run Application
streamlit run streamlit_app.py
```

### **2. Development Workflow**
```bash
# Development Process
1. Feature Planning
2. Code Implementation
3. Local Testing
4. Git Commit
5. Push to GitHub
6. Automatic Deployment
7. Production Testing
```

### **3. File Organization**
```
celebrant-portal/
├── streamlit_app.py          # Main application (all code)
├── celebrant_portal.db       # SQLite database
├── requirements.txt          # Dependencies
├── README.md                 # User documentation
├── ARCHITECTURE.md           # Technical architecture
├── STACK_BLUEPRINT.md        # This file
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT License
└── .streamlit/
    └── config.toml          # Streamlit configuration
```

## 🎨 UI/UX Blueprint

### **1. Design System**
```python
# Color Palette
PRIMARY_COLOR = "#FF6B6B"      # Celebrant red
SECONDARY_COLOR = "#4ECDC4"    # Teal accent
BACKGROUND_COLOR = "#FFFFFF"   # Clean white
TEXT_COLOR = "#2C3E50"         # Dark blue-gray

# Typography
HEADER_FONT = "Sans-serif"
BODY_FONT = "Sans-serif"
MONOSPACE_FONT = "Monaco"
```

### **2. Layout Structure**
```
┌─────────────────────────────────────┐
│              Header                 │
│    🌟 Melbourne Celebrant Portal    │
├─────────────────────────────────────┤
│ Sidebar  │    Main Content Area     │
│          │                          │
│ 🏠 Dash  │  ┌─────────────────────┐ │
│ 💑 Coup  │  │                     │ │
│ 📝 Temp  │  │   Page Content      │ │
│ ⚖️ Legal │  │                     │ │
│ 💰 Inv   │  │                     │ │
│ 🗺️ Trav  │  └─────────────────────┘ │
│ 📊 Rep   │                          │
└─────────────────────────────────────┘
```

### **3. Component Blueprint**
```python
# Reusable Components
def display_metric_card(title, value, delta=None):
    """Standard metric display"""
    st.metric(title, value, delta)

def display_couple_card(couple):
    """Couple information card"""
    with st.expander(f"💑 {couple['partner_1_name']} & {couple['partner_2_name']}"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"📅 Date: {couple['ceremony_date'] or 'TBD'}")
            st.write(f"📍 Location: {couple['ceremony_location'] or 'TBD'}")
        with col2:
            st.write(f"💰 Fee: ${couple['fee'] or 0}")
            st.write(f"🚗 Travel: ${couple['travel_fee'] or 0}")

def display_status_badge(status):
    """Status indicator badge"""
    colors = {
        'Inquiry': '🔵',
        'Consultation': '🟡',
        'Booked': '🟠',
        'Confirmed': '🟢',
        'Completed': '✅'
    }
    return f"{colors.get(status, '⚪')} {status}"
```

## 🔒 Security Blueprint

### **1. Authentication Flow**
```python
# Security Implementation
def authenticate_user(email, password):
    """Secure user authentication"""
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Database verification
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name FROM users WHERE email = ? AND password_hash = ?",
        (email, password_hash)
    )
    result = cursor.fetchone()
    conn.close()
    
    return {"id": result[0], "name": result[1], "email": email} if result else None

def check_authentication():
    """Verify user session"""
    if 'user' not in st.session_state or st.session_state.user is None:
        return False
    return True
```

### **2. Data Protection**
```python
# Input Validation
def validate_email(email):
    """Email format validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text):
    """Basic input sanitization"""
    if not text:
        return ""
    return text.strip()[:500]  # Limit length and trim

def validate_date(date_string):
    """Date format validation"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False
```

## 📊 Data Management Blueprint

### **1. Database Operations**
```python
# CRUD Operations Template
def create_record(table, data):
    """Generic create operation"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    values = list(data.values())
    
    cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id

def read_records(table, where_clause=None, params=None):
    """Generic read operation"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    query = f"SELECT * FROM {table}"
    if where_clause:
        query += f" WHERE {where_clause}"
    
    df = pd.read_sql_query(query, conn, params=params or [])
    conn.close()
    return df

def update_record(table, record_id, data):
    """Generic update operation"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
    values = list(data.values()) + [record_id]
    
    cursor.execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()

def delete_record(table, record_id):
    """Generic delete operation"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
```

### **2. Data Processing**
```python
# Business Logic Functions
def calculate_revenue_metrics(couples_df):
    """Calculate business metrics"""
    total_revenue = couples_df['fee'].sum() + couples_df['travel_fee'].sum()
    average_fee = couples_df['fee'].mean()
    confirmed_revenue = couples_df[couples_df['status'] == 'Confirmed']['fee'].sum()
    
    return {
        'total_revenue': total_revenue,
        'average_fee': average_fee,
        'confirmed_revenue': confirmed_revenue
    }

def get_upcoming_ceremonies(couples_df, days_ahead=30):
    """Get ceremonies in next N days"""
    today = datetime.now().date()
    upcoming = []
    
    for _, couple in couples_df.iterrows():
        if couple['ceremony_date']:
            ceremony_date = datetime.strptime(couple['ceremony_date'], '%Y-%m-%d').date()
            days_until = (ceremony_date - today).days
            if 0 <= days_until <= days_ahead:
                upcoming.append({
                    'couple': f"{couple['partner_1_name']} & {couple['partner_2_name']}",
                    'date': couple['ceremony_date'],
                    'days_until': days_until
                })
    
    return sorted(upcoming, key=lambda x: x['days_until'])
```

## 🚀 Deployment Blueprint

### **1. Streamlit Cloud Deployment**
```yaml
# .streamlit/config.toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[browser]
gatherUsageStats = false
```

### **2. Requirements Management**
```txt
# requirements.txt
streamlit>=1.28.0
pandas>=2.0.0
```

### **3. Git Configuration**
```gitignore
# .gitignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database (optional - include if you want to deploy with data)
# celebrant_portal.db
```

## 📈 Performance Blueprint

### **1. Optimization Strategies**
```python
# Caching Implementation
@st.cache_data
def load_couples_data():
    """Cache expensive database operations"""
    return get_couples()

@st.cache_data
def calculate_dashboard_metrics(couples_df):
    """Cache metric calculations"""
    return calculate_revenue_metrics(couples_df)

# Efficient Data Loading
def lazy_load_data(page_name):
    """Load data only when needed"""
    if page_name == "dashboard":
        return load_couples_data()
    elif page_name == "couples":
        return get_couples()
    return None
```

### **2. Database Optimization**
```sql
-- Index Creation for Performance
CREATE INDEX idx_couples_ceremony_date ON couples(ceremony_date);
CREATE INDEX idx_couples_status ON couples(status);
CREATE INDEX idx_couples_created_at ON couples(created_at);

-- Query Optimization Examples
SELECT * FROM couples WHERE status = 'Confirmed' ORDER BY ceremony_date;
SELECT COUNT(*) FROM couples WHERE ceremony_date BETWEEN ? AND ?;
```

## 🔧 Testing Blueprint

### **1. Testing Strategy**
```python
# Manual Testing Checklist
def test_application():
    """Comprehensive testing checklist"""
    tests = [
        "✅ Login functionality",
        "✅ Dashboard metrics display",
        "✅ Add new couple",
        "✅ View couples list",
        "✅ Template access",
        "✅ Legal forms tracking",
        "✅ Invoice creation",
        "✅ Travel calculator",
        "✅ Reports generation",
        "✅ Logout functionality"
    ]
    return tests

# Database Testing
def test_database_operations():
    """Test CRUD operations"""
    # Test data
    test_couple = {
        'partner_1_name': 'Test Partner 1',
        'partner_2_name': 'Test Partner 2',
        'ceremony_date': '2024-12-25',
        'status': 'Inquiry'
    }
    
    # Create
    couple_id = create_record('couples', test_couple)
    assert couple_id is not None
    
    # Read
    couples = read_records('couples', 'id = ?', [couple_id])
    assert len(couples) == 1
    
    # Update
    update_record('couples', couple_id, {'status': 'Confirmed'})
    
    # Delete
    delete_record('couples', couple_id)
```

## 📋 Maintenance Blueprint

### **1. Regular Maintenance Tasks**
```python
# Database Maintenance
def database_maintenance():
    """Regular database cleanup"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Vacuum database
    cursor.execute("VACUUM")
    
    # Analyze tables
    cursor.execute("ANALYZE")
    
    conn.close()

# Data Backup
def backup_database():
    """Create database backup"""
    import shutil
    from datetime import datetime
    
    backup_name = f"celebrant_portal_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DATABASE_PATH, backup_name)
    return backup_name
```

### **2. Monitoring & Health Checks**
```python
# Application Health Check
def health_check():
    """Verify application health"""
    checks = {
        'database_accessible': test_database_connection(),
        'tables_exist': verify_table_structure(),
        'admin_user_exists': check_admin_user(),
        'data_integrity': validate_data_integrity()
    }
    return all(checks.values()), checks

def test_database_connection():
    """Test database connectivity"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return True
    except Exception:
        return False
```

---

## 🎯 Implementation Roadmap

### **Phase 1: Core Foundation** ✅
- [x] Basic Streamlit app structure
- [x] SQLite database setup
- [x] User authentication
- [x] Dashboard implementation

### **Phase 2: Business Features** ✅
- [x] Couples management
- [x] Template system
- [x] Legal forms tracking
- [x] Invoice management
- [x] Travel calculator
- [x] Reports generation

### **Phase 3: Polish & Deployment** ✅
- [x] UI/UX improvements
- [x] Error handling
- [x] Documentation
- [x] Streamlit Cloud deployment

### **Phase 4: Future Enhancements** 🔄
- [ ] Multi-user support
- [ ] Email integration
- [ ] Calendar synchronization
- [ ] Payment processing
- [ ] Mobile app
- [ ] Advanced analytics

---

This comprehensive stack and blueprint provides everything needed to understand, develop, deploy, and maintain the Melbourne Celebrant Portal. The architecture prioritizes simplicity while maintaining professional functionality and future scalability.

**🚀 Ready for production deployment on Streamlit Cloud!** 