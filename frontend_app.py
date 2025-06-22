from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
AGENT_URL = "http://127.0.0.1:8003"
USERS_FILE = "user_profiles.json"

def load_users():
    """Load user profiles from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"users": {}, "metadata": {"total": 0, "last_updated": None}}
    return {"users": {}, "metadata": {"total": 0, "last_updated": None}}

@app.route('/')
def index():
    """Main page with user profile creation and matchmaking"""
    return render_template('index.html')

@app.route('/create_profile', methods=['POST'])
def create_profile():
    """Create a new user profile"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'name', 'bio']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Prepare request for agent
        profile_data = {
            'user_id': data['user_id'],
            'name': data['name'],
            'bio': data['bio'],
            'interests': data.get('interests', []),
            'skills': data.get('skills', []),
            'location': data.get('location', 'Unknown'),
            'profession': data.get('profession', 'Unknown')
        }
        
        # Send request to agent
        response = requests.post(f"{AGENT_URL}/create_profile", json=profile_data)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'message': f'Agent error: {response.status_code}'
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
            return jsonify({
                'success': False,
                'message': 'Match query is required'
            }), 400
        
        # Prepare request for agent
        match_data = {
            'query': query,
            'limit': data.get('limit', 3)
        }
        
        # Send request to agent
        response = requests.post(f"{AGENT_URL}/match_users", json=match_data)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'message': f'Agent error: {response.status_code}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error matching users: {str(e)}'
        }), 500

@app.route('/get_profile', methods=['POST'])
def get_profile():
    """Get a specific user profile"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', '').strip()
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User ID is required'
            }), 400
        
        # Prepare request for agent
        profile_data = {
            'user_id': user_id,
            'name': '',  # Required by model but not used for retrieval
            'bio': '',   # Required by model but not used for retrieval
            'interests': [],
            'skills': []
        }
        
        # Send request to agent
        response = requests.post(f"{AGENT_URL}/get_profile", json=profile_data)
        
        if response.status_code == 200:
            result = response.json()
            
            # If successful, get the actual profile data from local storage
            if result.get('success'):
                users_data = load_users()
                if user_id in users_data['users']:
                    profile = users_data['users'][user_id]
                    return jsonify({
                        'success': True,
                        'profile': profile,
                        'message': 'Profile retrieved successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Profile not found in local storage'
                    }), 404
            else:
                return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'message': f'Agent error: {response.status_code}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting profile: {str(e)}'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Check agent health
        response = requests.get(f"{AGENT_URL}/health")
        
        if response.status_code == 200:
            agent_health = response.json()
            return jsonify({
                'frontend': 'healthy',
                'agent': agent_health,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'frontend': 'healthy',
                'agent': 'unreachable',
                'timestamp': datetime.now().isoformat()
            }), 503
            
    except Exception as e:
        return jsonify({
            'frontend': 'healthy',
            'agent': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/api/users')
def list_users():
    """Get list of all users (for debugging)"""
    try:
        users_data = load_users()
        users = list(users_data['users'].values())
        
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users),
            'total': users_data['metadata']['total']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error listing users: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("Starting User Profile Frontend...")
    print(f"Agent URL: {AGENT_URL}")
    print("Make sure the user profile agent is running on port 8003")
    print("Access the frontend at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 