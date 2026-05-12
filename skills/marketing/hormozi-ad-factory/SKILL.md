---
name: hormozi-ad-factory
description: Generates 150-750+ ad variations using Alex Hormozi's combinatorial Hook x Meat x CTA framework. Triggers on requests to create ads, ad copy, ad scripts, marketing creatives, video ad scripts, ad hooks, CTAs, ad testing, ad scaling, or ad factories. Also triggers on mentions of Hormozi's ad method or combinatorial ad creation. Does not trigger for general copywriting, email marketing, landing pages, or non-advertising content.
---

# Hormozi Ad Factory

A systematic framework for generating 150-750+ unique ad variations from a single product or offer, based on Alex Hormozi's combinatorial ad creation method.

## Core Concept

Ads consist of three modular parts: **Hook**, **Meat**, and **CTA**. Instead of writing one ad at a time, generate each component independently, then combine them:

- 50 Hooks x 3-5 Meats x 1-3 CTAs = **150 to 750 unique ads**

This approach creates massive variety for testing, which is what wins at scale.

## Workflow

Execute the following four steps in order. Before starting, gather context from the user.

### Step 0: Gather Context

Before generating any ad components, ask the user these questions (skip any the user has already answered):

1. **Product/Offer**: What product, service, or offer is being advertised?
2. **Target Audience**: Who is the ideal customer? (demographics, psychographics, pain points)
3. **Platform**: Where will these ads run? (Instagram, YouTube, TikTok, Facebook, LinkedIn, Google)
4. **Format**: Text ads, video scripts, carousel, or a mix?
5. **Existing Assets**: Are there any past ads that performed well? Any organic content with strong engagement?
6. **Competitor References**: Any competitor ads to draw inspiration from?
7. **Unique Mechanism**: What makes this product/approach different from alternatives?
8. **Key Results/Proof**: Specific numbers, testimonials, or case studies available?
9. **Language**: Default to English. For Portuguese-speaking users, generate all content in Portuguese (BR) unless told otherwise.

If the user provides minimal context, infer reasonable defaults and state the assumptions clearly before proceeding.

### Step 1: Generate 50 Hooks

Hooks are the first 1-3 seconds (video) or first line (text) of the ad. They stop the scroll and earn attention. Use these five sourcing methods to create variety:

1. **Winning hooks from previous ads** — Adapt hooks from the user's past high-performing ads.
2. **Hooks from organic content** — Pull hooks from the user's best-performing free content.
3. **Winning hooks from competitors** — Adapt proven hooks from competitor paid ads.
4. **Hooks from competitors' organic content** — Pull hooks from competitor top free content.
5. **Platform ad libraries** — Use hooks found in Facebook Ad Library, TikTok Creative Center, etc.

Distribute the 50 hooks across **awareness levels** to cover different audience segments:

| Level | Description | Hook Style |
|-------|-------------|------------|
| Unaware | Does not know they have a problem | Pattern interrupt, curiosity, shock |
| Problem-Aware | Knows the problem, not the solution | Call out the pain, frustration, desire |
| Solution-Aware | Knows solutions exist, has not chosen one | Compare approaches, reveal flaws in alternatives |
| Product-Aware | Knows the product, has not bought | Overcome objections, social proof, urgency |
| Most Aware | Knows the product well, needs a push | Deals, bonuses, scarcity, direct offer |

Default to a balanced spread (~10 hooks per level) unless the user specifies a focus.

For hook formula templates and examples, read `references/hook-formulas.md`.

### Step 2: Generate 3-5 Meats

The meat is the body of the ad — it educates the audience on the offer, the product, the solution, or the problem. Generate one meat per format:

1. **Demonstration** — Show the product/service in action. Best for product-aware audiences.
2. **Testimonial** — Let customers tell the story. Best for solution-aware and product-aware audiences.
3. **Educational** — Teach something valuable. Best for problem-aware and solution-aware audiences.
4. **Story** — Tell a narrative (founder story, customer journey, transformation). Best for unaware and problem-aware audiences.
5. **Faceless** — Text on screen, voiceover, b-roll, or screen recordings. Best for scaling without personal brand dependency.

