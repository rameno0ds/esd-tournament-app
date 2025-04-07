from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Allow all origins for /dispute/* endpoints
CORS(app, resources={r"/dispute/*": {"origins": "*"}}, supports_credentials=True)

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

# @app.route("/dispute/resolve", methods=["POST"])
# def dispute_resolve():
#     try:
#         # Retrieve JSON payload from the request
#         payload = request.get_json()
#         if not payload:
#             return jsonify({"error": "No payload provided"}), 400
        
#         # Validate required fields
#         required_fields = ["matchId", "status", "resolvedBy"]
#         missing_fields = [field for field in required_fields if field not in payload]
#         if missing_fields:
#             return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

#         # Here you can add logic to resolve the dispute, e.g., updating a database or notifying other services.
        
#         return jsonify({
#             "message": "Dispute resolved successfully.",
#             "receivedPayload": payload
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Listen on all interfaces so Docker can map the port properly
    app.run(host="0.0.0.0", port=5008, debug=True)
