"""
Shell Completions Generator
Generates completion scripts for bash, zsh, and fish shells
"""
import os
from typing import Optional


# Bash completion script
BASH_COMPLETION = '''
# NC1709 Bash Completion
# Add to ~/.bashrc or ~/.bash_profile:
# source <(nc1709 --completion bash)
# or: eval "$(nc1709 --completion bash)"

_nc1709_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main options
    opts="--help --version --web --shell --config --resume --remote --api-key --serve --port --plugins --plugin --completion --mcp-serve"

    # Shell commands (when in interactive mode)
    shell_commands="help exit quit clear history config sessions index search plugins git docker mcp"

    # Plugin commands
    plugin_opts="git:status git:diff git:log git:branch git:commit git:push git:pull docker:ps docker:images docker:logs docker:compose_up docker:compose_down fastapi:scaffold nextjs:scaffold django:scaffold"

    case "${prev}" in
        --plugin)
            COMPREPLY=( $(compgen -W "${plugin_opts}" -- ${cur}) )
            return 0
            ;;
        --completion)
            COMPREPLY=( $(compgen -W "bash zsh fish" -- ${cur}) )
            return 0
            ;;
        --port)
            COMPREPLY=()
            return 0
            ;;
        --remote|--api-key)
            COMPREPLY=()
            return 0
            ;;
        --resume)
            # Could add session completion here
            COMPREPLY=()
            return 0
            ;;
    esac

    # Complete options or files
    if [[ ${cur} == -* ]]; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    else
        # Complete files for potential file paths
        COMPREPLY=( $(compgen -f -- ${cur}) )
    fi

    return 0
}

complete -F _nc1709_completions nc1709
'''


# Zsh completion script
ZSH_COMPLETION = '''
#compdef nc1709

# NC1709 Zsh Completion
# Add to ~/.zshrc:
# source <(nc1709 --completion zsh)
# or: eval "$(nc1709 --completion zsh)"
# or save to ~/.zsh/completions/_nc1709

_nc1709() {
    local -a commands
    local -a options
    local -a plugins

    options=(
        '--help[Show help message]'
        '--version[Show version]'
        '--web[Start web dashboard]'
        '--shell[Start interactive shell]'
        '--config[Show configuration]'
        '--resume[Resume session]:session_id:'
        '--remote[Remote server URL]:url:'
        '--api-key[API key for remote server]:key:'
        '--serve[Enable remote access]'
        '--port[Server port]:port:'
        '--plugins[List available plugins]'
        '--plugin[Run a plugin]:plugin:->plugins'
        '--completion[Generate shell completion]:shell:(bash zsh fish)'
        '--mcp-serve[Start MCP server]'
    )

    plugins=(
        'git\\:status:Show git status'
        'git\\:diff:Show git diff'
        'git\\:log:Show git log'
        'git\\:branch:List branches'
        'git\\:commit:Create commit'
        'git\\:push:Push to remote'
        'git\\:pull:Pull from remote'
        'docker\\:ps:List containers'
        'docker\\:images:List images'
        'docker\\:logs:View logs'
        'docker\\:compose_up:Start compose'
        'docker\\:compose_down:Stop compose'
        'fastapi\\:scaffold:Create FastAPI project'
        'nextjs\\:scaffold:Create Next.js project'
        'django\\:scaffold:Create Django project'
    )

    case $state in
        plugins)
            _describe 'plugin' plugins
            ;;
        *)
            _arguments -s $options
            ;;
    esac
}

_nc1709 "$@"
'''


# Fish completion script
FISH_COMPLETION = '''
# NC1709 Fish Completion
# Add to ~/.config/fish/completions/nc1709.fish
# or: nc1709 --completion fish > ~/.config/fish/completions/nc1709.fish

# Main options
complete -c nc1709 -l help -d "Show help message"
complete -c nc1709 -l version -d "Show version"
complete -c nc1709 -l web -d "Start web dashboard"
complete -c nc1709 -l shell -d "Start interactive shell"
complete -c nc1709 -l config -d "Show configuration"
complete -c nc1709 -l resume -d "Resume session" -x
complete -c nc1709 -l remote -d "Remote server URL" -x
complete -c nc1709 -l api-key -d "API key for remote server" -x
complete -c nc1709 -l serve -d "Enable remote access"
complete -c nc1709 -l port -d "Server port" -x
complete -c nc1709 -l plugins -d "List available plugins"
complete -c nc1709 -l plugin -d "Run a plugin" -xa "
    git:status\t'Show git status'
    git:diff\t'Show git diff'
    git:log\t'Show git log'
    git:branch\t'List branches'
    git:commit\t'Create commit'
    git:push\t'Push to remote'
    git:pull\t'Pull from remote'
    docker:ps\t'List containers'
    docker:images\t'List images'
    docker:logs\t'View logs'
    docker:compose_up\t'Start compose'
    docker:compose_down\t'Stop compose'
    fastapi:scaffold\t'Create FastAPI project'
    nextjs:scaffold\t'Create Next.js project'
    django:scaffold\t'Create Django project'
"
complete -c nc1709 -l completion -d "Generate shell completion" -xa "bash zsh fish"
complete -c nc1709 -l mcp-serve -d "Start MCP server"

# File completion for positional arguments
complete -c nc1709 -f -a "(__fish_complete_path)"
'''


