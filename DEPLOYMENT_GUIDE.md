# 🚀 Melbourne Celebrant Portal - Deployment Guide

## 📋 Overview

This guide provides step-by-step instructions for deploying the Melbourne Celebrant Portal to **Streamlit Cloud** for production use.

## 🎯 Deployment Options

### **Option 1: Streamlit Cloud (Recommended)**
- ✅ **Free hosting** for public repositories
- ✅ **Automatic deployments** from GitHub
- ✅ **HTTPS/SSL** included
- ✅ **Global CDN** for fast loading
- ✅ **Built-in monitoring** and analytics
- ✅ **Custom domains** supported

### **Option 2: Local Development**
- 🔧 For development and testing
- 💻 Runs on localhost:8501
- 🔄 Hot reload for development

## 🚀 Streamlit Cloud Deployment

### **Prerequisites**
1. **GitHub Account**: Free account required
2. **Streamlit Account**: Sign up at [streamlit.io](https://streamlit.io)
3. **Repository**: Code pushed to GitHub

### **Step 1: Prepare Repository**

Ensure your repository has these essential files:

```
celebrant-portal/
├── streamlit_app.py          # Main application
├── requirements.txt          # Dependencies
├── README.md                 # Documentation
├── .gitignore               # Git ignore rules
└── .streamlit/
    └── config.toml          # Streamlit configuration
```

### **Step 2: Create Streamlit Cloud Account**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign up"**
3. Choose **"Continue with GitHub"**
4. Authorize Streamlit to access your repositories

### **Step 3: Deploy Application**

1. **Click "New app"** in Streamlit Cloud dashboard
2. **Select repository**: Choose your celebrant-portal repository
3. **Set branch**: Usually `main` or `master`
4. **Set main file path**: `streamlit_app.py`
5. **Click "Deploy!"**

### **Step 4: Configure Application**

#### **Environment Variables** (if needed)
```python
# In Streamlit Cloud dashboard, go to:
# Settings > Environment Variables

# Example variables:
DATABASE_PATH = "/app/celebrant_portal.db"
DEBUG = "False"
```

#### **Streamlit Configuration**
Create `.streamlit/config.toml`:
```toml
[server]
port = 8501
enableCORS = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[browser]
gatherUsageStats = false
```

### **Step 5: Verify Deployment**

1. **Check build logs** for any errors
2. **Test application** functionality
3. **Verify login** with admin credentials
4. **Test all features** (Dashboard, Couples, etc.)

## 🔧 Local Development Setup

### **Step 1: Clone Repository**
```bash
git clone https://github.com/yourusername/celebrant-portal.git
cd celebrant-portal
```

### **Step 2: Create Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 4: Run Application**
```bash
streamlit run streamlit_app.py
```

### **Step 5: Access Application**
Open your browser to: `http://localhost:8501`

## 📁 File Structure Requirements

### **Essential Files**

#### **streamlit_app.py**
- Main application file
- Contains all functionality
- Must be named exactly `streamlit_app.py`

#### **requirements.txt**
```txt
streamlit>=1.28.0
pandas>=2.0.0
```

#### **README.md**
- Project documentation
- Installation instructions
- Usage guide

#### **.gitignore**
```gitignore
__pycache__/
*.py[cod]
*$py.class
venv/
env/
.DS_Store
*.log
```

### **Optional Files**

#### **.streamlit/config.toml**
```toml
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

## 🔒 Security Configuration

### **Authentication Setup**
The application includes a default admin user:
- **Email**: `admin@celebrant.com`
- **Password**: `admin123`

⚠️ **Important**: Change these credentials after first deployment!

### **Password Security**
```python
# Passwords are hashed with SHA256
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
```

### **Database Security**
- SQLite database is included in deployment
- Contains encrypted passwords
- Automatic backups recommended

## 🌐 Custom Domain Setup

### **Step 1: Purchase Domain**
- Choose a domain name (e.g., `celebrant-portal.com`)
- Purchase from domain registrar

### **Step 2: Configure DNS**
Add CNAME record pointing to your Streamlit app:
```
CNAME: www -> your-app-name.streamlit.app
```

### **Step 3: Update Streamlit Settings**
1. Go to Streamlit Cloud dashboard
2. Select your app
3. Go to **Settings > General**
4. Add your custom domain
5. Save changes

## 📊 Monitoring & Analytics

### **Streamlit Cloud Analytics**
- **Visitor metrics**: Page views and unique visitors
- **Performance data**: Load times and errors
- **Usage patterns**: Most popular features

### **Application Logs**
Access logs through Streamlit Cloud dashboard:
1. Select your app
2. Click **"Logs"** tab
3. View real-time application logs

### **Health Monitoring**
```python
# Add health check endpoint
def health_check():
    """Verify application health"""
    try:
        # Test database connection
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return True
    except Exception as e:
        st.error(f"Health check failed: {str(e)}")
        return False
```

## 🔄 Continuous Deployment

### **Automatic Deployments**
Streamlit Cloud automatically deploys when you:
1. Push changes to GitHub
2. Merge pull requests
3. Update the main branch

### **Deployment Workflow**
```
Local Development → Git Commit → GitHub Push → Automatic Deployment
```

### **Rollback Process**
If deployment fails:
1. Check build logs in Streamlit Cloud
2. Fix issues locally
3. Push corrected code
4. Redeploy automatically

## 🛠️ Troubleshooting

### **Common Issues**

#### **Build Failures**
```bash
# Check requirements.txt
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.8+

# Test locally first
streamlit run streamlit_app.py
```

#### **Database Issues**
```python
# Verify database file exists
import os
print(os.path.exists("celebrant_portal.db"))

# Test database connection
import sqlite3
conn = sqlite3.connect("celebrant_portal.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
conn.close()
```

#### **Authentication Problems**
```python
# Reset admin password
def reset_admin_password():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    new_password_hash = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE email = ?",
        (new_password_hash, "admin@celebrant.com")
    )
    conn.commit()
    conn.close()
```

### **Performance Issues**

#### **Slow Loading**
```python
# Add caching
@st.cache_data
def load_couples_data():
    return get_couples()

# Optimize database queries
def get_couples_optimized():
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM couples ORDER BY created_at DESC LIMIT 100", 
        conn
    )
    conn.close()
    return df
