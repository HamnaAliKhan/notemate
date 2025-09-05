import os
import sys
import tempfile
import subprocess
import whisper
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv('apikey.env')

# --- CONFIG ---
MODEL_NAME = "base"
CACHE_DIR = r"D:\whisper_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Gemini configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("⚠️ Warning: GEMINI_API_KEY not found in environment variables")
else:
    print("✅ Gemini API key loaded successfully")
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Update yt-dlp to latest version to avoid 403 errors
def update_yt_dlp():
    """Update yt-dlp to the latest version"""
    try:
        print("🔄 Updating yt-dlp to latest version...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], 
                      capture_output=True, text=True, check=True)
        print("✅ yt-dlp updated successfully!")
    except Exception as e:
        print(f"⚠️ Failed to update yt-dlp: {e}")

# Try to update yt-dlp
update_yt_dlp()

# Function to check if Chrome cookies are available
def check_chrome_cookies():
    """Check if Chrome cookies are available for YouTube"""
    try:
        # Try to get cookies from Chrome
        result = subprocess.run([
            "yt-dlp", "--cookies-from-browser", "chrome", "--print", "cookies", "https://www.youtube.com"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "youtube.com" in result.stdout:
            print("✅ Chrome cookies found for YouTube")
            return True
        else:
            print("⚠️ No Chrome cookies found for YouTube")
            return False
    except Exception as e:
        print(f"⚠️ Could not check Chrome cookies: {e}")
        return False

# Check cookies availability
check_chrome_cookies()

print(f"Loading Whisper model '{MODEL_NAME}'...")
model = whisper.load_model(MODEL_NAME, download_root=CACHE_DIR)
print("✅ Whisper model loaded!")

# --- Flask App ---
app = Flask(__name__)
CORS(app)

def format_timestamp(seconds: float) -> str:
    """Convert seconds to H:MM:SS format."""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def download_audio(youtube_url, temp_dir=None):
    """Download YouTube audio as MP3 using yt-dlp with enhanced headers to bypass 403."""
    # Create temp_audio directory if it doesn't exist
    temp_audio_dir = "temp_audio"
    os.makedirs(temp_audio_dir, exist_ok=True)
    
    # Generate a unique filename based on timestamp
    import time
    import urllib.parse
    timestamp = int(time.time())
    output_file = os.path.join(temp_audio_dir, f"audio_{timestamp}.%(ext)s")
    
    # Decode URL to fix encoding issues
    try:
        youtube_url = urllib.parse.unquote(youtube_url)
    except:
        pass
    
    # Use the full URL without stripping
    print(f"🔍 Processing full URL: {youtube_url}")

    # Method 1: Try with Chrome cookies and comprehensive headers
    cmd = [
        "yt-dlp",
        "-f", "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "--keep-video",  # Keep original file as backup
        "--output", output_file,
        "--no-playlist",
        "--cookies-from-browser", "chrome",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "--referer", "https://www.youtube.com/",
        "--add-header", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "--add-header", "Accept-Language: en-US,en;q=0.9",
        "--add-header", "Accept-Encoding: gzip, deflate, br",
        "--add-header", "DNT: 1",
        "--add-header", "Connection: keep-alive",
        "--add-header", "Sec-Fetch-Dest: document",
        "--add-header", "Sec-Fetch-Mode: navigate",
        "--add-header", "Sec-Fetch-Site: none",
        "--add-header", "Sec-Fetch-User: ?1",
        "--add-header", "Upgrade-Insecure-Requests: 1",
        "--add-header", "sec-ch-ua: \"Not A(Brand\";v=\"99\", \"Google Chrome\";v=\"121\", \"Chromium\";v=\"121\"",
        "--add-header", "sec-ch-ua-mobile: ?0",
        "--add-header", "sec-ch-ua-platform: \"Windows\"",
        "--no-check-certificates",
        "--no-cache-dir",
        "--extractor-args", "youtube:player_client=web",
        "--extractor-args", "youtube:player_skip=hls,dash"
    ]
    cmd.append(youtube_url)

    try:
        print(f"🔍 Attempting to download: {youtube_url}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ yt-dlp output:", result.stdout)
        
        # Wait a moment for file system operations to complete
        import time
        time.sleep(1)
        
        # Check what files exist in temp_audio directory
        print(f"🔍 Files in temp_audio directory: {os.listdir(temp_audio_dir)}")
        
        # Find the downloaded MP3 in temp_audio directory
        mp3_files = [f for f in os.listdir(temp_audio_dir) if f.endswith(".mp3")]
        if mp3_files:
            mp3_file = os.path.join(temp_audio_dir, mp3_files[0])
            print(f"✅ Found MP3 file: {mp3_file}")
            return mp3_file
        else:
            print("❌ No MP3 files found after conversion")
            # Fallback: try to find any audio file (m4a, webm, etc.)
            audio_files = [f for f in os.listdir(temp_audio_dir) if f.endswith(('.m4a', '.webm', '.wav', '.flac'))]
            if audio_files:
                audio_file = os.path.join(temp_audio_dir, audio_files[0])
                print(f"⚠️ Using fallback audio file: {audio_file}")
                return audio_file
            else:
                print("❌ No audio files found at all")
                return None
    except subprocess.CalledProcessError as e:
        print("❌ yt-dlp failed:", e.stderr)
        print("🔧 Trying alternative method...")
        
        # Method 2: Try with Firefox cookies
        try:
            print("🔧 Trying Method 2: Firefox cookies...")
            cmd_alt = [
                "yt-dlp",
                "-f", "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
                "--extract-audio",
                "--audio-format", "mp3",
                "--output", output_file,
                "--no-playlist",
                "--cookies-from-browser", "firefox",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
                "--referer", "https://www.youtube.com/",
                "--add-header", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "--add-header", "Accept-Language: en-US,en;q=0.5",
                "--add-header", "Accept-Encoding: gzip, deflate",
                "--add-header", "Connection: keep-alive",
                "--add-header", "Upgrade-Insecure-Requests: 1",
                "--no-check-certificates",
                "--no-cache-dir",
                "--extractor-args", "youtube:player_client=web",
                "--extractor-args", "youtube:player_skip=hls,dash"
            ]
            cmd_alt.append(youtube_url)
            
            result_alt = subprocess.run(cmd_alt, capture_output=True, text=True, check=True)
            print("✅ Method 2 succeeded:", result_alt.stdout)
            
            for file in os.listdir(temp_audio_dir):
                if file.endswith(".mp3"):
                    return os.path.join(temp_audio_dir, file)
            return None
        except subprocess.CalledProcessError as e2:
            print("❌ Method 2 failed:", e2.stderr)
            
            # Method 3: Try with mobile client
            try:
                print("🔧 Trying Method 3: Mobile client...")
                cmd_alt2 = [
                    "yt-dlp",
                    "-f", "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "--output", output_file,
                    "--no-playlist",
                    "--user-agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    "--referer", "https://m.youtube.com/",
                    "--add-header", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "--add-header", "Accept-Language: en-US,en;q=0.5",
                    "--add-header", "Accept-Encoding: gzip, deflate",
                    "--add-header", "Connection: keep-alive",
                    "--add-header", "Upgrade-Insecure-Requests: 1",
                    "--no-check-certificates",
                    "--no-cache-dir",
                    "--extractor-args", "youtube:player_client=android",
                    "--extractor-args", "youtube:player_skip=hls,dash",
                    "--extractor-args", "youtube:player_params={\"hl\":\"en\",\"gl\":\"US\"}",
                    "--force-generic-extractor"
                ]
                cmd_alt2.append(youtube_url)
                
                result_alt2 = subprocess.run(cmd_alt2, capture_output=True, text=True, check=True)
                print("✅ Method 3 succeeded:", result_alt2.stdout)
                
                for file in os.listdir(temp_audio_dir):
                    if file.endswith(".mp3"):
                        return os.path.join(temp_audio_dir, file)
                return None
            except subprocess.CalledProcessError as e3:
                print("❌ Method 3 failed:", e3.stderr)
                
                # Method 4: Try with minimal approach
                try:
                    print("🔧 Trying Method 4: Minimal approach...")
                    cmd_alt3 = [
                        "yt-dlp",
                        "-f", "bestaudio",
                        "--extract-audio",
                        "--audio-format", "mp3",
                        "--output", output_file,
                        "--no-playlist",
                        "--no-check-certificates",
                        "--no-cache-dir",
                        "--force-generic-extractor"
                    ]
                    cmd_alt3.append(youtube_url)
                    
                    result_alt3 = subprocess.run(cmd_alt3, capture_output=True, text=True, check=True)
                    print("✅ Method 4 succeeded:", result_alt3.stdout)
                    
                    for file in os.listdir(temp_audio_dir):
                        if file.endswith(".mp3"):
                            return os.path.join(temp_audio_dir, file)
                    return None
                except subprocess.CalledProcessError as e4:
                    print("❌ All methods failed. Last error:", e4.stderr)
                    print("💡 Try manually visiting YouTube in Chrome and then retry")
                    return None

def cleanup_old_audio_files():
    """Remove audio files older than 1 hour to prevent disk space issues"""
    import time
    temp_audio_dir = "temp_audio"
    if not os.path.exists(temp_audio_dir):
        return
    
    current_time = time.time()
    for filename in os.listdir(temp_audio_dir):
        if filename.endswith(".mp3"):
            file_path = os.path.join(temp_audio_dir, filename)
            # Remove files older than 1 hour (3600 seconds)
            if current_time - os.path.getmtime(file_path) > 3600:
                try:
                    os.remove(file_path)
                    print(f"🗑️ Cleaned up old file: {filename}")
                except Exception as e:
                    print(f"⚠️ Failed to remove {filename}: {e}")

def transcribe_audio(file_path):
    """Transcribe audio and format results for frontend"""
    try:
        result = model.transcribe(file_path, fp16=False)

        # Full text
        full_text = result["text"].strip()

        # Bullet points (split sentences)
        bullet_points = [s.strip() for s in full_text.split(". ") if s.strip()]

        # Timestamps (segments)
        timestamps = []
        for seg in result.get("segments", []):
            timestamps.append(
                {
                    "time": format_timestamp(seg["start"]),
                    "text": seg["text"].strip(),
                }
            )

        return {
            "full_text": full_text,
            "bullet_points": bullet_points,
            "timestamps": timestamps,
        }
    except Exception as e:
        print("❌ Whisper transcription failed:", str(e))
        return None

def generate_ai_bullets(text):
    """Generate AI-powered bullet points from transcript text"""
    if not GEMINI_API_KEY:
        return {"error": "Gemini API key not configured"}
    
    try:
        prompt = f"""Create concise, well-structured bullet points from this transcript. 
        Focus on key points, main ideas, and important details. 
        Make them clear and easy to read. Return only the bullet points, no additional text.
        
        Transcript: {text}"""
        
        response = gemini_model.generate_content(prompt)
        ai_bullets = response.text.strip()
        
        # Split into individual bullet points
        bullet_list = [point.strip() for point in ai_bullets.split('\n') if point.strip()]
        
        return {"ai_bullets": bullet_list}
    except Exception as e:
        print("❌ AI bullets generation failed:", str(e))
        return {"error": f"AI bullets generation failed: {str(e)}"}

def generate_ai_summary(text):
    """Generate AI summary from transcript text"""
    if not GEMINI_API_KEY:
        return {"error": "Gemini API key not configured"}
    
    try:
        prompt = f"""Create a comprehensive summary of this transcript. 
        Include the main topics, key points, and important insights. 
        Make it well-structured and easy to understand. Return only the summary, no additional text.
        
        Transcript: {text}"""
        
        response = gemini_model.generate_content(prompt)
        ai_summary = response.text.strip()
        return {"ai_summary": ai_summary}
    except Exception as e:
        print("❌ AI summary generation failed:", str(e))
        return {"error": f"AI summary generation failed: {str(e)}"}

def generate_linkedin_caption(text):
    """Generate LinkedIn post caption from transcript text"""
    if not GEMINI_API_KEY:
        return {"error": "Gemini API key not configured"}
    
    try:
        prompt = f"""Create an engaging LinkedIn post caption based on this transcript. 
        
        Requirements:
        - Keep it between 100-300 characters for optimal engagement
        - Start with a hook to grab attention
        - Include 2-3 key insights or takeaways
        - End with a call-to-action or question
        - Use professional but engaging tone
        - Include 3-5 relevant hashtags at the end
        - Format: Main caption + line break + hashtags
        
        Transcript: {text}
        
        Return only the LinkedIn caption, no additional text."""
        
        response = gemini_model.generate_content(prompt)
        linkedin_caption = response.text.strip()
        
        # Split caption and hashtags
        lines = linkedin_caption.split('\n')
        main_caption = lines[0] if lines else linkedin_caption
        hashtags = '\n'.join(lines[1:]) if len(lines) > 1 else ""
        
        return {
            "linkedin_caption": main_caption,
            "hashtags": hashtags,
            "full_caption": linkedin_caption,
            "character_count": len(main_caption)
        }
    except Exception as e:
        print("❌ LinkedIn caption generation failed:", str(e))
        return {"error": f"LinkedIn caption generation failed: {str(e)}"}

@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"ok": False, "error": "Missing 'url'"}), 400

    url = data["url"]
    print("Received URL:", url)
    
    # Clean up old audio files first
    cleanup_old_audio_files()
    
    # Download audio to temp_audio directory
    audio_file = download_audio(url, None)  # temp_dir parameter not needed anymore
    if not audio_file:
        return jsonify({"ok": False, "error": "Failed to download audio"}), 500

    transcript = transcribe_audio(audio_file)
    if not transcript:
        return jsonify({"ok": False, "error": "Transcription failed"}), 500

    return jsonify({"ok": True, **transcript})

@app.route("/ai-bullets", methods=["POST"])
def ai_bullets():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"ok": False, "error": "Missing 'text'"}), 400

    text = data["text"]
    result = generate_ai_bullets(text)
    
    if "error" in result:
        return jsonify({"ok": False, "error": result["error"]}), 500
    
    return jsonify({"ok": True, **result})

@app.route("/ai-summary", methods=["POST"])
def ai_summary():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"ok": False, "error": "Missing 'text'"}), 400

    text = data["text"]
    result = generate_ai_summary(text)
    
    if "error" in result:
        return jsonify({"ok": False, "error": result["error"]}), 500
    
    return jsonify({"ok": True, **result})

@app.route("/diagnose", methods=["GET"])
def diagnose():
    return jsonify({"ok": True, "message": "Server is running!"})

if __name__ == "__main__":
    app.run(debug=True)
