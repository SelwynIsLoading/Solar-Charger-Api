from flask import Flask, request, jsonify
from fingerprint import enroll_fingerprint, verify_fingerprint, delete_fingerprint
from serial_comm import send_command_to_arduino
# from coin_slot import setup_coin_slot, get_coin_count, reset_coin_count
from coin_slot import CoinSlot

# Initialize coin slot
try:
    coin_slot = CoinSlot(pin=16, debug=True)
    # Test the pin first
    if coin_slot.test_pin():
        print("GPIO pin test successful, starting coin slot...")
        coin_slot.start()
    else:
        print("Warning: GPIO pin test failed!")
except Exception as e:
    print(f"Error initializing coin slot: {e}")
    coin_slot = None

app = Flask(__name__)
# setup_coin_slot()

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

# @app.route("/coins", methods=["GET"])
# def coins():
#     return jsonify({"coins": get_coin_count()})

# @app.route("/coins/reset", methods=["POST"])
# def reset_coins():
#     reset_coin_count()
#     return jsonify({"status": "reset", "coins": 0})

@app.route("/coins/wait", methods=["GET"])
def wait_for_coins():
    try:
        pulse_count = coin_slot.wait_for_pulse()
        return jsonify({
            "pulses": pulse_count
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
