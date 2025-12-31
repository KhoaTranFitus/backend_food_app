# Food App - Backend (Flask API)

A robust RESTful API backend for the Food App, built with Flask and Firebase. Provides comprehensive services for user authentication, restaurant/food management, AI chatbot integration, and map-based features.

## Features

### Authentication & User Management
- Email/Password registration with email verification
- Google OAuth 2.0 Sign-In integration
- Secure Firebase Authentication
- User profile management (avatar, preferences, location)
- Password change functionality
- User favorites and viewing history

### Restaurant & Food Services
- Restaurant listing and details
- Food/dish catalog with images
- Category-based filtering
- Reviews and ratings management
- Restaurant search by location
- Popular dishes and recommendations

### AI Chatbot
- OpenAI-powered conversational assistant
- Context-aware food recommendations
- Natural language understanding
- Integration with restaurant database

### Map & Location Services
- Restaurant location filtering
- Distance-based search
- Geospatial queries using OSM data
- Custom map marker data

## Tech Stack

### Core Framework
- **Flask** (v3.1.3) - Web framework
- **Python** (3.9+) - Programming language
- **Flask-CORS** - Cross-Origin Resource Sharing

### Authentication & Database
- **Firebase Admin SDK** - Authentication and Firestore database
- **python-dotenv** - Environment variable management

### HTTP & API
- **Requests** (v2.32.5) - HTTP library
- **urllib3** (v2.5.0) - HTTP client
- **CacheControl** (v0.14.3) - HTTP caching

### AI & Machine Learning
- **OpenAI API** - GPT-powered chatbot

### Utilities
- **certifi** (v2025.10.5) - SSL certificates
- **charset-normalizer** - Character encoding detection
- **blinker** - Signal/event system
- **cachetools** - Caching utilities

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Firebase project with Firestore enabled
- OpenAI API key (for chatbot feature)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend_food_app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
   FIREBASE_API_KEY=your-firebase-api-key
   FIREBASE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   ```

5. **Setup Firebase credentials**
   - Download your Firebase Admin SDK service account key (JSON file)
   - Save it as `firebase_auth.json` in the root directory
   - **Important:** Never commit this file to version control!

6. **Run the application**
   ```bash
   python App.py
   ```

   The server will start on `http://localhost:5000`

## Project Structure

```
backend_food_app/
├── core/                    # Core services
│   ├── auth_service.py      # Firebase authentication
│   ├── database.py          # Database connection
│   └── ...
├── routes/                  # API route blueprints
│   ├── user/               # User-related endpoints
│   │   ├── login_route.py
│   │   ├── register_route.py
│   │   └── ...
│   ├── food/               # Food & restaurant endpoints
│   │   ├── food_route.py
│   │   ├── restaurant_route.py
│   │   ├── reviews_route.py
│   │   └── ...
│   ├── chatbot/            # AI chatbot endpoints
│   │   └── chatbot_route.py
│   └── map/                # Map & location endpoints
│       ├── filter_route.py
│       └── ...
├── services/               # Business logic services
├── data/                   # Static data files
├── static/                 # Static assets
├── docs/                   # API documentation
├── scripts/                # Utility scripts
├── App.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── firebase_auth.json      # Firebase credentials (not in git)
├── .env                    # Environment variables (not in git)
├── AUTH_API.md            # Authentication API docs
└── CHATBOT_API.md         # Chatbot API docs
```

## API Endpoints

### Authentication (`/api`)
- `POST /register` - Register new user
- `POST /verify` - Verify email with code
- `POST /login` - Login with email/password
- `POST /google-login` - Login with Google OAuth

### User Management (`/api`)
- `GET /user/<uid>` - Get user profile
- `PUT /user/<uid>` - Update user profile
- `POST /user/avatar` - Upload user avatar
- `PUT /user/change-password` - Change password
- `POST /user/favorites` - Add/remove favorites
- `GET /user/history` - Get view history

### Restaurants & Food (`/api`)
- `GET /restaurants` - List all restaurants
- `GET /restaurants/<id>` - Get restaurant details
- `GET /foods` - List all food items
- `GET /foods/<id>` - Get food details
- `GET /categories` - List food categories
- `POST /reviews` - Submit review
- `GET /reviews/<restaurant_id>` - Get restaurant reviews

