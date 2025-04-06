# schedule_service.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import logging

app = Flask(__name__)
app.url_map.strict_slashes = False  # Allow trailing slash variations
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
logging.basicConfig(level=logging.INFO)

# Initialize Firebase – update the path accordingly
cred = credentials.Certificate("/app/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

schedule_ref = db.collection("schedules")

# --- Create Schedule Document ---
@app.route("/schedule", methods=["POST", "OPTIONS"])
def create_schedule():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    tournament_id = data.get("tournamentId")
    round_number = data.get("roundNumber")
    tournament_name = data.get("tournamentName")
    if not tournament_id or round_number is None or not tournament_name:
        return jsonify({"error": "tournamentId, roundNumber, and tournamentName are required"}), 400

    # Check if schedule already exists.
    for doc in schedule_ref.where("roundNumber", "==", round_number).stream():
        d = doc.to_dict()
        if d.get("tournament") and tournament_id in d["tournament"]:
            return jsonify({"error": "Schedule for this tournament and round already exists"}), 400

    schedule_doc = {
        # "tournament": { tournament_id: tournament_name },

        "tournament": {
        "tournamentId": tournament_id,
        "name": tournament_name
        },


        "roundNumber": round_number,
        "dateTime": data.get("dateTime", ""),
        "teamAvailableDays": {}
    }
    schedule_ref.add(schedule_doc)
    logging.info(f"Created schedule for tournament {tournament_id}, round {round_number}")
    return jsonify({"message": "Schedule created successfully"}), 201

# --- Get Schedules for a Tournament ---
# @app.route("/schedule/<tournament_id>", methods=["GET", "OPTIONS"])
# def get_schedules(tournament_id):
#     if request.method == "OPTIONS":
#         return jsonify({}), 200

#     schedules = []
#     for doc in schedule_ref.stream():
#         d = doc.to_dict()
#         if d.get("tournament") and tournament_id in d["tournament"]:
#             schedules.append({"id": doc.id, **d})
#     if not schedules:
#         return jsonify({"error": "No schedules found for this tournament"}), 404
#     return jsonify(schedules), 200

@app.route("/schedule/by-tournament/<tournament_id>", methods=["GET"])
def get_schedules_by_tournament_id(tournament_id):
    try:
        schedules_ref = db.collection("schedules").stream()
        matching = []

        for doc in schedules_ref:
            schedule = doc.to_dict()
            schedule["id"] = doc.id  # include document ID
            logging.debug(f"Checking schedule: {schedule}")

            # Updated structure with tournamentId inside a field
            tournament_info = schedule.get("tournament", {})
            found_id = tournament_info.get("tournamentId")

            logging.debug(f"Comparing against: {found_id}")
            if found_id == tournament_id:
                matching.append(schedule)

        if not matching:
            return jsonify({"error": "No schedules found for this tournament"}), 404

        return jsonify(matching), 200

    except Exception as e:
        logging.error(f"Error fetching schedule: {e}")
        return jsonify({"error": "Internal error"}), 500

# --- Submit Availability ---
@app.route("/schedule/<tournament_id>/availability", methods=["POST", "OPTIONS"])
def submit_availability(tournament_id):
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    team_id = data.get("teamId")
    available_days = data.get("availableDays", [])
    round_number = data.get("roundNumber")
    logging.info(f"submit_availability payload: {data}")
    if not team_id or not available_days or round_number is None:
        return jsonify({"error": "Missing teamId, availableDays, or roundNumber"}), 400

    selected_doc = None
    for doc in schedule_ref.where("roundNumber", "==", round_number).stream():
        d = doc.to_dict()
        if d.get("tournament") and tournament_id in d["tournament"]:
            selected_doc = doc
            break

    if not selected_doc:
        return jsonify({"error": "Schedule for that round not found"}), 404

    schedule_data = selected_doc.to_dict()
    team_availability = schedule_data.get("teamAvailableDays", {})
    logging.info(f"Before update, teamAvailableDays: {team_availability}")

    for day in available_days:
        if day not in team_availability:
            team_availability[day] = []
        if team_id not in team_availability[day]:
            team_availability[day].append(team_id)

    schedule_ref.document(selected_doc.id).update({"teamAvailableDays": team_availability})
    logging.info(f"After update, teamAvailableDays: {team_availability}")
    return jsonify({"message": "Availability submitted"}), 200


if __name__ == "__main__":
    print("HELLO FROM schedule_service.py - LOADING ROUTES...")
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            print(rule.endpoint, "->", rule)
    app.run(host="0.0.0.0", port=5005, debug=True)
