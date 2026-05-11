# Pal Planner Reference

Expert guidance for using the Pal MCP planner tool for strategic planning and task breakdown.

## When to Use

- **Before complex tasks:** Break down complex tasks into manageable steps with clear dependencies
- **System design:** Plan architectural decisions and component design
- **Migration planning:** Develop migration strategies and execution plans
- **Project planning:** Define milestones, timelines, and resource requirements
- **Architectural decisions:** Evaluate technology choices and design alternatives
- **Implementation strategy:** Plan phased implementation and incremental delivery

## Planning Scope

The planner tool must analyze:

- **Task breakdown:** Decomposing complex tasks into manageable steps, identifying dependencies, sequencing work
- **System design:** Architectural decisions, component design, interface definitions, integration strategies
- **Migration strategies:** Migration paths, data transformation, backward compatibility, rollback plans
- **Project planning:** Milestone definition, resource allocation, timeline estimation, risk assessment
- **Architectural decisions:** Technology choices, pattern selection, trade-off analysis, design alternatives
- **Implementation strategy:** Phased approach, incremental delivery, testing strategy, deployment plan

## Required Parameters

```json
{
  "step": "Current planning phase description",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "model": "anthropic/claude-opus-4.6"
}
```

## Planning Approach

- Provide clear `step` description for each planning phase
- Use `step_number` to track planning progress (starts at 1)
- Set `total_steps` to estimated planning phases needed
- Use `next_step_required` to indicate if more planning is needed
- Document `findings` at each step covering task breakdown, dependencies, and strategy

## Advanced Features

### Step Revision

Use to refine previous steps as understanding deepens:

```json
{
  "is_step_revision": true,
  "revises_step_number": 2
}
```

### Branch Exploration

Use to explore alternative approaches:

```json
{
  "is_branch_point": true,
  "branch_from_step": 1,
  "branch_id": "approach-A"
}
```

### Scope Adjustment

```json
{
  "more_steps_needed": true
}
```

## Relevant Files

- Include full absolute paths to files or directories relevant to the planning scope
- Include related files that inform architectural decisions
- Include configuration files if planning system configuration changes
- Include test files to understand testing requirements and strategies

## Planning Process

1. Start with `step_number: 1` and outline the planning strategy
2. Progressively build the plan through multiple steps
3. Document `findings` at each step covering task breakdown, dependencies, and implementation strategy
4. Revise steps as needed using `is_step_revision` and `revises_step_number`
5. Create branches for alternative approaches when exploring options
6. Continue until comprehensive plan is achieved (`next_step_required: false`)

## Critical Requirements

- **MANDATORY**: Use Pal MCP planner tool **BEFORE INITIATING COMPLEX TASKS** or **WHEN NEEDING STRATEGIC PLANNING**
- **TASK INVALIDATION**: Task will be invalidated if you skip using the planner tool when required or don't complete ALL steps
- **NO EXCEPTIONS**: Complete the entire planning workflow (all steps until `next_step_required: false`) before proceeding with implementation
- **COMPLETE ALL STEPS**: Never stop in the middle of steps - completing partial workflows invalidates the task
- Use step revision capabilities to refine plans as understanding deepens
- Use branching capabilities to explore alternative approaches when multiple viable options exist
