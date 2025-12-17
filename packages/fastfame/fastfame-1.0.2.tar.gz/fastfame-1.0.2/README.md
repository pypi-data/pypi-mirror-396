FastFame Python Client Documentation
Overview

FastFame is a Python client for interacting with the FastFame TikTok Views API.
It allows premium users to programmatically send views to TikTok videos via their FastFame account.

Package Name: fastfame

Installation: pip install fastfame

Author: REAPXR

Official Website: https://fastfame.pro

Note: This package is intended only for premium FastFame users. Unauthorized use is prohibited.

Installation

Install via pip:

pip install fastfame


Ensure you are using Python 3.8 or newer.

Usage
1. Using FastFame as a Python Library
from fastfame import FastFameClient

# Create a client instance with your username
client = FastFameClient(username="your_fastfame_username")

# Send views to a TikTok video
video_url = "https://www.tiktok.com/@user/video/1234567890"
response = client.send_views(video_url)

# Print API response
print(response)


EXAMPLE CODE
```
from fastfame import FastFameClient

def demo_library_usage():
    # Replace with your FastFame username - https://fastfame.pro
    username = "your-username"
    
    # Example TikTok video URL
    video_url = "https://www.tiktok.com/@example/video/1234567890"
    
    # Create the FastFame client
    client = FastFameClient(username=username)
    
    # Send views (mocked response for demonstration)
    try:
        response = client.send_views(video_url)
        print("Library Usage Response:")
        print(response)
    except Exception as e:
        print("Error sending views:", e)
demo_library_usage()
```


Parameters:

username (str): Your FastFame account username (required)

video_url (str): The TikTok video URL to which you want to send views (required)

Returns:

dict: The response from the FastFame API. If the response is not JSON, returns a dictionary with raw_response.

2. Using FastFame via CLI

You can also use FastFame from the command line.

python -m fastfame --username your_username --url https://www.tiktok.com/@user/video/1234567890


Arguments:

--username: Your FastFame account username

--url: TikTok video URL

The command will print the API response in your terminal.

3. Example CLI Output
{
  "status": "success",
  "message": "Views sent successfully",
  "video_url": "https://www.tiktok.com/@user/video/1234567890",
  "views_added": 100
}

Error Handling

The client will raise errors in the following cases:

Missing username or video URL:

ValueError: "username is required"
ValueError: "video_url is required"


API request failures:

Network issues → requests.exceptions.RequestException

Non-JSON response → returns {"raw_response": "..."}

Best Practices

Always use your own username; do not hardcode another account.

Allow time for API requests to complete — responses may take a few seconds.

Make sure your TikTok video URL is valid and public.

Respect the FastFame Terms of Service and do not share this client.

Development / Contribution

If you want to contribute:

git clone https://github.com/REAPXR666/fastfame.git
cd fastfame
pip install -e .


This will install the package in editable mode for testing.

Support

For questions, bugs, or premium access:

https://fastfame.pro

Email: support@fastfame.pro

