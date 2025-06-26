#!/usr/bin/env python3
"""
PDF Generation Script for Melbourne Celebrant Portal
Converts the welcome guide markdown to a professional PDF
"""

import markdown
import pdfkit
import os
from datetime import datetime

def generate_welcome_pdf():
    """Generate a professional PDF from the welcome guide markdown."""
    
    # Read the markdown file
    try:
        with open('welcome-guide.md', 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print("Error: welcome-guide.md not found")
        return False
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        markdown_content, 
        extensions=['tables', 'toc', 'codehilite']
    )
    
    # Add professional styling
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Melbourne Celebrant Portal - Welcome Guide</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');
            
            body {{
                font-family: 'Inter', Arial, sans-serif;
                line-height: 1.6;
                color: #2D3748;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px;
                background-color: #FEFEFE;
            }}
            
            h1 {{
                font-family: 'Playfair Display', serif;
                color: #D4A373;
                font-size: 2.5em;
                text-align: center;
                margin-bottom: 0.5em;
                border-bottom: 3px solid #D4A373;
                padding-bottom: 20px;
            }}
            
            h2 {{
                font-family: 'Playfair Display', serif;
                color: #B8956A;
                font-size: 1.8em;
                margin-top: 40px;
                margin-bottom: 20px;
                border-left: 4px solid #D4A373;
                padding-left: 20px;
            }}
            
            h3 {{
                color: #2D3748;
                font-size: 1.3em;
                margin-top: 30px;
                margin-bottom: 15px;
                font-weight: 600;
            }}
            
            h4 {{
                color: #4A5568;
                font-size: 1.1em;
                margin-top: 25px;
                margin-bottom: 12px;
                font-weight: 500;
            }}
            
            p {{
                margin-bottom: 15px;
                text-align: justify;
            }}
            
            ul, ol {{
                margin-bottom: 20px;
                padding-left: 30px;
            }}
            
            li {{
                margin-bottom: 8px;
            }}
            
            code {{
                background-color: #F5F5F5;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }}
            
            pre {{
                background-color: #F5F5F5;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #D4A373;
                overflow-x: auto;
                margin: 20px 0;
            }}
            
            blockquote {{
                background-color: #E8C4A0;
                padding: 20px;
                border-left: 4px solid #D4A373;
                margin: 20px 0;
                border-radius: 0 8px 8px 0;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #E2E8F0;
            }}
            
            th {{
                background-color: #D4A373;
                color: white;
                font-weight: 600;
            }}
            
            tr:nth-child(even) {{
                background-color: #F5F5F5;
            }}
            
            .header-info {{
                text-align: center;
                margin-bottom: 40px;
                padding: 30px;
                background: linear-gradient(135deg, #D4A373 0%, #B8956A 100%);
                color: white;
                border-radius: 8px;
            }}
            
            .footer-info {{
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                background-color: #F5F5F5;
                border-radius: 8px;
                font-size: 0.9em;
                color: #4A5568;
            }}
            
            .page-break {{
                page-break-before: always;
            }}
            
            @media print {{
                body {{
                    padding: 20px;
                }}
                
                .header-info {{
                    background: #D4A373 !important;
                    -webkit-print-color-adjust: exact;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header-info">
            <h1>Melbourne Celebrant Portal</h1>
            <p style="font-size: 1.2em; margin: 0;">Welcome Guide & User Manual</p>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Your Professional Wedding Management Platform</p>
        </div>
        
        {html_content}
        
        <div class="footer-info">
            <p><strong>Melbourne Celebrant Portal</strong> - Empowering celebrants with professional tools</p>
            <p>Generated on {datetime.now().strftime('%B %d, %Y')} | Version 2.0.0</p>
            <p>For support: support@melbournecelebrant.com | 1300 CELEBRANT</p>
        </div>
    </body>
    </html>
    """
    
    # PDF generation options
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None,
        'print-media-type': None,
    }
    
    # Generate PDF
    try:
        output_filename = f"Melbourne_Celebrant_Portal_Welcome_Guide_{datetime.now().strftime('%Y%m%d')}.pdf"
        pdfkit.from_string(styled_html, output_filename, options=options)
        print(f"✅ PDF generated successfully: {output_filename}")
        return True
    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        print("💡 Note: You may need to install wkhtmltopdf:")
        print("   - macOS: brew install wkhtmltopdf")
        print("   - Ubuntu: sudo apt-get install wkhtmltopdf")
        print("   - Windows: Download from https://wkhtmltopdf.org/downloads.html")
        return False

def generate_marketing_checklist_pdf():
    """Generate a PDF from the marketing checklist markdown."""
    
    try:
        with open('marketing-launch-checklist.md', 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print("Error: marketing-launch-checklist.md not found")
        return False
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        markdown_content, 
        extensions=['tables', 'toc', 'codehilite']
    )
    
    # Add professional styling (similar to welcome guide but with checklist styling)
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Melbourne Celebrant Portal - Marketing Launch Checklist</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');
            
            body {{
                font-family: 'Inter', Arial, sans-serif;
                line-height: 1.6;
                color: #2D3748;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px;
                background-color: #FEFEFE;
            }}
            
            h1 {{
                font-family: 'Playfair Display', serif;
                color: #D4A373;
                font-size: 2.5em;
                text-align: center;
                margin-bottom: 0.5em;
                border-bottom: 3px solid #D4A373;
                padding-bottom: 20px;
            }}
            
            h2 {{
                font-family: 'Playfair Display', serif;
                color: #B8956A;
                font-size: 1.8em;
                margin-top: 40px;
                margin-bottom: 20px;
                border-left: 4px solid #D4A373;
                padding-left: 20px;
            }}
            
            h3 {{
                color: #2D3748;
                font-size: 1.3em;
                margin-top: 30px;
                margin-bottom: 15px;
                font-weight: 600;
            }}
            
            /* Checkbox styling for checklist items */
            ul li {{
                list-style: none;
                position: relative;
                padding-left: 30px;
                margin-bottom: 10px;
            }}
            
            ul li:before {{
                content: "☐";
                position: absolute;
                left: 0;
                color: #D4A373;
                font-size: 1.2em;
                font-weight: bold;
            }}
            
            /* Keep regular bullet points for nested lists */
            ul ul li:before {{
                content: "•";
                color: #4A5568;
            }}
            
            .header-info {{
                text-align: center;
                margin-bottom: 40px;
                padding: 30px;
                background: linear-gradient(135deg, #D4A373 0%, #B8956A 100%);
                color: white;
                border-radius: 8px;
            }}
            
            .footer-info {{
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                background-color: #F5F5F5;
                border-radius: 8px;
                font-size: 0.9em;
                color: #4A5568;
            }}
        </style>
    </head>
    <body>
        <div class="header-info">
            <h1>Melbourne Celebrant Portal</h1>
            <p style="font-size: 1.2em; margin: 0;">Marketing Launch Checklist</p>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Complete Guide for Successful Product Launch</p>
        </div>
        
        {html_content}
        
        <div class="footer-info">
            <p><strong>Melbourne Celebrant Portal</strong> - Marketing Launch Strategy</p>
            <p>Generated on {datetime.now().strftime('%B %d, %Y')} | Version 2.0.0</p>
        </div>
    </body>
    </html>
    """
    
    # PDF generation options
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None,
        'print-media-type': None,
    }
    
    # Generate PDF
    try:
        output_filename = f"Melbourne_Celebrant_Portal_Marketing_Checklist_{datetime.now().strftime('%Y%m%d')}.pdf"
        pdfkit.from_string(styled_html, output_filename, options=options)
        print(f"✅ Marketing checklist PDF generated successfully: {output_filename}")
        return True
    except Exception as e:
        print(f"❌ Error generating marketing checklist PDF: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 Melbourne Celebrant Portal - PDF Generator")
    print("=" * 50)
    
    # Generate welcome guide PDF
    print("\n📋 Generating Welcome Guide PDF...")
    generate_welcome_pdf()
    
    # Generate marketing checklist PDF
    print("\n📈 Generating Marketing Checklist PDF...")
    generate_marketing_checklist_pdf()
    
    print("\n✨ PDF generation complete!")
    print("\n💡 To install required dependencies:")
    print("   pip install markdown pdfkit")
    print("   # Also install wkhtmltopdf system package") 