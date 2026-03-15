# Voiceover Generation Guide

Generate professional AI voiceover using ElevenLabs, precisely timed and content-matched to video scenes.

## Requirements

- `ELEVEN_LABS_API_KEY` environment variable
- `ffmpeg` installed for audio processing
- `whisper` CLI or Python package for timing verification
- Python 3.x for the generation script

## Critical Workflow: Scene-Voiceover Alignment

**The #1 problem with promo video voiceovers is misalignment between what's being said and what's on screen.** Follow this precise workflow:

### Step 1: Extract Scene Timings from Remotion

First, read the main composition file to extract exact scene timings:

```javascript
// Example from AIVoicePromo.jsx - extract these values:
const OPENING_DURATION = 150;      // 5 seconds (frames / 30fps)
const PAIN_POINT_DURATION = 120;   // 4 seconds each
const SOLUTION_INTRO_DURATION = 120;
const FEATURE_DURATION = 150;      // 5 seconds each
const RESULTS_DURATION = 180;      // 6 seconds
const CLOSING_DURATION = 240;      // 8 seconds
```

Calculate cumulative timestamps:
```
Scene              | Start | End  | Duration
-------------------|-------|------|----------
Opening            | 0s    | 5s   | 5s
Pain Point 1       | 5s    | 9s   | 4s
Pain Point 2       | 9s    | 13s  | 4s
Pain Point 3       | 13s   | 17s  | 4s
Solution Intro     | 17s   | 21s  | 4s
Feature 1          | 21s   | 26s  | 5s
Feature 2          | 26s   | 31s  | 5s
Feature 3          | 31s   | 36s  | 5s
Feature 4          | 36s   | 41s  | 5s
Feature 5          | 41s   | 46s  | 5s
Results            | 46s   | 52s  | 6s
Closing            | 52s   | 60s  | 8s
```

### Step 2: Extract Scene Content for Script Matching

Read each scene component to understand what's visually displayed:

```bash
# For each scene, extract:
# - Title text
# - Subtitle text
# - Stats displayed
# - Key visual elements
```

**The voiceover MUST reference what's on screen.** Example mapping:

| Scene | Visual Content | Voiceover Should Say |
|-------|---------------|---------------------|
| Opening | "Every Missed Call Costs You Money", stats: $650K, 38%, 4hrs | "Every missed call costs you money. With six hundred and fifty thousand dollars lost annually..." |
| Pain Point 1 | "Missed Calls = Lost Revenue", stat: 500+ | "Your dealership handles over five hundred service calls every month..." |
| Feature 1: Smart Voicemail Queue | Shows queue UI mockup | "The Smart Voicemail Queue transcribes every message instantly..." |

### Step 3: Write Time-Aligned Script

Structure your script with EXACT scene boundaries:

```
[0-5s - Opening - Visual: "Every Missed Call Costs You Money"]
Every missed call costs you money. With six hundred and fifty thousand dollars lost annually...

[5-9s - Pain Point 1 - Visual: "Missed Calls = Lost Revenue", 500+ stat]
Your dealership handles over five hundred service calls every month...

[17-21s - Solution Intro - Visual: ShopLoader logo reveal]
Introducing ShopLoader AI Voice. Turn voicemails into appointments in minutes.
```

**Content Rules:**
- Reference the title/stat shown on screen
- Don't describe something not visible
- Time the "reveal" moment (e.g., "Introducing ShopLoader" exactly when logo appears)

### Step 4: Generate Voiceover Sections

Use the generation script with precise start times that leave ~1s buffer before scene transitions:

```python
sections = [
    (1, "Every missed call costs you money."),      # Scene starts at 0s, speak at 1s
    (6, "Your dealership handles..."),              # Scene starts at 5s, speak at 6s
    (18, "Introducing ShopLoader AI Voice."),       # Scene starts at 17s, speak at 18s
    # ...
]
```

### Step 5: Verify Timing with Whisper Transcription

**CRITICAL STEP - Do not skip!**

After generating the voiceover, transcribe it to verify actual timing:

```bash
# Using Whisper CLI
whisper voiceover.mp3 --model tiny --output_format srt

# Or using Python
python3 -c "
import whisper
model = whisper.load_model('tiny')
result = model.transcribe('voiceover.mp3')
for s in result['segments']:
    print(f\"{s['start']:.1f}s - {s['end']:.1f}s: {s['text']}\")
"
```