Each meat must be self-contained and work with any hook and any CTA.

For detailed meat structures and length guidelines, read `references/meat-formats.md`.

### Step 3: Generate 1-3 CTAs

The CTA tells the viewer exactly what to do next. A strong CTA includes up to five elements:

1. **What to do** — The specific action (click, comment, DM, sign up, buy)
2. **How to do it** — The mechanic (click the link below, comment "X", tap the button)
3. **What they get** — The immediate result of taking action
4. **Why now** — Urgency or scarcity element
5. **Risk reversal** — Remove the fear (free trial, money-back, no commitment)

Not every CTA needs all five, but the best ones cover most of them.

For CTA templates and examples, read `references/cta-templates.md`.

### Step 4: Assemble the Combinations

After generating all components, combine them into a matrix. Present the output as:

1. **Summary table** showing total combinations (Hooks x Meats x CTAs)
2. **Top 10-15 "golden" combinations** — the ones most likely to perform well based on audience-message fit, with rationale for each
3. **Full component library** organized by type, for the user to mix and match

For the full output format template, read `assets/output-template.md`.

## Platform Adaptation

Adapt the format of each component based on the target platform:

| Platform | Hook | Meat | CTA |
|----------|------|------|-----|
| **Video ads** (TikTok, YouTube, Reels) | Opening line/scene (1-3s) | Script section with visual directions (15-45s) | Closing sequence with on-screen text |
| **Text/copy ads** (Facebook, LinkedIn) | Headline or opening line | Body copy paragraphs (3-8 sentences) | Closing paragraph with link |
| **Carousel ads** (Instagram, LinkedIn) | Slide 1 | Slides 2-8 | Last slide |
| **Short-form** (Twitter/X, Stories) | Single punchy line | 1-3 sentences max | Inline CTA |

## Error Handling

- **User provides no product info**: Do not generate ads. Ask for at minimum: product name, what it does, and who it is for.
- **Vague audience**: Generate hooks for all five awareness levels with a balanced spread and note the assumption.
- **Too many platforms**: Generate a single platform-agnostic set first, then offer to adapt for specific platforms.
- **User wants fewer than 50 hooks**: Adjust proportionally but maintain the awareness-level distribution.
- **User wants full ads, not components**: Generate the components first, then assemble the top 15 golden combinations as complete ready-to-use ads.

## Examples

### Example 1: SaaS Product

**User**: "Generate ads for my project management tool aimed at remote teams."

**Process**:
1. Clarify: pricing, key differentiator, existing testimonials, platform
2. Generate 50 hooks across awareness levels (e.g., "Your remote team is wasting 5 hours/week in status meetings" for problem-aware)
3. Generate 4 meats: demo walkthrough, customer testimonial, educational ("3 signs your PM tool is slowing you down"), founder story
4. Generate 2 CTAs: free trial (risk reversal) + limited-time discount (urgency)
5. Assemble 400 combinations, highlight top 15 golden ads

### Example 2: Physical Product (Portuguese)

**User**: "Crie anuncios para meu curso de culinaria online para iniciantes."

**Process**:
1. All content generated in Portuguese (BR)
2. Hooks adapted for cooking/education audience awareness levels
3. Meats include: demo (cooking a recipe), testimonial (student transformation), educational (common beginner mistakes)
4. CTAs include engagement ("Comente RECEITA") and direct ("Clique no link da bio")
5. Golden combinations prioritize video format for Instagram/TikTok

### Example 3: Minimal Context

**User**: "I need some ad ideas for my coaching business."

**Process**:
1. Ask: What type of coaching? Who is the target client? What platform? What is the offer/price point?
2. Wait for answers before generating
3. If user says "just give me something," state assumptions explicitly and proceed with a general framework
