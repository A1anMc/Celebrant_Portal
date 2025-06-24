# 🌟 Melbourne Celebrant Portal - Streamlit Version

A modern, user-friendly web application for managing wedding couples and ceremonies, built with Streamlit.

## ✨ Features

- 🔐 **Secure Authentication** - Login system with admin access
- 💑 **Couple Management** - Add, edit, view, and search couples
- 📅 **Wedding Planning** - Track wedding dates, venues, and ceremony details
- 📊 **Dashboard** - Overview of upcoming weddings and statistics
- 🔍 **Search Functionality** - Find couples by name, email, or venue
- 📱 **Responsive Design** - Works on desktop and mobile devices

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r streamlit_requirements.txt
   ```

2. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Access the app:**
   - Open your browser to `http://localhost:8501`
   - Login with: `admin@celebrant.com` / `admin123`

### Deploy to Streamlit Cloud

1. **Push to GitHub:**
   ```bash
   git add streamlit_app.py streamlit_requirements.txt .streamlit/
   git commit -m "Add Streamlit version"
   git push
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repo
   - Set main file: `streamlit_app.py`
   - Deploy!

## 🎯 Default Login

- **Email:** `admin@celebrant.com`
- **Password:** `admin123`

## 📁 Database

The app uses SQLite for data storage:
- Database file: `celebrant_portal.db` (created automatically)
- Tables: `users`, `couples`
- All data persists between sessions

## 🛠️ Key Functions

- **Add Couples:** Complete wedding party information
- **View Dashboard:** Statistics and upcoming weddings
- **Search:** Find couples quickly by any field
- **Edit/Delete:** Manage existing couple records
- **Secure Login:** Password-protected access

## 🎨 UI Features

- Clean, modern interface with emojis and colors
- Expandable couple cards for easy viewing
- Form validation and user feedback
- Responsive layout for all devices
- Intuitive navigation with sidebar

## 🔧 Customization

- Modify colors in `.streamlit/config.toml`
- Add new fields to the couples table
- Extend authentication for multiple users
- Add email notifications or integrations

## 📝 Notes

- Much simpler than the Flask version
- No complex deployment configuration needed
- SQLite database is portable and reliable
- Perfect for small to medium celebrant businesses

---

**Ready to use! No more Railway headaches! 🎉** 