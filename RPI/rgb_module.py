from gpiozero import RGBLED
import threading
import time
import random
import logging

# Configure logging
logger = logging.getLogger("RGB_Module")


class RGBController:
    def __init__(self, red_pin=17, green_pin=27, blue_pin=22):
        """Initialize RGB LED controller"""
        self.rgb_led = RGBLED(red=red_pin, green=green_pin, blue=blue_pin)
        self.random_color_active = False
        self.random_color_thread = None
        logger.info(f"RGB LED initialized on pins R:{red_pin}, G:{green_pin}, B:{blue_pin}")

    def set_color(self, r, g, b):
        """Set RGB LED color"""
        # Ensure random mode is stopped
        self._stop_random_mode()

        # Ensure values are within range
        r = max(0, min(1, r))
        g = max(0, min(1, g))
        b = max(0, min(1, b))

        logger.info(f"Setting RGB LED color: ({r}, {g}, {b})")
        self.rgb_led.color = (r, g, b)

    def start_random_mode(self):
        """Start random color mode"""
        if not self.random_color_active:
            self.random_color_active = True
            self.random_color_thread = threading.Thread(target=self._random_color_mode)
            self.random_color_thread.daemon = True
            self.random_color_thread.start()
            logger.info("Random color mode started")
        else:
            logger.info("Random color mode already running")

    def _random_color_mode(self):
        """Thread function for random color mode"""
        logger.info("Starting random color mode")

        # Current color and target color
        current_color = (0, 0, 0)

        while self.random_color_active:
            # Generate new target color
            target_color = (random.random(), random.random(), random.random())

            # Set gradient transition
            steps = 50
            step_time = 0.5 / steps

            # Calculate step size
            r_step = (target_color[0] - current_color[0]) / steps
            g_step = (target_color[1] - current_color[1]) / steps
            b_step = (target_color[2] - current_color[2]) / steps

            # Execute transition
            for i in range(steps):
                if not self.random_color_active:
                    break

                r = current_color[0] + r_step * i
                g = current_color[1] + g_step * i
                b = current_color[2] + b_step * i

                # Ensure values are within range
                r = max(0, min(1, r))
                g = max(0, min(1, g))
                b = max(0, min(1, b))

                self.rgb_led.color = (r, g, b)
                time.sleep(step_time)

            current_color = target_color

        logger.info("Random color mode stopped")

    def _stop_random_mode(self):
        """Stop random color mode"""
        if self.random_color_active:
            self.random_color_active = False
            if self.random_color_thread:
                self.random_color_thread.join(timeout=1)
                self.random_color_thread = None

    def cleanup(self):
        """Clean up resources"""
        self._stop_random_mode()
        self.rgb_led.color = (0, 0, 0)
        self.rgb_led.close()
        logger.info("RGB LED resources cleaned up")
