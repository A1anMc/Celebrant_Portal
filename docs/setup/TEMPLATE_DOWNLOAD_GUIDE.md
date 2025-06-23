# 📄 Enhanced Template Download/Import Guide

## 🎯 Overview

Your celebrant portal now supports importing templates from multiple file formats stored in Google Drive:

- ✅ **Google Docs** - Full import and preview support
- ✅ **Word Documents (.docx)** - Full import support  
- ✅ **PDFs** - Import and preview support
- ✅ **Google Sheets** - Preview only (for ceremony schedules, etc.)
- ⚠️ **Word .doc files** - Limited support (recommend converting to .docx)
- ⚠️ **Excel files** - Basic support (better to use Google Sheets)

## 🔧 How It Works

### **1. File Detection**
The system automatically detects file types and shows:
- **File Type** (google_doc, word_docx, pdf, etc.)
- **Import Support** (✅ = can import, ❌ = preview only)
- **Preview Support** (✅ = can preview, ❌ = download only)

### **2. Content Processing**
Each file type is processed differently:

#### **Google Docs** 🟢
- **Best Support** - Exported as HTML
- **Features**: Full formatting, automatic placeholder conversion
- **Template Placeholders**: Names, dates, locations automatically converted
- **Recommended for**: Ceremony scripts, vows, email templates

#### **Word Documents (.docx)** 🟡  
- **Good Support** - Text extraction with formatting
- **Features**: Paragraph structure preserved, placeholder conversion
- **Requirements**: python-docx library (already installed)
- **Recommended for**: Existing ceremony templates, contracts

#### **PDFs** 🟡
- **Text Extraction** - Content extracted as plain text
- **Features**: Multi-page support, basic placeholder conversion
- **Requirements**: PyPDF2 library (already installed)
- **Best for**: Reference documents, existing ceremony scripts

#### **Google Sheets** 🔵
- **Preview Only** - Tables converted to readable format
- **Features**: Multiple sheet support, table formatting
- **Use cases**: Ceremony schedules, contact lists, planning sheets
- **Note**: Cannot be imported as ceremony templates

#### **Excel Files** ⚪
- **Basic Support** - Data extraction only
- **Requirements**: pandas + openpyxl libraries (already installed)
- **Recommendation**: Convert to Google Sheets for better support

## 🚀 How to Use

### **Step 1: Access Import Feature**
1. Go to **Templates** → **Import from Google Drive**
2. Ensure Google Drive API is enabled (if you see errors)
3. Authorize access if prompted

### **Step 2: Search for Templates**
The system searches for files containing keywords:
- `template`
- `ceremony` 
- `mc`
- `vow`
- `wedding`
- `celebrant`
- `script`
- `order of service`

### **Step 3: Choose Import Method**

#### **Preview First (Recommended)**
1. Click **Preview** to see content
2. Review the processed template
3. Click **Import This Template** if satisfied

#### **Direct Import**
1. Click **Import** directly
2. Configure template settings:
   - **Name**: Display name in your system
   - **Type**: Civil, Custom, MC, Email
   - **Description**: Optional notes
   - **Default**: Set as default for this type

### **Step 4: Template Processing**
The system automatically:
- Extracts and cleans content
- Converts common names to placeholders:
  - `John and Jane` → `{{ partner1_name }} and {{ partner2_name }}`
  - `the bride` → `{{ partner1_name }}`
  - `the groom` → `{{ partner2_name }}`
  - Dates → `{{ ceremony_date }}`
  - Times → `{{ ceremony_time }}`
  - Locations → `{{ ceremony_location }}`

## 🎨 Template Placeholders

### **Available Placeholders**
```
{{ partner1_name }}          - First partner's name
{{ partner2_name }}          - Second partner's name  
{{ ceremony_date }}          - Wedding date
{{ ceremony_time }}          - Ceremony time
{{ ceremony_location }}      - Venue/location
{{ celebrant_name }}         - Your name
{{ guest_count }}            - Number of guests
{{ ceremony_type }}          - Type of ceremony
```

### **Example Template**
```
Welcome everyone to the marriage ceremony of {{ partner1_name }} and {{ partner2_name }}.

Today, on {{ ceremony_date }} at {{ ceremony_time }}, we gather at {{ ceremony_location }} to witness their commitment.

{{ partner1_name }}, do you take {{ partner2_name }} to be your spouse...
```

## ⚡ Performance Tips

### **Best Practices**
1. **Use Google Docs** for new templates (best compatibility)
2. **Convert .doc to .docx** for better Word support
3. **Keep files under 10MB** for faster processing
4. **Use descriptive filenames** with keywords for easy discovery
5. **Organize in folders** for better searching

### **File Organization**
```
📁 Celebrant Templates/
├── 📁 Ceremony Scripts/
│   ├── 📄 Civil Ceremony Template.docx
│   ├── 📄 Beach Wedding Script.pdf
│   └── 📄 Custom Vows Template.gdoc
├── 📁 MC Scripts/
│   ├── 📄 Reception MC Template.docx
│   └── 📄 Wedding Party Intro.pdf
└── 📁 Email Templates/
    ├── 📄 Welcome Email.gdoc
    └── 📄 Reminder Template.docx
```

## 🔧 Troubleshooting

### **Common Issues**

#### **"Failed to search Drive files"**
- **Cause**: Google Drive API not enabled
- **Solution**: Enable Drive API in Google Cloud Console
- **Link**: Use the provided console link in error message

