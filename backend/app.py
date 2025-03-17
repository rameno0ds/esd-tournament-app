from flask import Flask
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)
# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")  # Download from Firebase
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route("/")
def home():
    return "Tournament Backend API is Running!"

if __name__ == "__main__":
    app.run(debug=True)
