# AI States Documentation

This directory contains detailed guides for the different AI development states used in the SpaceWar project. These states help maintain focus, consistency, and quality during development.

## Purpose of AI States

AI states are structured approaches that guide development work with clear processes and checkpoints. Using explicit state markers and disciplined practices helps the AI maintain focus on a specific development approach, resulting in higher quality code and fewer context-switching errors.

## Core Principles

1. **Explicit State Marking**: Always mark the current state with appropriate markers
2. **State Discipline**: Fully commit to one state at a time with explicit transitions
3. **Regular Reminders**: Periodically remind yourself of the current state
4. **Non-Fragile Code**: Each state emphasizes practices that lead to maintainable, extensible code
5. **Completion Before Transition**: Complete the current state fully before transitioning
6. **Checklist-Driven Development**: Follow user-defined checklists rigorously, implementing exactly what is required

## Avoiding Code Duplication and Inappropriate Reuse

Across all states, maintain awareness of the existing codebase to avoid these common issues:

1. **Search Before Creating**: Before implementing new functionality, thoroughly search the codebase to determine if similar code already exists that could be leveraged or extended.

2. **Verify Appropriate Reuse**: When reusing existing code, ensure it's appropriate for the new use case and won't violate the Single Responsibility Principle by serving multiple purposes.

3. **Balance Concerns**: Weigh the benefits of code reuse against the risks of tight coupling or creating components with multiple reasons to change.

4. **Document Decisions**: Whether creating new code or reusing existing components, document the rationale behind your decision to aid future maintenance.

This balanced approach prevents both unnecessary duplication ("reinventing the wheel") and inappropriate reuse that leads to fragile, tightly coupled code.

## Available States

- **[CHECKLIST.md](CHECKLIST.md)**: Checklist Workflow - Systematically breaking down and implementing user requirements
- **[TDD.md](TDD.md)**: Test-Driven Development - Writing tests before implementation
- **[EXPLORATORY.md](EXPLORATORY.md)**: Exploratory Programming - Discovering solutions through experimentation
- **[DEBUG.md](DEBUG.md)**: Debugging - Systematically finding and fixing bugs
- **[REFACTOR.md](REFACTOR.md)**: Refactoring - Improving code structure without changing behavior
- **[REVIEW.md](REVIEW.md)**: Code Review - Evaluating code quality and suggesting improvements
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Architecture Planning - Designing high-level system structures

## Workflow Integration

The CHECKLIST state works in conjunction with other states in the following way:

1. **CHECKLIST** provides the overall framework for working through user requirements
2. Other states (**TDD**, **EXPLORATORY**, etc.) are used during implementation of specific subtasks
3. Transitions between states are explicitly marked and documented

A typical workflow might look like:
```
[STATE: CHECKLIST] Working on "Implement game board component"
[STATE: CHECKLIST] [BREAKDOWN] Breaking down into subtasks
...
[STATE: CHECKLIST] [IMPLEMENTATION] Implementing collision detection
[TRANSITION: TDD] Implementing collision detection with TDD
...
[TRANSITION: CHECKLIST] Returning to checklist after implementing collision detection
[STATE: CHECKLIST] [VERIFICATION] Verifying game board component meets requirements
```

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

## How to Use AI States

### Loading a State

When beginning work on a task:

1. Determine the most appropriate state for the task
2. Read the corresponding state file carefully
3. Begin using the explicit state markers immediately
4. Follow the documented workflow and best practices

### Interpreting State Markers

State markers follow this pattern:
```
[STATE: NAME] Context information
[STATE: NAME] [PHASE] Specific phase information
```

These markers:
- Make the current state explicit
- Document the specific phase within the state
- Provide context for the current activity
- Maintain focus and discipline throughout the development process

### Transitioning Between States

When transitioning between states:
1. Complete the current state's workflow
2. Mark the transition explicitly using the transition marker
3. Read the new state file carefully
4. Begin using the new state's markers

Example transition:
```
[STATE: TDD] [REFACTOR] Refactoring complete, all tests passing
[TRANSITION: REVIEW] Moving to code review for final evaluation
```

### Customizing States

These state files can be updated as the team learns more about effective AI development practices. Consider:

1. Refining the workflows based on project experience
2. Adding project-specific examples
3. Updating state markers for clarity
4. Adding new states as needed

## Feedback

The effectiveness of these AI states should be regularly assessed. If you find that a state definition could be improved, please update the corresponding file and document the rationale for the changes. 