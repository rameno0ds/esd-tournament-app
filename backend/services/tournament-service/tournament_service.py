from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("../../serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

tournament_ref = db.collection("tournaments")

# Create a new tournament
@app.route("/tournament", methods=["POST"])
def create_tournament():
    data = request.json
    if not data.get("name") or not data.get("tournament_id"):
        return jsonify({"error": "Missing required fields"}), 400
    
    tournament_ref.document(data["tournament_id"]).set({
        "tournamentName": data["tournamentName"],
        "game": data.get("game", ""),
        "moderatorId": data.get("moderatorId", ""),
        "status": "upcoming",
        "prizePool": data.get("prizePool", 0),
        "startDate": data.get("startDate"),
        "endDate": data.get("endDate"),
        "players": data.get("players", []),
        "teamStats": data.get("teamStats", [])  # Adding teamStats field
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

# Add a player to a tournament
@app.route("/tournament/<tournament_id>/add_player", methods=["POST"])
def add_player(tournament_id):
    data = request.json
    player_id = data.get("player_id")
    if not player_id:
        return jsonify({"error": "Player ID is required"}), 400
    
    tournament = tournament_ref.document(tournament_id).get()
    if not tournament.exists:
        return jsonify({"error": "Tournament not found"}), 404
    
    tournament_data = tournament.to_dict()
    players = tournament_data.get("players", [])
    
    # Enforce the limit of 16 teams
    if len(players) >= 16:
        return jsonify({"error": "Tournament is already full with 16 teams"}), 400
    
    players.append(player_id)
    tournament_ref.document(tournament_id).update({"players": players})
    
    return jsonify({"message": "Player added successfully"}), 200

# Update team stats in a tournament
@app.route("/tournament/<tournament_id>/update_team_stats", methods=["PUT"])
def update_team_stats(tournament_id):
    data = request.json
    team_stats = data.get("teamStats")
    if not team_stats:
        return jsonify({"error": "Team stats data is required"}), 400
    
    tournament = tournament_ref.document(tournament_id).get()
    if not tournament.exists():
        return jsonify({"error": "Tournament not found"}), 404
    
    tournament_ref.document(tournament_id).update({"teamStats": team_stats})
    return jsonify({"message": "Team stats updated successfully"}), 200

if __name__ == "__main__":
    app.run(port=5002, debug=True)
