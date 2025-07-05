import os
import requests
import json
import base64

BASE_URL = "https://api.asi1.ai/v1"
API_KEY = os.getenv("ASI1_API_KEY")  # Make sure to set this in your environment

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def audio_to_base64(audio_path):
    with open(audio_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def stream_led_frames(audio_path):
    # Convert audio file to base64 to send in message
    audio_b64 = audio_to_base64(audio_path)

    system_message = {
        "role": "system",
        "content": (
            "You are a smart LED controller. "
            "Given a base64-encoded audio track, generate a sequence of LED frames chunk by chunk. "
            "Each frame is a 2D matrix representing LED colors as RGB values from 0 to 255. "
            "Stream the frames as JSON objects incrementally in this format: "
            "{\"frame_index\": <int>, \"frame\": [[{\"r\":0,\"g\":0,\"b\":0}, ...], ...]} "
            "Stop when the entire track is covered."
        )
    }

    user_message = {
        "role": "user",
        "content": f"Audio data (base64): {audio_b64}"
    }

    payload = {
        "model": "asi1-mini",
        "messages": [system_message, user_message],
        "temperature": 0.7,
        "max_tokens": 2048,
        "stream": True  # Enable streaming to receive chunked frames
    }

    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=HEADERS,
        json=payload,
        stream=True
    )

    frames = []
    print("Receiving frames...")

    try:
        for line in response.iter_lines():
            if line:
                # Each line is expected to be a JSON chunk with frames info
                decoded_line = line.decode('utf-8')
                # Usually ASI1 streams JSON objects line by line
                try:
                    data = json.loads(decoded_line)
                    # Example of expected data:
                    # {"frame_index": 0, "frame": [[{"r":10,"g":20,"b":30}, ...], ...]}
                    if "frame_index" in data and "frame" in data:
                        print(f"Received frame {data['frame_index']}")
                        frames.append(data)
                    else:
                        print("Received unknown chunk:", data)
                except json.JSONDecodeError:
                    print("Non-JSON chunk:", decoded_line)
    except Exception as e:
        print(f"Error reading stream: {e}")

    print(f"Total frames received: {len(frames)}")
    return frames


if __name__ == "__main__":
    audio_file = "audio.mp3"  # Replace with your audio path
    led_frames = stream_led_frames(audio_file)
    # Here you can save frames or feed them to your Qt app for display
