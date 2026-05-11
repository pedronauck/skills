---
name: pitch-deck
description: Generate professional PowerPoint pitch decks for startups and businesses. Use this skill when users request help creating investor pitch decks, sales presentations, or business pitch presentations. The skill follows standard 10-slide pitch deck structure and includes best practices for content and design.
---

# Pitch Deck Generator

## Overview

Generate professional PowerPoint pitch decks following industry best practices. This skill creates structured presentations for fundraising, sales, and business development using a proven 10-slide format.

## When to Use This Skill

Activate this skill when users request:
- Investor pitch decks for fundraising
- Sales or business development presentations
- Product launch presentations
- Startup pitch competition decks
- Any structured business presentation following standard pitch deck format

## Workflow

### Step 1: Gather Information

Collect necessary information from the user to populate the pitch deck. Use a conversational approach to gather details across the following categories:

**Required information:**
1. **Company basics**: Company name, tagline (one-liner describing what you do)
2. **Problem**: What problem are you solving? Include data or statistics if available
3. **Solution**: How does your product/service solve the problem? Key features and benefits
4. **Business model**: How do you make money? Pricing, revenue streams

**Recommended information** (include if available):
5. **Market opportunity**: Market size (TAM/SAM/SOM), growth rate, market trends
6. **Product details**: Product features, screenshots, technology highlights
7. **Traction**: Key metrics, revenue, users, growth rate, milestones, customer testimonials
8. **Competition**: Competitors, competitive advantages, differentiation
9. **Team**: Founders and key team members with relevant background
10. **Financials & Ask**: Funding amount, use of funds, financial projections, milestones

**Approach:**
- Ask open-ended questions to understand the business
- Probe for specific metrics and data points when possible
- For missing information, offer to create placeholder slides that can be updated later
- Adapt the standard 10-slide structure based on available information

### Step 2: Structure the Content

Organize the gathered information into the standard pitch deck structure:

1. **Title Slide**: Company name + tagline
2. **Problem**: Pain point being addressed
3. **Solution**: Product/service overview
4. **Market Opportunity**: Market size and growth
5. **Product**: Features and capabilities
6. **Traction**: Metrics and achievements
7. **Business Model**: Revenue and pricing
8. **Competition**: Competitive landscape
9. **Team**: Key people
10. **Financials & Ask**: Funding request and projections

**Reference best practices:** For detailed guidance on each slide's content and structure, consult `references/pitch_deck_best_practices.md`. Search for specific sections using grep:

```bash
grep -A 10 "### [Slide Number]. [Slide Name]" references/pitch_deck_best_practices.md
```

### Step 3: Create the JSON Data File

Format the collected information as a JSON file that will be consumed by the pitch deck generation script. Create a file called `pitch_data.json` with the following structure:

```json
{
  "company_name": "Company Name",
  "tagline": "One-line description of what you do",
  "problem": [
    "Problem statement 1 with data/statistics",
    "Problem statement 2 showing impact",
    "Problem statement 3 demonstrating urgency"
  ],
  "solution": [
    "How your product solves the problem",
    "Key feature 1 and its benefit",
    "Key feature 2 and its benefit",
    "Unique value proposition"
  ],
  "market": [
    "TAM: Total addressable market with $ figure",
    "SAM: Serviceable available market",
    "SOM: Serviceable obtainable market",
    "Market growth rate and trends"
  ],
  "product": [
    "Product feature 1",
    "Product feature 2",
    "Technology highlights",
    "User experience benefits"
  ],
  "traction": [
    "Revenue: $X (YY% growth)",
    "Users: X,XXX active users",
    "Key milestone 1",
    "Customer testimonial or social proof"
  ],
  "business_model": [
    "Revenue model (e.g., SaaS subscription)",
    "Pricing: $XX/month per user",
    "Unit economics: CAC, LTV, margins",
    "Sales channels"
  ],
  "competition": {
    "our_advantages": [
      "Advantage 1",
      "Advantage 2",
      "Unfair advantage/defensibility"
    ],
    "competitors": [
      "Competitor 1",
      "Competitor 2",
      "Alternative solutions"
    ]
  },
  "team": [
    "Founder 1: Name - Background and relevant experience",
    "Founder 2: Name - Background and relevant experience",
    "Key hire: Name - Background and why they matter",
    "Notable advisors"
  ],
  "financials": [
    "Raising: $X seed/Series A round",
    "Use of funds: XX% engineering, XX% sales, XX% ops",
    "Milestones with this funding",
    "Runway: X-X months to next milestone"
  ]
}
```

