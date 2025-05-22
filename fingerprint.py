from pyfingerprint.pyfingerprint import PyFingerprint
import time

# Initialize fingerprint sensor
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if not f.verifyPassword():
        raise ValueError('Fingerprint sensor password is incorrect!')
except Exception as e:
    print(f'Failed to initialize sensor: {e}')
    f = None


def enroll_fingerprint():
    """Enroll a new fingerprint and return the position ID"""
    if f is None:
        return {"status": "error", "message": "Fingerprint sensor not initialized"}

    try:
        print("Waiting for finger...")
        while not f.readImage():
            pass

        f.convertImage(0x01)

        if f.searchTemplate()[0] >= 0:
            return {"status": "error", "message": "Fingerprint already exists"}

        print("Remove finger...")
        time.sleep(2)

        print("Place same finger again...")
        while not f.readImage():
            pass

        f.convertImage(0x02)

        if f.compareCharacteristics() == 0:
            return {"status": "error", "message": "Fingerprints do not match"}

        f.createTemplate()
        position_number = f.storeTemplate()
        return {"status": "enrolled", "id": position_number}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def verify_fingerprint():
    """Verify a fingerprint and return its ID if found"""
    if f is None:
        return {"status": "error", "message": "Fingerprint sensor not initialized"}

    try:
        print("Waiting for finger...")
        while not f.readImage():
            pass

        f.convertImage(0x01)
        result = f.searchTemplate()

        position_number = result[0]
        accuracy_score = result[1]

        if position_number == -1:
            return {"status": "no match"}
        else:
            return {"status": "match", "id": position_number, "score": accuracy_score}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_fingerprint(fingerprint_id):
    """Delete a fingerprint by template position"""
    if f is None:
        return {"status": "error", "message": "Fingerprint sensor not initialized"}

    try:
        if f.deleteTemplate(int(fingerprint_id)):
            return {"status": "deleted", "id": fingerprint_id}
        else:
            return {"status": "error", "message": "Failed to delete fingerprint"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
