from flask import Flask, request, jsonify
from flask_cors import CORS
import requests


app = Flask(__name__)

CORS(app, resources={r"/composite/*": {"origins": "*"}}, supports_credentials=True)




@app.route("/composite/check_if_already_in_team", methods=["GET"])
def check_if_already_in_team():
    try:
        tournament_id = request.args.get("tournamentId")
        auth_header = request.headers.get("Authorization")
        if not tournament_id or not auth_header:
            return jsonify({ "error": "Missing tournamentId or auth header" }), 400

        res = requests.get(f"http://localhost:5001/player/my_teams?tournamentId={tournament_id}",
                           headers={"Authorization": auth_header})

        if res.status_code != 200:
            return jsonify({ "error": "Failed to fetch team info" }), res.status_code

        return jsonify({ "inTeam": res.json().get("inTeam", False) }), 200
    except Exception as e:
        return jsonify({ "error": str(e) }), 500
    
@app.route("/composite/tournament_details_with_teams/<tournament_id>", methods=["GET"])
def get_tournament_details_with_teams(tournament_id):
    try:
        # 1. Get tournament details from tournament service
        tourney_res = requests.get(f"http://localhost:5002/tournament/{tournament_id}")
        if tourney_res.status_code != 200:
            return jsonify({"error": "Tournament not found"}), 404
        tournament_data = tourney_res.json()

        raw_teams = tournament_data.get("teams", [])
        enriched_teams = []

        # 2. Get enriched data for each team from team service
        for team in raw_teams:
            team_id = team.get("teamId")
            if not team_id:
                continue
            team_detail_res = requests.get(f"http://localhost:5003/team/{team_id}")
            if team_detail_res.status_code == 200:
                team_info = team_detail_res.json()
                enriched_teams.append({
                    "teamId": team_id,
                    "name": team_info.get("name"),
                    "players": team_info.get("players", {})
                })
            else:
                enriched_teams.append(team)  # fallback to raw

        return jsonify({
            "tournamentName": tournament_data.get("name", ""),
            "enrichedTeams": enriched_teams
        }), 200



    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/composite/join_team", methods=["POST"])
def join_team():
    try:
        data = request.get_json()
        team_id = data.get("teamId")
        tournament_id = data.get("tournamentId")
        auth_header = request.headers.get("Authorization")

        if not team_id or not tournament_id or not auth_header:
            return jsonify({"error": "Missing fields"}), 400

        # Get player profile from player service
        player_res = requests.get("http://localhost:5001/player/profile", headers={
            "Authorization": auth_header
        })
        if player_res.status_code != 200:
            return jsonify({"error": "Unauthorized"}), 401

        player_data = player_res.json()
        player_id = player_data.get("userId")  
        player_name = player_data.get("username")


        # Join the team
        team_join_res = requests.post(
            f"http://localhost:5003/team/{team_id}/join",
            json={ "name": player_name },
            headers={ "Authorization": auth_header }
        )
        if team_join_res.status_code != 200:
            return jsonify({ "error": "Failed to join team" }), 400

        # Update tournament record
        tournament_res = requests.put(
            f"http://localhost:5002/tournament/{tournament_id}/add_player",
            json={ "player_id": player_id }
        )
        if tournament_res.status_code != 200:
            return jsonify({ "error": "Failed to update tournament" }), 400

        return jsonify({ "message": "Joined successfully!" }), 200

    except Exception as e:
        return jsonify({ "error": str(e) }), 500




if __name__ == "__main__":
    app.run(port=5005, debug=True)
