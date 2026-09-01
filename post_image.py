import os
import argparse
from instagrapi import Client
from content_generator import generate_daily_tip
from video_generator import generate_code_image
from datetime import datetime

def post_image_to_instagram(image_path, caption):
    """Uploads the image to Instagram using instagrapi."""
    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")
    
    if not username or not password:
        raise ValueError("Instagram credentials not set in environment variables.")
        
    print(f"Logging into Instagram as {username}...")
    cl = Client()
    
    # Session caching prevents Instagram from flagging new devices
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
        
    try:
        print(f"Uploading {image_path}...")
        media = cl.photo_upload(
            image_path,
            caption=caption
        )
        print(f"Upload successful. Media ID: {media.pk}")
        return media.code
    except Exception as e:
        print(f"Failed to upload image: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Generate and post a code tip image to Instagram.")
    parser.add_argument("--dry-run", action="store_true", help="Generate the image but don't post to Instagram")
    args = parser.parse_args()

    print("--- Step 1: Generating Content ---")
    title, code, hashtags = generate_daily_tip()
    
    if not title or not code:
        print("Failed to generate content. Exiting.")
        return
        
    print("--- Step 2: Generating Code Image ---")
    # Must save as .jpg because Instagram/instagrapi requires it for photo_upload
    image_path = generate_code_image(title, code, "output_image.jpg")
    
    if not image_path or not os.path.exists(image_path):
        print("Failed to generate image. Exiting.")
        return
        
    print("--- Step 3: Posting to Instagram ---")
    date_str = datetime.now().strftime("%B %d, %Y")
    
    author_info = """👨‍💻 Vallarasu Kanthasamy
🌐 Portfolio: vallarasuk.in
💻 GitHub: github.vallarasuk.in
🤝 LinkedIn: linkedin.vallarasuk.in
💬 WhatsApp Community: squad.vallarasuk.in"""

    caption = f"📌 Save this trick for your next project!\n\n{title}\n\n📅 {date_str}\nDaily coding tip! 💻✨\n\n{author_info}\n\n{hashtags} #codewithvallarasukanthasamy"
    
    if args.dry_run:
        print(f"[DRY-RUN] Would post {image_path} to Instagram with caption:\n{caption}")
    else:
        post_code = post_image_to_instagram(image_path, caption)
        if post_code:
            post_url = f"https://www.instagram.com/p/{post_code}/"
            print(f"Successfully posted image to Instagram! Link: {post_url}")
            # Write result for GitHub Actions email
            with open("post_result.txt", "w") as f:
                f.write(f"Title: {title}\nLink: {post_url}\n")
        else:
            print("Failed to post image to Instagram.")
            # Write failure for GitHub Actions email
            with open("post_result.txt", "w") as f:
                f.write(f"Failed to post image to Instagram.\nTitle: {title}\n")
            
    # Clean up (optional)
    # if os.path.exists(image_path):
    #     os.remove(image_path)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
