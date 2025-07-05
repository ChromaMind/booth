import requests
import json
import math

# === CONFIGURATION ===
from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env into os.environ
API_KEY = os.environ.get("ASI1_API_KEY")
if not API_KEY:
    raise ValueError("Missing ASI1_API_KEY in environment variables")


BASE_URL = "https://api.asi1.ai/v1"
MODEL = "asi1-mini"

COLUMNS = 8
ROWS = 4
FRAME_COUNT = 30  # Number of animation frames

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# === TOOLS ===
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
                },
            },
            "required": ["mood"]
        }
    }
}

# === USER INPUT ===
initial_message = [
    {
        "role": "system",
        "content": "You are a wellness assistant in LED sunglasses. When a user describes how they feel, you detect their mood and call choose_trip with it."
    },
    {
        "role": "user",
        "content": "I'm feeling really anxious today and need to calm down."
    }
]

# === API CALL ===
payload = {
    "model": MODEL,
    "messages": initial_message,
    "tools": [choose_trip_tool],
    "temperature": 0.7,
    "max_tokens": 1024
}

response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)

if response.status_code != 200:
    print("API call failed:", response.text)
    exit()

response_data = response.json()
message = response_data["choices"][0]["message"]

# === MOOD & TRIP EXTRACTION ===
def fallback_trip(mood):
    return {
        "stressed": "Ocean Calm",
        "anxious": "Forest Focus",
        "sad": "Sunrise Uplift",
        "happy": "Joy Ride",
        "energized": "Momentum",
        "tired": "Power Nap",
        "angry": "Cool Down",
        "neutral": "Balance Mode"
    }.get(mood, "Balance Mode")

if "tool_calls" in message:
    tool_args = json.loads(message["tool_calls"][0]["function"]["arguments"])
    mood = tool_args["mood"]
    trip = fallback_trip(mood)
    print(f"🧠 Mood: {mood}\n🎧 Trip: {trip}")
else:
    print("No tool call detected.")
    exit()

# === LED FRAME UTILITIES ===
def generate_led_matrix(columns, rows, r, g, b):
    return [[{"r": r, "g": g, "b": b} for _ in range(columns)] for _ in range(rows)]

def hsv_to_rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = int(v * (1 - s) * 255)
    q = int(v * (1 - f * s) * 255)
    t = int(v * (1 - (1 - f) * s) * 255)
    v = int(v * 255)
    if hi == 0: return v, t, p
    elif hi == 1: return q, v, p
    elif hi == 2: return p, v, t
    elif hi == 3: return p, q, v
    elif hi == 4: return t, p, v
    elif hi == 5: return v, p, q

# === ANIMATION FUNCTIONS ===
def ocean_calm(columns, rows, frames):
    anim = []
    for i in range(frames):
        val = int(100 + 80 * math.sin(i * 0.2))
        anim.append(generate_led_matrix(columns, rows, 0, 0, val))
    return anim

def forest_focus(columns, rows, frames):
    anim = []
    for i in range(frames):
        g = int(100 + 100 * math.sin(i * 0.15))
        anim.append(generate_led_matrix(columns, rows, 0, g, 0))
    return anim

def sunrise_uplift(columns, rows, frames):
    anim = []
    for i in range(frames):
        r = int((i / frames) * 255)
        g = int((i / frames) * 128)
        anim.append(generate_led_matrix(columns, rows, r, g, 0))
    return anim

def joy_ride(columns, rows, frames):
    anim = []
    for i in range(frames):
        hue = (i / frames) * 360
        frame = []
        for y in range(rows):
            row = []
            for x in range(columns):
                h = (hue + x * 15 + y * 10) % 360
                r, g, b = hsv_to_rgb(h, 1.0, 1.0)
                row.append({"r": r, "g": g, "b": b})
            frame.append(row)
        anim.append(frame)
    return anim

def momentum(columns, rows, frames):
    anim = []
    for i in range(frames):
        val = 255 if (i % 2 == 0) else 0
        anim.append(generate_led_matrix(columns, rows, val, 0, 0))
    return anim

def power_nap(columns, rows, frames):
    anim = []
    for i in range(frames):
        val = int(80 + 40 * math.sin(i * 0.1))
        anim.append(generate_led_matrix(columns, rows, val, val, val))
    return anim

def cool_down(columns, rows, frames):
    anim = []
    for i in range(frames):
        b = int(150 + 80 * math.sin(i * 0.2))
        anim.append(generate_led_matrix(columns, rows, 0, 0, b))
    return anim

def balance_mode(columns, rows, frames):
    anim = []
    for i in range(frames):
        r = int(100 + 50 * math.sin(i * 0.2))
        g = int(100 + 50 * math.sin(i * 0.2 + 2))
        b = int(100 + 50 * math.sin(i * 0.2 + 4))
        anim.append(generate_led_matrix(columns, rows, r, g, b))
    return anim

# === TRIP → ANIMATION ROUTER ===
def generate_animation(trip, columns, rows, frames):
    trip = trip.lower()
    if "ocean" in trip:
        return ocean_calm(columns, rows, frames)
    elif "forest" in trip:
        return forest_focus(columns, rows, frames)
    elif "sunrise" in trip:
        return sunrise_uplift(columns, rows, frames)
    elif "joy" in trip:
        return joy_ride(columns, rows, frames)
    elif "momentum" in trip:
        return momentum(columns, rows, frames)
    elif "nap" in trip:
        return power_nap(columns, rows, frames)
    elif "cool" in trip:
        return cool_down(columns, rows, frames)
    elif "balance" in trip:
        return balance_mode(columns, rows, frames)
    else:
        return balance_mode(columns, rows, frames)  # fallback

# === GENERATE & SAVE ===
animation = generate_animation(trip, COLUMNS, ROWS, FRAME_COUNT)

with open("trip_animation.json", "w") as f:
    json.dump(animation, f, indent=2)

print("✅ Saved LED frames to trip_animation.json")
