#!/usr/bin/env python3
"""
Generate timed voiceover for promo videos using ElevenLabs API.

Usage:
    1. Set ELEVEN_LABS_API_KEY environment variable
    2. Edit the `sections` list below with your script
    3. Run: python generate_voiceover.py

Requirements:
    - Python 3.x
    - ffmpeg installed
    - ELEVEN_LABS_API_KEY environment variable
"""

import urllib.request
import json
import subprocess
import os
import sys

# Configuration
API_KEY = os.environ.get("ELEVEN_LABS_API_KEY")
VOICE_ID = "XrExE9yKIg1WjnnlVkGX"  # Matilda - Professional, American
VIDEO_DURATION = 60  # seconds
OUTPUT_FILE = "voiceover.mp3"

# Voice settings for clear, professional delivery
VOICE_SETTINGS = {
    "stability": 0.65,        # Higher = less breathy
    "similarity_boost": 0.85,
    "style": 0.2,
    "use_speaker_boost": True
}

# Define your script sections here
# Format: (start_time_seconds, "text to speak")
sections = [
    (0, "Every missed call costs you money."),
    (5, "Your service drive is overwhelmed."),
    (9, "Four hours to call back? That's too late."),
    (13, "Customers won't wait."),
    (17, "Introducing Your Product. Turn problems into solutions."),
    (21, "Feature one described here, so you get the benefit."),
    (26, "Feature two described here, so you get the benefit."),
    (31, "Feature three described here, so you get the benefit."),
    (36, "Feature four described here, so you get the benefit."),
    (41, "Feature five described here, so you get the benefit."),
    (46, "The results speak for themselves. Better outcomes. Real results."),
    (52, "Your Product. Your tagline. Request your demo today."),
]


def check_requirements():
    """Verify API key and ffmpeg are available."""
    if not API_KEY:
        print("Error: ELEVEN_LABS_API_KEY environment variable not set")
        print("Set it with: export ELEVEN_LABS_API_KEY=your_key_here")
        sys.exit(1)

    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ffmpeg not found. Install it with: brew install ffmpeg")
        sys.exit(1)


