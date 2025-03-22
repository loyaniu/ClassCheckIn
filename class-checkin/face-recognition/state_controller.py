import sys
import paho.mqtt.client as mqtt

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(verbose=True, override=True)

# MQTT Configuration
BROKER = os.getenv("BROKER")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
BROKER_AUTH = int(os.getenv("BROKER_AUTH", "1")) == 1
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX")

# Available system states
STATES = ["IDLE", "SCANNING", "SUCCESS", "FAILURE", "ALREADY_SCANNED", "ERROR"]

# Global MQTT client
client = None


def initialize():
    """Initialize the MQTT client connection"""
    global client

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # For newer versions
    except AttributeError:
        client = mqtt.Client()

    if BROKER_AUTH:
        client.username_pw_set(USERNAME, PASSWORD)

    # Connect to the broker
    try:
        client.connect(BROKER, 1883, 60)
        client.loop_start()
        print(f"Connected to MQTT broker at {BROKER}")
        return True
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        return False


def send_command(device, command, params=None):
    """Send a command to control a device on the subscriber"""
    topic = TOPIC_PREFIX + device
    payload = command
    if params:
        payload += ":" + str(params)

    print(f"Sent: {topic} -> {payload}")
    # Actually send the message
    client.publish(topic, payload)


def set_state(state_name):
    """Set the system state"""
    # Import inside function to avoid circular import

    if state_name.upper() not in STATES:
        print(f"Invalid state: {state_name}")
        print(f"Available states: {', '.join(STATES)}")
        return False

    send_command("state", state_name.upper())
    return True


# Convenience functions for each state
def set_idle():
    return set_state("IDLE")


def set_scanning():
    return set_state("SCANNING")


def set_success():
    return set_state("SUCCESS")


def set_failure():
    return set_state("FAILURE")


def set_already_scanned():
    return set_state("ALREADY_SCANNED")


def disconnect():
    client.disconnect()


def set_error():
    return set_state("ERROR")


def reset_error():
    """Send a reset command to clear the error state"""
    # Import inside function to avoid circular import

    send_command("reset", "")


def run_state_menu():
    """Display and handle the state control menu"""
    print("\n--- State Control Menu ---")
    print("Available states:")

    for i, state in enumerate(STATES, 1):
        print(f"{i}. {state}")

    print("R. Return to main menu")

    choice = input("Select state or action: ").strip().upper()

    if choice == "R":
        return

    try:
        state_index = int(choice) - 1
        if 0 <= state_index < len(STATES):
            set_state(STATES[state_index])
            print(f"System state set to: {STATES[state_index]}")
        else:
            print("Invalid selection")
    except ValueError:
        print("Please enter a number or 'R'")


if __name__ == "__main__":
    # This allows the state controller to be run directly
    if not initialize():
        sys.exit(1)

    run_state_menu()
    # Clean up
    client.loop_stop()
    client.disconnect()
else:
    # When imported as a module, initialize the connection
    initialize()
