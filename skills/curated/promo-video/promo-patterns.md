# Visual Inspiration & Techniques

Ideas and techniques for creating premium promo videos. **These are suggestions, not templates.** Let your creative instincts lead.

---

## Animation Toolkit

### Spring Physics
Play with these parameters for different feels:
- `damping: 8-12` → bouncy, playful
- `damping: 15-20` → smooth, professional
- `damping: 25+` → snappy, minimal overshoot
- `mass: 0.5` → lighter, faster
- `mass: 1.5` → heavier, more momentum

### Timing Curves
- **Staggered reveals**: Delay each element by 10-20 frames for cascading effect
- **Anticipation**: Small backward motion before forward (scale 0.95 → 1.1 → 1)
- **Overshoot**: Go past target, settle back (translateY: 50 → -10 → 0)
- **Ease-out emphasis**: Quick start, slow finish draws attention

### 3D Transforms
```
transform: `perspective(1000px) rotateY(${angle}deg) rotateX(${tilt}deg)`
```
- Perspective 800-1200px for subtle depth
- Perspective 400-600px for dramatic angles
- Combine with translateZ for parallax layers

---

## Transition Ideas

**Metallic Swoosh Wipe**
- Diagonal gradient mask that moves across screen
- Add metallic sheen with animated gradient position
- Motion blur on the leading edge

**3D Flip Reveal**
- Element rotates on Y-axis to reveal new content
- Add backface-visibility for clean flip
- Slight scale increase during rotation adds impact

**Particle Dissolve**
- Break content into grid, animate each cell
- Random delays create organic dissolve
- Scale down + fade for dust effect

**Zoom Through**
- Camera pushes through current scene
- Scale up rapidly (1 → 3) with fade
- New scene scales down from large (3 → 1)

**Directional Slide**
- Content slides out, new content slides in
- Add subtle blur during motion
- Offset timing for overlap transition

**Morph Transform**
- Shape morphs into next shape
- Use clipPath animations
- Smooth color transitions during morph

---

## Visual Elements

### Browser Mockups
- **Floating**: Dramatic shadow, slight rotation (2-5deg)
- **Perspective**: rotateX(5deg) rotateY(-10deg) for 3D tilt
- **Device frame**: Wrap in laptop/phone bezel
- **Animated cursor**: Show interactions, clicks
- **Screen glow**: Soft light emanating from display

### Stat Presentations
- Counter animation (0 → final value)
- Circle/ring fill animation
- Bar chart that grows
- Number with pulsing glow on reveal

### Text Reveals
- Word-by-word fade-in
- Character stagger (typewriter+)
- Clip-path reveal (text slides out from behind mask)
- Blur-to-sharp focus transition
- Scale up from baseline

### Background Effects
- Subtle gradient animation (hue shift)
- Floating particles or dots
- Grid pattern with perspective
- Mesh gradient with smooth movement
- Noise texture overlay (very subtle, 2-5% opacity)

---

## Scene Concepts

### Opening Hook
- Start with the pain, not the product
- Big stat that stops scrolling
- Question that hits home
- Dark/urgent colors for problems

### Product Reveal
- Build anticipation with pause
- Logo animation with impact
- Sound design moment (sync to visual)
- Color shift from problem (red) to solution (blue)

### Feature Showcase
- Show the UI, not just describe it
- Highlight interactions with cursor/focus
- Before/after comparisons
- Split screen demonstrations

### Closing CTA
- Clear single action
- Urgency without desperation
- Reinforce brand identity
- Leave contact/URL visible

---

## Color Psychology

**Problems/Pain**: Red (#dc2626), Orange (#ea580c), Dark grays
**Solutions/Benefits**: Blue (#3b82f6), Green (#22c55e), Purple (#8b5cf6)
**Urgency**: Amber (#f59e0b), Red accents
**Trust**: Blue (#3b82f6), Navy (#1e3a5a)
**Premium**: Deep purple (#7c3aed), Gold accents (#fbbf24)

---

## Things That Pop

- Unexpected motion direction
- Pause before big reveal (2-3 seconds of buildup)
- Scale changes (tiny to big, big to tiny)
- Depth through layered parallax
- Consistent motion language throughout
- One "hero moment" per scene, not everything moving at once

---

## Technical Notes

**Performance**
- Keep transforms on GPU (transform, opacity)
- Avoid animating width/height (use scale)
- Pre-compose complex scenes

**Readability**
- 60-100px minimum for headlines at 1080p
- High contrast text/background
- Don't animate text people need to read

**Timing**
- 4-6 seconds per major scene
- 1-2 seconds for transitions
- Match voiceover rhythm, not just timestamps
