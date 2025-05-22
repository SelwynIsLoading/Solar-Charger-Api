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
import time

class CoinSlot:
    def __init__(self, pin=16, bouncetime=50, debug=True, timeout=1.0):  # Physical pin 16
        self.pin = pin
        self.bouncetime = bouncetime
        self.debug = debug
        self.timeout = timeout  # seconds between pulses to separate coins

        self._pulse_count = 0
        self._lock = threading.Lock()
        self._timer = None
        self._is_running = False

    def _handle_pulse_timeout(self):
        with self._lock:
            pulse_total = self._pulse_count
            self._pulse_count = 0

        if pulse_total > 0:
            if self.debug:
                print(f"[CoinSlot] Coin session ended: {pulse_total} pulses")

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
            # Set up GPIO using physical pin numbering
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            # Test if we can read the pin
            test_value = GPIO.input(self.pin)
            if self.debug:
                print(f"[CoinSlot] Initial pin state: {test_value}")

            # Add event detection
            GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self._coin_pulse, bouncetime=self.bouncetime)
            
            self._is_running = True
            if self.debug:
                print(f"[CoinSlot] Monitoring started on physical pin {self.pin}")
                
        except Exception as e:
            if self.debug:
                print(f"[CoinSlot] Error starting coin slot: {str(e)}")
            self.stop()  # Clean up on error
            raise RuntimeError(f"Failed to initialize coin slot: {str(e)}")

    def stop(self):
        try:
            if self._timer:
                self._timer.cancel()
            
            if self._is_running:
                try:
                    GPIO.remove_event_detect(self.pin)
                except:
                    pass
                GPIO.cleanup()
                self._is_running = False
                
            if self.debug:
                print("[CoinSlot] GPIO cleaned up and timer stopped.")
        except Exception as e:
            if self.debug:
                print(f"[CoinSlot] Error during cleanup: {str(e)}")

    def wait_for_pulse(self):
        """Wait for a pulse and return the pulse count."""
        with self._lock:
            current_count = self._pulse_count
            
        while current_count == 0:
            time.sleep(0.1)  # Small delay to prevent CPU hogging
            with self._lock:
                current_count = self._pulse_count
                
        return current_count

    def test_pin(self):
        """Test if the GPIO pin is working properly."""
        try:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            value = GPIO.input(self.pin)
            print(f"Physical pin {self.pin} current value: {value}")
            return True
        except Exception as e:
            print(f"Error testing pin: {e}")
            return False

