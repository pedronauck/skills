# Nano Banana Prompting Guide

## Technique 1: Narrative Prompts

Start with a simpler narrative approach if no need to provide detailed specifications.

### Scene Narrative

Describe a moment or action happening in the scene:

> "A young woman stands almost sideways, slightly bent forward, during the final preparation for the show. Makeup artists apply lipstick to her."

End with a style summary to anchor the aesthetic:

> "Victoria's Secret style: sensuality, luxury, glamour."

Direct attention to specific elements:

> "The main emphasis is on the girl's face and the details of her costume. Emphasize the expressiveness of the gaze."

---

## Technique 2: Structured Prompts

Use structured formats (YAML/JSON) when you need to provide more detailed specifications.

### Reference Preservation (when reference image available)

Use multiple reinforcing signals to preserve details from a reference image:

```yaml
face:
  preserve_original: true
  reference_match: true
  description: "The girl's facial features, expression, and identity must remain exactly the same as the reference image."
```

### Multi-Subject Handling

When a scene has multiple distinct elements, define each as a separate object:

```yaml
subject:
  girl:
    age: "young"
    hair: "long, wavy brown hair"
    expression: "puckering her lips toward the camera"
    clothing: "black hooded sweatshirt"
  puppy:
    type: "small white puppy"
    eyes: "light blue"
    expression: "calm, looking forward"
```

### Example: 2000s Mirror Selfie

```yaml
subject:
  description: "A young woman taking a mirror selfie with very long voluminous dark waves and soft wispy bangs"
  age: "young adult"
  expression: "confident and slightly playful"
  hair:
    color: "dark"
    style: "very long, voluminous waves with soft wispy bangs"
  clothing:
    top:
      type: "fitted cropped t-shirt"
      color: "cream white"
      details: "features a large cute anime-style cat face graphic with big blue eyes, whiskers, and a small pink mouth"
  face:
    preserve_original: true
    makeup: "natural glam makeup with soft pink dewy blush and glossy red pouty lips"

accessories:
  earrings:
    type: "gold geometric hoop earrings"
  jewelry:
    waistchain: "silver waistchain"
  device:
    type: "smartphone"
    details: "patterned case"

photography:
  camera_style: "early-2000s digital camera aesthetic"
  lighting: "harsh super-flash with bright blown-out highlights but subject still visible"
  angle: "mirror selfie"
  shot_type: "tight selfie composition"
  texture: "subtle grain, retro highlights, V6 realism, crisp details, soft shadows"

background:
  setting: "nostalgic early-2000s bedroom"
  wall_color: "pastel tones"
  elements:
    - "chunky wooden dresser"
    - "CD player"
    - "posters of 2000s pop icons"
    - "hanging beaded door curtain"
    - "cluttered vanity with lip glosses"
  atmosphere: "authentic 2000s nostalgic vibe"
  lighting: "retro"
```

---

## Technique 3: Vibe Library

The vibe is determined by **signature details** - specific elements that define an era or style. Knowing these elements is key to authentic results.

| Era/Style | Signature Details |
|-----------|-------------------|
| 2000s bedroom | CD player, beaded curtain, lip glosses, pop icon posters |
| 1990s film photography | direct flash, messy hair, dim lighting, magazine posters |
| Film noir | venetian blind shadows, cigarette smoke, fedora, rain on window |
| Wes Anderson | symmetry, pastels, vintage props, centered framing |
| Blade Runner | neon rain, holographic ads, steam, cramped urban spaces |

### Mood/Atmosphere Words

Use evocative words to set the emotional tone:

> "dreamy, storytelling vibe", "warm, nostalgic", "cinematic, emotional"

### Candid Actions

Natural poses and actions add authenticity:

> "The subject is looking slightly away from the camera, holding a coffee cup, with a relaxed, candid expression."

---

## Technique 4: Photography Terminology

Technical camera/lighting terms add realism and control.

### Camera/Lens Specs

Name specific gear to suggest quality and style:

> "Shot on a Sony A7III with an 85mm f/1.4 lens, creating a flattering portrait compression."

### Named Lighting Setups

Use known photography terms:

> "Use a classic three-point lighting setup. The main key light should create soft, defining shadows on the face. A subtle rim light should separate the subject's shoulders and hair from the dark background."

### Texture Realism

Explicitly request textures for authenticity:

> "Render natural skin texture with visible pores. The fabric of the suit should show a subtle wool texture."

### Time of Day

Specify lighting conditions by time:

> "Golden Hour (sunset). Warm, nostalgic lighting hitting the side of the face."

Other options: blue hour, harsh noon light, overcast diffused light, night with artificial lights.

### Framing & Composition

Specify how the subject is framed:

> "The subject is framed from the chest up, with ample headroom. Shot from a high angle. The person looks directly at the camera."

### Focus Target

Direct where sharpest focus should be:

> "exquisite focus on the eyes"

### Color Grading

Describe the overall color treatment:

