from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app) # Enable CORS for your entire app

# Configuration
AGENT_URL = "http://127.0.0.1:8003"
USERS_FILE = "user.json"

def load_users():
    """Load user profiles from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"users": [], "metadata": {"total": 0, "last_updated": None}}
    return {"users": [], "metadata": {"total": 0, "last_updated": None}}

@app.route('/create_profile', methods=['POST'])
def create_profile():
    """Create a new user profile"""
    try:
        data = request.get_json()
        
        # Prepare request for agent - forward the entire payload
        response = requests.post(f"{AGENT_URL}/create_profile", json=data)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'success': False,
                'message': f'Agent error: {response.status_code} - {response.text}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating profile: {str(e)}'
        }), 500

@app.route('/match_users', methods=['POST'])
def match_users():
    """Use Claude to find the best matches for a query"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'success': False, 'message': 'Match query is required'}), 400
        
        # Prepare request for agent
        match_data = {
            'query': query,
            'limit': data.get('limit', 3)
        }
        
        response = requests.post(f"{AGENT_URL}/match_users", json=match_data)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'success': False, 'message': f'Agent error: {response.status_code}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error matching users: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting User Profile Frontend...")
    print(f"Agent URL: {AGENT_URL}")
    print("Make sure the user profile agent is running on port 8003")
    # Change the port number in the next line
    app.run(debug=True, host='0.0.0.0', port=5001) 