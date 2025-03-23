from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Firebase
cred = credentials.Certificate("../../serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

tournament_ref = db.collection("tournaments")
match_ref = db.collection("matches")

# Create a new tournament
@app.route("/tournament", methods=["POST"])
def create_tournament():
    data = request.json
    if not data.get("name") or not data.get("tournament_id"):
        return jsonify({"error": "Missing required fields"}), 400
    
    tournament_ref.document(data["tournament_id"]).set({
        "name": data["name"],
        "game": data.get("game", ""),
        "moderatorId": data.get("moderatorId", ""),
        "status": "upcoming",
        "prizePool": data.get("prizePool", 0),
        "startDate": data.get("startDate"),
        "endDate": data.get("endDate"),
        # "players": data.get("players", []),
        # "teamStats": data.get("teamStats", [])  # Adding teamStats field
        "teams": [],  # Changed from players
    })
    return jsonify({"message": "Tournament created successfully"}), 201

# Get tournament details
@app.route("/tournament/<tournament_id>", methods=["GET"])
def get_tournament(tournament_id):
    tournament = tournament_ref.document(tournament_id).get()
    if tournament.exists:
        return jsonify(tournament.to_dict()), 200
    return jsonify({"error": "Tournament not found"}), 404

# Update tournament status
@app.route("/tournament/<tournament_id>", methods=["PUT"])
def update_tournament(tournament_id):
    data = request.json
    tournament_ref.document(tournament_id).update({"status": data.get("status", "upcoming")})
    return jsonify({"message": "Tournament updated successfully"}), 200

# # Add a player to a tournament
# @app.route("/tournament/<tournament_id>/add_player", methods=["POST"])
# def add_player(tournament_id):
#     data = request.json
#     player_id = data.get("player_id")
#     if not player_id:
#         return jsonify({"error": "Player ID is required"}), 400
    
#     tournament = tournament_ref.document(tournament_id).get()
#     if not tournament.exists:
#         return jsonify({"error": "Tournament not found"}), 404
    
#     tournament_data = tournament.to_dict()
#     players = tournament_data.get("players", [])
    
#     # Enforce the limit of 16 teams
#     if len(players) >= 16:
#         return jsonify({"error": "Tournament is already full with 16 teams"}), 400
    
#     players.append(player_id)
#     tournament_ref.document(tournament_id).update({"players": players})
    
#     return jsonify({"message": "Player added successfully"}), 200

# Add a team to a tournament
@app.route("/tournament/<tournament_id>/add_team", methods=["POST"])
def add_team(tournament_id):
    data = request.json
    team_id = data.get("teamId")
    player_ids = data.get("players", [])
    if not team_id or not player_ids:
        return jsonify({"error": "Team ID and players are required"}), 400
    
    tournament = tournament_ref.document(tournament_id).get()
    if not tournament.exists:
        return jsonify({"error": "Tournament not found"}), 404
    
    tournament_data = tournament.to_dict()
    teams = tournament_data.get("teams", [])
    
    # Enforce max 8 teams
    if len(teams) >= 8:
        return jsonify({"error": "Tournament already has 8 teams"}), 400
    
    # Enforce max 40 players
    total_players = sum(len(team.get("players", [])) for team in teams)
    if total_players + len(player_ids) > 40:
        return jsonify({"error": "Exceeds maximum number of players (40)"}), 400
    
    # Ensure no player is in more than one team
    existing_players = {player for team in teams for player in team.get("players", [])}
    if any(player in existing_players for player in player_ids):
        return jsonify({"error": "A player can only be in one team"}), 400
    
    teams.append({
        "teamId": team_id,
        "players": player_ids,
        "teamStats": {
            "elo": data.get("elo", 1500),
            "wins": 0,
            "losses": 0
        }
    })
    
    tournament_ref.document(tournament_id).update({"teams": teams})
    return jsonify({"message": "Team added successfully"}), 200

# # Update team stats in a tournament
# @app.route("/tournament/<tournament_id>/update_team_stats", methods=["PUT"])
# def update_team_stats(tournament_id):
#     data = request.json
#     team_stats = data.get("teamStats")
#     if not team_stats:
#         return jsonify({"error": "Team stats data is required"}), 400
    
#     tournament = tournament_ref.document(tournament_id).get()
#     if not tournament.exists():
#         return jsonify({"error": "Tournament not found"}), 404
    
#     tournament_ref.document(tournament_id).update({"teamStats": team_stats})
#     return jsonify({"message": "Team stats updated successfully"}), 200

# Update team stats after a match
@app.route("/tournament/<tournament_id>/update_match/<match_id>", methods=["POST"])
def update_match(tournament_id, match_id):
    match = match_ref.document(match_id).get()
    if not match.exists:
        return jsonify({"error": "Match not found"}), 404
    
    match_data = match.to_dict()
    if match_data.get("tournamentId") != tournament_id:
        return jsonify({"error": "Match does not belong to this tournament"}), 400
    
    result = match_data.get("result")
    team_a = match_data.get("teamAId")
    team_b = match_data.get("teamBId")
    
    if not result or not team_a or not team_b:
        return jsonify({"error": "Invalid match data"}), 400
    
    tournament = tournament_ref.document(tournament_id).get()
    if not tournament.exists:
        return jsonify({"error": "Tournament not found"}), 404
    
    tournament_data = tournament.to_dict()
    teams = tournament_data.get("teams", [])
    
    for team in teams:
        if team["teamId"] == team_a and result == "teamA won":
            team["teamStats"]["wins"] += 1
            team["teamStats"]["elo"] += 20
        elif team["teamId"] == team_b and result == "teamB won":
            team["teamStats"]["wins"] += 1
            team["teamStats"]["elo"] += 20
        elif team["teamId"] == team_a and result == "teamB won":
            team["teamStats"]["losses"] += 1
            team["teamStats"]["elo"] -= 20
        elif team["teamId"] == team_b and result == "teamA won":
            team["teamStats"]["losses"] += 1
            team["teamStats"]["elo"] -= 20
    
    tournament_ref.document(tournament_id).update({"teams": teams})
    return jsonify({"message": "Match results updated successfully"}), 200

if __name__ == "__main__":
    app.run(port=5002, debug=True)