#### **"No templates found"**
- **Cause**: Files don't contain search keywords
- **Solution**: Rename files to include keywords like "template", "ceremony", etc.

#### **"Cannot import this file type"**
- **Cause**: Unsupported file format
- **Solution**: Convert to Google Docs or .docx format

#### **"Error processing file"**
- **Cause**: Corrupted file or missing libraries
- **Solution**: Check file integrity, ensure all libraries installed

### **Library Requirements**
If you see import errors, ensure these are installed:
```bash
pip install python-docx PyPDF2 pandas openpyxl xlrd beautifulsoup4
```

## 📊 File Format Comparison

| Format | Import | Preview | Quality | Speed | Recommended |
|--------|--------|---------|---------|-------|-------------|
| Google Docs | ✅ | ✅ | Excellent | Fast | ⭐⭐⭐⭐⭐ |
| Word .docx | ✅ | ❌ | Good | Medium | ⭐⭐⭐⭐ |
| PDF | ✅ | ✅ | Fair | Slow | ⭐⭐⭐ |
| Google Sheets | ❌ | ✅ | Good | Fast | ⭐⭐ (preview only) |
| Word .doc | ⚠️ | ❌ | Poor | Slow | ⭐ (convert to .docx) |
| Excel | ⚠️ | ❌ | Poor | Slow | ⭐ (use Google Sheets) |

## 🎉 Success! 

Your enhanced template system now supports:
- **Multiple file formats** for maximum flexibility
- **Automatic content processing** with smart placeholder conversion
- **Preview capabilities** to review before importing
- **Intelligent file detection** with import/preview indicators
- **Robust error handling** with helpful error messages

Start importing your existing templates and enjoy the improved workflow! 🚀 

# Environment Variables Setup Guide

## 🔧 Setting Up Environment Variables for Google Maps

### **Step 1: Create a .env file**

Create a new file called `.env` in your project root directory (same folder as `app.py`) with the following content:

```env
# Google Maps Integration Configuration
# REQUIRED: Google Maps API Key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# REQUIRED: Your home/office address (starting point for distance calculations)
CELEBRANT_HOME_ADDRESS="123 Your Street, Your Suburb, Your City, State, Postcode, Australia"

# OPTIONAL: Travel Fee Configuration
BASE_TRAVEL_FEE=25
TRAVEL_RATE_PER_KM=1.50
FREE_TRAVEL_DISTANCE=20
MINIMUM_TRAVEL_FEE=25
```

### **Step 2: Replace with Your Actual Values**

1. **GOOGLE_MAPS_API_KEY**: Replace `your_google_maps_api_key_here` with your actual API key from Google Cloud Console
2. **CELEBRANT_HOME_ADDRESS**: Replace with your actual home or office address
3. **Travel Fee Settings**: Adjust the numbers to match your pricing structure

### **Example with Real Values:**

```env
GOOGLE_MAPS_API_KEY=AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CELEBRANT_HOME_ADDRESS="123 Collins Street, Melbourne, VIC 3000, Australia"
BASE_TRAVEL_FEE=30
TRAVEL_RATE_PER_KM=2.00
FREE_TRAVEL_DISTANCE=25
MINIMUM_TRAVEL_FEE=30
```

## 🖥️ Alternative Methods

### **Method 2: Terminal/Command Line (Temporary)**

For macOS/Linux (your current system):
```bash
export GOOGLE_MAPS_API_KEY="your_api_key_here"
export CELEBRANT_HOME_ADDRESS="123 Your Street, Your Suburb, Your City, State, Postcode, Australia"
export BASE_TRAVEL_FEE=25
export TRAVEL_RATE_PER_KM=1.50
export FREE_TRAVEL_DISTANCE=20
export MINIMUM_TRAVEL_FEE=25
```

### **Method 3: Add to Shell Profile (Permanent)**

Add to your `~/.zshrc` file (since you're using zsh):
```bash
echo 'export GOOGLE_MAPS_API_KEY="your_api_key_here"' >> ~/.zshrc
echo 'export CELEBRANT_HOME_ADDRESS="123 Your Street, Your City, State, Postcode, Australia"' >> ~/.zshrc
echo 'export BASE_TRAVEL_FEE=25' >> ~/.zshrc
echo 'export TRAVEL_RATE_PER_KM=1.50' >> ~/.zshrc
echo 'export FREE_TRAVEL_DISTANCE=20' >> ~/.zshrc
echo 'export MINIMUM_TRAVEL_FEE=25' >> ~/.zshrc
source ~/.zshrc
```

## 💰 Travel Fee Calculation Examples

With the example settings above:
- **Venue 10km away**: $30 (base fee only, within free distance)
- **Venue 30km away**: $30 + (10km × $2.00) = $50
- **Venue 50km away**: $30 + (25km × $2.00) = $80

## ✅ Verification

After setting up your environment variables, you can test them by running:

```bash
python test_maps_integration.py
```

This will verify your configuration and show you sample distance calculations.

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Keep your API key secure and don't share it
- The `.env` file should be in your `.gitignore` (it already is)
- Consider using API key restrictions in Google Cloud Console

## 🎯 Quick Setup Checklist

- [ ] Create `.env` file in project root
- [ ] Add your Google Maps API key
- [ ] Add your home/office address
- [ ] Configure travel fee settings
- [ ] Test with `python test_maps_integration.py`
- [ ] Restart your Flask application 