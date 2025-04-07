# =============================
# finalize_match_outcome_service.py
# =============================
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

MATCH_SERVICE_URL = "http://match-service:5004"
TOURNAMENT_SERVICE_URL = "http://tournament-service:5002"

@app.route("/finalize-outcome", methods=["POST"])
def finalize_outcome():
    data = request.json
    match_id = data.get("matchId")
    result = data.get("result")  # "teamA won", "teamB won", "draw"
    score = data.get("score", {})

    if not match_id or not result:
        return jsonify({"error": "Missing matchId or result"}), 400

    # 1. Get existing match data
    match_res = requests.get(f"{MATCH_SERVICE_URL}/match/{match_id}")
    if match_res.status_code != 200:
        return jsonify({"error": "Match not found"}), 404

    match_data = match_res.json()
    tournament_id = match_data.get("tournamentId")
    team_a = match_data.get("teamAId")
    team_b = match_data.get("teamBId")

    if not all([tournament_id, team_a, team_b]):
        return jsonify({"error": "Match data incomplete"}), 400

    # 2. Update match result in match_service
    match_update = {
        "result": result,
        "score": score
    }
    match_update_res = requests.put(f"{MATCH_SERVICE_URL}/match/{match_id}/result", json=match_update)
    if match_update_res.status_code != 200:
        return jsonify({"error": "Failed to update match"}), 500

    # 3. Get tournament data
    tourney_res = requests.get(f"{TOURNAMENT_SERVICE_URL}/tournament/{tournament_id}")
    if tourney_res.status_code != 200:
        return jsonify({"error": "Failed to retrieve tournament"}), 500

    tournament_data = tourney_res.json()
    teams = tournament_data.get("teams", [])

    # 4. Update stats in the correct team objects
    for team in teams:
        if team["teamId"] == team_a or team["teamId"] == team_b:
            if result == "teamA won" and team["teamId"] == team_a:
                team["teamStats"]["wins"] += 1
                team["teamStats"]["elo"] += 10
            elif result == "teamB won" and team["teamId"] == team_b:
                team["teamStats"]["wins"] += 1
                team["teamStats"]["elo"] += 10
            elif result == "draw":
                team["teamStats"]["elo"] += 5
            else:
                team["teamStats"]["losses"] += 1
                team["teamStats"]["elo"] -= 10

    # 5. Push updated teams array back to tournament_service
    patch_payload = {"teams": teams}
    patch_res = requests.put(f"{TOURNAMENT_SERVICE_URL}/tournament/{tournament_id}/update_team_stats", json=patch_payload)
    if patch_res.status_code != 200:
        return jsonify({"error": "Failed to update team stats"}), 500

    return jsonify({"message": "Match finalized and team stats updated"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5009, debug=True)
