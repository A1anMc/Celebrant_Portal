# 🏗️ Melbourne Celebrant Portal - Architecture & Blueprint

## 📋 Executive Summary

The Melbourne Celebrant Portal is a modern, streamlined web application built with **Streamlit** for managing celebrant business operations. The architecture prioritizes simplicity, maintainability, and rapid deployment while providing comprehensive business functionality.

## 🛠️ Technology Stack

### **Frontend Framework**
- **Streamlit 1.28+**: Python-based web framework
- **Responsive Design**: Mobile-friendly interface
- **Interactive Components**: Forms, charts, file uploads

### **Backend & Data**
- **SQLite**: Embedded relational database
- **Pandas**: Data manipulation and analysis
- **Python 3.8+**: Core programming language

### **Security & Authentication**
- **SHA256**: Password hashing
- **Session Management**: Streamlit session state
- **Input Validation**: Form sanitization

### **Deployment & DevOps**
- **Streamlit Cloud**: Hosting platform
- **GitHub**: Version control and CI/CD
- **Git**: Source control

## 🏛️ System Architecture

### **1. Presentation Layer**
```
┌─────────────────────────────────────┐
│           Web Interface             │
├─────────────────────────────────────┤
│ • Login/Authentication              │
│ • Dashboard & Navigation            │
│ • Forms & Data Entry                │
│ • Reports & Visualizations          │
│ • File Upload/Download              │
└─────────────────────────────────────┘
```

### **2. Business Logic Layer**
```
┌─────────────────────────────────────┐
│        Application Controllers      │
├─────────────────────────────────────┤
│ • Dashboard Controller              │
│ • Couples Management                │
│ • Template Engine                   │
│ • Legal Forms Handler               │
│ • Invoice System                    │
│ • Travel Calculator                 │
│ • Reports Generator                 │
└─────────────────────────────────────┘
```

### **3. Data Access Layer**
```
┌─────────────────────────────────────┐
│         Data Management             │
├─────────────────────────────────────┤
│ • SQLite Database Operations        │
│ • CRUD Operations                   │
│ • Data Validation                   │
│ • File I/O Operations               │
└─────────────────────────────────────┘
```

## 🗄️ Database Schema

### **Users Table**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Couples Table**
```sql
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
```

### **Templates Table** (Extended Schema)
```sql
CREATE TABLE ceremony_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Legal Forms Table** (Extended Schema)
```sql
CREATE TABLE legal_forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    couple_id INTEGER,
    form_type TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    deadline_date TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (couple_id) REFERENCES couples (id)
);
```

### **Invoices Table** (Extended Schema)
```sql
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

## 🔧 Application Components

### **1. Authentication System**
```python
# Core Functions:
- authenticate_user(email, password)
- hash_password(password)
- session_management()
- logout_user()
```

### **2. Dashboard Controller**
```python
# Key Features:
- Business metrics calculation
- Recent activity display
- Quick action buttons
- Revenue analytics
```

### **3. Couples Management**
```python
# CRUD Operations:
- add_couple(couple_data)
- get_couples()
- update_couple(id, data)
- delete_couple(id)
- search_couples(criteria)
```

### **4. Template Engine**
```python
# Template Operations:
- create_template(name, type, content)
- get_templates()
- edit_template(id, data)
- delete_template(id)
```

### **5. Legal Forms Handler**
```python
# Compliance Management:
- track_noim_status()
- calculate_deadlines()
- upload_legal_documents()
- generate_compliance_reports()
```

### **6. Invoice System**
```python
# Financial Management:
- create_invoice(couple_id, amount)
- track_payment_status()
- generate_financial_reports()
- calculate_revenue_metrics()
```

### **7. Travel Calculator**
```python
# Distance & Cost Calculation:
- calculate_distance(origin, destination)
- estimate_travel_cost(distance, rate)
- manage_location_data()
```

## 🚀 Deployment Architecture

### **Development Environment**
```
Local Machine
├── Python 3.8+
├── Virtual Environment
├── SQLite Database
└── Streamlit Dev Server (localhost:8501)
```

### **Production Environment**
```
Streamlit Cloud
├── GitHub Integration
├── Automatic Deployments
├── SSL/HTTPS Enabled
├── Global CDN
└── Monitoring & Analytics
```

### **CI/CD Pipeline**
```
GitHub Repository
├── Push to main branch
├── Automatic deployment trigger
├── Streamlit Cloud build
├── Health checks
└── Live deployment
```

## 📁 Project Structure

```
celebrant-portal/
├── streamlit_app.py          # Main application file
├── celebrant_portal.db       # SQLite database
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── ARCHITECTURE.md           # This architecture document
├── STREAMLIT_README.md       # Streamlit-specific docs
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT License
└── .streamlit/
    └── config.toml          # Streamlit configuration
```

## 🔒 Security Architecture

### **Authentication Flow**
1. User enters credentials
2. Password hashed with SHA256
3. Database verification
4. Session state management
5. Protected route access

### **Data Protection**
- **Input Sanitization**: All form inputs validated
- **SQL Injection Prevention**: Parameterized queries
- **Session Security**: Streamlit session management
- **File Upload Security**: Type validation and size limits

