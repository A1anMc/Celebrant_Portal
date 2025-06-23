import os
import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class GoogleMapsService:
    """Service for Google Maps integration - distance, travel time, and fee calculations."""
    
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            logger.warning("Google Maps API key not found. Set GOOGLE_MAPS_API_KEY environment variable.")
        
        # Default celebrant home address (update this with your actual address)
        self.home_address = os.environ.get('CELEBRANT_HOME_ADDRESS', 
                                         'Melbourne, VIC, Australia')
        
        # Travel fee calculation settings
        self.base_fee = float(os.environ.get('BASE_TRAVEL_FEE', '0'))  # Base fee regardless of distance
        self.rate_per_km = float(os.environ.get('TRAVEL_RATE_PER_KM', '1.50'))  # Rate per kilometer
        self.free_distance_km = float(os.environ.get('FREE_TRAVEL_DISTANCE', '20'))  # Free travel distance
        self.minimum_fee = float(os.environ.get('MINIMUM_TRAVEL_FEE', '0'))  # Minimum travel fee
        
        # API endpoints
        self.geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.distance_matrix_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        self.directions_url = "https://maps.googleapis.com/maps/api/directions/json"
    
    def geocode_address(self, address: str) -> Optional[Dict]:
        """Convert address to coordinates using Google Geocoding API."""
        if not self.api_key:
            return None
        
        try:
            params = {
                'address': address,
                'key': self.api_key,
                'region': 'au',  # Bias towards Australia
                'components': 'country:AU'  # Restrict to Australia
            }
            
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                location = result['geometry']['location']
                
                return {
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'formatted_address': result['formatted_address'],
                    'place_id': result.get('place_id'),
                    'address_components': result.get('address_components', [])
                }
            else:
                logger.warning(f"Geocoding failed for address '{address}': {data.get('status')}")
                return None
                
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {str(e)}")
            return None
    
    def calculate_distance_and_time(self, destination_address: str, 
                                  departure_time: Optional[datetime] = None) -> Optional[Dict]:
        """Calculate distance and travel time from home to destination."""
        if not self.api_key:
            return None
        
        try:
            params = {
                'origins': self.home_address,
                'destinations': destination_address,
                'key': self.api_key,
                'units': 'metric',
                'mode': 'driving',
                'avoid': 'tolls',  # Avoid tolls by default
                'region': 'au'
            }
            
            # Add departure time for traffic-aware routing
            if departure_time:
                timestamp = int(departure_time.timestamp())
                params['departure_time'] = timestamp
            
            response = requests.get(self.distance_matrix_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'OK' and data['rows']:
                element = data['rows'][0]['elements'][0]
                
                if element['status'] == 'OK':
                    distance = element['distance']
                    duration = element['duration']
                    
                    # Get traffic-aware duration if available
                    duration_in_traffic = element.get('duration_in_traffic', duration)
                    
                    distance_km = round(distance['value'] / 1000, 1)
                    zone_info = self.get_travel_zone(distance_km)
                    
                    result = {
                        'distance_km': distance_km,
                        'distance_text': distance['text'],
                        'duration_minutes': round(duration['value'] / 60),
                        'duration_text': duration['text'],
                        'duration_in_traffic_minutes': round(duration_in_traffic['value'] / 60),
                        'duration_in_traffic_text': duration_in_traffic['text'],
                        'origin': data['origin_addresses'][0],
                        'destination': data['destination_addresses'][0],
                        'travel_zone': zone_info['zone'],
                        'travel_zone_range': zone_info['range'],
                        'travel_fee': zone_info['fee']
                    }
                    
                    return result
                else:
                    logger.warning(f"Distance calculation failed for '{destination_address}': {element['status']}")
                    return None
            else:
                logger.warning(f"Distance Matrix API failed: {data.get('status')}")
                return None
                
        except Exception as e:
            logger.error(f"Error calculating distance to '{destination_address}': {str(e)}")
            return None
    
    def get_travel_zone(self, distance_km: float) -> Dict[str, any]:
        """Get travel zone information for a given distance."""
        if distance_km <= 5:
            return {"zone": "Zone 1", "range": "0-5km", "fee": 10.0}
        elif distance_km <= 10:
            return {"zone": "Zone 2", "range": "5-10km", "fee": 20.0}
        elif distance_km <= 15:
            return {"zone": "Zone 3", "range": "10-15km", "fee": 30.0}
        elif distance_km <= 25:
            return {"zone": "Zone 4", "range": "15-25km", "fee": 40.0}
        elif distance_km <= 40:
            return {"zone": "Zone 5", "range": "25-40km", "fee": 50.0}
        else:
            extra_distance = distance_km - 40
            extra_fee = extra_distance * 1.25
            total_fee = 50.0 + extra_fee
            return {"zone": "Zone 5+", "range": f"40km+ ({distance_km:.1f}km)", "fee": round(total_fee, 2)}

    def calculate_travel_fee(self, distance_km: float) -> float:
        """Calculate travel fee based on zone-based pricing structure."""
        # Zone-based pricing structure
        # Zone 1: 0-5km = $10, Zone 2: 5-10km = $20, Zone 3: 10-15km = $30
        # Zone 4: 15-25km = $40, Zone 5: 25-40km = $50
        
        zone_info = self.get_travel_zone(distance_km)
        return zone_info["fee"]
    
    def get_directions(self, destination_address: str, 
                      departure_time: Optional[datetime] = None) -> Optional[Dict]:
        """Get detailed directions from home to destination."""
        if not self.api_key:
            return None
        
        try:
            params = {
                'origin': self.home_address,
                'destination': destination_address,
                'key': self.api_key,
                'mode': 'driving',
                'avoid': 'tolls',
                'region': 'au'
            }
            
            if departure_time:
                timestamp = int(departure_time.timestamp())
                params['departure_time'] = timestamp
            
            response = requests.get(self.directions_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'OK' and data['routes']:
                route = data['routes'][0]
                leg = route['legs'][0]
                
                return {
                    'distance_km': round(leg['distance']['value'] / 1000, 1),
                    'distance_text': leg['distance']['text'],
                    'duration_minutes': round(leg['duration']['value'] / 60),
                    'duration_text': leg['duration']['text'],
                    'start_address': leg['start_address'],
                    'end_address': leg['end_address'],
                    'steps': [
                        {
                            'instruction': step['html_instructions'],
                            'distance': step['distance']['text'],
                            'duration': step['duration']['text']
                        }
                        for step in leg['steps']
                    ],
                    'overview_polyline': route['overview_polyline']['points']
                }
            else:
                logger.warning(f"Directions API failed: {data.get('status')}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting directions to '{destination_address}': {str(e)}")
            return None
    
    def get_venue_info(self, venue_name: str, address: str = None) -> Optional[Dict]:
        """Get comprehensive venue information including location and travel details."""
        search_query = f"{venue_name}"
        if address:
            search_query += f", {address}"
        
        # First geocode the venue
        location_info = self.geocode_address(search_query)
        if not location_info:
            return None
        
        # Calculate distance and travel time
        travel_info = self.calculate_distance_and_time(location_info['formatted_address'])
        
        result = {
            'venue_name': venue_name,
            'formatted_address': location_info['formatted_address'],
            'coordinates': {
                'lat': location_info['lat'],
                'lng': location_info['lng']
            },
            'place_id': location_info.get('place_id')
        }
        
        if travel_info:
            result.update(travel_info)
        
        return result
    
    def generate_maps_url(self, destination_address: str, mode: str = 'driving') -> str:
        """Generate Google Maps URL for directions."""
        base_url = "https://www.google.com/maps/dir/"
        origin = self.home_address.replace(' ', '+')
        destination = destination_address.replace(' ', '+')
        
        return f"{base_url}{origin}/{destination}/{mode}"
    
    def generate_embed_map_url(self, destination_address: str, zoom: int = 15) -> str:
        """Generate embeddable Google Maps URL."""
        if not self.api_key:
            return ""
        
        base_url = "https://www.google.com/maps/embed/v1/directions"
        params = {
            'key': self.api_key,
            'origin': self.home_address,
            'destination': destination_address,
            'mode': 'driving',
            'zoom': zoom
        }
        
        param_string = '&'.join([f"{k}={v.replace(' ', '+')}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
    
    def batch_calculate_distances(self, destinations: List[str]) -> Dict[str, Dict]:
        """Calculate distances to multiple destinations efficiently."""
        results = {}
        
        # Google Distance Matrix API supports up to 25 destinations per request
        batch_size = 25
        
        for i in range(0, len(destinations), batch_size):
            batch = destinations[i:i + batch_size]
            
            try:
                if not self.api_key:
                    continue
                
                params = {
                    'origins': self.home_address,
                    'destinations': '|'.join(batch),
                    'key': self.api_key,
                    'units': 'metric',
                    'mode': 'driving',
                    'avoid': 'tolls',
                    'region': 'au'
                }
                
                response = requests.get(self.distance_matrix_url, params=params, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                
                if data['status'] == 'OK' and data['rows']:
                    elements = data['rows'][0]['elements']
                    
                    for j, element in enumerate(elements):
                        destination = batch[j]
                        
                        if element['status'] == 'OK':
                            distance = element['distance']
                            duration = element['duration']
                            distance_km = round(distance['value'] / 1000, 1)
                            
                            results[destination] = {
                                'distance_km': distance_km,
                                'distance_text': distance['text'],
                                'duration_minutes': round(duration['value'] / 60),
                                'duration_text': duration['text'],
                                'travel_fee': self.calculate_travel_fee(distance_km),
                                'destination_formatted': data['destination_addresses'][j]
                            }
                        else:
                            results[destination] = {
                                'error': f"Could not calculate distance: {element['status']}"
                            }
                            
            except Exception as e:
                logger.error(f"Error in batch distance calculation: {str(e)}")
                for destination in batch:
                    if destination not in results:
                        results[destination] = {'error': str(e)}
        
        return results
    
    def update_couple_travel_info(self, couple_id: int) -> Dict:
        """Update travel information for a specific couple."""
        try:
            from models import Couple, db
            
            couple = Couple.query.get(couple_id)
            if not couple or not couple.ceremony_location:
                return {'success': False, 'error': 'Couple or ceremony location not found'}
            
            # Calculate travel info
            travel_info = self.calculate_distance_and_time(couple.ceremony_location)
            
            if travel_info:
                # Update the couple's travel fee
                couple.travel_fee = travel_info['travel_fee']
                
                # Store additional travel info in notes if needed
                travel_notes = (
                    f"Travel Distance: {travel_info['distance_text']} "
                    f"({travel_info['distance_km']}km)\n"
                    f"Travel Time: {travel_info['duration_text']}\n"
                    f"Travel Fee: ${travel_info['travel_fee']:.2f}"
                )
                
                if couple.notes:
                    # Remove existing travel info and add new
                    notes_lines = couple.notes.split('\n')
                    notes_lines = [line for line in notes_lines if not line.startswith('Travel')]
                    couple.notes = '\n'.join(notes_lines + [travel_notes])
                else:
                    couple.notes = travel_notes
                
                db.session.commit()
                
                return {
                    'success': True,
                    'travel_info': travel_info,
                    'updated_fields': ['travel_fee', 'notes']
                }
            else:
                return {'success': False, 'error': 'Could not calculate travel information'}
                
        except Exception as e:
            logger.error(f"Error updating travel info for couple {couple_id}: {str(e)}")
            return {'success': False, 'error': str(e)} 