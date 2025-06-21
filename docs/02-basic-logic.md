# Basic Logic Structures

Basic logic structures form the foundation of program logic. These fundamental building blocks are used to create more complex logical frameworks and algorithms.

## Sequential Logic

Sequential logic is the simplest form of program logic, where instructions are executed in a specific order.

### Characteristics
- Instructions are executed one after another
- The order of execution is predetermined
- Each step depends on the completion of the previous step

### Example
```python
def make_sandwich():
    get_bread()
    add_butter()
    add_filling()
    close_sandwich()
    serve()
```

## Conditional Logic

Conditional logic allows programs to make decisions based on specific conditions.

### Basic Conditional Structures
1. **If Statement**
   ```python
   if condition:
       perform_action()
   ```

2. **If-Else Statement**
   ```python
   if condition:
       perform_action_a()
   else:
       perform_action_b()
   ```

3. **If-Elif-Else Chain**
   ```python
   if condition_1:
       perform_action_a()
   elif condition_2:
       perform_action_b()
   else:
       perform_action_c()
   ```

### Best Practices for Conditionals
- Keep conditions simple and readable
- Avoid nested conditions when possible
- Use guard clauses for early returns
- Consider switch/match statements for multiple conditions

## Loop Structures

Loops allow for repeated execution of code blocks based on specific conditions.

### Types of Loops

1. **For Loop**
   - Used when the number of iterations is known
   - Iterates over a sequence of elements
   ```python
   for item in collection:
       process(item)
   ```

2. **While Loop**
   - Used when the number of iterations is unknown
   - Continues until a condition is met
   ```python
   while condition:
       perform_action()
   ```

### Loop Control
- **Break**: Exits the loop
- **Continue**: Skips to the next iteration
- **Loop Guards**: Conditions to prevent infinite loops

## Logical Operators

Logical operators combine or modify conditions.

### Basic Operators
- **AND**: Both conditions must be true
- **OR**: At least one condition must be true
- **NOT**: Inverts a condition

### Example
```python
if (is_valid AND is_active) OR is_admin:
    grant_access()
```

## Error Handling

Error handling is a crucial part of basic logic structures.

### Try-Except Pattern
```python
try:
    perform_risky_operation()
except SpecificError:
    handle_specific_error()
except Exception:
    handle_general_error()
finally:
    cleanup()
```

## Best Practices

1. **Clarity Over Cleverness**
   - Write clear, straightforward logic
   - Avoid overly complex expressions

2. **Proper Naming**
   - Use descriptive names for variables and functions
   - Make the logic self-documenting

3. **Comments and Documentation**
   - Explain complex logic
   - Document assumptions and edge cases

4. **Testing**
   - Test edge cases
   - Verify error handling
   - Ensure logical completeness

## Common Pitfalls

1. **Off-by-One Errors**
   - Incorrect loop boundaries
   - Index misalignment

2. **Infinite Loops**
   - Missing exit conditions
   - Incorrect loop guards

3. **Logic Gaps**
   - Missing else clauses
   - Unhandled edge cases

## Next Steps

Continue to [Control Flow Patterns](03-control-flow.md) to learn about more advanced ways to structure and control program execution. 