### Chatbot (`/api`)
- `POST /chatbot/message` - Send message to AI chatbot
- `GET /chatbot/session/<uid>` - Get chat session

### Map & Location (`/api`)
- `POST /map/filter` - Filter restaurants by location
- `GET /map/nearby` - Get nearby restaurants
- `POST /map/distance` - Calculate distance

For detailed API documentation, see:
- [AUTH_API.md](AUTH_API.md) - Complete authentication API documentation
- [CHATBOT_API.md](CHATBOT_API.md) - Chatbot API documentation

## Running the Application

### Development Mode
```bash
python App.py
```
Server runs on `http://localhost:5000` with debug mode and hot reload enabled.

### Production Mode
For production deployment, use a WSGI server like Gunicorn:

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 App:app
```

### Using Docker (Optional)
```bash
# Build image
docker build -t food-app-backend .

# Run container
docker run -p 5000:5000 --env-file .env food-app-backend
```

## Security

### Environment Variables
- **Never commit** `.env` or `firebase_auth.json` to version control
- Add them to `.gitignore`
- Use environment-specific configurations

### Firebase Security
- Service account key (`firebase_auth.json`) has admin privileges
- Restrict access to this file (chmod 600 on Unix systems)
- Use Firebase Security Rules for Firestore

### API Security
- CORS is enabled for cross-origin requests
- Implement rate limiting for production
- Use HTTPS in production
- Validate and sanitize all user inputs

## Database Schema

### Users Collection (Firestore)
```json
{
  "uid": "string",
  "name": "string",
  "email": "string",
  "avatar_url": "string",
  "favorites": ["restaurant_id", ...],
  "history": [
    {
      "restaurant_id": "number",
      "timestamp": "datetime"
    }
  ],
  "location": {
    "latitude": "number",
    "longitude": "number"
  }
}
```

### Restaurants & Foods
- Restaurant and food data stored in Firestore or local JSON files
- Images stored in Firebase Storage or served from `/static`

## Testing

### Manual Testing with cURL

**Register a new user:**
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Testing with Postman
Import the API endpoints into Postman for interactive testing. See `AUTH_API.md` for request/response examples.

## Troubleshooting

### Common Issues

**Firebase credentials error:**
```
Error: Could not find firebase_auth.json
```
- Ensure `firebase_auth.json` exists in the root directory
- Verify the file has valid Firebase Admin SDK credentials

**Environment variables not loaded:**
```
Error: OPENAI_API_KEY not found
```
- Check that `.env` file exists
- Verify environment variables are properly formatted
- Ensure `python-dotenv` is installed

**Port already in use:**
```
Error: Address already in use
```
- Change port in `App.py`: `app.run(port=5001)`
- Or kill the process using port 5000

**Module import errors:**
```
ModuleNotFoundError: No module named 'flask'
```
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

## Performance Optimization

- **Caching**: Implement Redis for frequently accessed data
- **Database Indexing**: Add indexes to Firestore collections
- **Image Optimization**: Compress images before serving
- **CDN**: Use CDN for static assets in production
- **Connection Pooling**: Configure database connection pooling

## Development Workflow

1. Create a new branch for features
2. Implement changes in appropriate route/service files
3. Test endpoints manually or with automated tests
4. Update API documentation if needed
5. Commit and push changes
6. Create pull request for review

## API Documentation

Comprehensive API documentation is available in:
- `AUTH_API.md` - Authentication endpoints
- `CHATBOT_API.md` - Chatbot endpoints

Include request/response examples, error codes, and usage instructions.

## CORS Configuration

CORS is enabled for all origins in development. For production:

```python
# In App.py
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourfrontend.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## License

This project is part of a private food app system.

## Contributing

1. Follow PEP 8 style guide for Python code
2. Add docstrings to functions and classes
3. Update documentation for API changes
4. Test thoroughly before committing

## Support

For issues or questions:
1. Check existing documentation (AUTH_API.md, CHATBOT_API.md)
2. Review error logs in console
3. Verify Firebase and OpenAI configurations
4. Check environment variables

## Version

**Current Version:** 1.0.0
**API Version:** 1.0
**Status:** Production Ready ✅

---

**Built with Flask & Firebase**
