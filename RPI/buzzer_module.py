from gpiozero import Buzzer
import time
import logging

# Configure logging
logger = logging.getLogger("Buzzer_Module")


class BuzzerController:
    def __init__(self, pin=23):
        """Initialize buzzer controller"""
        self.buzzer = Buzzer(pin)
        logger.info(f"Buzzer initialized on pin {pin}")

    def beep(self, duration=1):
        """Make the buzzer beep for specified duration"""
        logger.info(f"Buzzer beeping for {duration} seconds")
        self.buzzer.on()
        time.sleep(duration)
        self.buzzer.off()

    def pattern(self, count=3, duration=0.2):
        """Make the buzzer beep in a pattern"""
        logger.info(f"Buzzer pattern: {count} times, {duration} seconds each")
        for _ in range(count):
            self.buzzer.on()
            time.sleep(duration)
            self.buzzer.off()
            time.sleep(duration)

    def cleanup(self):
        """Clean up resources"""
        self.buzzer.off()
        self.buzzer.close()
        logger.info("Buzzer resources cleaned up")