def generate_audio(text: str, filename: str) -> float:
    """Generate audio for a single text section using ElevenLabs API."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": VOICE_SETTINGS
    }
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        with open(filename, "wb") as f:
            f.write(response.read())

    # Get duration using ffprobe
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", filename],
        capture_output=True,
        text=True
    )
    duration = float(result.stdout.strip())
    return duration


def create_silence_base(duration: int, filename: str):
    """Create a silent audio file as the base track."""
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
        "-t", str(duration), "-q:a", "9", "-acodec", "libmp3lame", filename
    ], capture_output=True)


def combine_audio_sections(section_files: list, start_times: list, output: str):
    """Combine all audio sections with proper timing into final voiceover."""
    inputs = ["-i", "silence_base.mp3"]
    filter_parts = []

    for i, (filename, start_time) in enumerate(zip(section_files, start_times)):
        inputs.extend(["-i", filename])
        delay_ms = int(start_time * 1000)
        filter_parts.append(f"[{i+1}]adelay={delay_ms}|{delay_ms}[d{i}]")

    mix_inputs = "[0]" + "".join(f"[d{i}]" for i in range(len(section_files)))
    filter_str = ";".join(filter_parts) + f";{mix_inputs}amix=inputs={len(section_files)+1}:duration=first"

    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_str, output]
    subprocess.run(cmd, capture_output=True)


def normalize_audio(input_file: str, output_file: str):
    """Normalize audio levels for consistent volume."""
    subprocess.run([
        "ffmpeg", "-y", "-i", input_file,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        output_file
    ], capture_output=True)


def cleanup(files: list):
    """Remove temporary files."""
    for f in files:
        try:
            os.remove(f)
        except OSError:
            pass


def verify_timing_with_whisper(audio_file: str) -> list:
    """Use Whisper to transcribe and get actual timestamps."""
    try:
        import whisper
        print("Transcribing with Whisper to verify timing...")
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_file)
        return result.get("segments", [])
    except ImportError:
        print("  Whisper not installed. Install with: pip install openai-whisper")
        print("  Skipping timing verification.")
        return []
    except Exception as e:
        print(f"  Whisper error: {e}")
        return []


def check_timing_alignment(segments: list, sections: list) -> list:
    """Compare Whisper timestamps against expected scene timing."""
    issues = []

    # Build expected timing windows
    # Each section should start at its defined time and end before the next section
    for i, (start_time, text) in enumerate(sections):
        next_start = sections[i + 1][0] if i + 1 < len(sections) else VIDEO_DURATION

        # Find matching Whisper segment
        for seg in segments:
            if text[:20].lower() in seg.get("text", "").lower():
                actual_start = seg.get("start", 0)
                actual_end = seg.get("end", 0)

                if actual_start < start_time - 0.5:
                    issues.append(f"Section {i} starts too early: expected {start_time}s, actual {actual_start:.1f}s")
                if actual_end > next_start:
                    issues.append(f"Section {i} overlaps into next scene: ends at {actual_end:.1f}s, next scene at {next_start}s")
                break

    return issues


def main():
    check_requirements()

    print(f"Generating voiceover with {len(sections)} sections...")
    print(f"Voice: Matilda (ID: {VOICE_ID})")
    print()

    section_files = []
    start_times = []
    temp_files = ["silence_base.mp3"]

    # Generate each section
    for i, (start_time, text) in enumerate(sections):
        filename = f"section_{i:02d}.mp3"
        section_files.append(filename)
        start_times.append(start_time)
        temp_files.append(filename)

        print(f"  [{start_time:2d}s] Generating: {text[:50]}...")
        duration = generate_audio(text, filename)
        print(f"       -> {duration:.1f}s audio")

        # Check if this section will overlap with next
        if i + 1 < len(sections):
            next_start = sections[i + 1][0]
            if start_time + duration > next_start:
                print(f"       WARNING: May overlap with next section (ends at {start_time + duration:.1f}s, next at {next_start}s)")

    print()
    print("Creating silence base track...")
    create_silence_base(VIDEO_DURATION, "silence_base.mp3")

    print("Combining sections...")
    combine_audio_sections(section_files, start_times, "voiceover_raw.mp3")
    temp_files.append("voiceover_raw.mp3")

    print("Normalizing audio levels...")
    normalize_audio("voiceover_raw.mp3", OUTPUT_FILE)

    # Verify timing with Whisper
    print()
    segments = verify_timing_with_whisper(OUTPUT_FILE)
    if segments:
        print("\nWhisper transcription timestamps:")
        for seg in segments:
            print(f"  {seg['start']:5.1f}s - {seg['end']:5.1f}s: {seg['text'][:60]}")

        issues = check_timing_alignment(segments, sections)
        if issues:
            print("\n" + "="*60)
            print("OVERLAPS DETECTED - MUST FIX BEFORE PROCEEDING")
            print("="*60)
            for issue in issues:
                print(f"  - {issue}")
            print("\nFIX OPTIONS:")
            print("  1. Shorten the overlapping text (make it punchier)")
            print("  2. Increase the next section's start time")
            print("  3. Add '...' to create natural pauses")
            print("\nThen regenerate and verify again. Do NOT proceed with overlaps.")
            print("="*60)
        else:
            print("\nTIMING VERIFIED - No overlaps detected")

    print("Cleaning up temporary files...")
    cleanup(temp_files)

    print()
    print(f"Success! Saved to: {OUTPUT_FILE}")
    print()
    print("Next steps:")
    print("  1. If timing issues were detected, adjust sections[] and run again")
    print("  2. Add background music:")
    print(f"     ffmpeg -y -i {OUTPUT_FILE} -i music.mp3 \\")
    print('       -filter_complex "[1:a]volume=0.15,afade=t=in:st=0:d=2,afade=t=out:st=57:d=3[music];[0:a][music]amix=inputs=2:duration=first" \\')
    print("       voiceover-with-music.mp3")
    print("  3. Combine with video:")
    print("     ffmpeg -y -i video.mp4 -i voiceover-with-music.mp3 -c:v copy -map 0:v:0 -map 1:a:0 final.mp4")


if __name__ == "__main__":
    main()
