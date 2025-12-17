# MADE BY REAPXR - FASTFAME.PRO
# DO NOT SHARE OR REUPLOAD THIS CODE WITHOUT PERMISSION
#
# This code is permitted for use only by premium users of fastfame.pro.
# Unauthorized distribution is strictly prohibited.
# https://fastfame.pro

import requests

API_URL = "https://d0828c46-d3ae-45a9-8d86-2efa2c9a6e66-00-195g1wx50nwts.kirk.replit.dev/api/v1/tiktok/views"


class FastFameClient:
    def __init__(self, username: str, timeout: int = 30):
        if not username:
            raise ValueError("username is required")

        self.username = username
        self.timeout = timeout

    def send_views(self, video_url: str) -> dict:
        if not video_url:
            raise ValueError("video_url is required")

        payload = {
            "video_url": video_url,
            "username": self.username,
        }

        response = requests.post(
            API_URL,
            data=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        try:
            return response.json()
        except ValueError:
            return {"raw_response": response.text}

