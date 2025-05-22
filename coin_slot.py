import RPi.GPIO as GPIO
import threading

COIN_PIN = 17
coin_count = 0
lock = threading.Lock()

def coin_inserted(channel):
    global coin_count
    with lock:
        coin_count += 1
        print(f"[Coin Slot] Coin detected! Total = {coin_count}")

def setup_coin_slot():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(COIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.remove_event_detect(COIN_PIN)
    GPIO.add_event_detect(COIN_PIN, GPIO.RISING, callback=coin_inserted, bouncetime=200)

def get_coin_count():
    with lock:
        return coin_count

def reset_coin_count():
    global coin_count
    with lock:
        coin_count = 0
