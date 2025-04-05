# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import requests


# app = Flask(__name__)
# CORS(app)

# @app.route("/composite/join_team", methods=["POST"])
# def join_team():
#     try:
#         data = request.get_json()
#         team_id = data.get("teamId")
#         tournament_id = data.get("tournamentId")
#         auth_header = request.headers.get("Authorization")

#         if not team_id or not tournament_id or not auth_header:
#             return jsonify({"error": "Missing fields"}), 400

#         # Step 1: Get player info
#         player_res = requests.get("http://localhost:5001/player/profile", headers={
#             "Authorization": auth_header
#         })
#         if player_res.status_code != 200:
#             return jsonify({"error": "Unauthorized"}), 401

#         player_data = player_res.json()
#         player_id = player_data.get("userId")
#         player_name = player_data.get("name")

#         # Step 2: Join the team
#         team_join_res = requests.post(f"http://localhost:5003/team/{team_id}/join", json={
#             "name": player_name
#         }, headers={
#             "Authorization": auth_header
#         })
#         if team_join_res.status_code != 200:
#             return jsonify({ "error": "Failed to join team" }), 400

#         # Step 3: Add player to tournament
#         tournament_res = requests.put(f"http://localhost:5002/tournament/{tournament_id}/add_player", json={
#             "playerId": player_id
#         })
#         if tournament_res.status_code != 200:
#             return jsonify({ "error": "Failed to update tournament" }), 400

#         return jsonify({ "message": "Joined successfully!" }), 200

#     except Exception as e:
#         return jsonify({ "error": str(e) }), 500
