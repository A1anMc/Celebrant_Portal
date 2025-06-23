# Marriage Celebrant Portal

A comprehensive web application for marriage celebrants to manage couples, ceremonies, and legal compliance.

## Features

- **Couple Management**: Track couples, ceremony details, and communication
- **Google Maps Integration**: Calculate travel distances and fees automatically
- **Template Management**: Create and manage ceremony templates
- **Legal Forms**: Simplified legal forms dashboard (basic version)
- **Email Integration**: Gmail API integration for email scanning
- **Import/Export**: CSV import and export functionality
- **Admin Dashboard**: User management and system overview

## Project Structure

```
├── app/                    # Future modular app structure
│   ├── models/            # Database models (planned)
│   ├── routes/            # Route blueprints (planned)
│   ├── services/          # Business logic services (planned)
│   └── utils/             # Utility functions (planned)
├── database/              # Database files
├── docs/                  # Documentation
│   ├── deployment/        # Deployment guides
│   ├── setup/             # Setup instructions
│   └── guides/            # User guides
├── logs/                  # Application logs
├── migrations/            # Database migrations
├── scripts/               # Utility scripts
├── services/              # Current service modules
├── static/                # Static assets (CSS, JS, images)
├── templates/             # Jinja2 templates
├── tests/                 # Test files
├── uploads/               # File uploads
└── temp/                  # Temporary files
```

## Key Files

- `app.py` - Main Flask application
- `models.py` - Database models
- `forms.py` - WTForms definitions
- `config.py` - Configuration settings
- `requirements.txt` - Python dependencies

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Initialize Database**
   ```bash
   python scripts/init_db.py
   ```

4. **Create Admin User**
   ```bash
   python scripts/create_admin.py
   ```

5. **Run Application**
   ```bash
   python app.py
   ```

## Configuration

The application uses environment variables for configuration:

- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Database connection string
- `GOOGLE_MAPS_API_KEY` - Google Maps API key
- `GMAIL_CREDENTIALS` - Gmail API credentials

## Google Maps Integration

The application includes comprehensive Google Maps integration for:
- Distance calculation between celebrant and venue
- Travel time estimation with traffic
- Zone-based pricing for travel fees
- Interactive maps with route visualization

See `docs/setup/GOOGLE_MAPS_SETUP.md` for detailed setup instructions.

## Development

The backend has been organized and cleaned up with:
- ✅ Organized directory structure
- ✅ Clean requirements.txt with categorized dependencies
- ✅ Comprehensive .gitignore
- ✅ Fixed SQLAlchemy deprecation warnings
- ✅ Proper database file organization
- ✅ Utility scripts organized in scripts/ directory

## License

This project is licensed under the MIT License - see the LICENSE file for details.
