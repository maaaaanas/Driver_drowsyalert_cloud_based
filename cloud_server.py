from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
from twilio.rest import Client
import datetime
from dotenv import load_dotenv
import os


load_dotenv()


# ================= FIREBASE SETUP =================
cred = credentials.Certificate("firebase_key.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://drowsy-22-default-rtdb.firebaseio.com/"
})

TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH = os.getenv('TWILIO_AUTH')
TWILIO_FROM = os.getenv('TWILIO_FROM')
TWILIO_TO = os.getenv('TWILIO_TO')

client = Client(TWILIO_SID, TWILIO_AUTH)

# ================= FLASK SERVER =================
app = Flask(__name__)

@app.route("/alert", methods=["POST"])
def send_alert():
    data = request.json

    now = datetime.datetime.now()
    record = {
        "driver_id": data.get("driver_id"),
        "status": data.get("status"),
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%d-%m-%Y"),
        "vehicle": data.get("vehicle")
    }

    # Upload to Firebase
    db.reference("drowsiness_logs").push(record)

    # Send SMS
    sms = client.messages.create(
        body=f"🚨 DROWSINESS ALERT! Driver {record['driver_id']} is DROWSY at {record['time']}",
        from_=TWILIO_FROM,
        to=TWILIO_TO
    )

    return jsonify({"status": "success", "sms_sid": sms.sid})

if __name__ == "__main__":
    app.run(debug=True)
