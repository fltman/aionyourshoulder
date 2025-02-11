import pyautogui
import base64
import requests
import time
from io import BytesIO
import os
from dotenv import load_dotenv
import pygame
import datetime
from PIL import Image
from openai import OpenAI

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = "NfUrCNRReUL9RXS9upG1"  # Josh voice ID

def take_screenshot():
    """Capture screenshot and convert to base64"""
    try:
        # For macOS, use screencapture command
        import subprocess
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshots_dir = 'screenshots'
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
            
        screenshot_path = os.path.join(screenshots_dir, f'screenshot_{timestamp}.png')
        
        # Use screencapture command
        subprocess.run(['screencapture', '-x', screenshot_path], check=True)
        
        # Open the saved screenshot
        im = Image.open(screenshot_path)
        
    except (ImportError, subprocess.SubprocessError):
        # Fallback to pyautogui for other operating systems
        im = pyautogui.screenshot()
        
        # Save the screenshot
        screenshots_dir = 'screenshots'
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(screenshots_dir, f'screenshot_{timestamp}.png')
        im.save(screenshot_path)
    
    print(f"Screenshot saved to: {screenshot_path}")
    
    # Convert to base64
    buffered = BytesIO()
    im.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_image(base64_image):
    """Send image to GPT-4V for analysis"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Look at the content I provide (this could be code, text, images, or screenshots) and give me immediate feedback. Keep it casual and direct — no formalities or long explanations unless something's really off. If everything looks good, just encourage me and acknowledge my progress. If you notice anything that can be improved or needs attention, point it out briefly and give me a suggestion. Make sure the feedback is focused on what's immediately visible on the screen, and avoid going into unnecessary details unless needed. no labels, no bulletpoints, you are just a college sitting beside me. keep it short and conciese. The only problem is, you are a slightly drunk scottosh mideval mad sourcerer with a heavy accent as picked out of any monty python movie..."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this screenshot and provide feedback."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )
    
    print(response.choices[0].message)
    return response.choices[0].message.content

def speak_feedback(text):
    """Convert text to speech using ElevenLabs and play it"""
    eleven_labs_url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_flash_v2_5",
        "voice_settings": {
            "stability": 0.3,
            "similarity_boost": 0.95,
            "style": 0.47,
            "use_speaker_boost": True
        }
    }

    response = requests.post(eleven_labs_url, json=data, headers=headers)

    if response.status_code != 200:
        raise Exception(f"ElevenLabs API error: {response.text}")

    # Save audio to a temporary file
    temp_dir = 'temp_audio'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_audio_path = os.path.join(temp_dir, f'voice_{timestamp}.mp3')
    
    with open(temp_audio_path, 'wb') as f:
        f.write(response.content)

    # Play the audio using pygame
    pygame.mixer.init()
    pygame.mixer.music.load(temp_audio_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Clean up old audio files
    try:
        files = os.listdir(temp_dir)
        if len(files) > 5:  # Keep only the 5 most recent files
            files.sort()
            for old_file in files[:-5]:
                os.remove(os.path.join(temp_dir, old_file))
    except Exception as e:
        print(f"Error cleaning up audio files: {e}")

def cleanup_old_files(directory, keep_count=5):
    """Clean up old files, keeping only the most recent ones"""
    try:
        files = os.listdir(directory)
        if len(files) > keep_count:
            files.sort()
            for old_file in files[:-keep_count]:
                os.remove(os.path.join(directory, old_file))
    except Exception as e:
        print(f"Error cleaning up files in {directory}: {e}")

def main():
    print("Taking screenshots every 30 seconds. Press Ctrl+C to exit")
    try:
        while True:
            # Take screenshot
            print("\nTaking screenshot...")
            base64_image = take_screenshot()
            
            # Analyze with GPT-4V
            print("Analyzing screenshot...")
            feedback = analyze_image(base64_image)
            print(f"Feedback: {feedback}")
            
            # Speak feedback
            print("Speaking feedback...")
            speak_feedback(feedback)
            
            # Wait 30 seconds before next screenshot
            print("\nWaiting 30 seconds...")
            time.sleep(2)
            
            # Clean up old screenshots and audio files
            cleanup_old_files('screenshots')
            cleanup_old_files('temp_audio')
            
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main() 