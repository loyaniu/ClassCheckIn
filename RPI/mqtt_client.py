import logging
import time
import sys
import signal
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Main")

# Import MQTT handler
from mqtt_handler import MQTTHandler

# Global variable for cleanup
mqtt_handler = None


def cleanup(signum=None, frame=None):
    """Clean up resources and exit"""
    logger.info("Cleaning up resources...")
    # Add any necessary cleanup code here
    logger.info("Cleanup complete")
    sys.exit(0)


def start_mqtt_handler():
    """Start the MQTT handler"""
    mqtt_handler = MQTTHandler()
    mqtt_handler.start()

    # Initialize state manager
    from state_manager import StateManager

    mqtt_handler.state_manager = StateManager(mqtt_handler)

    return mqtt_handler


if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        logger.info("Starting Raspberry Pi control system")

        # Start MQTT handler
        mqtt_handler = start_mqtt_handler()
        logger.info("MQTT handler started")

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Program interrupted")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        cleanup()
