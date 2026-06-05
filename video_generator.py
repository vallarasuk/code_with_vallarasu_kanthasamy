import os
import json
import textwrap
import random
from datetime import datetime
import requests
import gdown
import PIL
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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
        font_size=50,
        line_numbers=True,
        line_number_bg="#161b22",
        line_number_fg="#858585",
        line_number_chars=4,
        background_color="#161b22",
        padding=40,
    )

    code_img_data = highlight(code, lexer, formatter)
    with open("raw_code.png", "wb") as f:
        f.write(code_img_data)

    code_img = Image.open("raw_code.png").convert("RGBA")

    # 2. Create the Instagram Post canvas (1080x1350) - Rich Gradient Background
    WIDTH, HEIGHT = 1080, 1350
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), "#0d1117")
    
    # Create a nice mesh/radial-like glow in the background
    bg_layer = Image.new("RGBA", (WIDTH, HEIGHT), (13, 17, 23, 255))
    bg_draw = ImageDraw.Draw(bg_layer)
    bg_draw.ellipse((-300, -300, 800, 800), fill=(40, 20, 80, 100))
    bg_draw.ellipse((600, 800, 1500, 1700), fill=(20, 60, 80, 100))
    bg_layer = bg_layer.filter(ImageFilter.GaussianBlur(150))
    canvas = Image.alpha_composite(canvas, bg_layer)
    draw = ImageDraw.Draw(canvas)
    
    # Load fonts
    base_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        font_large = ImageFont.truetype(os.path.join(base_dir, "fonts", "Z003-MediumItalic.otf"), 75)
    except IOError:
        font_large = ImageFont.load_default()
        
    try:
        font_medium = ImageFont.truetype(os.path.join(base_dir, "fonts", "ClickerScript-Regular.ttf"), 60)
    except IOError:
        font_medium = ImageFont.load_default()
        
    try:
        font_small = ImageFont.truetype(os.path.join(base_dir, "fonts", "NotoSans-Regular.ttf"), 35)
    except IOError:
        font_small = ImageFont.load_default()

    # Draw Date stamp at the top
    date_str = datetime.now().strftime("%B %d, %Y")
    date_text = f"• {date_str} •"
    date_bbox = draw.textbbox((0, 0), date_text, font=font_small)
    date_w = date_bbox[2] - date_bbox[0]
    draw.text(((WIDTH - date_w) // 2, 80), date_text, font=font_small, fill=(150, 180, 200, 255))

    # Draw Wrapped Title
    lines = textwrap.wrap(title, width=30)
    text_y = 150
    for line in lines:
        text_bbox = draw.textbbox((0, 0), line, font=font_large)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        draw.text(((WIDTH - text_w) // 2, text_y), line, font=font_large, fill=(255, 255, 255, 255))
        text_y += text_h + 15

    # 3. Create IDE Window background and paste code image
    # Scale code image if it's too wide or too small
    max_w = 980
    if code_img.width > max_w:
        ratio = max_w / float(code_img.width)
        new_h = int(float(code_img.height) * float(ratio))
        code_img = code_img.resize((max_w, new_h), Image.Resampling.LANCZOS)
    elif code_img.width < 800:
        ratio = 800 / float(code_img.width)
        new_h = int(float(code_img.height) * float(ratio))
        code_img = code_img.resize((800, new_h), Image.Resampling.LANCZOS)

    # Calculate position to center the IDE window
    x_offset = (WIDTH - code_img.width) // 2
    y_offset = (HEIGHT - code_img.height) // 2

    # IDE Window Frame
    padding = 30
    header_height = 50
    rect_coords = [
        x_offset - padding,
        y_offset - padding - header_height,
        x_offset + code_img.width + padding,
        y_offset + code_img.height + padding,
    ]
    
    # Drop Shadow
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_offset = 25
    shadow_draw.rounded_rectangle(
        [r + shadow_offset for r in rect_coords],
        radius=25,
        fill=(0, 0, 0, 150)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))
    canvas = Image.alpha_composite(canvas, shadow)
    draw = ImageDraw.Draw(canvas) # re-init draw after composite

    # IDE Window Frame (Rounded)
    draw.rounded_rectangle(
        rect_coords,
        radius=25,
        fill="#161b22",
        outline="#30363d",
        width=3,
    )
    
    # macOS-like window buttons
    btn_y = y_offset - padding - header_height + 25
    btn_x = x_offset - padding + 25
    draw.ellipse([btn_x, btn_y, btn_x + 15, btn_y + 15], fill="#ff5f56")
    draw.ellipse([btn_x + 25, btn_y, btn_x + 40, btn_y + 15], fill="#ffbd2e")
    draw.ellipse([btn_x + 50, btn_y, btn_x + 65, btn_y + 15], fill="#27c93f")

    canvas.paste(code_img, (x_offset, y_offset), code_img)
    
    # Add Social Handle and Call to Action at the bottom
    handle_text = "@code_with_vallarasu_kanthasamy"
    handle_bbox = draw.textbbox((0, 0), handle_text, font=font_medium)
    handle_w = handle_bbox[2] - handle_bbox[0]
    draw.text(((WIDTH - handle_w) // 2, HEIGHT - 180), handle_text, font=font_medium, fill=(200, 200, 200, 255))
    
    save_text = "• Save & Follow for more! •"
    save_bbox = draw.textbbox((0, 0), save_text, font=font_small)
    save_w = save_bbox[2] - save_bbox[0]
    draw.text(((WIDTH - save_w) // 2, HEIGHT - 100), save_text, font=font_small, fill=(255, 215, 0, 255))

    if output_path.lower().endswith(".jpg") or output_path.lower().endswith(".jpeg"):
        canvas.convert("RGB").save(output_path, quality=100, subsampling=0)
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
            "-filter_complex", "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,zoompan=z='min(zoom+0.00015,1.1)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=24,format=yuv420p[v]",
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
