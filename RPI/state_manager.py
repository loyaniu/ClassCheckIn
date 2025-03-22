import logging
import time
from enum import Enum, auto
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("StateManager")


class SystemState(Enum):
    """Enum representing possible system states as defined in process.md"""

    IDLE = 0
    SCANNING = 1
    SUCCESS = 2
    FAILURE = 3
    ALREADY_SCANNED = 4
    ERROR = 5


class StateManager:
    """Manages system states and associated behaviors"""

    def __init__(self, mqtt_handler):
        """Initialize the state manager with a reference to the MQTT handler"""
        self.mqtt_handler = mqtt_handler
        self.current_state = SystemState.IDLE
        self.previous_state = None
        logger.info(f"State Manager initialized in {self.current_state.name} state")

        # Dictionary of state transition handlers
        self.state_transitions = {
            SystemState.IDLE: self.enter_idle_state,
            SystemState.SCANNING: self.enter_scanning_state,
            SystemState.SUCCESS: self.enter_success_state,
            SystemState.FAILURE: self.enter_failure_state,
            SystemState.ALREADY_SCANNED: self.enter_already_scanned_state,
            SystemState.ERROR: self.enter_error_state,
        }

        # Run initial state setup
        self.state_transitions[self.current_state]()

    def transition_to(self, new_state):
        """Transition to a new state"""
        if new_state == self.current_state:
            logger.info(f"Already in {new_state.name} state")
            return

        logger.info(f"Transitioning from {self.current_state.name} to {new_state.name}")
        self.previous_state = self.current_state
        self.current_state = new_state

        # Execute the state transition handler
        self.state_transitions[new_state]()

    def enter_idle_state(self):
        """
        Idle State
        LED: Solid blue
        Buzzer: Silent
        Description: System ready
        """
        logger.info("Entering IDLE state")
        self.mqtt_handler.rgb.set_color(0, 0, 1)  # Solid blue

    def enter_scanning_state(self):
        """
        Scanning State
        LED: Blinking yellow
        Buzzer: Single short beep
        Description: Processing detection
        """
        logger.info("Entering SCANNING state")
        # Yellow light
        self.mqtt_handler.rgb.set_color(1, 1, 0)  # Yellow
        # Single short beep
        self.mqtt_handler.buzzer.beep(0.2)

    def enter_success_state(self):
        """
        Success State
        LED: Solid green (3 seconds)
        Buzzer: Two short beeps
        Description: Detection successful
        """
        logger.info("Entering SUCCESS state")

        # Start a thread for solid green light
        def show_green():
            self.mqtt_handler.rgb.set_color(0, 1, 0)  # Green
            time.sleep(0.2)
            self.mqtt_handler.rgb.set_color(0, 0, 0)  # Off
            time.sleep(0.2)
            self.mqtt_handler.rgb.set_color(0, 1, 0)  # Green

        # Start green light in a separate thread
        green_thread = threading.Thread(target=show_green)
        green_thread.daemon = True
        green_thread.start()

        # Two short beeps (happens simultaneously with green light)
        self.mqtt_handler.buzzer.pattern(2, 0.2)

        # Wait for the green light to complete
        green_thread.join()

        # Return to IDLE state
        self.transition_to(SystemState.IDLE)

    def enter_failure_state(self):
        """
        Failure State
        LED: Solid red (3 seconds)
        Buzzer: One long beep
        Description: Detection failed
        """
        logger.info("Entering FAILURE state")

        # Start a thread for solid red light
        def show_red():
            self.mqtt_handler.rgb.set_color(1, 0, 0)  # Red
            time.sleep(1)  # Keep red light on for 3 seconds

        # Start red light in a separate thread
        red_thread = threading.Thread(target=show_red)
        red_thread.daemon = True
        red_thread.start()

        # One long beep (happens simultaneously with red light)
        self.mqtt_handler.buzzer.beep(1.0)

        # Wait for the red light to complete
        red_thread.join()

        # Return to IDLE state
        self.transition_to(SystemState.IDLE)

    def enter_already_scanned_state(self):
        """
        Already Scanned State
        LED: Green double flash
        Buzzer: Three rapid beeps
        Description: Object previously detected
        """
        logger.info("Entering ALREADY_SCANNED state")

        # Start a thread for green double flash
        def show_green():
            self.mqtt_handler.rgb.set_color(0, 1, 0)  # Green
            time.sleep(0.1)
            self.mqtt_handler.rgb.set_color(0, 0, 0)  # Off
            time.sleep(0.1)
            self.mqtt_handler.rgb.set_color(0, 1, 0)  # Green
            time.sleep(0.1)
            self.mqtt_handler.rgb.set_color(0, 0, 0)  # Off
            time.sleep(0.1)
            self.mqtt_handler.rgb.set_color(0, 1, 0)  # Green

        # Start green light in a separate thread
        green_thread = threading.Thread(target=show_green)
        green_thread.daemon = True
        green_thread.start()

        # Three rapid beeps (happens simultaneously with green light)
        self.mqtt_handler.buzzer.pattern(3, 0.1)

        # Wait for the green light to complete
        green_thread.join()

        # Return to IDLE state
        self.transition_to(SystemState.IDLE)

    def enter_error_state(self):
        """
        Error State
        LED: Rapid red flashing
        Buzzer: Three intermittent warning beeps
        Description: System error detected
        """
        logger.info("Entering ERROR state")

        # Start a thread for rapid red flashing
        def flash_red():
            for _ in range(6):  # Flash for about the same duration as the buzzer
                self.mqtt_handler.rgb.set_color(1, 0, 0)  # Red
                time.sleep(0.1)
                self.mqtt_handler.rgb.set_color(0, 0, 0)  # Off
                time.sleep(0.1)

        # Start flashing in a separate thread
        flash_thread = threading.Thread(target=flash_red)
        flash_thread.daemon = True
        flash_thread.start()

        # Three intermittent warning beeps (happens simultaneously with flashing)
        self.mqtt_handler.buzzer.pattern(3, 0.3)

        # Wait for the flashing to complete
        flash_thread.join()

        # Return to IDLE state
        self.transition_to(SystemState.IDLE)

    def handle_message(self, topic, payload):
        """Handle incoming messages and change state if needed"""
        # Extract state command if present
        if topic.endswith("/state"):
            try:
                new_state = SystemState[payload.upper()]
                self.transition_to(new_state)
                return True
            except KeyError:
                logger.error(f"Invalid state requested: {payload}")
                return False

        # Special command handling based on current state
        if self.current_state == SystemState.SCANNING:
            if topic.endswith("/camera"):
                # In SCANNING state, always capture with high resolution
                self.mqtt_handler.camera.set_resolution("high")
                self.mqtt_handler.camera.capture()
                return True

        elif self.current_state == SystemState.ERROR:
            # In ERROR state, acknowledge and clear error
            if topic.endswith("/reset"):
                logger.info("Acknowledging error and resetting")
                self.transition_to(SystemState.IDLE)
                return True

        # If not handled by state logic, return False to let normal command processing occur
        return False

    def run_state_cycle(self):
        """Run any periodic tasks for the current state"""
        if self.current_state == SystemState.SCANNING:
            # Blinking yellow in scanning state
            self.mqtt_handler.rgb.set_color(1, 1, 0)  # Yellow
            time.sleep(0.3)
            self.mqtt_handler.rgb.set_color(0, 0, 0)  # Off
            time.sleep(0.3)

        elif self.current_state == SystemState.ERROR:
            # Rapid red flashing in error state
            self.mqtt_handler.rgb.set_color(1, 0, 0)  # Red
            time.sleep(0.2)
            self.mqtt_handler.rgb.set_color(0, 0, 0)  # Off
            time.sleep(0.2)


# Function to create and return a new StateManager instance
def create_state_manager(mqtt_handler):
    """Create and initialize a new StateManager"""
    return StateManager(mqtt_handler)
