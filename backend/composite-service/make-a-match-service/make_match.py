from flask import Flask, request, jsonify
import requests
from collections import defaultdict
import random

app = Flask(__name__)

SCHEDULE_SERVICE_URL = "http://localhost:5005"
TOURNAMENT_SERVICE_URL = "http://localhost:5002"
MATCH_SERVICE_URL = "http://localhost:5003"

# Helper: Sort teams by wins then ELO
def sort_teams(teams):
    return sorted(teams, key=lambda t: (-t['teamStats']['wins'], -t['teamStats']['elo']))

# Helper: Find best matching pairs given availability
def create_match_pairs(teams, availability):
    pairs = []
    unpaired_teams = {t['teamId']: t for t in teams}
    team_days = defaultdict(list)

    # Build reverse map of team to available days
    for day, day_teams in availability.items():
        for team_id in day_teams:
            team_days[team_id].append(day)

    # Try pairing teams with common days, sorted by win/ELO
    sorted_teams = sort_teams(teams)

    used = set()
    for i in range(len(sorted_teams)):
        t1 = sorted_teams[i]['teamId']
        if t1 in used:
            continue
        for j in range(i + 1, len(sorted_teams)):
            t2 = sorted_teams[j]['teamId']
            if t2 in used:
                continue
            common_days = set(team_days[t1]) & set(team_days[t2])
            if common_days:
                selected_day = sorted(common_days)[0]
                pairs.append({"teamA": t1, "teamB": t2, "day": selected_day})
                used.update([t1, t2])
                break

    # Fallback: Pair remaining unpaired teams randomly on any available day
    remaining = [t for t in teams if t['teamId'] not in used]
    random.shuffle(remaining)

    while len(remaining) >= 2:
        t1 = remaining.pop()
        t2 = None
        for i, candidate in enumerate(remaining):
            common_days = set(team_days[t1['teamId']]) & set(team_days[candidate['teamId']])
            if common_days:
                t2 = candidate
                selected_day = sorted(common_days)[0]
                pairs.append({"teamA": t1['teamId'], "teamB": t2['teamId'], "day": selected_day})
                remaining.pop(i)
                break
        if not t2:
            return None  # Unable to match this team with anyone

    return pairs

@app.route("/make-match", methods=["POST"])
def make_match():
    data = request.json
    tournament_id = data.get("tournamentId")
    round_number = data.get("roundNumber")

    if not tournament_id or round_number is None:
        return jsonify({"error": "Missing tournamentId or roundNumber"}), 400

    # 1. Get availability from schedule service
    schedule_res = requests.get(f"{SCHEDULE_SERVICE_URL}/schedule/{tournament_id}/{round_number}")
    if schedule_res.status_code != 200:
        return jsonify({"error": "Failed to fetch schedule"}), 500
    availability = schedule_res.json().get("teamAvailableDays", {})

    # 2. Get teams and stats from tournament service
    tournament_res = requests.get(f"{TOURNAMENT_SERVICE_URL}/tournament/{tournament_id}")
    if tournament_res.status_code != 200:
        return jsonify({"error": "Failed to fetch tournament"}), 500
    tournament_data = tournament_res.json()
    teams = tournament_data.get("teams", [])

    if len(teams) % 2 != 0:
        return jsonify({"error": "Odd number of teams cannot be paired evenly"}), 400

    # 3. Form matchups
    pairs = create_match_pairs(teams, availability)
    if pairs is None or len(pairs) * 2 != len(teams):
        return jsonify({"error": "Unable to pair all teams. Check availability."}), 400

    # 4. Post matches to match service
    for pair in pairs:
        match_data = {
            "tournamentId": tournament_id,
            "roundNumber": round_number,
            "teamA": pair["teamA"],
            "teamB": pair["teamB"],
            "day": pair["day"],
            "status": "upcoming"
        }
        match_res = requests.post(f"{MATCH_SERVICE_URL}/match", json=match_data)
        if match_res.status_code != 201:
            return jsonify({"error": f"Failed to create match for {pair['teamA']} vs {pair['teamB']}"}), 500

    return jsonify({"message": f"{len(pairs)} matches created successfully"}), 201

if __name__ == "__main__":
    app.run(port=5007, debug=True)