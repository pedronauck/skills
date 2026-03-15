---
name: nano-banana-prompting
description: This skill should be used when crafting prompts for Nano Banana Pro (Gemini image generation). Use when users want help writing image generation prompts, need guidance on prompt structure, or want to optimize their prompts for better results.
---

# Nano Banana Prompting

Interactive prompt crafting for Nano Banana Pro image generation. This skill guides users through a structured process to create effective prompts by clarifying intent and applying proven techniques.

## Workflow

### Step 1: Gather Reference Materials

Before asking questions, check if the user has provided:

- **Reference images** - Photos to use for character consistency, style, or composition
- **Existing prompts** - Previous attempts to improve upon
- **Visual references** - Screenshots or examples of desired output

If reference materials are available, this affects which techniques apply (e.g., Reference Role Assignment, Character Consistency).

### Step 2: Clarify Intent with Questions

Use the `AskUserQuestion` tool to understand the user's goal. Ask questions in batches of 2-4, focusing on the most important aspects first.

#### Core Questions (always ask)

1. **Output Type** - What kind of image?
   - Photo/realistic
   - Illustration/artistic
   - Infographic/educational
   - Product shot/commercial
   - UI mockup/design

2. **Subject** - Who or what is the main focus?
   - Person (with or without reference)
   - Object/product
   - Scene/environment
   - Concept/abstract

#### Technique-Specific Questions (based on answers)

**If Photo/Realistic:**
- What era or camera style? (modern DSLR, 1990s film, 2000s digital)
- Specific lighting? (golden hour, studio, flash)
- Aspect ratio needed? (16:9, 9:16, 1:1)

**If Reference Images Provided:**
- What role for each image? (pose, style, color palette, background)
- Should character identity be preserved?
- Combine images or use as style reference?

**If Text Needed:**
- What text should appear?
- What font style? (serif, sans-serif, handwritten)
- Where should text be placed?

**If Educational/Infographic:**
- What concept to explain?
- Target audience level?
- Should it include labels, arrows, flow?

### Step 3: Determine Prompt Style

Based on user responses, select the appropriate prompt format from `references/guide.md`:

| User Need | Recommended Style |
|-----------|-------------------|
| Simple, quick generation | Narrative Prompt (Technique 1) |
| Precise control over details | Structured Prompt (Technique 2) |
| Era-specific aesthetic | Vibe Library + Photography Terms (Techniques 3-4) |
| Magazine/poster with text | Physical Object Framing (Technique 5) |
| Conceptual/interpretive | Perspective Framing (Technique 6) |
| Diagram/infographic | Educational Imagery (Technique 7) |
| Editing existing image | Image Transformation (Technique 8) |
| Multiple views/panels | Multi-Panel Output (Technique 9) |
| Multiple reference images | Reference Role Assignment (Technique 12) |

### Step 4: Generate the Prompt

Construct the prompt by:

1. **Loading `references/guide.md`** to access technique details
2. **Applying relevant techniques** based on Step 3 selection
3. **Cross-checking** against guide examples for proper formatting
4. **Including negative prompts** if needed (Technique 10)
5. **Specifying aspect ratio/resolution** if required (Technique 11)

#### Prompt Construction Checklist

- [ ] Subject clearly defined
- [ ] Action/pose specified (if applicable)
- [ ] Location/background described
- [ ] Style/aesthetic anchored
- [ ] Technical specs included (aspect ratio, lighting, camera)
- [ ] Text integration specified (if needed)
- [ ] Negative prompts added (if needed)
- [ ] Reference image roles assigned (if using references)

### Step 5: Present and Iterate

Present the generated prompt to the user with:

1. **The prompt** - Ready to use
2. **Technique explanation** - Why this structure was chosen
3. **Variation suggestions** - Alternative approaches to try

Offer to refine based on feedback.

### Step 6: Generate the Image

After the user is satisfied with the prompt, recommend using the **nano-banana** skill to generate the actual image. Inform the user:

> "Your prompt is ready! Would you like me to generate the image now? I can use the nano-banana skill to create it."

If the user agrees, invoke the `nano-banana` skill with the crafted prompt.

## Quick Reference: Technique Selection

```
User wants...                    → Use Technique...
─────────────────────────────────────────────────────
Simple description               → 1 (Narrative)
Detailed control                 → 2 (Structured YAML/JSON)
Specific era look                → 3 (Vibe Library)
Professional photo style         → 4 (Photography Terms)
Magazine/poster                  → 5 (Physical Object Framing)
"How X sees Y"                   → 6 (Perspective Framing)
Educational diagram              → 7 (Educational Imagery)
Edit existing image              → 8 (Image Transformation)
Multiple panels in one           → 9 (Multi-Panel)
Exclude something                → 10 (Negative Prompts)
Specific dimensions              → 11 (Aspect Ratio)
Multiple reference images        → 12 (Reference Roles)
Same character across images     → 13 (Character Consistency)
Merge multiple images            → 14 (Image Blending)
Enhance/restore image            → 15 (Upscaling)
Translate text in image          → 16 (Translation)
```

## Resources

### references/

- `guide.md` - Complete prompting guide with 16 techniques, examples, and patterns. Load this file when constructing prompts to access specific technique details and examples.