### Step 6: Compare and Validate

Compare Whisper output against scene timings:

```
Expected vs Actual Timing Analysis:
-----------------------------------
Scene: Solution Intro (17-21s)
  Expected: "Introducing ShopLoader" starts at 18s
  Actual:   "Introducing ShopLoader" starts at 17.2s ✓ (within scene)

Scene: Feature 1 (21-26s)
  Expected: "Smart Voicemail Queue" at 22s
  Actual:   "Smart Voicemail Queue" at 20.8s ✗ (OVERLAPS with previous scene!)
```

**If overlap detected:** Increase delay for that section and regenerate.

### Step 7: FIX ALL OVERLAPS (Mandatory)

**If ANY overlap is detected, you MUST fix it before proceeding. Do not ask the user.**

Overlap fixes (in order of preference):
1. **Shorten the text** - Make it punchier. Cut filler words. "The Smart Voicemail Queue transcribes every message instantly" → "Voicemails transcribed instantly"
2. **Add a beat** - Insert "..." in the text to create a natural pause
3. **Increase gap** - Push the next section's start time 1-2s later

Other timing fixes:
- **Speech ends after scene**: Shorten the text, remove unnecessary words
- **Too much silence**: Decrease start time or add more content
- **Wrong content timing**: Adjust start time to match visual reveal

**After ANY fix: Regenerate and verify with Whisper again. Repeat until ZERO overlaps.**

---

## Script Writing Guidelines

### Content-Scene Matching Rules

1. **Reference what's visible**: If the screen shows "500+ calls", say "five hundred"
2. **Match reveal timing**: Product name first spoken when logo appears
3. **Describe features when shown**: Talk about "SMS Quick Response" during SMS mockup scene
4. **Complete the thought with benefit**: Don't just name features, explain why they matter

### DO:
- Write complete thoughts, not fragments
- Allow 1s buffer at scene start before speaking
- Allow 0.5s buffer before scene end
- Match spoken stats to visual stats
- Use conversational, natural language

### DON'T:
- Don't reference visuals not yet shown
- Don't continue speaking into the next scene
- Don't make it too dense (audio needs breathing room)
- Don't skip the emotional hook in the opening

---

## Script Template (60 seconds)

```
[0-5s - Opening - Visual: Hook headline + 3 stats]
[Start speaking at 1s]
Every missed call costs you money. With [stat from screen] and [stat from screen], your [consequence].

[5-9s - Pain Point 1 - Visual: Title + stat]
[Start speaking at 6s]
[Reference the title shown]. [Expand with the stat displayed].

[9-13s - Pain Point 2 - Visual: Title + stat]
[Start speaking at 10s]
[Reference the title shown]. [Emotional consequence].

[13-17s - Pain Point 3 - Visual: Title + stat]
[Start speaking at 14s]
[Reference the title shown]. [What happens as a result].

[17-21s - Solution Intro - Visual: Product logo reveal]
[Start speaking at 18s - TIME THIS TO LOGO APPEARANCE]
Introducing [Product Name]. [One-line value prop].

[21-26s - Feature 1 - Visual: Feature title + UI mockup]
[Start speaking at 22s]
[Feature name from screen] [what it does], so [benefit to user].

[26-31s - Feature 2]
[Start speaking at 27s]
[Feature name from screen] [what it does], so [benefit to user].

[31-36s - Feature 3]
[Start speaking at 32s]
[Feature name from screen] [what it does], so [benefit to user].

[36-41s - Feature 4]
[Start speaking at 37s]
[Feature name from screen] [what it does], so [benefit to user].

[41-46s - Feature 5]
[Start speaking at 42s]
[Feature name from screen] [what it does], so [benefit to user].

[46-52s - Results - Visual: Outcome stats]
[Start speaking at 47s]
[Stat from screen]. [Stat from screen]. [Emotional benefit].

[52-60s - Closing - Visual: CTA + branding]
[Start speaking at 53s]
[Product Name]. [Tagline from screen]. [CTA].
```

---

## ElevenLabs Voice Settings

