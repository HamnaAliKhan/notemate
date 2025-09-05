#!/usr/bin/env python3
"""
Test script to verify the transcription fix works properly.
This script tests the download_audio function with a sample YouTube URL.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import download_audio, transcribe_audio

def test_transcription():
    """Test the transcription process with a sample URL"""
    # Use a short, reliable YouTube video for testing
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - short and reliable
    
    print("🧪 Testing transcription process...")
    print(f"📺 Test URL: {test_url}")
    
    # Test download_audio function
    print("\n1️⃣ Testing download_audio function...")
    audio_file = download_audio(test_url)
    
    if audio_file:
        print(f"✅ Audio file downloaded successfully: {audio_file}")
        
        # Test transcribe_audio function
        print("\n2️⃣ Testing transcribe_audio function...")
        transcript = transcribe_audio(audio_file)
        
        if transcript:
            print("✅ Transcription completed successfully!")
            print(f"📝 Transcript preview: {transcript['full_text'][:100]}...")
            print(f"🔘 Number of bullet points: {len(transcript['bullet_points'])}")
            print(f"⏱️ Number of timestamped segments: {len(transcript['timestamps'])}")
        else:
            print("❌ Transcription failed")
            return False
    else:
        print("❌ Audio download failed")
        return False
    
    print("\n🎉 All tests passed!")
    return True

if __name__ == "__main__":
    success = test_transcription()
    sys.exit(0 if success else 1)

