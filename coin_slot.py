# import RPi.GPIO as GPIO
# import threading

# COIN_PIN = 17
# coin_count = 0
# lock = threading.Lock()

# def coin_inserted(channel):
#     global coin_count
#     with lock:
#         coin_count += 1
#         print(f"[Coin Slot] Coin detected! Total = {coin_count}")

# def setup_coin_slot():
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(COIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#     GPIO.remove_event_detect(COIN_PIN)
#     GPIO.add_event_detect(COIN_PIN, GPIO.RISING, callback=coin_inserted, bouncetime=200)

# def get_coin_count():
#     with lock:
#         return coin_count

# def reset_coin_count():
#     global coin_count
#     with lock:
#         coin_count = 0


import RPi.GPIO as GPIO
import threading
import requests
import time

class CoinSlot:
    def __init__(self, pin=17, bouncetime=50, debug=True, webhook_url=None, timeout=1.0):
        self.pin = pin
        self.bouncetime = bouncetime
        self.debug = debug
        self.webhook_url = webhook_url
        self.timeout = timeout  # seconds between pulses to separate coins

        self._pulse_count = 0
        self._lock = threading.Lock()
        self._timer = None

    def _handle_pulse_timeout(self):
        with self._lock:
            pulse_total = self._pulse_count
            self._pulse_count = 0

        if pulse_total > 0:
            if self.debug:
                print(f"[CoinSlot] Coin session ended: {pulse_total} pulses")

            if self.webhook_url:
                try:
                    requests.post(self.webhook_url, json={"pulses": pulse_total})
                    if self.debug:
                        print(f"[CoinSlot] Webhook sent: {pulse_total} pulses → {self.webhook_url}")
                except Exception as e:
                    print(f"[CoinSlot] Webhook failed: {e}")

    def _coin_pulse(self, channel):
        with self._lock:
            self._pulse_count += 1
            if self.debug:
                print(f"[CoinSlot] Pulse received. Total pulses this session: {self._pulse_count}")

            # Reset timeout
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.timeout, self._handle_pulse_timeout)
            self._timer.start()

    def start(self):
        try:
            # First cleanup any existing GPIO setup
            GPIO.cleanup()
            
            # Set up GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            
            # Remove any existing event detection
            try:
                GPIO.remove_event_detect(self.pin)
            except RuntimeError:
                pass  # Ignore if no event detection was set up
                
            # Add new event detection
            GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self._coin_pulse, bouncetime=self.bouncetime)
            
            if self.debug:
                print(f"[CoinSlot] Monitoring started on GPIO {self.pin}")
                
        except Exception as e:
            if self.debug:
                print(f"[CoinSlot] Error starting coin slot: {str(e)}")
            raise RuntimeError(f"Failed to initialize coin slot: {str(e)}")

    def stop(self):
        if self._timer:
            self._timer.cancel()
        GPIO.cleanup()
        if self.debug:
            print("[CoinSlot] GPIO cleaned up and timer stopped.")

    def wait_for_pulse(self):
        """Wait for a pulse and return the pulse count."""
        with self._lock:
            current_count = self._pulse_count
            
        while current_count == 0:
            time.sleep(0.1)  # Small delay to prevent CPU hogging
            with self._lock:
                current_count = self._pulse_count
                
        return current_count

