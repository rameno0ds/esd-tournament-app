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

schedule_ref = db.collection("schedules")

tournament_ref = db.collection("tournaments")
match_ref = db.collection("matches")

# Create a new schedule
@app.route("/schedule", methods=["POST"])
def create_schedule():
    data = request.json
    tournament_id = data.get("tournamentId")
    if not tournament_id:
        return jsonify({"error": "Tournament ID is required"}), 400
    
    # Determine the round number by counting existing schedules for the tournament
    existing_schedules = schedule_ref.where("tournamentId", "==", tournament_id).stream()
    round_number = sum(1 for _ in existing_schedules) + 1
    
    schedule_ref.add({
        "tournamentId": tournament_id,
        "dateTime": data.get("dateTime"),
        "roundNumber": round_number,
        "teamAvailableDays": {}
    })
    return jsonify({"message": "Schedule created successfully", "roundNumber": round_number}), 201

# Get schedule details
@app.route("/schedule/<tournament_id>", methods=["GET"])
def get_schedule(tournament_id):
    schedules = schedule_ref.where("tournamentId", "==", tournament_id).stream()
    schedule_list = [{"id": s.id, **s.to_dict()} for s in schedules]
    if schedule_list:
        return jsonify(schedule_list), 200
    return jsonify({"error": "Schedule not found"}), 404

# Set team availability
@app.route("/schedule/<tournament_id>/availability", methods=["POST"])
def set_team_availability(tournament_id):
    data = request.json
    team_id = data.get("teamId")
    available_days = data.get("availableDays", [])
    round_number = data.get("roundNumber")
    
    if not team_id or not available_days or round_number is None:
        return jsonify({"error": "Team ID, available days, and round number are required"}), 400
    
    schedule_query = schedule_ref.where("tournamentId", "==", tournament_id).where("roundNumber", "==", round_number).stream()
    schedule_docs = list(schedule_query)
    
    if not schedule_docs:
        return jsonify({"error": "Schedule for the specified round not found"}), 404
    
    schedule_doc = schedule_docs[0]
    schedule_data = schedule_doc.to_dict()
    team_available_days = schedule_data.get("teamAvailableDays", {})
    
    for day in available_days:
        if day not in team_available_days:
            team_available_days[day] = []
        if team_id not in team_available_days[day]:
            team_available_days[day].append(team_id)
    
    schedule_ref.document(schedule_doc.id).update({"teamAvailableDays": team_available_days})
    return jsonify({"message": "Availability updated successfully"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)