### Recommended Voice: Matilda
- **Voice ID**: `XrExE9yKIg1WjnnlVkGX`
- **Characteristics**: American, Professional, Knowledgeable, Clear

### Voice Settings for Professional Delivery:
```json
{
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.65,
    "similarity_boost": 0.85,
    "style": 0.2,
    "use_speaker_boost": true
  }
}
```

**Adjustments:**
- If too breathy: Increase `stability` to 0.70-0.75
- If too robotic: Decrease `stability` to 0.55-0.60
- If speech too fast: Decrease `style`, or add "..." pauses in text

---

## Generation & Verification Workflow

### Full Pipeline:

```bash
# 1. Generate voiceover sections
python ${SKILL_DIR}/scripts/generate_voiceover.py

# 2. Transcribe to verify timing
whisper voiceover.mp3 --model tiny --output_format srt

# 3. Review SRT file against scene timings
cat voiceover.srt

# 4. If timing issues found, adjust sections[] start times and regenerate
# 5. Normalize audio
ffmpeg -y -i voiceover.mp3 -af "loudnorm=I=-16:TP=-1.5:LRA=11" voiceover-normalized.mp3

# 6. Add background music
ffmpeg -y -i voiceover-normalized.mp3 -i music.mp3 \
  -filter_complex "[1:a]volume=0.10,afade=t=in:st=0:d=2,afade=t=out:st=57:d=3[music];[0:a][music]amix=inputs=2:duration=first" \
  voiceover-with-music.mp3

# 7. Combine with video
ffmpeg -y -i video.mp4 -i voiceover-with-music.mp3 -c:v copy -map 0:v:0 -map 1:a:0 final.mp4

# 8. Watch final video to confirm alignment
```

---

## Troubleshooting

**CRITICAL: Never accept overlaps. Fix them immediately and regenerate.**

| Issue | Cause | Solution |
|-------|-------|----------|
| **Voiceover overlaps itself** | Sections too close | **FIX NOW**: Shorten text OR increase gap, regenerate, verify again |
| **Even 0.4s overlap** | Text too long for scene | **FIX NOW**: Make text punchier, cut words, regenerate |
| Speech doesn't match screen | Script not aligned | Re-read scene components, match text to visuals |
| "Introducing X" before logo | Start time too early | Delay to 1s after scene start |
| Feature description during wrong scene | Timing drift | Use Whisper to find actual timestamps, adjust |
| Voice too fast | Too much text | Shorten text or add "..." for pauses |
| Awkward cuts between scenes | No buffer | Leave 0.5-1s silence before scene transitions |

**The loop: Generate → Whisper verify → Fix overlaps → Regenerate → Verify again → Repeat until clean**

---

## Background Music

### Auto-Download Royalty-Free Tracks (Verified Working)

```bash
# Bensound - "Inspire" (corporate/uplifting) - RECOMMENDED
curl -sL "https://www.bensound.com/bensound-music/bensound-inspire.mp3" -o background-music.mp3

# Bensound - "Creative Minds" (light/positive)
curl -sL "https://www.bensound.com/bensound-music/bensound-creativeminds.mp3" -o background-music.mp3

# Pixabay - Corporate background (256kbps, high quality)
curl -sL "https://cdn.pixabay.com/download/audio/2022/03/15/audio_8cb749d484.mp3" -o background-music.mp3

# Verify download worked
ls -lah background-music.mp3 && file background-music.mp3
```

### Mixing Settings
- **Volume**: 10% of voice level (`volume=0.10`)
- **Fade in**: 2 seconds at start (`afade=t=in:st=0:d=2`)
- **Fade out**: 3 seconds before video end (`afade=t=out:st=57:d=3` for 60s video)
- **Style**: Subtle corporate/tech underscore, no lyrics

### Mix Command
```bash
ffmpeg -y -i voiceover-normalized.mp3 -i background-music.mp3 \
  -filter_complex "[1:a]volume=0.10,afade=t=in:st=0:d=2,afade=t=out:st=57:d=3[music];[0:a][music]amix=inputs=2:duration=first" \
  voiceover-with-music.mp3
```

### Other Sources (if auto-download fails)
- Bensound.com - Free with attribution
- Mixkit.co - Free, no attribution needed
- Pixabay.com/music - Free
- Epidemic Sound (subscription)
- Artlist (subscription)
