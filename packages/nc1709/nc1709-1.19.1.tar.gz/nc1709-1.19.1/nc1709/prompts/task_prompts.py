"""
Task-Specific Prompts for NC1709

These prompts are added to the base agent prompt based on what the user is trying to do.
Auto-detection determines which prompt addition to use.
"""

from enum import Enum
from typing import Optional
import re


class TaskType(Enum):
    """Types of tasks the user might request."""
    TROUBLESHOOT = "troubleshoot"  # Fix errors, debug issues
    BUILD = "build"                # Create new code/features
    MODIFY = "modify"              # Change existing code
    EXPLAIN = "explain"            # Understand/review code
    GENERAL = "general"            # Default fallback


# Keywords that trigger each task type
TASK_KEYWORDS = {
    TaskType.TROUBLESHOOT: [
        "fix", "error", "bug", "issue", "not working", "doesn't work", "failing",
        "broken", "crash", "exception", "troubleshoot", "debug", "wrong",
        "incorrect", "problem", "why is", "why does", "why am i getting",
        "help me fix", "can you check why", "what's wrong", "throwing",
        "returns 500", "returns 404", "undefined", "null", "NaN",
    ],
    TaskType.BUILD: [
        "create", "build", "make", "implement", "add", "scaffold", "setup",
        "set up", "new", "generate", "write", "develop", "start building",
        "i want to make", "i have this in mind", "can we build", "let's create",
        "initialize", "bootstrap", "project for", "app that", "feature for",
    ],
    TaskType.MODIFY: [
        "change", "update", "modify", "refactor", "convert", "remove", "rename",
        "replace", "improve", "optimize", "clean up", "restructure", "migrate",
        "upgrade", "make this", "can you make", "modification", "edit",
        "transform", "rewrite", "adjust", "tweak",
    ],
    TaskType.EXPLAIN: [
        "explain", "what does", "how does", "review", "audit", "understand",
        "tell me about", "describe", "analyze", "what is", "how is",
        "walk me through", "breakdown", "overview", "summarize", "check",
        "look at", "examine", "inspect",
    ],
}


def detect_task_type(user_message: str) -> TaskType:
    """
    Detect the task type from the user's message.

    Args:
        user_message: The user's input message

    Returns:
        The detected TaskType
    """
    message_lower = user_message.lower()

    # Score each task type based on keyword matches
    scores = {task_type: 0 for task_type in TaskType if task_type != TaskType.GENERAL}

    for task_type, keywords in TASK_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                # Longer keywords get higher scores (more specific)
                scores[task_type] += len(keyword.split())

    # Find the highest scoring task type
    max_score = max(scores.values())

    if max_score == 0:
        return TaskType.GENERAL

    for task_type, score in scores.items():
        if score == max_score:
            return task_type

    return TaskType.GENERAL


# ============================================================================
# Task-Specific Prompt Additions
# ============================================================================

TROUBLESHOOT_PROMPT = """
## TROUBLESHOOTING MODE

The user needs help fixing an issue. Follow this process:

### Step 1: Understand the Error
- If an error message is provided, analyze it carefully
- Identify the file and line number from stack traces
- Note the error type (syntax, runtime, logic, etc.)

### Step 2: Gather Context
```tool
{"tool": "Read", "parameters": {"file_path": "<file from error>"}}
```
- Read the file where the error occurs
- Read 20 lines before and after the error line
- Check imports and dependencies

### Step 3: Find Root Cause
- Is it a typo or syntax error?
- Missing import or dependency?
- Wrong variable type or null reference?
- Logic error in conditions?
- API/external service issue?

### Step 4: Propose Fix
- Show the EXACT change needed using Edit tool
- Explain WHY this fixes the issue
- Mention if there are related issues to address

### Common Patterns
| Error Type | Likely Cause | Check |
|------------|--------------|-------|
| ImportError | Missing package or wrong path | requirements.txt, imports |
| TypeError | Wrong type passed | Function signatures |
| AttributeError | Accessing non-existent property | Object structure |
| KeyError | Missing dict key | Dict initialization |
| ConnectionError | Network/service issue | URLs, credentials |

### Do NOT
- Suggest "try adding print statements" without reading the code
- Give generic debugging advice
- Assume the error without reading the actual code
"""

