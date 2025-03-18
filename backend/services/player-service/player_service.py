from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Load Firebase credentials
cred = credentials.Certificate("../../serviceAccountKey.json")  # Ensure correct path 
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

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True, port=5001)
