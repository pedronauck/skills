---
name: startup-validator
description: Comprehensive startup idea validation and market analysis tool. Use when users need to evaluate a startup idea, assess market fit, analyze competition, validate problem-solution fit, or determine market positioning. Triggers include requests to "validate my startup idea", "analyze market opportunity", "check if there's demand for", "research competition for", "evaluate business idea", or "see if my idea is viable". Provides data-driven analysis using web search, market frameworks, competitive research, and positioning recommendations.
---

# Startup Validator

A comprehensive tool for analyzing startup ideas through systematic market research, competitive analysis, problem validation, and positioning strategy. This skill helps evaluate whether a startup idea has genuine market potential and how to position it effectively.

## Core Workflow

When a user presents a startup idea, follow this systematic validation process:

### 1. Idea Clarification & Scoping (2-3 minutes)

Ensure complete understanding before research begins:

**Extract key information:**
- Problem being solved
- Target customer/market
- Proposed solution
- Business model (if mentioned)
- Geographic focus (default: global/US)

**Ask clarifying questions only if critical information is missing:**
- "Who specifically is your target customer?"
- "What problem are they currently facing?"
- "How are they solving this problem today?"

**Do not ask** for information you can research independently (market size, competitors, trends).

### 2. Research Plan Development (1 minute)

Based on the idea, create a research plan identifying:
- Market size queries needed
- Competitor research keywords
- Problem validation searches
- Trend analysis topics
- Pricing/business model research

Use templates from `references/research_templates.md` for query formulation.

### 3. Comprehensive Market Research (10-15 tool calls minimum)

Execute systematic research across all dimensions. **Always use at least 10-15 web searches** to ensure thorough analysis.

#### A. Market Opportunity (3-5 searches)
Search for:
- Market size and projections
- Growth rates and trends
- TAM/SAM calculations
- Industry reports and forecasts

**Query examples:**
- "[industry] market size 2025"
- "global [product category] market forecast"
- "[industry] growth rate CAGR"

#### B. Competitive Landscape (3-5 searches)
Search for:
- Direct competitors
- Alternative solutions
- Market leaders
- Recent funding/acquisitions

**Query examples:**
- "[solution type] companies"
- "[product category] alternatives"
- "best [product type] 2025"
- "[industry] startups funding"

#### C. Problem Validation (2-3 searches)
Search for:
- Evidence of the problem
- Current pain points
- Customer behavior patterns
- Existing budget allocation

**Query examples:**
- "[target customer] challenges [industry]"
- "why [target customer] need [solution]"
- "[problem] statistics"

#### D. Market Trends (2-3 searches)
Search for:
- Technology trends
- Regulatory changes
- Consumer behavior shifts
- Investment patterns

**Query examples:**
- "[industry] trends 2025"
- "future of [technology/market]"
- "[industry] investment report"

#### E. Business Model Research (1-2 searches)
Search for:
- Pricing models in the space
- Unit economics benchmarks
- Customer acquisition strategies

**Query examples:**
- "[product] pricing models"
- "[industry] average customer acquisition cost"

**CRITICAL:** Use `web_fetch` to read full articles from authoritative sources (Gartner, McKinsey, Statista, Crunchbase, industry reports) to get detailed data, not just snippets.

### 4. Data Analysis & Synthesis

After gathering data, analyze using frameworks from `references/frameworks.md`:

#### Market Opportunity Assessment
- Calculate/estimate TAM, SAM, SOM
- Evaluate growth trajectory
- Identify market trends (favorable/unfavorable)
- Assess market maturity stage

#### Competitive Positioning
- Map competitive landscape (direct/indirect/adjacent)
- Identify market gaps
- Evaluate barriers to entry
- Assess competitive advantages needed

#### Problem-Solution Fit
- Validate problem frequency and intensity
- Assess willingness to pay
- Evaluate current solutions and their limitations
- Identify unique value proposition opportunities

#### Business Model Viability
- Estimate unit economics potential
- Assess scalability
- Evaluate pricing power
- Consider customer acquisition channels

**Optional:** If quantitative data is available, create a JSON file and use `scripts/market_analyzer.py` to calculate metrics and generate additional insights.

### 5. Risk & Opportunity Identification

Clearly articulate:
- **Critical Risks:** Deal-breakers or major challenges
- **Manageable Risks:** Solvable with strategy/execution
- **Key Opportunities:** Market gaps, timing advantages, trends
- **Assumptions to Validate:** Hypotheses needing testing

### 6. Positioning Strategy

Develop specific recommendations:
- **Target Market Segmentation:** Primary beachhead market
- **Value Proposition:** Core benefit statement
- **Differentiation Strategy:** How to stand out
- **Go-to-Market Approach:** Distribution and acquisition strategy
- **Positioning Statement:** Concise market positioning

### 7. Report Generation

Create a comprehensive markdown report with:

