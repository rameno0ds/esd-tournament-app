from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Allow all origins for /dispute/* endpoints
CORS(app, resources={r"/dispute/*": {"origins": "*"}}, supports_credentials=True)

PLAYER_SERVICE_URL = "http://player-service:5001/player"

@app.route("/dispute/new", methods=["POST"])
def dispute_new():
    try:
        # Retrieve JSON payload from the request
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "No payload provided"}), 400
        
        # Validate required fields
        required_fields = ["matchId", "status", "raisedBy", "teamId", "reason", "evidenceUrl"]
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        # Forward to Outsystems
        outsystemsUrl = "https://personal-xxidmbev.outsystemscloud.com/disputeAPI/rest/v1/disputes"
        outsystems_payload = payload 
        outsystem_res = requests.post(outsystemsUrl, json=outsystems_payload)
        if outsystem_res.status_code != 200:
            return jsonify({"error": "Failed to forward to Outsystems"}), 500
        
        # Note: Use the Docker Compose service name for bot_api if running in the same network.
        notify_url = "http://notification-service:8000/notify_moderator"  # Adjust the port if needed
        notify_payload = {
            "matchId": payload.get("matchId"),
            "raisedBy": payload.get("raisedBy")
        }
        notify_res = requests.post(notify_url, json=notify_payload)
        if notify_res.status_code != 200:
            return jsonify({"error": "Failed to notify moderator"}), 500

        return jsonify({
            "status": "success",
            "message": "Composite dispute processed successfully.",
            "receivedPayload": payload,
            "outsystemsResponse": outsystem_res.json(),
            "moderatorNotification": notify_res.json()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/dispute/resolve", methods=["POST"])
def dispute_resolve():
    try:
        # Retrieve JSON payload from the request
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "No payload provided"}), 400
        
        match_id = payload["matchId"]
        status = payload["status"]  # "resolved" or "rejected"
        result = payload["result"]
        score = payload["score"]   # { teamA, teamB }
        raised_by = payload["raisedBy"]
        
        # 1) Outsystems DB update
        outsystems_url = "https://personal-xxidmbev.outsystemscloud.com/disputeAPI/rest/v1/disputes"
        outsystems_payload = {
            "matchId": match_id,
            "status": status,
        }
        outsystems_res = requests.put(outsystems_url, json=outsystems_payload)
        if outsystems_res.status_code != 200:
            return jsonify({"error": "Failed to update dispute in OutSystems"}), 500

        # 2) Notify the player via Discord
        # 2a) Need to fetch player name from player service
        
        player_res = requests.get(f"{PLAYER_SERVICE_URL}/{raised_by}")
        if player_res.status_code != 200:
            return jsonify({"error": "Failed to update match"}), 500
        player_data = player_res.json()
        player_name = player_data.get("username")

        # 2b) Notify the player
        player_notify_url = "http://notification-service:8000/dispute_outcome"
        player_notify_payload = {
            "player_name": player_name,
            "match_id": match_id,
            "result": result
        }
        player_notify_res = requests.post(player_notify_url, json=player_notify_payload)
        if player_notify_res.status_code != 200:
            return jsonify({"error": "Failed to notify player"}), 500
        
        # 3) Update match service with the result
        finalize_match_service_url = "http://finalize-match-outcome-service:5009/finalize-outcome"
        finalize_match_payload = {
            "matchId": match_id,
            "result": result,
            "score": score
        }
        finalize_match_res = requests.post(finalize_match_service_url, json=finalize_match_payload)
        if finalize_match_res.status_code != 200:
            return jsonify({"error": "Failed to update match service"}), 500

        return jsonify({
            "message": "Dispute resolved successfully.",
            "receivedPayload": payload
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Listen on all interfaces so Docker can map the port properly
    app.run(host="0.0.0.0", port=5008, debug=True)
