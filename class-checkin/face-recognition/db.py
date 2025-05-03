"""
Author: Zhonglin Niu (zn23) and Yuese Li (yl77)
"""

import os
from dotenv import load_dotenv
from convex import ConvexClient

load_dotenv("../.env.local")
CONVEX_URL = os.getenv("VITE_CONVEX_URL")

client = ConvexClient(CONVEX_URL)


def create_checkin(email, timestamp, name):
    id_ = client.mutation(
        "checkins:create", {"email": email, "timestamp": timestamp, "name": name}
    )

    print(f"Created checkin with ID: {id_}")
    return id_