```markdown
# [Startup Idea] Validation Report

## Executive Summary
- One-paragraph overview
- Bottom-line recommendation: STRONG GO / PROCEED WITH VALIDATION / PIVOT RECOMMENDED / NOT VIABLE
- 3-5 key findings

## Market Analysis
### Market Size & Growth
- TAM/SAM/SOM estimates with sources
- Growth rate and trajectory
- Market maturity assessment

### Market Trends
- Key favorable trends
- Potential headwinds
- Timing considerations

## Competitive Landscape
### Direct Competitors
- List with brief descriptions
- Market share/position
- Strengths and weaknesses

### Indirect Competition
- Alternative solutions
- Substitutes

### Competitive Gaps
- Unmet needs
- Positioning opportunities

## Problem-Solution Fit
### Problem Validation
- Evidence of problem
- Frequency and intensity
- Current solutions and limitations

### Solution Differentiation
- Unique value proposition
- Competitive advantages
- Potential moats

## Business Model Assessment
### Revenue Model
- Pricing strategy alignment
- Unit economics potential
- Scalability factors

### Customer Acquisition
- Primary channels
- CAC considerations
- Sales cycle estimates

## Risk Analysis
### Critical Risks
- Deal-breakers
- Major challenges

### Manageable Risks
- Addressable concerns
- Mitigation strategies

## Positioning Recommendations
### Target Market
- Primary customer segment
- Beachhead market strategy

### Value Proposition
- Core benefit statement
- Key differentiators

### Go-to-Market Strategy
- Distribution approach
- Partnership opportunities
- Initial traction strategy

## Validation Next Steps
1. Immediate actions to validate assumptions
2. Customer interviews needed
3. MVPs or prototypes to test
4. Metrics to track

## Sources
[List all key sources with links]
```

**Formatting Guidelines:**
- Use clear headers and subheaders
- Bold key metrics and findings
- Include specific numbers with sources
- Use bullet points for scannability
- Cite sources inline with links
- Keep executive summary under 200 words

## Quality Standards

### Research Thoroughness
- **Minimum 10-15 web searches** across all dimensions
- Use authoritative sources (prioritize: Gartner, Forrester, McKinsey, Statista, Crunchbase, industry analysts)
- Cross-validate data from multiple sources
- Fetch full articles for detailed analysis, not just snippets

### Analysis Depth
- Apply multiple frameworks from `references/frameworks.md`
- Provide specific numbers and estimates (not vague statements)
- Identify both opportunities AND risks
- Include actionable recommendations

### Report Quality
- Clear executive summary with definitive recommendation
- Well-structured with logical flow
- Specific and actionable insights
- Properly cited sources
- Honest about data limitations and assumptions

## Bundled Resources

### `references/frameworks.md`
Comprehensive market analysis frameworks including:
- TAM/SAM/SOM analysis methodology
- Porter's Five Forces
- Problem-solution fit criteria
- Business model assessment frameworks
- Risk assessment categories
- Positioning frameworks

**When to use:** Reference throughout analysis to ensure comprehensive evaluation across all dimensions.

### `references/research_templates.md`
Search query templates and reliable data sources including:
- Market size research queries
- Competitive analysis searches
- Problem validation queries
- Trend analysis keywords
- Recommended data sources by category
- Source quality hierarchy

**When to use:** During research planning and execution to formulate effective searches and identify authoritative sources.

### `scripts/market_analyzer.py`
Python script for quantitative market analysis:
- Market metric calculations (TAM/SAM/SOM percentages, growth projections)
- Unit economics analysis (LTV:CAC, payback period, margins)
- Viability scoring algorithm
- Automated report generation

**When to use:** When quantitative data is available and calculations would strengthen the analysis. Input data via JSON file, outputs calculated metrics and markdown report sections.

**Example usage:**
```bash
python scripts/market_analyzer.py analysis_data.json
```

**Input format:**
```json
{
  "startup_name": "Example Startup",
  "market_data": {
    "tam": 10000000000,
    "sam": 2000000000,
    "som": 200000000,
    "current_market_size": 5000000000,
    "growth_rate": 15,
    "years": 5,
    "competition_level": "medium",
    "market_maturity": "growing"
  },
  "business_data": {
    "cac": 500,
    "ltv": 2000,
    "monthly_revenue": 50,
    "revenue": 1000,
    "cost": 300
  }
}
```

## Common Pitfalls to Avoid

1. **Insufficient research:** Do not rely on 1-3 searches. Always conduct 10-15+ searches minimum.

2. **Vague conclusions:** Avoid statements like "the market is large" without specific numbers.

3. **Missing critical dimensions:** Ensure analysis covers market opportunity, competition, problem validation, trends, and business model.

4. **Over-optimism:** Present balanced view including real risks and challenges.

5. **Poor source quality:** Prioritize primary sources and reputable analysts over blog posts and promotional content.

6. **Ignoring timing:** Market readiness and trend timing are critical factors.

7. **No actionable recommendations:** Always provide specific next steps for validation.

## Example Trigger Phrases

Users may request validation using phrases like:
- "Validate my startup idea about..."
- "Is there a market for..."
- "Analyze the opportunity for..."
- "Research if people need..."
- "Check competition for..."
- "See if my business idea is viable..."
- "Evaluate this concept..."
- "Do market research on..."
- "What's the potential for..."
