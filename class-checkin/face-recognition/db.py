import os
from dotenv import load_dotenv
from convex import ConvexClient

# Load environment variables
load_dotenv("../.env.local")
CONVEX_URL = os.getenv("VITE_CONVEX_URL")

# Create a client
client = ConvexClient(CONVEX_URL)


def create_checkin(email, timestamp, name):
    # Insert data by calling your mutation
    id_ = client.mutation(
        "checkins:create", {"email": email, "timestamp": timestamp, "name": name}
    )

    print(f"Created checkin with ID: {id_}")
    return id_
