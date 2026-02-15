from flask import Blueprint, request, jsonify, session, redirect
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
import json
from datetime import datetime
from flask_cors import cross_origin

auth_bp = Blueprint('auth', __name__)

# Gmail OAuth2 configuration
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "client_secrets.json")
SCOPES = ['https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
          'openid']

# Database file path
DB_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"users": []}

def save_users(users):
    with open(DB_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@auth_bp.route('/api/gmail-callback')
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500"], supports_credentials=True)
def gmail_callback():
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code:
            return jsonify({"error": "No authorization code provided"}), 400
        if not state:
            return jsonify({"error": "No state parameter provided"}), 400

        # Create flow instance
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri="http://127.0.0.1:5000/api/gmail-callback"
        )

        # Exchange authorization code for credentials
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Get user info from Gmail API
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()

        # Load existing users
        users = load_users()
        
        # Check if user exists
        user = next((u for u in users["users"] if u["email"] == user_info["email"]), None)
        
        if not user:
            # Create new user
            user = {
                "id": len(users["users"]) + 1,
                "email": user_info["email"],
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture", ""),
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat()
            }
            users["users"].append(user)
            save_users(users)
        else:
            # Update last login
            user["last_login"] = datetime.now().isoformat()
            save_users(users)

        # Store user info in session
        session['user_id'] = user["id"]
        session['user_email'] = user["email"]
        print(f"DEBUG: Session after gmail_callback: user_id={session.get('user_id')}, user_email={session.get('user_email')}")

        # Return HTML that sends the code back to the opener window
        return f"""
        <html>
            <body>
                <script>
                    window.opener.postMessage({{ 
                        code: '{code}',
                        state: '{state}'
                    }}, 'http://127.0.0.1:5000');
                    window.close();
                </script>
            </body>
        </html>
        """

    except Exception as e:
        print("Error in gmail_callback:", str(e))
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/api/gmail-login', methods=['POST'])
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500"], supports_credentials=True)
def gmail_login():
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({"error": "No authorization code provided"}), 400

        # Create flow instance
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri="http://127.0.0.1:5000/api/gmail-callback"
        )

        # Exchange authorization code for credentials
        flow.fetch_token(code=data['code'])
        credentials = flow.credentials

        # Get user info from Gmail API
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()

        # Load existing users
        users = load_users()
        
        # Check if user exists
        user = next((u for u in users["users"] if u["email"] == user_info["email"]), None)
        
        if not user:
            # Create new user
            user = {
                "id": len(users["users"]) + 1,
                "email": user_info["email"],
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture", ""),
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat()
            }
            users["users"].append(user)
            save_users(users)
        else:
            # Update last login
            user["last_login"] = datetime.now().isoformat()
            save_users(users)

        # Store user info in session
        session['user_id'] = user["id"]
        session['user_email'] = user["email"]
        print(f"DEBUG: Session after gmail_login: user_id={session.get('user_id')}, user_email={session.get('user_email')}")

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "picture": user["picture"]
            }
        })

    except Exception as e:
        print("Error in gmail_login:", str(e))
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/api/gmail-logout', methods=['POST'])
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500"], supports_credentials=True)
def gmail_logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})

@auth_bp.route('/api/check-auth', methods=['GET'])
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500"], supports_credentials=True)
def check_auth():
    print(f"DEBUG: check_auth called. Session has user_id: {'user_id' in session}")
    if 'user_id' in session:
        users = load_users()
        user = next((u for u in users["users"] if u["id"] == session['user_id']), None)
        if user:
            return jsonify({
                "is_authenticated": True,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "picture": user["picture"]
                }
            })
    return jsonify({"is_authenticated": False}) 