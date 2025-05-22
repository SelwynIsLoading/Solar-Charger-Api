from flask import Flask, request, jsonify
from fingerprint import enroll_fingerprint, verify_fingerprint, delete_fingerprint
from serial_comm import send_command_to_arduino
from coin_slot import setup_coin_slot, get_coin_count

app = Flask(__name__)
setup_coin_slot()

@app.route("/fingerprint/enroll", methods=["POST"])
def enroll():
    result = enroll_fingerprint()
    return jsonify(result)

@app.route("/fingerprint/verify", methods=["POST"])
def verify():
    result = verify_fingerprint()
    return jsonify(result)

@app.route("/fingerprint/delete", methods=["POST"])
def delete():
    fingerprint_id = request.json.get("id")
    result = delete_fingerprint(fingerprint_id)
    return jsonify(result)

@app.route("/arduino/send", methods=["POST"])
def send_to_arduino():
    command = request.json.get("command")
    result = send_command_to_arduino(command)
    return jsonify(result)

@app.route("/coin/count", methods=["GET"])
def coin_count():
    result = get_coin_count()
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
