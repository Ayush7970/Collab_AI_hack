from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import subprocess
from datetime import datetime
from models import Proposal  # Assuming Proposal is defined in models.py

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests from React

# Serve top 3 match recommendations
@app.route("/get_recommendations", methods=["GET"])
def get_recommendations():
    try:
        with open("top_matches.json", "r") as f:
            matches = json.load(f)
        return jsonify({"success": True, "matches": matches})
    except FileNotFoundError:
        return jsonify({"success": False, "error": "No matches found"}), 404

# Handle profile creation
@app.route("/create_profile", methods=["POST"])
def create_profile():
    try:
        data = request.get_json()
        print("📥 Received profile data:", data)

        if not data:
            return jsonify({"success": False, "message": "Invalid JSON"}), 400

        save_path = os.path.join(os.path.dirname(__file__), "profiles.json")
        print("📁 Saving to:", save_path)

        if os.path.exists(save_path):
            with open(save_path, 'r') as f:
                try:
                    profiles = json.load(f)
                except json.JSONDecodeError:
                    print("⚠️ profiles.json is corrupt. Reinitializing.")
                    profiles = []
        else:
            profiles = []

        profiles.append(data)
        with open(save_path, 'w') as f:
            json.dump(profiles, f, indent=2)

        return jsonify({"success": True, "message": "Profile saved."})

    except Exception as e:
        print("❌ Internal server error:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500


# Handle collaboration query and trigger user_send_agent
@app.route("/submit_collab_query", methods=["POST"])
def submit_collab_query():
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"success": False, "message": "No query provided."}), 400

    try:
        # Save the query to file
        with open("collab_query.json", "w") as f:
            json.dump({"query": query}, f)

        # Launch user_send_agent.py in the background with full path
        agent_path = os.path.abspath("user_send_request.py")
        subprocess.Popen(["python3", agent_path])

        return jsonify({"success": True, "message": "Query saved and agent launched."})

    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to trigger agent: {str(e)}"}), 500

# Log selected match and serve chat log
@app.route("/select_match", methods=["POST"])
def select_match():
    data = request.get_json()
    if not data or "name" not in data or "address" not in data:
        return jsonify({"success": False, "message": "Missing required fields."}), 400

    # Simply acknowledge the match without logging to file
    return jsonify({"success": True, "message": "Match acknowledged."})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)


# NEW: Check if negotiation is complete (via .txt flag)
@app.route("/negotiation_complete", methods=["GET"])
def check_negotiation():
    try:
        if os.path.exists("negotiation_complete.txt"):
            with open("negotiation_complete.txt", "r") as f:
                if f.read().strip().lower() == "true":
                    return jsonify({"done": True})
    except:
        pass
    return jsonify({"done": False})