# make_a_match.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
logging.basicConfig(level=logging.INFO)

# Update these base URLs if needed.
SCHEDULE_SERVICE_URL = "http://localhost:5005"  # schedule_service now on 5005
TOURNAMENT_SERVICE_URL = "http://localhost:5002"  # if applicable
MATCH_SERVICE_URL = "http://localhost:5002"

def pair_teams_by_wl(teams, team_wl_map):
    sorted_teams = sorted(
        teams,
        key=lambda t: (team_wl_map.get(t, {}).get("wins", 0) - team_wl_map.get(t, {}).get("losses", 0)),
        reverse=True
    )
    pairs = []
    i = 0
    while i < len(sorted_teams) - 1:
        pairs.append((sorted_teams[i], sorted_teams[i+1]))
        i += 2
    return pairs

@app.route("/make_matches", methods=["POST", "OPTIONS"])
def make_matches():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    tournament_id = data.get("tournamentId")
    round_number = data.get("roundNumber")
    if not tournament_id or round_number is None:
        return jsonify({"error": "tournamentId and roundNumber are required"}), 400

    # Retrieve schedule document from the schedule service.
    schedule_url = f"{SCHEDULE_SERVICE_URL}/schedule/{tournament_id}"
    try:
        schedule_resp = requests.get(schedule_url)
        if schedule_resp.status_code != 200:
            return jsonify({"error": f"Failed to retrieve schedule: {schedule_resp.text}"}), schedule_resp.status_code
        all_schedules = schedule_resp.json()
    except Exception as e:
        logging.error(f"Error calling schedule service: {e}")
        return jsonify({"error": "Schedule service error"}), 500

    # Filter for the schedule doc matching the specified round and tournament.
    schedule_doc = None
    for s in all_schedules:
        if s.get("roundNumber") == round_number and s.get("tournament") and tournament_id in s["tournament"]:
            schedule_doc = s
            break
    if not schedule_doc:
        return jsonify({"error": "No schedule found for that round"}), 404

    team_available_days = schedule_doc.get("teamAvailableDays", {})

    # Optionally, retrieve team win/loss data from the Tournament service.
    try:
        tournament_resp = requests.get(f"{TOURNAMENT_SERVICE_URL}/tournament/{tournament_id}")
        if tournament_resp.status_code != 200:
            logging.warning("Tournament service error; proceeding without W-L data.")
            team_wl_map = {}
        else:
            tournament_data = tournament_resp.json()
            team_wl_map = {}
            for t in tournament_data.get("teams", []):
                tid = t.get("teamId")
                stats = t.get("teamStats", {})
                team_wl_map[tid] = {"wins": stats.get("wins", 0), "losses": stats.get("losses", 0)}
    except Exception as e:
        logging.error(f"Error calling tournament service: {e}")
        team_wl_map = {}

    created_matches = []
    # For each day, pair teams (limit to 4 teams per day) and create matches via the Match service.
    for day, teams in team_available_days.items():
        if len(teams) < 2:
            logging.info(f"Not enough teams available on {day} to create a match.")
            continue

        teams_for_day = teams[:4]
        pairs = pair_teams_by_wl(teams_for_day, team_wl_map)
        for team_a, team_b in pairs:
            match_payload = {
                "tournamentId": tournament_id,
                "teamAId": team_a,
                "teamBId": team_b,
                "scheduledTime": day
            }
            try:
                match_resp = requests.post(f"{MATCH_SERVICE_URL}/match", json=match_payload)
                if match_resp.status_code == 201:
                    match_data = match_resp.json()
                    created_matches.append(match_data)
                    logging.info(f"Match created: {team_a} vs {team_b} on {day}")
                else:
                    logging.error(f"Match service error: {match_resp.text}")
            except Exception as e:
                logging.error(f"Error calling match service: {e}")

    if not created_matches:
        return jsonify({"message": "No matches created. Check team availability."}), 200

    return jsonify({"message": f"Matches for round {round_number} created!", "matches": created_matches}), 201

if __name__ == "__main__":
    app.run(port=5007, debug=True)
