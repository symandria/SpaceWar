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

## Available States

- **[TDD.md](TDD.md)**: Test-Driven Development - Writing tests before implementation
- **[EXPLORATORY.md](EXPLORATORY.md)**: Exploratory Programming - Discovering solutions through experimentation
- **[DEBUG.md](DEBUG.md)**: Debugging - Systematically finding and fixing bugs
- **[REFACTOR.md](REFACTOR.md)**: Refactoring - Improving code structure without changing behavior
- **[REVIEW.md](REVIEW.md)**: Code Review - Evaluating code quality and suggesting improvements
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Architecture Planning - Designing high-level system structures

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

As you work with these states, note what works well and what could be improved. The state definitions should evolve based on practical experience to become more effective over time. 