### **Access Control**
- **Single Admin User**: Simplified access model
- **Session-based Authentication**: No JWT complexity
- **Logout Functionality**: Secure session termination

## 📊 Performance Considerations

### **Database Optimization**
- **SQLite**: Optimal for single-user applications
- **Indexed Queries**: Primary keys and common searches
- **Connection Management**: Proper open/close patterns

### **Application Performance**
- **Streamlit Caching**: `@st.cache_data` for expensive operations
- **Lazy Loading**: Data loaded on-demand
- **Minimal Dependencies**: Only essential packages

### **Scalability**
- **Horizontal Scaling**: Multiple Streamlit Cloud instances
- **Database Migration**: Easy SQLite to PostgreSQL upgrade path
- **Modular Design**: Easy feature addition/removal

## 🔄 Data Flow Architecture

### **User Interaction Flow**
```
User Input → Form Validation → Business Logic → Database Update → UI Refresh
```

### **Report Generation Flow**
```
Data Query → Pandas Processing → Chart Generation → Streamlit Display
```

### **File Upload Flow**
```
File Selection → Validation → Processing → Database Storage → Confirmation
```

## 🎯 Business Logic Architecture

### **Core Business Rules**
1. **NOIM Compliance**: 1-month deadline tracking
2. **Invoice Management**: Status-based workflow
3. **Ceremony Scheduling**: Date/time validation
4. **Travel Calculations**: Distance-based pricing
5. **Template Management**: Type-based categorization

### **Workflow States**
```
Couple Status Flow:
Inquiry → Consultation → Booked → Confirmed → Completed

Invoice Status Flow:
Draft → Sent → Paid → Overdue

Legal Forms Flow:
Pending → Submitted → Approved → Filed
```

## 🛡️ Error Handling & Logging

### **Error Management**
- **Try-Catch Blocks**: Database operations wrapped
- **User-Friendly Messages**: Clear error communication
- **Graceful Degradation**: Fallback for missing data
- **Input Validation**: Prevent invalid data entry

### **Logging Strategy**
- **Streamlit Logging**: Built-in error reporting
- **Database Errors**: Connection and query logging
- **User Actions**: Session-based activity tracking

## 🔮 Future Architecture Considerations

### **Potential Enhancements**
1. **Multi-User Support**: Role-based access control
2. **API Layer**: REST API for mobile apps
3. **Advanced Analytics**: Machine learning insights
4. **Email Integration**: Automated communications
5. **Calendar Sync**: Google Calendar integration
6. **Payment Processing**: Stripe/PayPal integration
7. **Document Generation**: PDF certificate creation

### **Migration Paths**
- **Database**: SQLite → PostgreSQL/MySQL
- **Framework**: Streamlit → FastAPI + React
- **Hosting**: Streamlit Cloud → AWS/Azure
- **Authentication**: Simple → OAuth/SAML

## 📈 Monitoring & Analytics

### **Application Metrics**
- **User Sessions**: Login frequency and duration
- **Feature Usage**: Most-used application sections
- **Performance**: Page load times and responsiveness
- **Error Rates**: Application stability metrics

### **Business Metrics**
- **Revenue Tracking**: Monthly/yearly income
- **Couple Pipeline**: Conversion rates
- **Ceremony Types**: Popular service categories
- **Geographic Distribution**: Service area analysis

## 🎨 UI/UX Architecture

### **Design System**
- **Streamlit Components**: Native UI elements
- **Responsive Layout**: Mobile-first design
- **Color Scheme**: Professional celebrant branding
- **Typography**: Clear, readable fonts
- **Icons**: Emoji-based visual hierarchy

### **User Experience Flow**
1. **Login**: Simple credential entry
2. **Dashboard**: Overview and quick actions
3. **Navigation**: Sidebar-based menu system
4. **Forms**: Step-by-step data entry
5. **Reports**: Visual data presentation

## 📋 Development Standards

### **Code Quality**
- **PEP 8**: Python style guide compliance
- **Type Hints**: Function parameter typing
- **Documentation**: Inline code comments
- **Modular Functions**: Single responsibility principle

### **Testing Strategy**
- **Manual Testing**: UI interaction validation
- **Database Testing**: CRUD operation verification
- **Integration Testing**: End-to-end workflows
- **Performance Testing**: Load and stress testing

## 🔧 Configuration Management

### **Environment Variables**
```python
# Development
DEBUG = True
DATABASE_PATH = "celebrant_portal.db"

# Production
DEBUG = False
DATABASE_PATH = "/app/data/celebrant_portal.db"
```

### **Streamlit Configuration**
```toml
[server]
port = 8501
enableCORS = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
```

---

## 🎯 Summary

The Melbourne Celebrant Portal represents a **modern, simplified architecture** that prioritizes:

- **Rapid Development**: Streamlit's Python-first approach
- **Easy Deployment**: One-click Streamlit Cloud hosting
- **Low Maintenance**: Minimal infrastructure requirements
- **Business Focus**: Core celebrant functionality
- **Future Growth**: Modular, extensible design

This architecture provides a **solid foundation** for a professional celebrant business while maintaining the flexibility to evolve with changing requirements.

---

**Built with ❤️ using modern Python web technologies** 