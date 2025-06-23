#!/usr/bin/env python3
"""
Startup script for the Celebrant Portal with Google Drive Import functionality
"""

from app import app

if __name__ == '__main__':
    print('🚀 Starting Celebrant Portal with Google Drive Import...')
    print('📍 Access: http://127.0.0.1:8085')
    print('🔗 New Feature: Google Drive Template Import')
    print('👤 Login: admin@celebrant.local / admin123')
    print('=' * 60)
    
    # Start the Flask development server
    app.run(host='0.0.0.0', port=8085, debug=True) 