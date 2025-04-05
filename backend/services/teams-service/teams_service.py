from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# Initialize Firebase Admin SDK
cred = credentials.Certificate("/app/serviceAccountKey.json")  # Ensure the correct path
firebase_admin.initialize_app(cred)
db = firestore.client()

# Helper function to get the user ID from the Firebase ID token
def get_user_id_from_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token['uid']
    except Exception as e:
        return None

# New endpoint to fetch team info by team ID
@app.route("/team/<team_id>", methods=["GET"])
def get_team_by_id(team_id):
    try:
        team_doc = db.collection("teams").document(team_id).get()
        if not team_doc.exists:
            return jsonify({"error": "Team not found"}), 404

        team_data = team_doc.to_dict()

        return jsonify({
            "teamId": team_id,
            "name": team_data.get("name"),
            "captain_id": team_data.get("captain_id"),
            "captain_name": team_data.get("captain_name"),
            "players": team_data.get("players", {}),
            "player_ids": list(team_data.get("players", {}).keys()),
            "player_names": list(team_data.get("players", {}).values())
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to get the teams the user is part of
@app.route("/teams", methods=["GET"])
def get_teams_for_player():
    try:
        # Get the Firebase ID token from the Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "Authorization token is missing"}), 400

        # Extract the token from the header (it should be in the format "Bearer <id_token>")
        # Extract the token from the "Bearer <id_token>" format
        if auth_header.startswith("Bearer "):
            id_token = auth_header.split(" ")[1]
        else:
            return jsonify({"error": "Invalid token format. Expected 'Bearer <id_token>'"}), 400

        if not id_token:
            return jsonify({"error": "Missing ID token"}), 400


        # Get the user's UID using the token
        user_id = get_user_id_from_token(id_token)
        
        if not user_id:
            return jsonify({"error": "Invalid token or user not authenticated"}), 400

        # Fetch all teams from Firestore
        teams_ref = db.collection("teams")
        teams_snapshot = teams_ref.stream()

        user_teams = []


        # Loop through teams and check if the player is part of the team
        for team_doc in teams_snapshot:
            team_data = team_doc.to_dict()
            if user_id in team_data.get("players", []):  # Default to an empty list if "players_id" is missing
                players_map = team_data.get("players", {})
                tournaments_map = team_data.get("tournaments", {})
                user_teams.append({
                    'id': team_doc.id,
                    'name': team_data['name'],
                    'captain_id': team_data['captain_id'],
                    'captain_name': team_data['captain_name'],
                    'players': players_map,
                    'player_ids': list(players_map.keys()),         # optional: if you still need the IDs
                    'player_names': list(players_map.values()),      # optional: if you want just names
                    'team_id': team_data['team_id'],
                    # 'wins': team_data.get('wins', 0),
                    # 'losses': team_data.get('losses', 0),
                    'tournament_id': list(tournaments_map.keys()),
                    'tournament_names': list(tournaments_map.values())
                })


        print("Authorization header:", request.headers.get('Authorization'))

        return jsonify({"teams": user_teams}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/team/<team_id>/join", methods=["POST"])
def join_team(team_id):
    try:
        # Get the Firebase ID token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 400
        
        id_token = auth_header.split(" ")[1]
        user_id = get_user_id_from_token(id_token)

        if not user_id:
            return jsonify({"error": "Invalid token or user not authenticated"}), 400

        # Get the user name from request body
        data = request.get_json()
        name = data.get("name", "Unnamed Player")

        # Fetch the team
        team_ref = db.collection("teams").document(team_id)
        team_doc = team_ref.get()

        if not team_doc.exists:
            return jsonify({"error": "Team not found"}), 404

        team_data = team_doc.to_dict()
        players = team_data.get("players", {})

        if user_id in players:
            return jsonify({"message": "User already in this team"}), 200

        if len(players) >= 5:
            return jsonify({"error": "Team is already full"}), 400

        players[user_id] = name
        team_ref.update({"players": players})

        return jsonify({"message": "User successfully added to team"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    

# Run Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5003)
