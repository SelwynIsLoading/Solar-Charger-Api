import serial

arduino_serial = serial.Serial("/dev/ttyAMA0", 9600, timeout=1)

def send_command_to_arduino(command: str):
    if not command.endswith('\n'):
        command += '\n'
    arduino_serial.write(command.encode('utf-8'))
    response = arduino_serial.readline().decode().strip()
    return {"command": command.strip(), "response": response}
