---
name: deep-research
description: Perform comprehensive research and analysis using multiple discovery and analysis tools to provide a solid foundation for complex tasks.
---

# Deep Research

This skill provides a systematic approach to researching and analyzing the codebase and external dependencies. It is designed to be used before starting complex implementation tasks.

<critical_tools>
You MUST strictly follow the rules defined in the project's command guides.

1. **Local Code Discovery**
   - **REQUIRED SUB-SKILL:** Use `codebase_search` for local code discovery.
   - **MANDATORY**: Use codebase_search for local code discovery.

2. **Sourcebot (External Search)**
   - Reference: `.claude/commands/sourcebot.md`
   - **MANDATORY**: Use Sourcebot (5-7 times) for **EXTERNAL** libraries/frameworks only.
   - **NEVER** use it for local code.
   - **Workflow**: `list_repos` -> Identify ID -> `search_code` with `filterByRepoIds`.

3. **Pal MCP Toolkit (Architecture Analysis)**
   - Reference: `.claude/commands/pal.md` (unified Pal skill)
   - **MANDATORY**: Use `pal` skill and appropriate Pal MCP tools before complex tasks.
   - **Available Tools**: `mcp__zen__analyze`, `mcp__zen__debug`, `mcp__zen__planner`, `mcp__zen__refactor`, `mcp__zen__codereview`, `mcp__zen__tracer`
   - **Scope**: Architecture, Quality, Performance, Security, Tech Debt.
   - **CRITICAL ENFORCEMENT**:
     - **YOU MUST ALWAYS** complete ALL THE STEPS when using any Pal MCP tool.
     - **NEVER** stop in the middle of the steps.
     - If you don't complete the steps until `next_step_required: false`, YOUR TASK WILL BE INVALIDATED.
     - **NO EXCEPTIONS**.
   - **MODEL REQUIREMENT**:
     - **MANDATORY**: Always use `model: "anthropic/claude-opus-4.6"` for ALL Pal MCP tool calls.
     - **NEVER** use any other model when calling Pal MCP tools.

4. **Context7 & Perplexity (External Knowledge)**
   - Reference: `.claude/commands/perplexity.md`
   - **Context7**: Use for **3rd party libraries NOT in Sourcebot**. Resolve ID -> Get Docs.
   - **Perplexity**: Use for **ANY** broad research, latest docs, or debugging.
     </critical_tools>

<research_strategy>
**MANDATORY: You MUST use your tools for EVERY research task. NO EXCEPTIONS.**

1. **Understand the Request**: Identify the specific task, goal, or question.
2. **Internal Discovery**:
   - **REQUIRED SUB-SKILL:** Use `codebase_search` for local code discovery.
   - Search for relevant local code concepts, patterns, and files using natural language.
   - Identify existing architectural patterns.
   - Use `codebase_search` to search specific areas.
3. **External Research (Sourcebot)**:
   - If the task involves external libraries, search for their usage patterns and docs using Sourcebot.
4. **External Knowledge (Context7 & Perplexity)**:
   - Use Context7 for libraries not in Sourcebot.
   - Use Perplexity for broad research or debugging.
5. **Deep Analysis (Pal Analyze)**:
   - Run the `zen_analyze` tool to get a comprehensive view of the architecture, risks, and quality.
   - Complete the analysis loop.
6. **Synthesize**: Combine findings from all sources into the final report.
   </research_strategy>

<quality_standards>

- **MANDATORY**: Use tools extensively before answering.
- **Conciseness**: Keep summaries high-signal and low-noise.
- **Authoritative**: Prioritize findings from the codebase and official documentation (via Sourcebot/Context7).
- **No Hallucinations**: NEVER include information not found via tools.
- **Direct Output**: Do NOT create files. Return the report directly in the chat.
  </quality_standards>

<output_format>
Return a SINGLE comprehensive message with the following structure:

# Deep Analysis Report: [Topic]

### 1. Context Summary

[Concise summary of what was found in the local codebase, including key files and architectural patterns]

### 2. External Insights

[Relevant patterns, best practices, or documentation found for external libraries]

### 3. Deep Analysis Findings

[Insights on Architecture, Security, Performance, and Tech Debt derived from Pal Analyze]

### 4. Implementation Plan / Recommendations

[Concrete next steps, solution design, or answer to the user's request]

### 5. Relevant Files

[List of absolute paths to the most important files discovered during research]
</output_format>
