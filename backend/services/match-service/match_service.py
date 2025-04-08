from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Firebase
cred = credentials.Certificate("/app/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

match_ref = db.collection("matches")

tournament_ref = db.collection("tournaments")
team_ref = db.collection("teams")

# Create a new match
@app.route("/match", methods=["POST"])
def create_match():
    data = request.json
    tournament_id = data.get("tournamentId")
    team_a = data.get("teamAId")
    team_b = data.get("teamBId")
    scheduled_time = data.get("scheduledTime")
    status = data.get("status")
    roundNumber = data.get("roundNumber")
    

    if not all([tournament_id, team_a, team_b, scheduled_time, status, roundNumber]):
        return jsonify({"error": "Missing required fields"}), 400

    match_doc = match_ref.add({
        "tournamentId": tournament_id,
        "teamAId": team_a,
        "teamBId": team_b,
        "scheduledTime": scheduled_time,
        "result": "pending",
        "score": {"teamA": 0, "teamB": 0},
        "status": status,
        "roundNumber": roundNumber
    })

    return jsonify({"message": "Match created successfully", "matchId": match_doc[1].id}), 201

# Get match details
@app.route("/match/<match_id>", methods=["GET"])
def get_match(match_id):
    match_doc = match_ref.document(match_id).get()
    if match_doc.exists:
        return jsonify(match_doc.to_dict()), 200
    return jsonify({"error": "Match not found"}), 404

# Update match result
@app.route("/match/<match_id>/result", methods=["PUT"])
def update_match_result(match_id):
    data = request.json
    result = data.get("result")  # "teamA won", "teamB won", "draw"
    score = data.get("score", {})
    
    if result not in ["teamA won", "teamB won", "draw"]:
        return jsonify({"error": "Invalid result"}), 400

    match_doc = match_ref.document(match_id)
    match_data = match_doc.get().to_dict()
    if not match_data:
        return jsonify({"error": "Match not found"}), 404

    match_doc.update({"result": result, "score": score, "status": "completed"})

    # Update team stats
    # update_team_stats(match_data["tournamentId"], match_data["teamAId"], match_data["teamBId"], result)

    return jsonify({"message": "Match result updated successfully"}), 200


@app.route("/match/<match_id>/finalize", methods=["PUT"])
def finalize_match(match_id):
    data = request.json
    result = data.get("result")
    score = data.get("score")

    if not result or not score:
        return jsonify({"error": "Missing result or score"}), 400

    match_doc = match_ref.document(match_id)
    if not match_doc.get().exists:
        return jsonify({"error": "Match not found"}), 404

    match_doc.update({
        "result": result,
        "score": score,
        "status": "completed"
    })

    return jsonify({"message": "Match updated successfully"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
