# Huffman Coding Application

A web application for encoding and decoding text using Huffman coding algorithm, with user authentication and database storage.

## Features

- User authentication (login/register)
- Text encoding and decoding
- File encoding and decoding
- Dark/Light theme support
- Database storage of encodings
- User-specific encoding history

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database:
The database will be automatically created when you run the application for the first time.

3. Run the Flask backend:
```bash
python app.py
```

4. Open `index.html` in your web browser or serve it using a local web server.

## Database Structure

The application uses SQLite with two main tables:

1. `User` table:
   - id (Primary Key)
   - email (Unique)
   - password
   - created_at

2. `Encoding` table:
   - id (Primary Key)
   - original_text
   - encoded_text
   - code_map
   - created_at
   - user_id (Foreign Key to User)

## Security Notes

- In a production environment, you should:
  - Hash passwords before storing them
  - Use HTTPS
  - Implement proper session management
  - Add input validation and sanitization
  - Use environment variables for sensitive data

## API Endpoints

- POST `/api/register` - Register a new user
- POST `/api/login` - User login
- POST `/api/encode` - Encode text
- GET `/api/encodings` - Get user's encoding history 