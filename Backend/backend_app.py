# import json
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import os
# import subprocess

# app = Flask(__name__)
# CORS(app)

# @app.route('/create_profile', methods=['POST'])
# def create_profile():
#     data = request.get_json()
#     if not data:
#         return jsonify({"success": False, "message": "Invalid JSON"}), 400

#     save_path = os.path.join(os.path.dirname(__file__), '../frontend/profiles.json')

#     try:
#         # Read existing data
#         if os.path.exists(save_path):
#             with open(save_path, 'r') as f:
#                 profiles = json.load(f)
#         else:
#             profiles = []

#         # Append new profile
#         profiles.append(data)

#         # Save back
#         with open(save_path, 'w') as f:
#             json.dump(profiles, f, indent=2)

#         return jsonify({"success": True, "message": "Profile saved."})
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500
    

# @app.route('/submit_collab_query', methods=['POST'])
# def submit_collab_query():
#     data = request.get_json()
#     if not data or 'query' not in data:
#         return jsonify({"success": False, "message": "Missing query in request."}), 400

#     query = data['query']
#     print("Received collaborator query:", query)

#     try:
#         # Write query to temporary file
#         with open("collab_query.json", "w") as f:
#             json.dump({"query": query}, f)

#         # Launch agent
#         subprocess.Popen(["python", "user_send_request.py"])
#         return jsonify({"success": True, "message": "Agent launched with query."})
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500
    

# @app.route('/get_recommendations', methods=['GET'])
# def get_recommendations():
#     save_path = os.path.join(os.path.dirname(__file__), '../frontend/match_results.json')
    
#     try:
#         with open(save_path, 'r') as f:
#             data = json.load(f)
#         return jsonify({"success": True, "matches": data})
#     except FileNotFoundError:
#         return jsonify({"success": False, "message": "No match results yet."}), 404
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500


# @app.route('/select_match', methods=['POST'])
# def select_match():
#     try:
#         data = request.get_json()
#         index = int(data.get("selection", -1))

#         match_path = os.path.join(os.path.dirname(__file__), '../frontend/match_results.json')
#         with open(match_path, 'r') as f:
#             matches = json.load(f)

#         if index < 0 or index >= len(matches):
#             return jsonify({"success": False, "message": "Invalid match index"}), 400

#         selected_agent = matches[index]
#         match_name = selected_agent["name"]
#         match_address = selected_agent.get("address")

#         if not match_address:
#             return jsonify({"success": False, "message": "Missing address"}), 500

#         # Send MatchResult to user agent
#         from uagents import Context
#         from models import MatchResult
#         import asyncio

#         async def send_to_user():
#             ctx = Context()  # create a fresh context
#             await ctx.send(
#                 "agent1qwusk4z83wtga2wl9l4r8kls5j2hmvz8uyzfvz6xkuldz383mfvrwenc98k",  # user_requestor address
#                 MatchResult(name=match_name, address=match_address)
#             )

#         asyncio.run(send_to_user())

#         return jsonify({"success": True, "match": selected_agent})
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500
    

# if __name__ == "__main__":
#     app.run(debug=True, host='0.0.0.0', port=5001)
