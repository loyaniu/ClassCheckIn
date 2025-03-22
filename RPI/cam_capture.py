from picamera2 import Picamera2
from flask import Flask, send_file, render_template
import io
import logging
import threading
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create Flask application
app = Flask(__name__)

# Image save path
STATIC_FOLDER = 'static'
IMAGE_PATH = os.path.join(STATIC_FOLDER, 'latest_image.jpg')

# Ensure static folder exists
os.makedirs(STATIC_FOLDER, exist_ok=True)

# Initialize camera
def init_camera(resolution="low"):
    picam2 = Picamera2()
    
    # Camera is OV5647, maximum resolution is 2592 x 1944
    resolutions = {
        "low": (640, 480),       # Prioritize smoothness
        "medium": (1280, 720),   # Balance resolution and performance
        "high": (1920, 1080),    # HD resolution
        "max": (2592, 1944)      # Maximum resolution (use with caution)
    }
    
    selected_res = resolutions.get(resolution, resolutions["low"])
    logging.info(f"Starting camera, resolution set to: {selected_res[0]} x {selected_res[1]}")
    
    config = picam2.create_still_configuration(main={"size": selected_res})
    picam2.configure(config)
    picam2.start()
    return picam2

# Thread function for periodic image capture
def capture_images(picam2, interval=0.2):  # 0.2 second interval, approx 5 images per second
    while True:
        try:
            # Capture image directly to file
            picam2.capture_file(IMAGE_PATH)
            time.sleep(interval)
        except Exception as e:
            logging.error(f"Error capturing image: {e}")
            time.sleep(1)  # Wait longer before retrying on error

# Route setup
@app.route('/')
def index():
    # Generate a random parameter to ensure the browser doesn't cache the image
    timestamp = int(time.time())
    return render_template('index.html', timestamp=timestamp)

@app.route('/change_resolution/<resolution>')
def change_resolution(resolution):
    global picam2, capture_thread, current_resolution
    
    if resolution in ["low", "medium", "high", "max"]:
        current_resolution = resolution
        
        # Stop current camera
        if picam2:
            picam2.close()
        
        # Reinitialize camera
        picam2 = init_camera(resolution)
        
        # Restart capture thread
        if capture_thread and capture_thread.is_alive():
            # Cannot directly stop thread, but a new thread will start
            pass
        
        capture_thread = threading.Thread(target=capture_images, args=(picam2,), daemon=True)
        capture_thread.start()
        
    return render_template('redirect.html')

# Set global variables
current_resolution = "low"
picam2 = None
capture_thread = None

if __name__ == '__main__':
    # Initialize camera
    picam2 = init_camera(current_resolution)
    
    # Start image capture thread
    capture_thread = threading.Thread(target=capture_images, args=(picam2,), daemon=True)
    capture_thread.start()
    
    try:
        # Run Flask application in a separate thread
        app.run(host='0.0.0.0', port=8000, threaded=True)
    finally:
        # Ensure camera stops on exit
        if picam2:
            picam2.close()
