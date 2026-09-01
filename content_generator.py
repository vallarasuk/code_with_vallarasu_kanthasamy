import os
from google import genai
import json

def get_available_models(client):
    """Dynamically fetches models that support content generation."""
    pro_models = []
    flash_models = []
    try:
        for m in client.models.list():
            if hasattr(m, 'supported_actions') and m.supported_actions and 'generateContent' in m.supported_actions:
                name = m.name.lower()
                # Filter out specialized, audio/image, or internal preview models
                if any(x in name for x in ['vision', 'tts', 'image', 'customtools', 'lyria', 'banana', 'deep-research']):
                    continue
                
                # Since you have a Pro account, we prioritize Pro models first
                if 'pro' in name:
                    pro_models.append(m.name)
                elif 'flash' in name:
                    flash_models.append(m.name)
    except Exception as e:
        print(f"Failed to fetch models from API: {e}")
        
    pro_models.sort(reverse=True)
    flash_models.sort(reverse=True)
    
    models = pro_models + flash_models
    
    if not models:
        # Absolute fallback if API listing fails
        models = ["gemini-2.5-pro", "gemini-2.0-pro", "gemini-2.5-flash", "gemini-2.0-flash"]
        
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
    You are an expert software engineer and tech educator. Generate a highly practical, advanced, or intermediate coding trick that provides real value to developers.
    Avoid basic concepts. Focus on real-world scenarios, performance optimizations, clean code patterns, or hidden language features.
    Examples of good topics: React custom hooks, TypeScript utility types, Python decorators, or clever JavaScript methods.
    
    The title MUST be an engaging "curiosity hook" that makes people want to read. 
    Examples: "Stop using if-else. Use this pattern!", "The TS trick senior devs use", "Why your React app is slow".
    
    Focus on popular technologies: Python, JavaScript, TypeScript, or React.
    If possible, show a brief "Bad" vs "Good" approach in the code.
    
    IMPORTANT: DO NOT use any emojis in the title or the code snippet. Our image rendering engine does not support emojis and they will render as broken square boxes.
    
    Return ONLY a JSON object with three keys:
    - "title": A curiosity-inducing hook (max 60 chars).
    - "code": The actual code snippet demonstrating the tip. It MUST be exactly between 10 and 15 lines long. To fit on mobile screens, NEVER exceed 45 characters per line! Wrap lines if needed.
    - "hashtags": A string of 5-8 highly relevant hashtags based specifically on the language/framework used (e.g. "#python #reactjs #cleancode").
    
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
            default_hashtags = "#coding #programming #developer #tech #codewithvallarasukanthasamy"
            return data.get("title", "Daily Coding Tip"), data.get("code", "print('Hello World')"), data.get("hashtags", default_hashtags)
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue
            
    print("All models failed due to rate limits or API errors.")
    return "Daily Coding Tip", "print('Keep coding!')", "#coding #programming #developer"

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    title, code = generate_daily_tip()
    print(f"Title: {title}\nCode:\n{code}")
