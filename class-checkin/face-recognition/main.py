"""
Author: Zhonglin Niu (zn23) and Yuese Li (yl77)
"""

import time
import requests
import os
from deepface import DeepFace
from db import create_checkin
import state_controller

RPI_HOST = os.getenv("RPI_HOST", "localhost")


def download_latest_image():
    # Add timestamp to URL to avoid caching
    url = f"http://{RPI_HOST}:8000/static/latest_image.jpg?{time.time()}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        save_path = "latest_image.jpg"
        with open(save_path, "wb") as f:
            f.write(response.content)

        return save_path

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return None


def recognize_face(image_path):
    try:
        # Use DeepFace to find matching faces in the database
        result = DeepFace.find(
            img_path=image_path,
            db_path="pictures",
            model_name="ArcFace",
            distance_metric="cosine",
            enforce_detection=False,
            detector_backend="mtcnn",
        )

        print(result)

        if not result[0].empty:
            best_match = result[0].iloc[0]
            # Extract student ID and name from filename (format: zn23_Loya-Niu)
            filename = os.path.splitext(os.path.basename(best_match["identity"]))[0]

            parts = filename.split("_")
            if len(parts) == 2:
                email = parts[0]  # Student ID/email (e.g., zn23)
                name_parts = parts[1].split("-")
                full_name = " ".join(name_parts)

                print(f"Recognized person: {full_name} ({email})")

                # Record successful check-in to database
                create_checkin(email, time.time(), full_name)
                state_controller.set_success()

                return full_name
            else:
                print(f"Filename format not recognized: {filename}")
                return None

        print("No matching face found")
        return None

    except Exception as e:
        print(f"Error during face recognition: {e}")
        return None


def main():
    image_path = download_latest_image()
    if image_path:
        recognized_person = recognize_face(image_path)
        return recognized_person
    return None


if __name__ == "__main__":
    try:
        # Continuous recognition loop
        while True:
            print("Starting recognition")
            start_time = time.time()
            main()
            end_time = time.time()
            print(f"Recognition time: {end_time - start_time:.2f} seconds")
            print("Recognition completed")
            time.sleep(1)  # Brief pause between recognition attempts
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Shutting down...")
        state_controller.disconnect()
