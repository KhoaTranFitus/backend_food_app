"""
TomTom API service for routing and mapping operations
"""
import requests

# TomTom API Key
TOMTOM_API_KEY = 'yyxXlbgc7wMsUKBZY88fGXiCqM0IHspm'

def get_route_coordinates(start_lat, start_lon, end_lat, end_lon):
    """
    Get route coordinates from TomTom Routing API
    
    Args:
        start_lat (float): Starting latitude
        start_lon (float): Starting longitude
        end_lat (float): Ending latitude
        end_lon (float): Ending longitude
    
    Returns:
        list: List of coordinate dictionaries in format [{"latitude": float, "longitude": float}, ...]
              Returns empty list if API call fails
    
    Example:
        >>> coords = get_route_coordinates(10.7760, 106.7000, 10.7770, 106.7010)
        >>> # [{"latitude": 10.7760, "longitude": 106.7000}, ...]
    """
    try:
        # Build TomTom Routing API URL
        # Format: /calculateRoute/{latitude},{longitude}:{latitude},{longitude}/
        url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json"
        params = {
            'key': TOMTOM_API_KEY,
            'routeType': 'fastest',
            'traffic': 'false'
        }
        
        # Make request to TomTom API
        print(f"🌐 Calling TomTom API: {url}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes
        
        data = response.json()
        
        # Extract route coordinates from response
        route_coordinates = []
        
        # TomTom returns routes array, each route has legs, each leg has points
        if data.get('routes') and len(data['routes']) > 0:
            route = data['routes'][0]
            
            # Process all legs in the route
            for leg in route.get('legs', []):
                for point in leg.get('points', []):
                    route_coordinates.append({
                        'latitude': point['latitude'],
                        'longitude': point['longitude']
                    })
        
        print(f"✅ Retrieved {len(route_coordinates)} route points from TomTom")
        return route_coordinates
        
    except requests.exceptions.RequestException as e:
        print(f"❌ TomTom API Error: {str(e)}")
        return []
    except (KeyError, IndexError, ValueError) as e:
        print(f"❌ Error parsing TomTom response: {str(e)}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error in get_route_coordinates: {str(e)}")
        return []