```

#### **Memory Issues**
```python
# Clear cache when needed
st.cache_data.clear()

# Limit data loading
def paginate_couples(page_size=10, page_num=1):
    offset = (page_num - 1) * page_size
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query(
        f"SELECT * FROM couples LIMIT {page_size} OFFSET {offset}",
        conn
    )
    conn.close()
    return df
```

## 📈 Performance Optimization

### **Database Optimization**
```sql
-- Create indexes for better performance
CREATE INDEX idx_couples_ceremony_date ON couples(ceremony_date);
CREATE INDEX idx_couples_status ON couples(status);
CREATE INDEX idx_couples_created_at ON couples(created_at);
```

### **Caching Strategy**
```python
# Cache expensive operations
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_dashboard_metrics():
    couples_df = get_couples()
    return calculate_revenue_metrics(couples_df)

@st.cache_data
def load_templates():
    return get_ceremony_templates()
```

### **Resource Management**
```python
# Efficient database connections
def with_database_connection(func):
    """Context manager for database operations"""
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(DATABASE_PATH)
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    return wrapper
```

## 🔐 Production Security

### **Security Checklist**
- [ ] Change default admin credentials
- [ ] Enable HTTPS (automatic with Streamlit Cloud)
- [ ] Validate all user inputs
- [ ] Use parameterized database queries
- [ ] Implement session timeouts
- [ ] Regular security updates

### **Data Protection**
```python
# Input validation
def validate_input(text, max_length=255):
    if not text or len(text) > max_length:
        return False
    # Remove potentially harmful characters
    import re
    return re.match(r'^[a-zA-Z0-9\s\-\.@_]+$', text) is not None

# SQL injection prevention
def safe_database_query(query, params):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)  # Always use parameterized queries
    result = cursor.fetchall()
    conn.close()
    return result
```

## 📞 Support & Maintenance

### **Regular Maintenance**
- **Weekly**: Check application logs
- **Monthly**: Review performance metrics
- **Quarterly**: Update dependencies
- **Annually**: Security audit

### **Backup Strategy**
```python
# Database backup
import shutil
from datetime import datetime

def backup_database():
    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DATABASE_PATH, backup_name)
    return backup_name

# Automated backups (run monthly)
def schedule_backups():
    # Implementation depends on hosting platform
    pass
```

### **Support Contacts**
- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues**: Repository issue tracker
- **Documentation**: [docs.streamlit.io](https://docs.streamlit.io)

---

## 🎯 Quick Deployment Checklist

### **Pre-Deployment**
- [ ] Code tested locally
- [ ] All features working
- [ ] Requirements.txt updated
- [ ] Documentation complete
- [ ] Repository clean

### **Deployment**
- [ ] GitHub repository created
- [ ] Streamlit Cloud account setup
- [ ] Application deployed
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active

### **Post-Deployment**
- [ ] Application accessible
- [ ] Login functionality tested
- [ ] All features verified
- [ ] Performance acceptable
- [ ] Monitoring configured

---

**🚀 Your Melbourne Celebrant Portal is now ready for production use!**

**Live URL**: `https://your-app-name.streamlit.app`
**Login**: `admin@celebrant.com` / `admin123` (change after first login)

**Need help?** Check the troubleshooting section or contact support through the Streamlit community. 