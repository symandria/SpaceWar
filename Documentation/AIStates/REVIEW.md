# AI State: Code Review

## Purpose
This state guides the AI in systematically evaluating code quality, identifying potential issues, and suggesting improvements. The focus is on ensuring correctness, maintainability, and adherence to project standards.

## When to Use This State
- When evaluating existing code for quality and correctness
- When checking for issues before merging changes
- When identifying opportunities for improvement
- When ensuring adherence to project standards
- When documenting design decisions and trade-offs

## State Maintenance Protocol
To maintain this REVIEW state throughout the session, you MUST:

1. **Systematically analyze the code** from multiple perspectives
2. **Mark each review phase** using the state markers below
3. **Document findings clearly** with specific examples
4. **Prioritize issues** by severity and impact
5. **Maintain discipline** by explicitly stating your current focus

### Required State Markers
```
[STATE: REVIEW] Reviewing {component/file}
[STATE: REVIEW] [CORRECTNESS] Evaluation of functional correctness
[STATE: REVIEW] [STRUCTURE] Evaluation of code organization
[STATE: REVIEW] [STYLE] Evaluation of code style and standards
[STATE: REVIEW] [PERFORMANCE] Evaluation of performance considerations
[STATE: REVIEW] [SECURITY] Evaluation of security considerations
[STATE: REVIEW] [TESTING] Evaluation of test coverage
[STATE: REVIEW] [SUMMARY] Summary of findings and recommendations
```

## The Code Review Workflow

### 1. Define Review Scope
```
[STATE: REVIEW] Reviewing {component/file}
```

- Clearly define what code is being reviewed
- Establish the context and purpose of the code
- Identify relevant requirements and constraints
- Note dependencies and interfaces

### 2. Correctness Review
```
[STATE: REVIEW] [CORRECTNESS] Evaluation of functional correctness
```

- Verify logic and algorithm correctness
- Check for edge cases and error handling
- Validate business logic implementation
- Ensure proper resource management
- Identify potential bugs or unexpected behaviors

### 3. Structural Review
```
[STATE: REVIEW] [STRUCTURE] Evaluation of code organization
```

- Evaluate class and method organization
- Check for proper separation of concerns
- Assess naming and abstraction quality
- Identify violations of SOLID principles
- Evaluate modularity and code reuse

### 4. Style Review
```
[STATE: REVIEW] [STYLE] Evaluation of code style and standards
```

- Check adherence to project coding standards
- Evaluate naming conventions
- Review comment quality and documentation
- Check formatting consistency
- Assess readability and maintainability

### 5. Performance Review
```
[STATE: REVIEW] [PERFORMANCE] Evaluation of performance considerations
```

- Identify potential performance bottlenecks
- Check resource usage efficiency
- Evaluate algorithm complexity
- Assess memory management
- Consider scalability implications

### 6. Security Review
```
[STATE: REVIEW] [SECURITY] Evaluation of security considerations
```

- Identify potential security vulnerabilities
- Check for proper input validation
- Evaluate authentication and authorization
- Assess data protection practices
- Review error messages for sensitive information

### 7. Testing Review
```
[STATE: REVIEW] [TESTING] Evaluation of test coverage
```

- Assess test coverage completeness
- Evaluate test quality and meaningfulness
- Check for edge case testing
- Verify test readability and maintainability
- Identify untested or undertested areas

### 8. Findings Summary
```
[STATE: REVIEW] [SUMMARY] Summary of findings and recommendations
```

- Prioritize findings by severity and impact
- Group related issues together
- Provide clear, actionable recommendations
- Recognize positive aspects of the code
- Suggest next steps based on findings

## Best Practices for Effective Code Reviews

### Systematic Approach
- Review systematically rather than randomly
- Use checklists to ensure thoroughness
- Focus on one aspect at a time
- Be specific about issues and recommendations
- Provide context and rationale for feedback

### Constructive Feedback
- Focus on the code, not the author
- Recognize positive aspects
- Suggest specific improvements
- Explain the reasoning behind feedback
- Prioritize issues rather than overwhelming

### Non-Fragile Code Principles
- Prefer composition over inheritance
- Look for tight coupling and suggest improvements
- Evaluate testability of the code design
- Check for proper abstraction and encapsulation
- Consider maintainability and future changes

## Example (Shortened)
```csharp
[STATE: REVIEW] Reviewing WeaponSystem.cs

[STATE: REVIEW] [CORRECTNESS]
- Weapon damage calculation correctly applies critical hit multipliers
- Edge case: Damage calculation doesn't handle negative defense values properly
- Error handling is missing when weapon data can't be loaded

[STATE: REVIEW] [STRUCTURE]
- Single responsibility principle violation: WeaponSystem handles both damage calculation and rendering
- Recommend extracting DamageCalculator class for better separation of concerns
- Method "UpdateWeaponState" is too long (75 lines) and should be broken down

[STATE: REVIEW] [PERFORMANCE]
- Recalculating weapon effects every frame even when not changed
- Suggest caching calculation results until inputs change

[STATE: REVIEW] [SUMMARY]
- Primary concerns: Missing error handling, SRP violations, performance optimizations
- Recommend: 1) Add proper error handling, 2) Extract damage calculator, 3) Implement caching
- Code is well-commented and generally follows naming conventions
```

## Common Pitfalls to Avoid
- **Nitpicking**: Focus on substantial issues over minor preferences
- **Inconsistent Standards**: Apply the same standards throughout the review
- **Vague Feedback**: Be specific about problems and solutions
- **Overlooking Positives**: Acknowledge what works well
- **Scope Creep**: Stay focused on the code being reviewed
- **Missing Context**: Consider the code's purpose and constraints

## Transitioning to Other States
When appropriate, transition to:

- **To REFACTOR**: `[TRANSITION: REFACTOR]` - When review identifies refactoring needs
- **To DEBUG**: `[TRANSITION: DEBUG]` - When review uncovers bugs
- **To TDD**: `[TRANSITION: TDD]` - When review reveals missing functionality
- **To ARCHITECTURE**: `[TRANSITION: ARCHITECTURE]` - When review suggests architectural changes

## Required Discipline Practices

1. **At the start of review**: Explicitly define the scope with `[STATE: REVIEW] Reviewing {component/file}`
2. **For each review aspect**: Mark with appropriate state marker like `[STATE: REVIEW] [CORRECTNESS]`
3. **After completing the review**: Summarize with `[STATE: REVIEW] [SUMMARY]`
4. **Every 15 minutes**: Remind yourself "I am reviewing {component/file} systematically"
5. **If interrupted**: Re-read this section to realign with REVIEW state
6. **For each finding**: Provide a specific example, explain the issue, and suggest an improvement 