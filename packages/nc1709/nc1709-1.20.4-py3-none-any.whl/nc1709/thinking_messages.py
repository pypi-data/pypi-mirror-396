"""
Dynamic Thinking Messages
Engaging, varied status messages to keep users informed during processing.
"""
import random
import time
from typing import List, Optional, Tuple
from enum import Enum


class ThinkingPhase(Enum):
    """Different phases of processing"""
    INITIAL = "initial"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    RESEARCHING = "researching"
    CODING = "coding"
    REVIEWING = "reviewing"
    FINALIZING = "finalizing"


# Dynamic thinking messages organized by phase
THINKING_MESSAGES = {
    ThinkingPhase.INITIAL: [
        "Let me think about this...",
        "Hmm, interesting question...",
        "Give me a moment to process this...",
        "Let me understand what you need...",
        "Processing your request...",
        "Analyzing your input...",
        "Let me work on this...",
        "I'm on it...",
        "Just a second, thinking...",
        "Let me see what we can do here...",
    ],
    ThinkingPhase.ANALYZING: [
        "Analyzing the codebase...",
        "Looking at the structure...",
        "Understanding the context...",
        "Examining the code...",
        "Digging deeper into this...",
        "Studying the patterns...",
        "Mapping out the architecture...",
        "Tracing the dependencies...",
        "Checking the relationships...",
        "Scanning for relevant code...",
    ],
    ThinkingPhase.PLANNING: [
        "Planning my approach...",
        "Figuring out the best way...",
        "Strategizing the solution...",
        "Breaking this down...",
        "Mapping out the steps...",
        "Designing the approach...",
        "Working out the details...",
        "Thinking through the logic...",
        "Considering the options...",
        "Evaluating different approaches...",
    ],
    ThinkingPhase.RESEARCHING: [
        "Searching for information...",
        "Looking up references...",
        "Finding relevant examples...",
        "Checking documentation...",
        "Gathering context...",
        "Exploring possibilities...",
        "Investigating the best practices...",
        "Reviewing similar patterns...",
        "Looking for the right approach...",
        "Consulting my knowledge...",
    ],
    ThinkingPhase.CODING: [
        "Writing the code...",
        "Crafting the solution...",
        "Building this out...",
        "Implementing the changes...",
        "Putting it together...",
        "Coding away...",
        "Making it happen...",
        "Bringing this to life...",
        "Creating the implementation...",
        "Working on the code...",
    ],
    ThinkingPhase.REVIEWING: [
        "Double-checking my work...",
        "Reviewing the solution...",
        "Making sure everything's right...",
        "Validating the approach...",
        "Checking for issues...",
        "Looking over the code...",
        "Ensuring quality...",
        "Verifying the logic...",
        "Testing my assumptions...",
        "Polishing the solution...",
    ],
    ThinkingPhase.FINALIZING: [
        "Almost there...",
        "Finishing up...",
        "Wrapping things up...",
        "Just about done...",
        "Final touches...",
        "Putting on the finishing touches...",
        "One moment more...",
        "Just finalizing...",
        "Nearly there...",
        "Preparing the response...",
    ],
}

# Engaging idle messages when waiting longer
LONG_WAIT_MESSAGES = [
    "Still working on it, thanks for your patience...",
    "This is taking a bit longer, but I'm making progress...",
    "Complex task, but I'm getting there...",
    "Bear with me, almost got it...",
    "Working through some tricky parts...",
    "Thorough analysis takes a moment...",
    "Good things take time...",
    "Deep diving into this one...",
    "Making sure I get it right...",
    "Quality takes a moment...",
]

# Personal/friendly messages for casual interaction
CASUAL_MESSAGES = [
    "Let me see...",
    "Okay, working on it...",
    "Sure thing, give me a sec...",
    "On it!",
    "Let me figure this out...",
    "Alright, let's do this...",
    "Got it, processing...",
    "Looking into it...",
    "Here we go...",
    "Let me help with that...",
]

# Tool action messages - what to show when specific tools are being used
TOOL_MESSAGES = {
    "Read": [
        "Reading {target}...",
        "Looking at {target}...",
        "Examining {target}...",
        "Opening {target}...",
        "Checking {target}...",
    ],
    "Write": [
        "Writing to {target}...",
        "Creating {target}...",
        "Saving {target}...",
        "Updating {target}...",
    ],
    "Edit": [
        "Editing {target}...",
        "Modifying {target}...",
        "Updating {target}...",
        "Changing {target}...",
    ],
    "Bash": [
        "Running command...",
        "Executing...",
        "Processing command...",
        "Working on it...",
    ],
    "Grep": [
        "Searching for patterns...",
        "Looking for matches...",
        "Scanning files...",
        "Finding occurrences...",
    ],
    "Glob": [
        "Finding files...",
        "Searching for files...",
        "Locating files...",
        "Scanning directory...",
    ],
}


