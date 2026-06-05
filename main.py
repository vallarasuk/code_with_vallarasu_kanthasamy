import os
import argparse
from datetime import datetime
from content_generator import generate_daily_tip
from video_generator import fetch_random_audio, generate_code_image, create_video
from instagram_poster import post_to_instagram
from dotenv import load_dotenv

def main():
    parser = argparse.ArgumentParser(description="Generate and post daily coding tips to Instagram.")
    parser.add_argument("--dry-run", action="store_true", help="Generate video but do not post to Instagram.")
    args = parser.parse_args()

    load_dotenv()
    
    print("--- Step 1: Generating Content ---")
    title, code = generate_daily_tip()
    print(f"Title: {title}")
    print(f"Code:\n{code}\n")
    
    print("--- Step 2: Fetching Audio ---")
    audio_path = fetch_random_audio("temp_audio.mp3")
    if not audio_path:
        print("Failed to fetch audio. Exiting.")
        return
        
    print("--- Step 3: Generating Code Image ---")
    image_path = generate_code_image(title, code, "temp_image.png")
    
    print("--- Step 4: Creating Video ---")
    video_path = create_video(image_path, audio_path, "output.mp4", target_duration=25)
    
    if not video_path or not os.path.exists(video_path):
        print("Failed to generate video. Exiting.")
        return
        
    print("--- Step 5: Posting to Instagram ---")
    date_str = datetime.now().strftime("%B %d, %Y")
    caption = f"{title}\n\n📅 {date_str}\nDaily coding tip! 💻✨\n\n#coding #programming #developer #python #javascript #tech #webdev #software #codewithvallarasukanthasamy"
    
    if args.dry_run:
        print(f"[DRY-RUN] Would post {video_path} to Instagram with caption:\n{caption}")
    else:
        success = post_to_instagram(video_path, caption)
        if success:
            print("Successfully posted to Instagram!")
        else:
            print("Failed to post to Instagram.")
            
    # Cleanup temporary files
    for temp_file in [audio_path, image_path]:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"Cleaned up {temp_file}")

if __name__ == "__main__":
    main()
