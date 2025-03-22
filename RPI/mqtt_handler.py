import paho.mqtt.client as mqtt
import logging
import sys
import os

# Add parent directory to path to import from sub modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import device controllers
from buzzer_module import BuzzerController
from rgb_module import RGBController

import os
from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)

# MQTT Configuration
BROKER = os.getenv("BROKER")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
BROKER_AUTH = int(os.getenv("BROKER_AUTH", "1")) == 1
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MQTT_Handler")


class MQTTHandler:
    def __init__(self):
        """Initialize MQTT handler"""
        # Initialize device controllers
        self.buzzer = BuzzerController()
        self.rgb = RGBController()

        # Initialize MQTT client
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Set authentication if needed
        if BROKER_AUTH:
            self.client.username_pw_set(USERNAME, PASSWORD)

    def start(self):
        """Start the MQTT client"""
        self.client.connect(BROKER, 1883, 60)
        self.client.loop_start()
        logger.info("MQTT client started")
        return self.client

    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        logger.info(f"Connected to MQTT broker with result code {rc}")

        # Subscribe to all control topics
        client.subscribe(TOPIC_PREFIX + "#")
        logger.info(f"Subscribed to {TOPIC_PREFIX}#")

    def on_message(self, client, userdata, msg):
        """Callback when message is received"""
        topic = msg.topic
        payload = msg.payload.decode()
        logger.info(f"Received message: {topic} -> {payload}")

        # Extract the device type from the topic
        device_type = topic.split("/")[-1]

        # Handle state change commands
        if device_type == "state":
            if hasattr(self, "state_manager"):
                try:
                    # Convert string state to enum
                    from state_manager import SystemState

                    new_state = SystemState[payload]
                    self.state_manager.transition_to(new_state)
                except (KeyError, AttributeError) as e:
                    logger.error(f"Invalid state or state manager error: {e}")
            else:
                logger.warning("State manager not initialized")
            return

        # Handle other device commands
        # Extract device from topic
        device = topic.replace(TOPIC_PREFIX, "")

        # Parse command and parameters
        if ":" in payload:
            command, params = payload.split(":", 1)
        else:
            command = payload
            params = None

        # Handle commands based on device
        if device == "buzzer":
            self.handle_buzzer_command(command, params)
        elif device == "rgb":
            self.handle_rgb_command(command, params)
        
       

    def handle_buzzer_command(self, command, params):
        """Handle buzzer commands"""
        if command == "beep":
            duration = float(params) if params else 1
            self.buzzer.beep(duration)

        elif command == "pattern":
            if params:
                count, duration = map(float, params.split(","))
                count = int(count)
            else:
                count, duration = 3, 0.2

            self.buzzer.pattern(count, duration)

    def handle_rgb_command(self, command, params):
        """Handle RGB LED commands"""
        if command == "color":
            if params:
                r, g, b = map(float, params.split(","))
                self.rgb.set_color(r, g, b)
            else:
                logger.error("Color command requires RGB parameters")

        elif command == "random":
            self.rgb.start_random_mode()

    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up MQTT handler resources...")

        # Clean up device controllers
        self.buzzer.cleanup()
        self.rgb.cleanup()

        # Disconnect MQTT
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT handler resources cleaned up")


def start_mqtt_handler():
    """Start the MQTT handler"""
    handler = MQTTHandler()
    handler.start()
    return handler


if __name__ == "__main__":
    try:
        logger.info("Starting MQTT handler")
        handler = start_mqtt_handler()

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Stopping MQTT handler")
    finally:
        # Clean up
        handler.cleanup()
