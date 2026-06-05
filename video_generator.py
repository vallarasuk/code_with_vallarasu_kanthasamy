import os
import json
import textwrap
import random
from datetime import datetime
import requests
import gdown
import PIL
from PIL import Image, ImageDraw, ImageFont

if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

import subprocess
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import ImageFormatter


def fetch_random_audio(output_path="temp_audio.mp3"):
    """Fetches a random audio file from the provided JSON endpoint."""
    url = "https://audio.vallarasuk.com/audio.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        audio_ids = data.get("arr", [])

        if not audio_ids:
            raise ValueError("No audio IDs found in JSON.")

        random_id = random.choice(audio_ids)
        print(f"Selected audio ID: {random_id}")

        download_url = f"https://drive.google.com/uc?id={random_id}"
        gdown.download(download_url, output_path, quiet=False)
        return output_path
    except Exception as e:
        print(f"Error fetching audio: {e}")
        return None


def generate_code_image(title, code, output_path="temp_image.png"):
    """Generates an IDE-like image with the provided code snippet."""
    # 1. Generate highlighted code image using Pygments
    try:
        lexer = guess_lexer(code)
    except Exception:
        from pygments.lexers import PythonLexer

        lexer = PythonLexer()

    formatter = ImageFormatter(
        style="monokai",
        font_size=24,
        line_numbers=True,
        line_number_bg="#1e1e1e",
        line_number_fg="#858585",
        line_number_chars=4,
        background_color="#1e1e1e",
        padding=40,
    )

    code_img_data = highlight(code, lexer, formatter)
    with open("raw_code.png", "wb") as f:
        f.write(code_img_data)

    code_img = Image.open("raw_code.png").convert("RGBA")

    # 2. Create the Instagram Reel canvas (1080x1920) - Rich Gradient Background
    canvas = Image.new("RGBA", (1080, 1920))
    draw = ImageDraw.Draw(canvas)
    
    # Draw dark modern gradient
    for y in range(1920):
        r = int(20 - (15 * (y / 1920)))
        g = int(20 - (10 * (y / 1920)))
        b = int(30 + (25 * (y / 1920)))
        draw.line([(0, y), (1080, y)], fill=(r, g, b, 255))
    
    # Load fonts
    try:
        font_large = ImageFont.truetype("arial.ttf", 60)
        font_medium = ImageFont.truetype("arial.ttf", 45)
        font_small = ImageFont.truetype("arial.ttf", 35)
    except IOError:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw Date stamp at the top
    date_str = datetime.now().strftime("%B %d, %Y")
    date_text = f"📅 {date_str}"
    date_bbox = draw.textbbox((0, 0), date_text, font=font_small)
    date_w = date_bbox[2] - date_bbox[0]
    draw.text(((1080 - date_w) // 2, 80), date_text, font=font_small, fill=(150, 150, 150, 255))

    # Draw Wrapped Title
    lines = textwrap.wrap(title, width=32)
    text_y = 150
    for line in lines:
        text_bbox = draw.textbbox((0, 0), line, font=font_large)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        draw.text(((1080 - text_w) // 2, text_y), line, font=font_large, fill=(255, 255, 255, 255))
        text_y += text_h + 15

    # 3. Create IDE Window background and paste code image
    # Scale code image if it's too wide
    max_w = 980
    if code_img.width > max_w:
        ratio = max_w / float(code_img.width)
        new_h = int(float(code_img.height) * float(ratio))
        code_img = code_img.resize((max_w, new_h), Image.Resampling.LANCZOS)

    # Calculate position to center the IDE window
    x_offset = (1080 - code_img.width) // 2
    y_offset = (1920 - code_img.height) // 2

    # IDE Window Frame
    padding = 20
    draw.rectangle(
        [
            x_offset - padding,
            y_offset - padding - 40,
            x_offset + code_img.width + padding,
            y_offset + code_img.height + padding,
        ],
        fill="#1e1e1e",
        outline="#444444",
        width=4,
    )
    # macOS-like window buttons
    draw.ellipse(
        [x_offset, y_offset - 40 + 10, x_offset + 15, y_offset - 40 + 25],
        fill="#ff5f56",
    )
    draw.ellipse(
        [x_offset + 25, y_offset - 40 + 10, x_offset + 40, y_offset - 40 + 25],
        fill="#ffbd2e",
    )
    draw.ellipse(
        [x_offset + 50, y_offset - 40 + 10, x_offset + 65, y_offset - 40 + 25],
        fill="#27c93f",
    )

    canvas.paste(code_img, (x_offset, y_offset), code_img)
    
    # Add Social Handle and Call to Action at the bottom
    handle_text = "@code_with_vallarasu_kanthasamy"
    handle_bbox = draw.textbbox((0, 0), handle_text, font=font_medium)
    handle_w = handle_bbox[2] - handle_bbox[0]
    draw.text(((1080 - handle_w) // 2, 1700), handle_text, font=font_medium, fill=(200, 200, 200, 255))
    
    save_text = "💾 Save & Follow for more!"
    save_bbox = draw.textbbox((0, 0), save_text, font=font_small)
    save_w = save_bbox[2] - save_bbox[0]
    draw.text(((1080 - save_w) // 2, 1770), save_text, font=font_small, fill=(255, 215, 0, 255))

    if output_path.lower().endswith(".jpg") or output_path.lower().endswith(".jpeg"):
        canvas.convert("RGB").save(output_path)
    else:
        canvas.save(output_path)
        
    if os.path.exists("raw_code.png"):
        os.remove("raw_code.png")
    return output_path


def create_video(image_path, audio_path, output_path="output.mp4", target_duration=25):
    """Combines the image and audio into a video using FFmpeg directly."""
    print("Generating video with FFmpeg...")
    
    try:
        # ffmpeg command for zooming and audio muxing
        # Fix for unplayable video (PTS timestamp bug): Use -loop 1 with framerate 24 on input,
        # and set zoompan d=1 so it processes 1 output frame per input frame continuously!
        cmd = [
            "ffmpeg",
            "-y", # overwrite output
            "-loop", "1",
            "-framerate", "24",
            "-i", image_path,
            "-i", audio_path,
            "-filter_complex", "[0:v]scale=1080:1920,zoompan=z='min(zoom+0.00015,1.1)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=24,format=yuv420p[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            "-shortest",
            "-t", str(target_duration),
            output_path
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print(f"Video saved to {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Failed to create video with FFmpeg: {e}")
        return None


if __name__ == "__main__":
    # Test execution
    audio = fetch_random_audio()
    if audio:
        img = generate_code_image(
            "How to print Hello World", "print('Hello World')\n# This is a comment"
        )
        create_video(img, audio)