def get_completion_script(shell: str) -> str:
    """Get completion script for specified shell

    Args:
        shell: Shell type (bash, zsh, fish)

    Returns:
        Completion script content
    """
    scripts = {
        "bash": BASH_COMPLETION,
        "zsh": ZSH_COMPLETION,
        "fish": FISH_COMPLETION
    }

    script = scripts.get(shell.lower())
    if not script:
        raise ValueError(f"Unknown shell: {shell}. Supported: bash, zsh, fish")

    return script.strip()


def install_completions(shell: Optional[str] = None) -> str:
    """Install completions for the detected or specified shell

    Args:
        shell: Shell type (auto-detect if None)

    Returns:
        Installation status message
    """
    if shell is None:
        shell = detect_shell()

    script = get_completion_script(shell)
    home = os.path.expanduser("~")

    if shell == "bash":
        # Try to install to .bash_completion.d or .bashrc
        completion_dir = os.path.join(home, ".bash_completion.d")
        if os.path.isdir(completion_dir):
            path = os.path.join(completion_dir, "nc1709")
            with open(path, "w") as f:
                f.write(script)
            return f"Installed to {path}. Restart your shell to use completions."
        else:
            # Add to .bashrc
            bashrc = os.path.join(home, ".bashrc")
            source_line = '\n# NC1709 completions\neval "$(nc1709 --completion bash)"\n'
            with open(bashrc, "a") as f:
                f.write(source_line)
            return f"Added to {bashrc}. Run 'source ~/.bashrc' or restart your shell."

    elif shell == "zsh":
        # Install to .zsh/completions or add to .zshrc
        completion_dir = os.path.join(home, ".zsh", "completions")
        os.makedirs(completion_dir, exist_ok=True)
        path = os.path.join(completion_dir, "_nc1709")
        with open(path, "w") as f:
            f.write(script)

        # Ensure completions dir is in fpath
        zshrc = os.path.join(home, ".zshrc")
        fpath_line = f'\nfpath=({completion_dir} $fpath)\nautoload -Uz compinit && compinit\n'

        # Check if already added
        try:
            with open(zshrc, "r") as f:
                content = f.read()
            if completion_dir not in content:
                with open(zshrc, "a") as f:
                    f.write(fpath_line)
        except FileNotFoundError:
            with open(zshrc, "w") as f:
                f.write(fpath_line)

        return f"Installed to {path}. Run 'source ~/.zshrc' or restart your shell."

    elif shell == "fish":
        # Install to fish completions directory
        completion_dir = os.path.join(home, ".config", "fish", "completions")
        os.makedirs(completion_dir, exist_ok=True)
        path = os.path.join(completion_dir, "nc1709.fish")
        with open(path, "w") as f:
            f.write(script)
        return f"Installed to {path}. Completions will be available in new fish sessions."

    else:
        raise ValueError(f"Cannot install completions for shell: {shell}")


def detect_shell() -> str:
    """Detect the current shell

    Returns:
        Shell name (bash, zsh, or fish)
    """
    shell_path = os.environ.get("SHELL", "")
    shell_name = os.path.basename(shell_path)

    if "zsh" in shell_name:
        return "zsh"
    elif "fish" in shell_name:
        return "fish"
    else:
        return "bash"


def print_installation_instructions(shell: str) -> None:
    """Print installation instructions for a shell

    Args:
        shell: Shell type
    """
    instructions = {
        "bash": """
# Bash Completion Installation

Option 1: Add to .bashrc (recommended)
  echo 'eval "$(nc1709 --completion bash)"' >> ~/.bashrc
  source ~/.bashrc

Option 2: Create completion file
  nc1709 --completion bash > ~/.bash_completion.d/nc1709
  # Requires bash-completion to be installed
""",
        "zsh": """
# Zsh Completion Installation

Option 1: Add to .zshrc (simplest)
  echo 'eval "$(nc1709 --completion zsh)"' >> ~/.zshrc
  source ~/.zshrc

Option 2: Save to completions directory
  mkdir -p ~/.zsh/completions
  nc1709 --completion zsh > ~/.zsh/completions/_nc1709
  # Add to .zshrc: fpath=(~/.zsh/completions $fpath)
  # Then run: autoload -Uz compinit && compinit
""",
        "fish": """
# Fish Completion Installation

  nc1709 --completion fish > ~/.config/fish/completions/nc1709.fish

  # Completions will be available immediately in new shells
"""
    }

    print(instructions.get(shell, f"Unknown shell: {shell}"))


# Entry point for CLI
def handle_completion_command(args: list) -> None:
    """Handle completion command from CLI

    Args:
        args: Command arguments (e.g., ['bash'] or ['--install', 'zsh'])
    """
    if not args:
        # Print detected shell and instructions
        shell = detect_shell()
        print(f"Detected shell: {shell}")
        print_installation_instructions(shell)
        return

    if args[0] == "--install":
        shell = args[1] if len(args) > 1 else None
        result = install_completions(shell)
        print(result)
    else:
        # Print completion script
        shell = args[0]
        print(get_completion_script(shell))
