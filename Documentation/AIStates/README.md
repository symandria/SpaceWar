# AI Working States for Game Development

This directory contains documentation files that define various working states for AI assistance during game development. Each state is designed to guide the AI in maintaining a specific mindset and workflow, ensuring consistent, high-quality contribution to the project.

## Purpose

These state files address a fundamental challenge when working with AI assistants: ensuring the AI maintains a consistent workflow and doesn't "forget" its operational mode during complex tasks. By explicitly loading these states at the beginning of a session, we create a shared understanding of how the AI should approach the current task.

## Available States

1. **[TDD.md](TDD.md)** - Test-Driven Development
   - For developing new features with tests first
   - Ensures code is tested and stable from the beginning
   - Follows the Red, Green, Refactor cycle

2. **[EXPLORATORY.md](EXPLORATORY.md)** - Exploratory Programming
   - For developing UI, visual components, or complex integrations
   - When traditional TDD might be impractical
   - Focuses on incremental development with clear verification

3. **[DEBUG.md](DEBUG.md)** - Debugging
   - For identifying and fixing bugs
   - Includes creating regression tests to prevent recurrence
   - Systematic approach to finding root causes

4. **[REFACTOR.md](REFACTOR.md)** - Refactoring
   - For improving existing code without changing behavior
   - Incremental improvements backed by tests
   - Following established refactoring patterns

5. **[REVIEW.md](REVIEW.md)** - Code Review
   - For evaluating code quality and correctness
   - Providing constructive feedback
   - Identifying potential issues and improvements

6. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture Planning
   - For designing high-level system structure
   - Planning components and their interactions
   - Making technology and pattern decisions

## How to Use

When starting a work session with the AI, begin by specifying which state you want the AI to operate in:

```
@AI please load the DEBUG state. I need help fixing an issue with the collision detection system.
```

The AI will then review the appropriate state file and acknowledge that it will operate in that mode:

```
[STATE: DEBUG] I'll help you debug the collision detection system using a systematic approach.
[PROBLEM] Let me first understand what issue you're experiencing with collisions.
```

Throughout the session, the AI will continue to tag its responses with the appropriate state markers to maintain focus.

## State Transitions

When the work requires a change in approach, you can request a state transition:

```
@AI We've identified the bug, but we need to refactor this code to prevent similar issues. Please transition to REFACTOR state.
```

Or the AI might suggest a transition:

```
[STATE: DEBUG] [ANALYSIS] I've found the root cause. The collision detection fails because of a deeper structural issue with how game objects are managed.
[TRANSITION: REFACTOR] We should refactor the game object management system to fix this issue properly. Would you like me to switch to refactoring mode?
```

## Benefits

1. **Consistency** - The AI maintains a consistent approach throughout the task
2. **Focus** - Clear boundaries for the current work mode prevent scope creep
3. **Quality** - Each state enforces best practices for that type of work
4. **Communication** - State markers make it clear what the AI is doing at each step
5. **Learning** - State documentation serves as a reference for development best practices

## Extending States

If you identify a new working mode that would benefit from explicit state guidance:

1. Create a new markdown file in this directory following the existing pattern
2. Define the purpose, workflow, and markers for the new state
3. Add the new state to this README
4. Reference it in your work with the AI

## Customizing States

Feel free to modify these state definitions to better match your project's specific needs or development philosophy. The key is to create a shared understanding between you and the AI assistant about how work should proceed in each context.

## Feedback

As you work with these states, note what works well and what could be improved. The state definitions should evolve based on practical experience to become more effective over time. 