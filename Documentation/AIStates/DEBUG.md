# AI State: Debugging

## Purpose
This state guides the AI in systematically identifying, isolating, fixing, and preventing bugs. The focus is on creating regression tests that prevent the same issue from reoccurring in the future.

## When to Use This State
- When encountering unexpected behavior or error messages
- When code is not producing expected output
- When investigating performance issues
- When addressing crash reports
- When fixing a bug reported by a user or tester

## State Maintenance Protocol
To maintain this DEBUG state throughout the session, you MUST:

1. **Always reproduce the issue** before attempting to fix it
2. **Mark each debugging phase** using the state markers below
3. **Document your findings** at each step
4. **Create a regression test** to prevent recurrence
5. **Maintain discipline** by explicitly stating your current phase

### Required State Markers
```
[STATE: DEBUG] Investigating {issue/bug}
[STATE: DEBUG] [REPRODUCE] Steps to reproduce the issue
[STATE: DEBUG] [HYPOTHESIZE] Potential causes of the issue
[STATE: DEBUG] [INVESTIGATE] Specific area being investigated
[STATE: DEBUG] [TEST] Testing potential fix
[STATE: DEBUG] [FIX] Implementing the solution
[STATE: DEBUG] [PREVENT] Creating regression test
```

## The Debugging Workflow

### 1. Reproduce the Issue
```
[STATE: DEBUG] Investigating {issue description}
[STATE: DEBUG] [REPRODUCE] Steps to reproduce the issue
```

- Define clear steps to reliably reproduce the bug
- Record the expected vs. actual behavior
- Identify the specific conditions required
- Document any relevant error messages or logs

### 2. Form Hypotheses
```
[STATE: DEBUG] [HYPOTHESIZE] Potential causes of the issue
```

- List possible causes based on observed symptoms
- Prioritize hypotheses by likelihood
- Consider edge cases and exceptional conditions
- Connect symptoms to potential code areas

### 3. Investigate Systematically
```
[STATE: DEBUG] [INVESTIGATE] Examining {specific area}
```

- Examine relevant code and data
- Trace execution paths
- Check input validation and error handling
- Review recent changes to the affected area
- Use debugging tools to gather more information

### 4. Test Potential Fixes
```
[STATE: DEBUG] [TEST] Testing {proposed solution}
```

- Create isolated tests for the issue
- Verify that the proposed fix resolves the issue
- Check for any regression or side effects
- Document the results of each test

### 5. Implement the Fix
```
[STATE: DEBUG] [FIX] Implementing solution for {issue}
```

- Apply the minimal change needed to fix the issue
- Maintain code quality and style standards
- Add appropriate error handling if needed
- Document the fix with clear comments

### 6. Prevent Recurrence
```
[STATE: DEBUG] [PREVENT] Creating regression test for {issue}
```

- Create automated tests that would have caught this bug
- Document the root cause and solution
- Update validation or error handling as needed
- Consider similar areas where the same issue might occur

## Best Practices for Non-Fragile Bug Fixes

### Systematic Approach
- Work methodically through the debugging process
- Avoid making random changes to see what works
- Document each step of the investigation
- Validate assumptions with evidence

### Root Cause Analysis
- Dig beyond symptoms to find underlying causes
- Consider architectural implications of the bug
- Look for patterns that might indicate larger issues
- Fix the cause, not just the symptoms

### Defensive Programming
- Add appropriate validation and error handling
- Make code more explicit and less assumption-dependent
- Improve logging and diagnostics in problematic areas
- Consider failure modes during development

## Example (Shortened)
```csharp
[STATE: DEBUG] Investigating game crash when transitioning to battle screen
[STATE: DEBUG] [REPRODUCE] 
1. Start new game
2. Click on "Battle" button
3. Game crashes with NullReferenceException

[STATE: DEBUG] [HYPOTHESIZE]
1. Battle screen resources not properly loaded
2. Game state not initialized correctly
3. Race condition in resource loading

[STATE: DEBUG] [INVESTIGATE] Examining battle transition code
// Findings from code examination

[STATE: DEBUG] [TEST] Testing initialization sequence fix
// Test implementation and results

[STATE: DEBUG] [FIX] Implementing proper initialization sequence
// Fix implementation

[STATE: DEBUG] [PREVENT] Creating regression test for battle transition
// Regression test implementation
```

## Common Pitfalls to Avoid
- **Fixing Symptoms Only**: Ensure you address the root cause
- **No Regression Test**: Always create tests to prevent recurrence
- **Confirmation Bias**: Consider alternative explanations
- **Random Changes**: Avoid trial-and-error without understanding
- **Tunnel Vision**: Consider the broader system context
- **Excessive Complexity**: Prefer simple, clear fixes over complex ones

## Transitioning to Other States
When appropriate, transition to:

- **To REFACTOR**: `[TRANSITION: REFACTOR]` - When the bug reveals design issues
- **To TDD**: `[TRANSITION: TDD]` - When adding new tests for missing functionality
- **To REVIEW**: `[TRANSITION: REVIEW]` - When the fix needs evaluation
- **To EXPLORATORY**: `[TRANSITION: EXPLORATORY]` - When investigating complex issues
- **To CHECKLIST**: `[TRANSITION: CHECKLIST]` - When returning to the main checklist after fixing a bug

### Integration with Checklist Workflow

The DEBUG state is typically used in two contexts with the CHECKLIST workflow:

1. **As a subtask implementation state**:
   - When a checklist item specifically involves fixing a known bug
   - CHECKLIST state breaks down the bug fix into subtasks
   - Transition to DEBUG state to systematically address the bug
   - Return to CHECKLIST state with `[TRANSITION: CHECKLIST]` when complete

2. **As an interruption to normal workflow**:
   - When a bug is discovered during implementation of another checklist item
   - Temporarily transition to DEBUG state to address the issue
   - Return to the original state (and checklist item) after fixing

During debugging, maintain awareness of the original checklist scope to ensure that fixes don't introduce unrelated changes beyond what's required.

## Required Discipline Practices

1. **At the start of debugging**: Explicitly define the issue with `[STATE: DEBUG] Investigating {issue}`
2. **Before making any changes**: Reproduce the issue with `[STATE: DEBUG] [REPRODUCE]`
3. **Before exploring code**: List hypotheses with `[STATE: DEBUG] [HYPOTHESIZE]`
4. **During investigation**: Mark each area with `[STATE: DEBUG] [INVESTIGATE]`
5. **When testing solutions**: Document with `[STATE: DEBUG] [TEST]`
6. **When implementing fixes**: Mark with `[STATE: DEBUG] [FIX]`
7. **After fixing**: Create prevention with `[STATE: DEBUG] [PREVENT]`
8. **Every 15 minutes**: Remind yourself "I am debugging {specific issue} systematically"
9. **If interrupted**: Re-read this section to realign with DEBUG state 