BUILD_PROMPT = """
## BUILD MODE

The user wants to create something new. Follow this process:

### Step 1: Understand Requirements
- What exactly does the user want to build?
- What language/framework should be used?
- Are there existing patterns in the codebase to follow?

### Step 2: Check Existing Project Structure
```tool
{"tool": "Glob", "parameters": {"pattern": "*.py"}}
```
```tool
{"tool": "Read", "parameters": {"file_path": "package.json"}}
```
- Understand the existing project structure
- Match the existing code style
- Use existing utilities/helpers if available

### Step 3: Plan the Implementation
Before writing code, outline:
1. Files to create/modify
2. Dependencies needed
3. Key functions/classes
4. Integration points with existing code

### Step 4: Implement Incrementally
- Create one file at a time
- Write clean, readable code
- Add error handling
- Include basic comments for complex logic

### Step 5: Provide Next Steps
- How to test the new code
- Any manual setup required
- Suggestions for improvements

### Best Practices
- Follow existing code conventions in the project
- Don't over-engineer - start simple
- Make code testable
- Handle edge cases
"""

MODIFY_PROMPT = """
## MODIFY MODE

The user wants to change existing code. Follow this process:

### Step 1: Read Before Changing
```tool
{"tool": "Read", "parameters": {"file_path": "<target file>"}}
```
ALWAYS read the entire file first. Never modify code you haven't seen.

### Step 2: Understand the Current Implementation
- What does the current code do?
- What are the inputs/outputs?
- What depends on this code?

### Step 3: Plan the Change
- What's the minimal change needed?
- Will this break anything else?
- Are there tests that need updating?

### Step 4: Make Precise Changes
Use Edit tool with EXACT strings:
```tool
{"tool": "Edit", "parameters": {"file_path": "...", "old_string": "exact old code", "new_string": "exact new code"}}
```

### Step 5: Verify Dependencies
- Check if imports need updating
- Search for other usages of modified functions
```tool
{"tool": "Grep", "parameters": {"pattern": "function_name"}}
```

### Rules
- Make ONE logical change at a time
- Preserve existing functionality unless asked to remove it
- Don't change code style unnecessarily
- Keep the same indentation
- Update related comments/docstrings
"""

EXPLAIN_PROMPT = """
## EXPLAIN MODE

The user wants to understand code. Follow this process:

### Step 1: Read the Relevant Code
```tool
{"tool": "Read", "parameters": {"file_path": "<file to explain>"}}
```
Read the actual code before explaining anything.

### Step 2: Identify Key Components
- Entry points (main functions, API routes)
- Core logic
- Data models/structures
- External dependencies

### Step 3: Explain at the Right Level
- Start with high-level overview
- Dive into specifics when relevant
- Use analogies for complex concepts
- Reference specific line numbers

### For Code Audits/Reviews
Check for:

**Security Issues**
- Hardcoded secrets (API keys, passwords)
- SQL injection vulnerabilities
- XSS vulnerabilities
- Insecure dependencies
- Missing input validation

**Code Quality**
- Functions over 50 lines
- Duplicated code blocks
- Missing error handling
- Unclear naming
- Dead code

**Architecture**
- Circular dependencies
- Tight coupling
- Missing abstractions
- Inconsistent patterns

### Output Format
For audits, use this format:
```
## Summary
[1-2 sentence overview]

## Findings

### Critical
- **[Issue]** in `file.py:line` - [description]

### Warnings
- **[Issue]** in `file.py:line` - [description]

### Suggestions
- [improvement idea]

## Recommendations
[prioritized action items]
```
"""

GENERAL_PROMPT = """
## GENERAL ASSISTANCE

Approach:
1. First, understand what the user is asking
2. If about code: read relevant files before responding
3. If about concepts: provide clear, practical explanations
4. If unclear: use tools to explore before asking questions

Default to being proactive - use tools to gather information rather than asking the user.
"""


# Mapping task types to their prompts
TASK_PROMPTS = {
    TaskType.TROUBLESHOOT: TROUBLESHOOT_PROMPT,
    TaskType.BUILD: BUILD_PROMPT,
    TaskType.MODIFY: MODIFY_PROMPT,
    TaskType.EXPLAIN: EXPLAIN_PROMPT,
    TaskType.GENERAL: GENERAL_PROMPT,
}


def get_task_prompt(task_type: TaskType) -> str:
    """Get the prompt addition for a specific task type."""
    return TASK_PROMPTS.get(task_type, GENERAL_PROMPT)


def get_full_prompt(cwd: str, user_message: str) -> str:
    """
    Get the complete prompt with base + task-specific additions.

    Args:
        cwd: Current working directory
        user_message: The user's message (used for task detection)

    Returns:
        Complete system prompt
    """
    from .agent_system import get_agent_prompt

    # Get base prompt
    base_prompt = get_agent_prompt(cwd)

    # Detect task type and get addition
    task_type = detect_task_type(user_message)
    task_prompt = get_task_prompt(task_type)

    # Combine them
    return base_prompt + "\n" + task_prompt
