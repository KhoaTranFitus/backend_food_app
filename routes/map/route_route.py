"""
Route endpoints for map routing operations
"""
from flask import jsonify, request
from routes.map import map_bp
from services.tomtom_service import get_route_coordinates
import logging

logger = logging.getLogger(__name__)

@map_bp.route("/get-route", methods=["POST"])
def get_route():
    """
    Calculate route between two coordinates
    
    Request Body:
        {
            "start_lat": float - Starting latitude,
            "start_lon": float - Starting longitude,
            "end_lat": float - Ending latitude,
            "end_lon": float - Ending longitude
        }
    
    Response:
        {
            "success": bool,
            "message": str,
            "coordinates": [{"latitude": float, "longitude": float}, ...],
            "total_points": int
        }
    """
    try:
        data = request.get_json() or {}
        
        # 🔍 DEBUG LOG: Log incoming request data
        logger.info(f"📥 /get-route request received")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Raw data: {data}")
        logger.info(f"Data keys: {list(data.keys()) if data else 'empty'}")
        
        # Validate required parameters
        required_fields = ['start_lat', 'start_lon', 'end_lat', 'end_lon']
        for field in required_fields:
            if field not in data:
                logger.error(f"❌ Missing required field: {field}")
                logger.error(f"   Available fields: {list(data.keys())}")
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}",
                    "coordinates": [],
                    "total_points": 0
                }), 400
        
        start_lat = data.get('start_lat')
        start_lon = data.get('start_lon')
        end_lat = data.get('end_lat')
        end_lon = data.get('end_lon')
        
        logger.info(f"✅ All required fields present")
        logger.info(f"   start_lat={start_lat}, start_lon={start_lon}")
        logger.info(f"   end_lat={end_lat}, end_lon={end_lon}")
        
        # Validate coordinate values
        try:
            start_lat = float(start_lat)
            start_lon = float(start_lon)
            end_lat = float(end_lat)
            end_lon = float(end_lon)
            logger.info(f"✅ Coordinates converted to float successfully")
        except (ValueError, TypeError) as e:
            logger.error(f"❌ Invalid coordinate format: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Invalid coordinate format. Must be floats.",
                "coordinates": [],
                "total_points": 0
            }), 400
        
        # Check if start and end coordinates are the same
        if abs(start_lat - end_lat) < 0.0001 and abs(start_lon - end_lon) < 0.0001:
            logger.error(f"❌ Start and end coordinates are too close (difference < 0.0001)")
            return jsonify({
                "success": False,
                "message": "Start and end coordinates are the same",
                "coordinates": [],
                "total_points": 0
            }), 400
        
        logger.info(f"✅ Coordinates are valid (distance sufficient)")
        
        # Call TomTom service to get route
        logger.info(f"🌐 Calling TomTom service...")
        coordinates = get_route_coordinates(start_lat, start_lon, end_lat, end_lon)
        
        if not coordinates:
            logger.error(f"❌ TomTom service returned empty coordinates")
            return jsonify({
                "success": False,
                "message": "Could not calculate route",
                "coordinates": [],
                "total_points": 0
            }), 400
        
        logger.info(f"✅ Route calculated successfully with {len(coordinates)} points")
        return jsonify({
            "success": True,
            "message": f"Route calculated with {len(coordinates)} points",
            "coordinates": coordinates,
            "total_points": len(coordinates)
        }), 200
        
    except Exception as e:
        logger.exception(f"❌ Unexpected error in /get-route: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error calculating route: {str(e)}",
            "coordinates": [],
            "total_points": 0
        }), 500
