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


        return jsonify({
            "message": "Composite dispute processed successfully.",
            "receivedPayload": payload
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Listen on all interfaces so Docker can map the port properly
    app.run(host="0.0.0.0", port=5008, debug=True)
