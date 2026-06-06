import os
from instagrapi import Client

def post_to_instagram(video_path, caption):
    """Uploads the video to Instagram using instagrapi."""
    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")
    
    if not username or not password:
        raise ValueError("Instagram credentials not set in environment variables.")
        
    print(f"Logging into Instagram as {username}...")
    cl = Client()
    
    # Login with session caching to prevent Challenge/Checkpoint errors
    session_file = "session.json"
    if os.path.exists(session_file):
        cl.load_settings(session_file)
    else:
        # Save generated device info BEFORE login so it matches the phone approval
        cl.dump_settings(session_file)
        
    try:
        cl.login(username, password)
        # Update session with cookies
        cl.dump_settings(session_file)
        print("Login successful.")
    except Exception as e:
        print(f"Failed to login: {e}")
        return False
        
    # Upload Reel
    try:
        print(f"Uploading {video_path}...")
        media = cl.clip_upload(
            video_path,
            caption=caption
        )
        print(f"Upload successful. Media ID: {media.pk}")
        return media.code
    except Exception as e:
        print(f"Failed to upload video: {e}")
        return None

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # Test (requires valid creds and a test video)
    # post_to_instagram("output.mp4", "Testing automated reel #coding #python")
