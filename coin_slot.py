import RPi.GPIO as GPIO
import time

COIN_PIN = 17  # Change to your GPIO pin

pulse_count = 0

def setup_coin_slot():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(COIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(COIN_PIN, GPIO.RISING, callback=coin_inserted, bouncetime=200)

def coin_inserted(channel):
    global pulse_count
    pulse_count += 1

def get_coin_count():
    global pulse_count
    count = pulse_count
    pulse_count = 0  # Reset after reading
    return {"coins": count}
