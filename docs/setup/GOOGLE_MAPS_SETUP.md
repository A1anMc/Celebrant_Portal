# Google Maps Integration Setup Guide

This guide will help you set up the Google Maps integration for automatic distance calculation, travel time estimation, and travel fee calculation.

## Features

✅ **Automatic Distance Calculation** - Calculate distance from your home to ceremony venues  
✅ **Travel Time Estimation** - Get real-time travel time including traffic conditions  
✅ **Automatic Travel Fee Calculation** - Calculate fees based on configurable rates  
✅ **Embedded Maps** - View routes directly in the application  
✅ **Batch Processing** - Calculate distances for all couples at once  
✅ **Venue Search** - Quick lookup for any venue or address  

## Prerequisites

1. **Google Cloud Platform Account** - You'll need a Google Cloud account
2. **Google Maps API Key** - With the following APIs enabled:
   - Google Maps Geocoding API
   - Google Maps Distance Matrix API
   - Google Maps Directions API
   - Google Maps Embed API

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

## Step 2: Enable Required APIs

1. In the Google Cloud Console, go to **APIs & Services > Library**
2. Search for and enable the following APIs:
   - **Maps Geocoding API**
   - **Maps Distance Matrix API** 
   - **Maps Directions API**
   - **Maps Embed API**

## Step 3: Create API Key

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > API Key**
3. Copy the generated API key
4. **Important**: Restrict the API key for security:
   - Click on the API key to edit it
   - Under "API restrictions", select "Restrict key"
   - Choose the 4 APIs you enabled above
   - Under "Application restrictions", add your domain/IP address

## Step 4: Configure Environment Variables

Add the following environment variables to your system or `.env` file:

```bash
# Required - Google Maps API Key
GOOGLE_MAPS_API_KEY=your_api_key_here

# Required - Your home/office address (starting point for all calculations)
CELEBRANT_HOME_ADDRESS="123 Your Street, Your City, State, Australia"

# Optional - Travel fee calculation settings
BASE_TRAVEL_FEE=0              # Base fee regardless of distance ($)
TRAVEL_RATE_PER_KM=1.50        # Rate per kilometer ($)
FREE_TRAVEL_DISTANCE=20        # Free distance in kilometers
MINIMUM_TRAVEL_FEE=0           # Minimum travel fee ($)
```

### Example Configuration

```bash
GOOGLE_MAPS_API_KEY=AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CELEBRANT_HOME_ADDRESS="123 Collins Street, Melbourne, VIC 3000, Australia"
BASE_TRAVEL_FEE=25
TRAVEL_RATE_PER_KM=1.50
FREE_TRAVEL_DISTANCE=20
MINIMUM_TRAVEL_FEE=25
```

## Step 5: Install Required Dependencies

The Google Maps service uses the `requests` library which should already be installed. If not:

```bash
pip install requests
```

## Step 6: Test the Integration

1. **Start your Flask application**:
   ```bash
   python app.py
   ```

2. **Test the health endpoint**:
   ```bash
   curl http://localhost:8085/api/health
   ```

3. **Test Google Maps integration**:
   - Log into your celebrant portal
   - Go to **Maps & Travel** in the navigation
   - Try the "Quick Venue Lookup" feature
   - Enter a venue name or address and click "Search"

## How Travel Fees Are Calculated

The system calculates travel fees using this formula:

```
Travel Fee = Base Fee + (Distance beyond free distance × Rate per KM)
```

### Example Calculation

With these settings:
- Base Fee: $25
- Rate per KM: $1.50
- Free Distance: 20 KM

**For a venue 35 KM away:**
- Chargeable distance: 35 - 20 = 15 KM
- Travel fee: $25 + (15 × $1.50) = $47.50

**For a venue 15 KM away:**
- Chargeable distance: 0 KM (within free distance)
- Travel fee: $25 (base fee only)

## Using the Features

### 1. Individual Couple Distance Calculation

1. Go to **Couples > Edit Couple**
2. Enter or update the ceremony location
3. Click **Calculate Distance**
4. The system will automatically:
   - Calculate distance and travel time
   - Show estimated travel fee
   - Display embedded map with route
   - Update the travel fee field

### 2. Batch Distance Calculation

1. Go to **Maps & Travel**
2. Click **Calculate All Distances**
3. The system processes all couples with ceremony locations
4. Updates travel fees for all couples automatically

### 3. Quick Venue Lookup

1. Go to **Maps & Travel**
2. Use the "Quick Venue Lookup" section
3. Enter any venue name or address
4. Get instant distance and fee calculations

### 4. Maps & Travel Dashboard

The Maps & Travel page provides:
- Overview of all venues and their distances
- Travel fees for each couple
- Quick actions to recalculate or view in Google Maps
- Batch processing capabilities

## Troubleshooting

### Common Issues

**1. "Google Maps API key not found" error**
- Ensure `GOOGLE_MAPS_API_KEY` environment variable is set
- Check that the API key is valid and not expired

**2. "Could not calculate distance" error**
- Verify the required APIs are enabled in Google Cloud
- Check API key restrictions and quotas
- Ensure the ceremony location address is valid

**3. "Access denied" or quota exceeded**
- Check your Google Cloud billing account
- Review API usage limits in Google Cloud Console
- Consider upgrading your Google Cloud plan

**4. Incorrect distance calculations**
- Verify your `CELEBRANT_HOME_ADDRESS` is accurate
- Check that addresses are in Australia (the system is optimized for AU)

### API Limits

Google Maps APIs have usage limits:
- **Free tier**: 40,000 requests per month
- **Paid tier**: Higher limits available

Monitor your usage in the Google Cloud Console.

## Security Best Practices

1. **Restrict your API key**:
   - Limit to specific APIs only
   - Add domain/IP restrictions
   - Regenerate keys periodically

2. **Environment variables**:
   - Never commit API keys to version control
   - Use `.env` files or system environment variables
   - Restrict access to production environment variables

3. **Rate limiting**:
   - The system includes built-in rate limiting
   - Consider implementing additional rate limiting for high-volume usage

## Cost Optimization

1. **Batch calculations**: Use the batch processing feature to minimize API calls
2. **Cache results**: The system stores calculated travel fees to avoid recalculation
3. **Efficient addressing**: Use complete, accurate addresses to reduce failed requests

## Support

If you encounter issues:

1. Check the Flask application logs for error messages
2. Verify your Google Cloud Console for API usage and errors
3. Test individual API endpoints using curl or Postman
4. Review the Google Maps API documentation for specific error codes

## Advanced Configuration

### Custom Travel Fee Logic

You can customize the travel fee calculation by modifying the `calculate_travel_fee` method in `services/maps_service.py`.

### Integration with Other Services

The Google Maps service can be extended to integrate with:
- Calendar systems for ceremony scheduling
- CRM systems for client management
- Accounting systems for fee tracking

### Multiple Starting Locations

For celebrants with multiple offices, you can modify the service to support multiple starting locations based on the ceremony date or location.

---

**Note**: This integration requires an active Google Cloud account with billing enabled. Google Maps API usage may incur charges based on your usage volume. 