> "Clean and bright cinematic color grading with subtle warmth and balanced tones, ensuring a polished and contemporary feel."

### Era-Specific Camera Styles

Reference camera aesthetics from specific eras:

- `camera_style: "early-2000s digital camera aesthetic"`
- `lighting: "harsh super-flash with bright blown-out highlights but subject still visible"`
- `texture: "subtle grain, retro highlights, crisp details, soft shadows"`

---

## Technique 5: Physical Object Framing

Generate an image OF a physical object (magazine, poster, photo on desk) rather than just the content itself.

> "A photo of a glossy magazine cover... The magazine is on a white shelf against a wall."

### Typography Instructions

Specify font style for text in images:

> "The text is in a serif font, black on white, and fills the view."

### Realistic Details

Add authenticity with real-world elements:

> "Put the issue number and today's date in the corner along with a barcode and a price."

---

## Technique 6: Perspective Framing

Ask for an interpretation from a specific viewpoint rather than a literal image.

> "How engineers see the San Francisco Bridge"

The model infers what that perspective would emphasize (structural elements, blueprints, stress diagrams, etc.).

Other examples:
- "How a child sees a hospital"
- "How a chef sees a kitchen"
- "How an architect sees a city"

---

## Technique 7: Educational/Instructional Imagery

Create infographics, diagrams, and educational visuals.

### Educational Framing

Start with the purpose:

> "Create an educational infographic explaining [Photosynthesis]."

### Visual Elements List

Explicitly list components to include:

> "Illustrate the key components: The Sun, a green Plant, Water (H2O) entering roots, Carbon Dioxide (CO2) entering leaves, and Oxygen (O2) being released."

### Audience Reference

Target the complexity level:

> "suitable for a high school science textbook"

### Flow & Labeling

Add structure and annotations:

> "Use arrows to show the flow of energy and matter. Label each element clearly."

---

## Technique 8: Image Transformation

Transform a reference image by specifying operations to perform.

### Task-Based Verbs

Use action words to direct the transformation:

> "Identify the main product... Cleanly extract the product... Recreate it as a premium e-commerce product shot... Place the product on a pure white studio background."

### Removal Instructions

Specify what to remove from the reference:

> "automatically removing any hands holding it or messy background details"
> "completely removing any fingers, hands, or clutter"

---

## Technique 9: Multi-Panel/Collage Output

Generate multiple views or panels in a single image.

### Layout Specification

Define the panel arrangement:

> "a collage with one large main image at the top, and several smaller images below it"

### Numbered Panel Content

Specify what each panel shows:

> "1. Main Image (Top): A wide-angle perspective view of the main living area"
> "2. Small Image (Bottom Left): A view of the Master Bedroom"
> "3. Small Image (Bottom Right): A 3D top-down floor plan view"

### Consistent Style Across Panels

Ensure visual coherence:

> "Apply a consistent Modern Minimalist style with warm oak wood flooring and off-white walls across ALL images."

---

## Technique 10: Negative Prompts

Tell the model what NOT to include to avoid unwanted elements.

> "no date stamp"
> "no text"
> "not rustic"
> "No monkeys"

Useful for stopping repeated unwanted outputs.

---

## Technique 11: Aspect Ratio & Resolution

Specify canvas dimensions and output quality.

### Aspect Ratio

> "A 9:16 vertical poster"
> "A cinematic 21:9 wide shot"
> "4:5 Instagram format"

### Resolution

> "Upscale to 4K"
> "1K, 2K or 4K resolution"

---

## Technique 12: Reference Role Assignment

When using multiple reference images, assign specific roles to each.

> "Use Image A for the character's pose, Image B for the art style, and Image C for the background environment."

> "Put the logo from image 1 onto the device in image 2. The woman from image 3 is holding it. Use the color palette from image 4."

Common roles:
- Character/subject reference
- Style/aesthetic reference
- Color palette reference
- Background/environment reference
- Branding/logo reference

---

## Technique 13: Character Consistency

Maintain the same character across multiple outputs.

### Single Reference

Start with one image, generate variations to build a reference library.

> "A 360 turnaround view in 4 different angles, full body pose"

### Multiple References (up to 5)

Use diverse references for better consistency:
- Close-ups
- Full body shots
- Different clothes/poses
- Different expressions/orientations

> "She is giving a talk at a large tech conference"

---

## Technique 14: Image Blending

Combine multiple input images into a single output.

> "Combine these images into one appropriately arranged cinematic image in 16:9 format"

> "Take the subjects from images 1-3 and place them in the environment from image 4"

---

## Technique 15: Upscaling & Restoration

Enhance image quality or restore old photos.

### Upscaling

> "Upscale to 4K"

Works with images as small as 150x150.

### Restoration

> "Faithfully restore this old photo"

---

## Technique 16: Translation & Localization

Translate or adapt text within images.

> "Translate all the English text on the cans into Korean, while keeping everything else the same"

> "Generate localized text for international markets"