**Notes:**
- All fields are optional except `company_name`
- Use arrays for bullet points (will be rendered as bullet lists)
- Competition can be either an object with `our_advantages` and `competitors` keys (for two-column layout) or a simple array
- Keep bullet points concise (1-2 lines each)
- Include specific numbers and metrics where possible

### Step 4: Generate the PowerPoint

Execute the Python script to create the PowerPoint presentation:

```bash
python3 scripts/create_pitch_deck.py pitch_data.json output_filename.pptx
```

The script will:
- Generate a professional PowerPoint file with proper formatting
- Apply consistent color scheme and typography
- Create slides based on available data (skipping sections if data not provided)
- Output a `.pptx` file ready for presentation or further customization

### Step 5: Review and Iterate

Present the generated pitch deck location to the user and offer to:
- Add missing sections if information becomes available
- Refine bullet points for clarity and impact
- Adjust structure based on specific audience (investor vs. sales pitch)
- Provide guidance on presenting the deck

**Iteration approach:**
- User can update the JSON file with new information
- Re-run the script to regenerate the updated presentation
- For design customizations beyond the script's capabilities, advise manual editing in PowerPoint

## Design Guidelines

The generated pitch deck follows these design principles:

**Color Scheme:**
- Primary: Blue (#2962FF) for titles and emphasis
- Secondary: Gray (#646464) for body text
- Clean white background for readability

**Typography:**
- Title slides: 54pt bold
- Section titles: 40pt bold
- Body text: 18-20pt with appropriate line spacing

**Layout:**
- Consistent margins and spacing
- One key message per slide
- Bullet points limited to 3-5 items per slide
- Two-column layouts for comparison slides

**Visual Hierarchy:**
- Clear title at top of each slide
- Content organized with proper spacing
- Emphasis on readability and professional appearance

## Best Practices Reference

For detailed guidance on pitch deck content, structure, and presentation tips, reference:
- `references/pitch_deck_best_practices.md` - Comprehensive guide covering:
  - Standard 10-slide structure with examples
  - Content guidelines for each slide type
  - Design best practices
  - Common mistakes to avoid
  - Tailoring for different audiences (investor, sales, product launch)
  - Pre-pitch checklist

Load this reference when providing detailed advice on pitch content or structure.

## Example Usage Scenarios

**Scenario 1: Early-stage startup seeking seed funding**
- Focus on problem, solution, market opportunity, and team
- Emphasize founder expertise and early traction
- Include clear funding ask and use of funds

**Scenario 2: Growth-stage company creating sales deck**
- Emphasize product features and customer ROI
- Include customer testimonials and case studies
- De-emphasize fundraising, focus on value proposition

**Scenario 3: Product launch presentation**
- Focus on product features and market need
- Include demo or product screenshots
- Emphasize innovation and competitive positioning

## Customization and Extensions

After generating the base deck:
- Users can manually add images, charts, and custom graphics in PowerPoint
- Suggest creating appendix slides for detailed backup information
- Recommend PDF export for sharing (File → Save As → PDF in PowerPoint)
- Advise on presentation timing (typically 10-15 minutes for 10 slides)

## Troubleshooting

**Script errors:**
- Ensure `python-pptx` library is installed: `pip3 install python-pptx`
- Verify JSON file is properly formatted (use JSON validator if needed)
- Check file paths are correct and user has write permissions

**Content issues:**
- If slides appear crowded, reduce bullet points to 3-5 per slide
- For complex competition analysis, consider manually creating comparison tables in PowerPoint
- For financial projections, consider creating charts in Excel and importing as images

## Resources

### scripts/
- `create_pitch_deck.py`: Python script that generates PowerPoint presentations from structured JSON data

### references/
- `pitch_deck_best_practices.md`: Comprehensive guide on pitch deck content, structure, and design principles
