import requests
from groq import Groq
import time

# Initialize Groq client with hardcoded API key
groq_client = Groq(api_key="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")

# Fetch screen data from Screenpipe
def capture_screen_data():
    try:
        response = requests.get("http://localhost:3030/search?q=&limit=1&content_type=ocr", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"Raw Screenpipe response: {data}")  # Debug: see full response
        if data.get("data") and len(data["data"]) > 0:
            return data["data"][0]["content"].get("text", "No text found on screen")
        return "No data returned"
    except requests.RequestException as e:
        return f"Error fetching screen data: {e}"

# Process screen data with Groq and get suggestions
def process_with_groq(screen_data):
    prompt = f"""
    Analyze the following screen content and provide a smart productivity suggestion:
    "{screen_data}"
    """
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            max_tokens=100
        )
        print(f"Raw Groq response: {response}")  # Debug: see full response
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq error: {e}")  # Debug: log the exact error
        return f"Error processing with Groq: {e}"

# Main loop
def task_buddy():
    print("TaskBuddy is running. Monitoring your screen...")
    while True:
        # Capture screen data
        screen_content = capture_screen_data()
        print(f"Screen content: {screen_content}")
        
        # Process with Groq and get suggestion
        suggestion = process_with_groq(screen_content)
        print(f"TaskBuddy suggests: {suggestion}")
        
        # Wait before next check (e.g., every 30 seconds)
        time.sleep(30)

if __name__ == "__main__":
    task_buddy()