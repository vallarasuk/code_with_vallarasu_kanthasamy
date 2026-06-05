import os
from google import genai
import json

def get_available_models(client):
    """Dynamically fetches models that support content generation."""
    models = []
    try:
        for m in client.models.list():
            if hasattr(m, 'supported_actions') and m.supported_actions and 'generateContent' in m.supported_actions:
                # Prefer fast/cheap flash models
                if 'flash' in m.name.lower():
                    models.append(m.name)
    except Exception as e:
        print(f"Failed to fetch models from API: {e}")
        
    if not models:
        # Absolute fallback if API listing fails
        models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-flash-lite"]
        
    # Sort to prioritize newer models (e.g., gemini-2.5 before gemini-1.5)
    models.sort(reverse=True)
    return models

def generate_daily_tip():
    """Generates a daily coding tip using the Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    client = genai.Client(api_key=api_key)
    
    # Dynamically fetch available models
    available_models = get_available_models(client)
    
    prompt = """
    You are an expert software developer and social media marketer. Generate a practical coding trick or tip.
    The title MUST be a "curiosity hook" or clickbait-style sentence that makes people want to watch. 
    Examples of good titles: "Stop using if-else. Do this instead!", "99% of React devs make this mistake", "The secret trick senior devs use".
    
    Focus on popular languages like Python, JavaScript, TypeScript, or React.
    
    IMPORTANT: DO NOT use any emojis in the title or the code snippet. Our image rendering engine does not support emojis and they will render as broken square boxes.
    
    Return ONLY a JSON object with two keys:
    - "title": A curiosity-inducing hook (max 60 chars).
    - "code": The actual code snippet demonstrating the tip. It MUST be exactly between 10 and 15 lines long. If the tip is shorter, add meaningful context, usage examples, or comments to reach the minimum 10 lines.
    
    Do not include markdown backticks around the JSON.
    """
    
    # Try models one by one
    for model_name in available_models:
        try:
            print(f"Trying model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            clean_response = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(clean_response)
            return data.get("title", "Daily Coding Tip"), data.get("code", "print('Hello World')")
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue
            
    print("All models failed due to rate limits or API errors.")
    return "Daily Coding Tip", "print('Keep coding!')"

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    title, code = generate_daily_tip()
    print(f"Title: {title}\nCode:\n{code}")
