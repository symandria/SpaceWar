# AI State: Checklist Workflow

## Purpose
This state guides the AI in systematically working through user-defined checklists, ensuring that implementation precisely matches requirements while maintaining a self-documenting development process.

## When to Use This State
- When working through a structured roadmap or plan
- When implementing features with clearly defined requirements
- When complex tasks need to be broken into manageable steps
- When strict adherence to specifications is required
- When documentation of implementation decisions is important

## State Maintenance Protocol
To maintain this CHECKLIST state throughout the session, you MUST:

1. **Always verify each checklist item** against the original requirements
2. **Document all decisions and verifications** directly in the checklist file
3. **Break down complex items** into detailed subtasks
4. **Verify that implementations meet requirements** but don't exceed scope
5. **Maintain discipline** by explicitly marking progress on each item

### Required State Markers
```
[STATE: CHECKLIST] Working on {checklist_item}
[STATE: CHECKLIST] [BREAKDOWN] Subtask analysis for {checklist_item}
[STATE: CHECKLIST] [IMPLEMENTATION] Implementing {subtask}
[STATE: CHECKLIST] [VERIFICATION] Verifying {checklist_item} meets requirements
[STATE: CHECKLIST] [SCOPE-CHECK] Verifying no scope creep in {checklist_item}
[STATE: CHECKLIST] [COMPLETE] {checklist_item} is complete and verified
```

## The Checklist Workflow

### 1. Analyze Checklist Item
```
[STATE: CHECKLIST] Working on {checklist_item}
[STATE: CHECKLIST] [BREAKDOWN] Subtask analysis for {checklist_item}
```

- Review the checklist item thoroughly
- Break down complex items into clear, manageable subtasks
- Define expected outcomes for each subtask
- Specify verification methods for each subtask
- Document this breakdown in the checklist file

#### Standard Subtask Documentation Format
```
TASK: [Original roadmap/checklist item]

SUBTASKS:
[ ] 1. [Specific implementation step]
  - Expected Outcome: [What completing this will achieve]
  - Verification Method: [How we'll know it's done correctly]
[ ] 2. [Next implementation step]
  ...

VERIFICATION:
- Complete Requirements Test: [How we'll verify all requirements are met]
- Scope Containment Test: [How we'll verify nothing extra was added]
```

### 2. Implement Subtasks
```
[STATE: CHECKLIST] [IMPLEMENTATION] Implementing {subtask}
```

- Implement each subtask according to the breakdown
- Document implementation decisions and approaches
- Use appropriate AI states (TDD, EXPLORATORY, etc.) during implementation
- Mark subtasks as completed when finished
- Add implementation notes to the checklist file

### 3. Verify Implementation
```
[STATE: CHECKLIST] [VERIFICATION] Verifying {checklist_item} meets requirements
```

- Verify that the implementation satisfies the original requirements
- Execute the defined verification methods for each subtask
- Document verification results in the checklist file
- Ensure all expected outcomes have been achieved

### 4. Check Scope Containment
```
[STATE: CHECKLIST] [SCOPE-CHECK] Verifying no scope creep in {checklist_item}
```

- Ensure the implementation does not exceed the original requirements
- Identify and document any additions beyond the specified scope
- Remove or flag any functionality not specified in the requirements
- Document scope verification in the checklist file

### 5. Mark Item as Complete
```
[STATE: CHECKLIST] [COMPLETE] {checklist_item} is complete and verified
```

- Mark the checklist item as complete
- Summarize what was implemented and how it was verified
- Document any lessons learned or considerations for future items
- Move to the next checklist item

## User Consultation Protocol

The AI should ONLY consult the user when:

1. A task **cannot be completed** as specified due to technical constraints or conflicts
2. A task **won't achieve what was intended** based on the AI's understanding of the project
3. There's a **critical flaw** in the specifications that would lead to problematic outcomes
4. Multiple valid **implementation alternatives** exist that would significantly impact future development

The AI should NOT consult the user:
- For routine implementation decisions
- For items that are merely incomplete (but progressing)
- For minor clarifications that can be reasonably inferred from context
- For verification that can be performed by the AI itself

## Checklist File Management

The AI will create and maintain checklist files that serve as both work plans and documentation:

1. **Main Checklist Files**: Based on the user's roadmap or high-level requirements
2. **Subtask Checklist Files**: Created by the AI to break down complex items
3. **Verification Documentation**: Added to checklist files during implementation

All checklist files should be stored in a structured location (e.g., `Documentation/Checklists/`) for easy reference.

## Best Practices for Checklist-Driven Development

### Clear Subtask Definition
- Make subtasks specific and actionable
- Include clear success criteria for each subtask
- Ensure subtasks collectively fulfill the original requirement
- Break down complex subtasks further if needed

### Thorough Verification
- Verify against the original requirements, not the subtask breakdown
- Include both positive verification (does it do what it should) and negative verification (does it avoid what it shouldn't)
- Document evidence of verification, not just a claim of verification
- Consider edge cases and potential issues

### Disciplined Scope Management
- Be vigilant about identifying scope creep
- Document and justify any additions beyond the original scope
- Consider the impact of implementation decisions on future checklist items
- Maintain focus on the current checklist item

## Example (Shortened)
```
TASK: Implement animated background system for splash screen

SUBTASKS:
[x] 1. Create Background class that supports multiple layers
  - Expected Outcome: A class that can render multi-layered backgrounds
  - Verification Method: Visually verify layers render correctly with test images

[x] 2. Implement animation system for background layers
  - Expected Outcome: Background layers can be animated independently
  - Verification Method: Verify different movement patterns on each layer

[x] 3. Add configuration options for animation speed and pattern
  - Expected Outcome: Animation parameters can be customized
  - Verification Method: Test changing parameters at runtime

VERIFICATION:
- Complete Requirements Test: Background system renders multiple layers with independent animations
- Scope Containment Test: System is focused only on background animation and doesn't include unrelated features like UI controls or interaction

STATUS: COMPLETE - All requirements satisfied with no scope creep
```

## Transitioning to Other States
When appropriate, transition to:

- **To TDD**: `[TRANSITION: TDD]` - When implementing testable components
- **To EXPLORATORY**: `[TRANSITION: EXPLORATORY]` - When implementing visual or interactive elements
- **To REFACTOR**: `[TRANSITION: REFACTOR]` - When improving existing code
- **To DEBUG**: `[TRANSITION: DEBUG]` - When fixing issues in implementation
- **To REVIEW**: `[TRANSITION: REVIEW]` - When evaluating completed implementation
- **To ARCHITECTURE**: `[TRANSITION: ARCHITECTURE]` - When designing implementation approach

## Required Discipline Practices

1. **At the start of a checklist item**: Define subtasks, expected outcomes, and verification methods
2. **During implementation**: Document progress and decisions in the checklist file
3. **After implementation**: Verify against requirements and check for scope containment
4. **Every few checklist items**: Verify alignment with overall project objectives
5. **If interrupted**: Re-read the checklist file to realign with current task
6. **Before marking complete**: Perform final verification against original requirements 