from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Load Firebase credentials
cred = credentials.Certificate("/app/serviceAccountKey.json")  # Ensure correct path 
firebase_admin.initialize_app(cred)
db = firestore.client()

# Route: Register a Player (Auto-registration included)
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")

         # Validate input
        if not email or not username or not password:
            return jsonify({"error": "Missing fields"}), 400

        # Create the user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password
        )

        # Add new player data to Firestore
        player_ref = db.collection("players").document(user.uid)
        player_ref.set({
            "playerId": user.uid,
            "username": username,
            "email": email,
            "teams": [],  # Empty array to store teams
            "tournamentParticipation": []  # Empty array for tournament and team associations
        })

        return jsonify({"message": "Player registered successfully!", "playerId": user.uid}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route: Login Player
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data["email"]
        password = data["password"]

        # Authenticate user with Firebase Authentication
        user = auth.get_user_by_email(email)

        # Check if player exists in Firestore
        player_ref = db.collection("players").document(user.uid)
        player = player_ref.get()

        if player.exists:
            # Return player data
            return jsonify(player.to_dict()), 200
        else:
            return jsonify({"error": "Player not found in Firestore. Please sign up."}), 404

    except auth.UserNotFoundError:
        return jsonify({"error": "User does not exist. Please sign up."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route: Get Player Profile
@app.route("/player/<playerId>", methods=["GET"])
def get_player(playerId):
    try:
        player_ref = db.collection("players").document(playerId)
        player = player_ref.get()
        if player.exists:
            return jsonify(player.to_dict()), 200
        else:
            return jsonify({"error": "Player not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Decodes the token, returns userId and username
@app.route("/player/profile", methods=["GET"])
def get_player_profile():
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        id_token = auth_header.split(" ")[1]

        # Decode token
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]

        # Look up player in Firestore
        player_ref = db.collection("players").document(uid)
        player_doc = player_ref.get()
        if not player_doc.exists:
            return jsonify({"error": "Player profile not found"}), 404

        player_data = player_doc.to_dict()
        return jsonify({
            "userId": uid,
            "username": player_data.get("username", "Unnamed Player")
        }), 200


    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Checks if this player is already in a team for that tournament
@app.route("/player/my_teams", methods=["GET"])
def get_user_teams_for_tournament():
    try:
        tournament_id = request.args.get("tournamentId")
        if not tournament_id:
            return jsonify({"error": "Missing tournamentId parameter"}), 400

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        id_token = auth_header.split(" ")[1]

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]

        # Look in Firestore for any teams containing this player
        teams_ref = db.collection("teams")
        snapshot = teams_ref.where(f"players.{uid}", "!=", None).stream()

        for doc in snapshot:
            team_data = doc.to_dict()
            if tournament_id in team_data.get("tournaments", {}):
                return jsonify({
                    "inTeam": True,
                    "teamId": team_data["team_id"],
                    "teamName": team_data.get("name", "")
                }), 200

        return jsonify({ "inTeam": False }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
# Run Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)
