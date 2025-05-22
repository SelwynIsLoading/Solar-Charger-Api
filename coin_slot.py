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
    def __init__(self, pin=27, bouncetime=50, debug=True, timeout=1.0):
        self.pin = pin
        self.bouncetime = bouncetime
        self.debug = debug
        self.timeout = timeout  # seconds between pulses to separate coins

        self._pulse_count = 0
        self._lock = threading.Lock()
        self._timer = None
        self._is_running = False
        self._poll_thread = None
        self._last_state = None

    def _handle_pulse_timeout(self):
        with self._lock:
            pulse_total = self._pulse_count
            self._pulse_count = 0

        if pulse_total > 0:
            if self.debug:
                print(f"[CoinSlot] Coin session ended: {pulse_total} pulses")

    def _poll_pin(self):
        while self._is_running:
            try:
                current_state = GPIO.input(self.pin)
                
                # Detect falling edge (1 -> 0)
                if self._last_state == 1 and current_state == 0:
                    with self._lock:
                        self._pulse_count += 1
                        if self.debug:
                            print(f"[CoinSlot] Pulse received. Total pulses this session: {self._pulse_count}")

                        # Reset timeout
                        if self._timer:
                            self._timer.cancel()
                        self._timer = threading.Timer(self.timeout, self._handle_pulse_timeout)
                        self._timer.start()

                self._last_state = current_state
                time.sleep(0.01)  # Small delay to prevent CPU hogging
            except Exception as e:
                if self.debug:
                    print(f"[CoinSlot] Error in polling: {e}")
                time.sleep(0.1)

    def start(self):
        if self._is_running:
            if self.debug:
                print("[CoinSlot] Already running")
            return

        try:
            # Set up GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            # Test if we can read the pin
            self._last_state = GPIO.input(self.pin)
            if self.debug:
                print(f"[CoinSlot] Initial pin state: {self._last_state}")

            # Start polling thread
            self._is_running = True
            self._poll_thread = threading.Thread(target=self._poll_pin)
            self._poll_thread.daemon = True
            self._poll_thread.start()
            
            if self.debug:
                print(f"[CoinSlot] Monitoring started on GPIO {self.pin}")
                
        except Exception as e:
            if self.debug:
                print(f"[CoinSlot] Error starting coin slot: {str(e)}")
            self.stop()  # Clean up on error
            raise RuntimeError(f"Failed to initialize coin slot: {str(e)}")

    def stop(self):
        try:
            self._is_running = False
            if self._timer:
                self._timer.cancel()
            
            if self._poll_thread and self._poll_thread.is_alive():
                self._poll_thread.join(timeout=1.0)
            
            GPIO.cleanup()
            if self.debug:
                print("[CoinSlot] GPIO cleaned up and threads stopped.")
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
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            value = GPIO.input(self.pin)
            print(f"Pin {self.pin} current value: {value}")
            return True
        except Exception as e:
            print(f"Error testing pin: {e}")
            return False
        finally:
            GPIO.cleanup()

