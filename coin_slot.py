import RPi.GPIO as GPIO
import time

COIN_PIN = 17
coin_count = 0

def coin_inserted(channel):
    global coin_count
    coin_count += 1
    print(f"Coin inserted! Total: {coin_count}")

def setup_coin_slot():
    GPIO.setmode(GPIO.BCM)  # or GPIO.BOARD if using pin numbers
    GPIO.setup(COIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Clean up previous events to avoid double edge detection
    GPIO.remove_event_detect(COIN_PIN)

    GPIO.add_event_detect(COIN_PIN, GPIO.RISING, callback=coin_inserted, bouncetime=200)
