# AI State: Refactoring

## Purpose
This state guides the AI in improving code structure, readability, and maintainability without changing behavior. The focus is on creating more robust, reusable, and adaptable code while maintaining full functionality.

## When to Use This State
- When code works but needs structural improvement
- When reducing duplication or complexity
- When improving performance with the same behavior
- When preparing code for extension or enhancement
- When adapting code to meet architecture standards

## State Maintenance Protocol
To maintain this REFACTOR state throughout the session, you MUST:

1. **Verify functionality before** making any changes
2. **Mark each refactoring phase** using the state markers below
3. **Make small, incremental refactoring steps**
4. **Verify functionality after** each change
5. **Maintain discipline** by explicitly stating your current phase

### Required State Markers
```
[STATE: REFACTOR] Refactoring {component/area}
[STATE: REFACTOR] [BEFORE] Description of current code issues
[STATE: REFACTOR] [VERIFY-BEFORE] Verification of current functionality
[STATE: REFACTOR] [STEP #N] Specific refactoring action
[STATE: REFACTOR] [VERIFY-AFTER] Verification that functionality is preserved
[STATE: REFACTOR] [AFTER] Description of improvements made
```

## The Refactoring Workflow

### 1. Analyze Code Issues
```
[STATE: REFACTOR] Refactoring {component/area}
[STATE: REFACTOR] [BEFORE] Description of current code issues
```

- Identify code smells and structural problems
- Document the current design and its limitations
- Prioritize refactoring targets by impact
- Consider architectural alignment

### 2. Verify Existing Functionality
```
[STATE: REFACTOR] [VERIFY-BEFORE] Verification of current functionality
```

- Document or run existing tests to establish baseline behavior
- Note edge cases and expected outputs
- Capture current performance metrics if relevant
- Create temporary tests if existing coverage is insufficient

### 3. Implement Refactoring in Small Steps
```
[STATE: REFACTOR] [STEP #1] Extract method for duplicate code
```

- Make one well-defined change at a time
- Apply standard refactoring patterns
- Keep each step simple and focused
- Document the purpose of each change

### 4. Verify Preserved Functionality
```
[STATE: REFACTOR] [VERIFY-AFTER] Verification that functionality is preserved
```

- Run tests to confirm behavior is unchanged
- Verify edge cases are still handled correctly
- Check performance impacts if relevant
- Document any unexpected changes

### 5. Summarize Improvements
```
[STATE: REFACTOR] [AFTER] Description of improvements made
```

- Document the structural improvements achieved
- Note any performance or maintainability benefits
- Highlight areas for potential future refactoring
- Explain how the new structure better supports the architecture

## Best Practices for Non-Fragile Refactoring

### Clean Code Principles
- Prioritize readability and simplicity
- Ensure each method/class has a single responsibility
- Create meaningful abstractions and naming
- Reduce coupling between components
- Increase cohesion within components

### Refactoring Techniques
- Extract Method/Class for code reuse
- Replace conditional logic with polymorphism
- Introduce interfaces for better abstraction
- Apply design patterns appropriately
- Move functionality to existing abstractions

### Safe Refactoring Approach
- Always verify before and after each change
- Commit after each successful refactoring step
- Work from the specific to the general
- Focus on creating testable code
- Maintain backward compatibility

## Example (Shortened)
```csharp
[STATE: REFACTOR] Refactoring weapon damage calculation system
[STATE: REFACTOR] [BEFORE] Current system has duplicate calculations spread across multiple classes

[STATE: REFACTOR] [VERIFY-BEFORE] Current tests for damage calculation all pass

[STATE: REFACTOR] [STEP #1] Extract common damage calculation logic to DamageCalculator class
// Implementation changes

[STATE: REFACTOR] [VERIFY-AFTER] All damage calculation tests still pass with new DamageCalculator

[STATE: REFACTOR] [STEP #2] Update weapon classes to use the DamageCalculator
// Implementation changes

[STATE: REFACTOR] [VERIFY-AFTER] Weapon behavior is unchanged in all test scenarios

[STATE: REFACTOR] [AFTER] Damage calculation now centralized in a single class, improving maintainability and making future damage system changes easier
```

## Common Refactoring Patterns
- **Extract Method**: Create focused, reusable methods
- **Extract Class**: Create new class for related functionality
- **Replace Conditional with Polymorphism**: Use inheritance instead of if/switch
- **Introduce Parameter Object**: Group related parameters
- **Replace Temp with Query**: Replace temporary variables with method calls
- **Encapsulate Field**: Hide implementation details
- **Move Method**: Place method closer to related data

## Common Pitfalls to Avoid
- **Changing Behavior**: Refactoring should never alter functionality
- **Giant Steps**: Refactoring in large chunks rather than small steps
- **Neglecting Tests**: Failing to verify before and after changes
- **Premature Abstraction**: Creating overly complex designs
- **Incomplete Refactoring**: Leaving the code in a transitional state
- **Mixing Refactoring with New Features**: Combine the two only when necessary

## Transitioning to Other States
When appropriate, transition to:

- **To TDD**: `[TRANSITION: TDD]` - When adding new features after refactoring
- **To DEBUG**: `[TRANSITION: DEBUG]` - When refactoring reveals bugs
- **To REVIEW**: `[TRANSITION: REVIEW]` - When refactoring is complete
- **To EXPLORATORY**: `[TRANSITION: EXPLORATORY]` - When exploring alternative designs

## Required Discipline Practices

1. **At the start of refactoring**: Explicitly define the scope with `[STATE: REFACTOR] Refactoring {component/area}`
2. **Before making changes**: Document issues with `[STATE: REFACTOR] [BEFORE]` and verify functionality with `[STATE: REFACTOR] [VERIFY-BEFORE]`
3. **For each refactoring step**: Mark with `[STATE: REFACTOR] [STEP #N]`
4. **After each step**: Verify with `[STATE: REFACTOR] [VERIFY-AFTER]`
5. **At completion**: Summarize with `[STATE: REFACTOR] [AFTER]`
6. **Every 15 minutes**: Remind yourself "I am refactoring {component/area} without changing behavior"
7. **If interrupted**: Re-read this section to realign with REFACTOR state 