class ThinkingMessageManager:
    """
    Manages dynamic thinking messages to keep users engaged.

    Tracks time elapsed and switches messages to maintain variety
    and show progress even during long processing.
    """

    def __init__(self):
        self.start_time: Optional[float] = None
        self.current_phase: ThinkingPhase = ThinkingPhase.INITIAL
        self.last_message: str = ""
        self.last_message_time: float = 0
        self.message_count: int = 0
        self.used_messages: set = set()

    def start(self) -> None:
        """Start a new thinking session"""
        self.start_time = time.time()
        self.message_count = 0
        self.used_messages.clear()
        self.current_phase = ThinkingPhase.INITIAL

    def reset(self) -> None:
        """Reset the manager for a new request"""
        self.start()

    def set_phase(self, phase: ThinkingPhase) -> None:
        """Set the current processing phase"""
        self.current_phase = phase

    def get_elapsed(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def should_update(self, interval: float = 3.0) -> bool:
        """Check if it's time for a new message"""
        now = time.time()
        if now - self.last_message_time >= interval:
            return True
        return False

    def get_message(self, phase: Optional[ThinkingPhase] = None, casual: bool = False) -> str:
        """
        Get a thinking message for the current state.

        Args:
            phase: Optional phase override
            casual: Use more casual/friendly messages

        Returns:
            A contextually appropriate thinking message
        """
        phase = phase or self.current_phase
        elapsed = self.get_elapsed()

        # After 10+ seconds, add some long-wait messages
        if elapsed > 10 and random.random() < 0.3:
            messages = LONG_WAIT_MESSAGES
        # Use casual messages for variety
        elif casual or (random.random() < 0.2 and self.message_count > 0):
            messages = CASUAL_MESSAGES
        else:
            messages = THINKING_MESSAGES.get(phase, THINKING_MESSAGES[ThinkingPhase.INITIAL])

        # Try to get an unused message for variety
        available = [m for m in messages if m not in self.used_messages]
        if not available:
            # Reset if we've used all messages
            self.used_messages.clear()
            available = messages

        message = random.choice(available)
        self.used_messages.add(message)
        self.last_message = message
        self.last_message_time = time.time()
        self.message_count += 1

        return message

    def get_tool_message(self, tool_name: str, target: str = "") -> str:
        """
        Get a message for a specific tool action.

        Args:
            tool_name: Name of the tool being used
            target: Target of the action (file, command, etc.)

        Returns:
            Formatted tool action message
        """
        templates = TOOL_MESSAGES.get(tool_name, ["Working..."])
        template = random.choice(templates)

        if "{target}" in template and target:
            # Truncate long targets
            if len(target) > 40:
                target = "..." + target[-37:]
            return template.format(target=target)
        return template

    def get_progress_message(self) -> str:
        """
        Get a progress-aware message based on elapsed time.

        Returns:
            Message appropriate for current progress
        """
        elapsed = self.get_elapsed()

        if elapsed < 2:
            return self.get_message(ThinkingPhase.INITIAL)
        elif elapsed < 5:
            return self.get_message(ThinkingPhase.ANALYZING)
        elif elapsed < 10:
            return self.get_message(ThinkingPhase.PLANNING)
        elif elapsed < 20:
            return self.get_message(ThinkingPhase.CODING)
        elif elapsed < 30:
            return self.get_message(ThinkingPhase.REVIEWING)
        else:
            return self.get_message(ThinkingPhase.FINALIZING)


# Global instance for convenience
_manager = ThinkingMessageManager()


def start_thinking() -> None:
    """Start a new thinking session"""
    _manager.start()


def get_thinking_message(phase: Optional[ThinkingPhase] = None, casual: bool = False) -> str:
    """Get a dynamic thinking message"""
    return _manager.get_message(phase, casual)


def get_tool_message(tool_name: str, target: str = "") -> str:
    """Get a tool-specific message"""
    return _manager.get_tool_message(tool_name, target)


def get_progress_message() -> str:
    """Get a progress-aware message"""
    return _manager.get_progress_message()


def set_phase(phase: ThinkingPhase) -> None:
    """Set the current thinking phase"""
    _manager.set_phase(phase)


def should_update_message(interval: float = 3.0) -> bool:
    """Check if we should update the thinking message"""
    return _manager.should_update(interval)
