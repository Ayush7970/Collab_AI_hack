import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/create_profile', methods=['POST'])
def create_profile():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON"}), 400

    save_path = os.path.join(os.path.dirname(__file__), '../frontend/profiles.json')

    try:
        # Read existing data
        if os.path.exists(save_path):
            with open(save_path, 'r') as f:
                profiles = json.load(f)
        else:
            profiles = []

        # Append new profile
        profiles.append(data)

        # Save back
        with open(save_path, 'w') as f:
            json.dump(profiles, f, indent=2)

        return jsonify({"success": True, "message": "Profile saved."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    

@app.route('/submit_collab_query', methods=['POST'])
def submit_collab_query():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"success": False, "message": "Missing query in request."}), 400

    query = data['query']
    print("Received collaborator query:", query)

    try:
        # Write query to temporary file
        with open("collab_query.json", "w") as f:
            json.dump({"query": query}, f)

        # Launch agent
        subprocess.Popen(["python", "user_send_request.py"])
        return jsonify({"success": True, "message": "Agent launched with query."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
