# Mode: `infographic` — Swiss Pulse PNG via Gemini

Generate a professional infographic **image** from the acquired document using Gemini's image-generation API, following Swiss International Typographic Style.

Prerequisite: the dispatcher (`SKILL.md` Step 3) has already extracted the document text. This file covers the Gemini API call and the Swiss Pulse design brief.

## Step 1: Load design tokens

Read `assets/swiss-pulse-tokens.md` to retrieve the canonical palette (black, white, electric blue #0066FF), typography (Helvetica / Swiss grotesque), and layout rules referenced by the Gemini prompt below.

## Step 2: Verify environment

Confirm the `GEMINI_API_KEY` environment variable is set. If missing, stop and request it from the user. Do not hardcode the key in the script.

## Step 3: Call Gemini to generate the infographic

Run this Python script, substituting the extracted document text into `document_text`:

```python
import os
import requests
import json
import base64

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"

document_text = """<PASTE EXTRACTED TEXT HERE>"""

design_prompt = f"""Create a professional infographic image in the Swiss International Typographic Style (inspired by Josef Müller-Brockmann).

DESIGN RULES — follow these strictly:
- Grid-locked layout: everything aligned to a strict modular grid
- Color palette: black, white, and ONE accent color: electric blue (#0066FF). No other colors.
- Typography: Helvetica or Swiss grotesque style only — clean, bold headings, light body text
- Lead with a large hero metric or key number displayed prominently at the top
- Use clean data visualizations: bar charts, line charts, or donut charts where appropriate
- Generous whitespace — never cramped
- No decorative elements — every element earns its place
- Subtle diagonal composition elements for dynamism
- Professional, clinical, precise aesthetic

CONTENT TO VISUALIZE:
{document_text}

Create a complete, polished infographic that communicates the key information from this content. Include a clear title, key metrics displayed prominently, supporting data points, and a bottom-line takeaway. Make it look like it was designed by a Swiss design studio."""

payload = {
    "contents": [{"parts": [{"text": design_prompt}]}],
    "generationConfig": {
        "responseModalities": ["IMAGE", "TEXT"],
        "temperature": 1.0,
        "maxOutputTokens": 8192
    }
}

response = requests.post(GEMINI_URL, json=payload, headers={"Content-Type": "application/json"})
result = response.json()

# Extract and save the image
for part in result["candidates"][0]["content"]["parts"]:
    if "inlineData" in part:
        image_data = part["inlineData"]["data"]
        mime_type = part["inlineData"]["mimeType"]
        ext = "png" if "png" in mime_type else "jpg" if "jpeg" in mime_type else "webp"
        output_path = f"/mnt/user-data/outputs/infographic.{ext}"
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(image_data))
        print(f"Saved to {output_path}")
        break
else:
    print("No image in response. Full response:")
    print(json.dumps(result, indent=2))
```

## Step 4: Present the output

Use `present_files` to share the generated infographic. Keep the response minimal — the visual speaks for itself.

## Error Handling

- If Gemini returns no image → retry once with a simplified prompt.
- If the document is empty → report the empty source to the user.
- If the API call fails → print the error for debugging and report to the user.
- Always check that `result["candidates"]` exists before accessing it.

## Mode-Specific Rules

- Always produce an image file (PNG/JPG/WEBP). Never substitute HTML, Excalidraw, or a text summary.
- Never embed colors outside the Swiss Pulse palette defined in `assets/swiss-pulse-tokens.md`.
- Never add commentary beyond a single sentence when presenting the image.
