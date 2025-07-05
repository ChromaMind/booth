import requests
import json

# === Configuration ===
# API_KEY = "your_api_key_here"
from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env into os.environ
API_KEY = os.environ.get("ASI1_API_KEY")
if not API_KEY:
    raise ValueError("Missing ASI1_API_KEY in environment variables")
BASE_URL = "https://api.asi1.ai/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# === Tool: Choose Trip Based on Mood ===
choose_trip_tool = {
    "type": "function",
    "function": {
        "name": "choose_trip",
        "description": "Selects a trip based on the user's mood.",
        "parameters": {
            "type": "object",
            "properties": {
                "mood": {
                    "type": "string",
                    "enum": ["stressed", "anxious", "sad", "happy", "energized", "tired", "angry", "neutral"]
                }
            },
            "required": ["mood"]
        }
    }
}

# === Trip Logic ===
def choose_trip(mood):
    trips = {
        "stressed": "Ocean Calm – Soothing blues, slow theta waves",
        "anxious": "Forest Focus – Green ambient lights, grounding beta-theta blend",
        "sad": "Sunrise Uplift – Warm orange glow, uplifting alpha waves",
        "happy": "Joy Ride – Vibrant rainbow pulses, gamma bursts",
        "energized": "Momentum – Fast red strobes, beta waves",
        "tired": "Power Nap – Soft purples, delta waves",
        "angry": "Cool Down – Icy blues, deep theta rhythms",
        "neutral": "Balance Mode – Gentle white lights, balanced alpha"
    }
    return trips.get(mood, "Balance Mode")

# === Initial Conversation ===
initial_message = [
    {
        "role": "system",
        "content": (
            "You are a wellness assistant built into smart sunglasses. "
            "You chat with the user and determine their mood. "
            "Then you recommend an audio-visual therapy 'trip' using LED lights and binaural beats "
            "to match or improve their emotional state."
        )
    },
    {
        "role": "user",
        "content": "I'm feeling a bit stressed and overwhelmed today."
    }
]

# === Step 1: Ask ASI1 Model to interpret user mood and suggest a trip ===
payload = {
    "model": "asi1-mini",
    "messages": initial_message,
    "tools": [choose_trip_tool],
    "temperature": 0.7,
    "max_tokens": 1024
}

response = requests.post(
    f"{BASE_URL}/chat/completions",
    headers=headers,
    json=payload
)

if response.status_code != 200:
    print("API call failed:", response.text)
    exit()

response_data = response.json()
message = response_data["choices"][0]["message"]

# === Step 2: If ASI1 used a tool to call "choose_trip" ===
if "tool_calls" in message:
    for tool_call in message["tool_calls"]:
        if tool_call["function"]["name"] == "choose_trip":
            args = json.loads(tool_call["function"]["arguments"])
            mood = args["mood"]
            trip_recommendation = choose_trip(mood)

            print(f"Detected mood: {mood}")
            print(f"Recommended trip: {trip_recommendation}")

            # === Optional: Send command to smart glasses device ===
            def start_trip(trip_name):
                # Stub function – replace with real device control logic
                print(f"Starting trip: {trip_name}")
                # e.g. send command via Bluetooth, Serial, etc.

            start_trip(trip_recommendation)
        else:
            print("No recognized tool call.")
else:
    # ASI1 didn't call the tool, fallback to default assistant message
    print("Assistant response:")
    print(message.get("content", "[No content]"))
