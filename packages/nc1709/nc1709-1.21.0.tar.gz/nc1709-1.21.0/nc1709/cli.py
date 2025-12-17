"""
NC1709 CLI - Main Command Line Interface
Provides both direct command mode and interactive shell mode with optional agentic execution
"""
import sys
import os
import argparse
from pathlib import Path
from typing import Optional

from .config import get_config
from .llm_adapter import LLMAdapter, TaskType, TaskClassifier
from .file_controller import FileController
from .executor import CommandExecutor
from .reasoning_engine import ReasoningEngine
from .remote_client import RemoteClient, is_remote_mode
from .cli_ui import (
    ActionSpinner, Color, Icons,
    status, thinking, success, error, warning, info,
    action_spinner, print_response, format_response,
    log_action, log_output, get_terminal_width
)

# Default server URL - users connect to this server by default
DEFAULT_API_URL = "https://nc1709.lafzusa.com"

# Import agent module
try:
    from .agent import Agent, AgentConfig, PermissionManager, PermissionPolicy, integrate_mcp_with_agent
    HAS_AGENT = True
except ImportError:
    HAS_AGENT = False

# Import checkpoints module
try:
    from .checkpoints import get_checkpoint_manager
    HAS_CHECKPOINTS = True
except ImportError:
    HAS_CHECKPOINTS = False

# Import git integration
try:
    from .git_integration import get_git_integration, GitIntegration
    HAS_GIT_INTEGRATION = True
except ImportError:
    HAS_GIT_INTEGRATION = False

# Import custom commands
try:
    from .custom_commands import get_custom_command_manager, execute_custom_command
    HAS_CUSTOM_COMMANDS = True
except ImportError:
    HAS_CUSTOM_COMMANDS = False

# Import image input
try:
    from .image_input import (
        get_image_handler, load_image, capture_screenshot,
        get_clipboard_image, get_image_info, is_image_file
    )
    HAS_IMAGE_INPUT = True
except ImportError:
    HAS_IMAGE_INPUT = False

# Import plan mode
try:
    from .plan_mode import get_plan_manager, PLAN_MODE_SYSTEM_PROMPT
    HAS_PLAN_MODE = True
except ImportError:
    HAS_PLAN_MODE = False

# Import GitHub integration
try:
    from .github_integration import (
        get_github_integration, format_pr_summary, format_issue_summary
    )
    HAS_GITHUB = True
except ImportError:
    HAS_GITHUB = False

# Import linting integration
try:
    from .linting import (
        get_linting_manager, format_lint_result, generate_fix_prompt
    )
    HAS_LINTING = True
except ImportError:
    HAS_LINTING = False

# Import telemetry (non-blocking, fire-and-forget)
try:
    from .telemetry import telemetry
    HAS_TELEMETRY = True
except ImportError:
    HAS_TELEMETRY = False

# Import cognitive architecture
try:
    from .cognitive import (
        CognitiveSystem, CognitiveRequest, CognitiveResponse,
        get_cognitive_system
    )
    HAS_COGNITIVE = True
except ImportError:
    HAS_COGNITIVE = False

# Import requirements tracker
try:
    from .requirements_tracker import (
        RequirementsTracker, RequirementStatus, RequirementPriority,
        get_tracker, reset_tracker
    )
    HAS_REQUIREMENTS = True
except ImportError:
    HAS_REQUIREMENTS = False

# Import conversation logger
try:
    from .conversation_logger import (
        ConversationLogger, init_logger, get_logger,
        log_user, log_assistant, log_tool, log_error, log_system
    )
    HAS_CONVERSATION_LOGGER = True
except ImportError:
    HAS_CONVERSATION_LOGGER = False


class NC1709CLI:
    """Main CLI application"""

    def __init__(self, remote_url: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the CLI

        Args:
            remote_url: URL of remote NC1709 server (uses local if None)
            api_key: API key for remote server authentication
        """
        self.config = get_config()
        self.running = True

        # Check for remote mode - use default server if no local override
        self.remote_url = remote_url or os.environ.get("NC1709_API_URL") or DEFAULT_API_URL
        self.api_key = api_key or os.environ.get("NC1709_API_KEY")
        self.remote_client: Optional[RemoteClient] = None

        if self.remote_url:
            # Remote mode - connect to remote server
            self._init_remote_mode()
        else:
            # Local mode - use local LLMs
            self._init_local_mode()

        # Memory module (lazy loaded)
        self._session_manager = None
        self._project_indexer = None
        self._memory_enabled = self.config.get("memory.enabled", True)

        # Plugin system (lazy loaded)
        self._plugin_manager = None

        # MCP support (lazy loaded)
        self._mcp_manager = None

        # Agent mode (lazy loaded) - ON by default for full tool execution
        self._agent = None
        self._agent_mode = self.config.get("agent.enabled", True)  # Enabled by default

        # Cognitive system (lazy loaded)
        self._cognitive_system = None
        self._cognitive_enabled = self.config.get("cognitive.enabled", True)  # Enabled by default

    def _init_remote_mode(self):
        """Initialize remote mode"""
        import uuid
        try:
            self.remote_client = RemoteClient(
                server_url=self.remote_url,
                api_key=self.api_key
            )
            # Verify connection
            server_status = self.remote_client.check_status()

            # Get server host for display
            from urllib.parse import urlparse
            parsed = urlparse(self.remote_url)
            server_host = parsed.netloc or self.remote_url

            # Store tools count for banner
            self._remote_tools_count = server_status.get('tools_count', 17)  # Default to 17

            # Clean connection display (Claude Code style)
            print(f"\n{Color.GREEN}●{Color.RESET} Connected to {Color.BOLD}{server_host}{Color.RESET}")

            # Set up minimal local components (no LLM needed)
            self.file_controller = FileController()
            self.executor = CommandExecutor()
            self.llm = None
            self.reasoning_engine = None

            # Generate unique user ID for this machine (persistent across sessions)
            self._user_id = self._get_or_create_user_id()

            # Track files to index (batched for efficiency)
            self._files_to_index = []
            self._indexed_files = set()  # Don't re-index same files

        except Exception as e:
            error_msg = str(e).lower()

            # Check if it's an authentication error
            if "401" in error_msg or "unauthorized" in error_msg or "authentication" in error_msg:
                # Show clean startup screen with API key instructions
                self._print_auth_screen()
                sys.exit(1)
            else:
                # Other connection errors
                print(f"❌ Failed to connect to NC1709 server: {e}")
                print(f"\n📧 For support, contact: support@lafzusa.com")
                sys.exit(1)

    def _get_or_create_user_id(self) -> str:
        """Get or create a persistent user ID for this machine"""
        import uuid
        import hashlib

        # Use machine-specific info to create a stable ID
        user_id_file = Path.home() / ".nc1709_user_id"

        if user_id_file.exists():
            return user_id_file.read_text().strip()

        # Create new ID based on machine info
        import platform
        import getpass
        try:
            username = getpass.getuser()
        except Exception:
            username = os.environ.get('USER', os.environ.get('USERNAME', 'user'))
        machine_info = f"{platform.node()}-{platform.machine()}-{username}"
        user_id = hashlib.sha256(machine_info.encode()).hexdigest()[:16]

        # Save for future sessions
        try:
            user_id_file.write_text(user_id)
        except Exception:
            pass  # If we can't save, that's ok

        return user_id

    def _init_local_mode(self):
        """Initialize local mode"""
        self.llm = LLMAdapter()
        self.file_controller = FileController()
        self.executor = CommandExecutor()
        self.reasoning_engine = ReasoningEngine()

    @property
    def session_manager(self):
        """Lazy load session manager"""
        if self._session_manager is None:
            try:
                from .memory.sessions import SessionManager
                self._session_manager = SessionManager()
            except ImportError:
                pass
        return self._session_manager

    @property
    def project_indexer(self):
        """Lazy load project indexer"""
        if self._project_indexer is None and self._memory_enabled:
            try:
                from .memory.indexer import ProjectIndexer
                self._project_indexer = ProjectIndexer(str(Path.cwd()))
            except ImportError:
                pass
        return self._project_indexer

    @property
    def plugin_manager(self):
        """Lazy load plugin manager"""
        if self._plugin_manager is None:
            try:
                from .plugins import PluginManager
                self._plugin_manager = PluginManager()
                # Discover and load built-in plugins
                self._plugin_manager.discover_plugins()
                self._plugin_manager.load_all()
            except ImportError:
                pass
        return self._plugin_manager

    @property
    def mcp_manager(self):
        """Lazy load MCP manager"""
        if self._mcp_manager is None:
            try:
                from .mcp import MCPManager
                self._mcp_manager = MCPManager(name="nc1709", version="1.0.0")
                self._mcp_manager.setup_default_tools()
            except ImportError:
                pass
        return self._mcp_manager

    @property
    def cognitive_system(self):
        """Lazy load cognitive system - the brain of NC1709"""
        if self._cognitive_system is None and self._cognitive_enabled and HAS_COGNITIVE:
            try:
                self._cognitive_system = get_cognitive_system(
                    llm_adapter=self.llm if hasattr(self, 'llm') else None,
                    project_root=Path.cwd(),
                    enable_anticipation=True,
                    enable_learning=True,
                )
                # Index project for context awareness (in background)
                # self._cognitive_system.index_project(incremental=True)
            except Exception:
                pass
        return self._cognitive_system

    @property
    def agent(self):
        """Lazy load agent"""
        if self._agent is None and HAS_AGENT and self.llm:
            try:
                # Create agent configuration
                config = AgentConfig(
                    max_iterations=self.config.get("agent.max_iterations", 50),
                    verbose=self.config.get("ui.verbose", False),
                )

                # Create agent
                self._agent = Agent(llm=self.llm, config=config)

                # Integrate MCP tools if available
                if self.mcp_manager:
                    try:
                        integrate_mcp_with_agent(self._agent, self.mcp_manager)
                    except Exception as e:
                        warning(f"Failed to integrate MCP with agent: {e}")

            except Exception as e:
                error(f"Failed to create agent: {e}")
                self._agent = None
        return self._agent

    def run(self, args: Optional[list] = None) -> int:
        """Run the CLI

        Args:
            args: Command line arguments (default: sys.argv)

        Returns:
            Exit code
        """
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)

        # Handle different modes
        if parsed_args.version:
            self._print_version()
            return 0

        if parsed_args.config:
            self._show_config()
            return 0

        # Session management
        if parsed_args.sessions:
            return self._list_sessions()

        if parsed_args.resume:
            return self._run_shell(resume_session=parsed_args.resume)

        # Project indexing
        if parsed_args.index:
            return self._index_project()

        if parsed_args.search:
            return self._search_code(parsed_args.search)

        # Plugin commands
        if parsed_args.plugins:
            return self._list_plugins()

        if parsed_args.plugin:
            return self._run_plugin_action(parsed_args.plugin)

        # MCP commands
        if parsed_args.mcp_status:
            return self._mcp_show_status()

        if parsed_args.mcp_serve:
            return self._mcp_run_server()

        if parsed_args.mcp_connect:
            return self._mcp_connect_servers(parsed_args.mcp_connect)

        if parsed_args.mcp_tool:
            args_json = parsed_args.args if parsed_args.args else "{}"
            return self._mcp_call_tool(parsed_args.mcp_tool, args_json)

        # Web dashboard
        if parsed_args.web:
            serve_remote = getattr(parsed_args, 'serve', False)
            return self._run_web_dashboard(parsed_args.port, serve_remote=serve_remote)

        # Shell completions
        if parsed_args.completion:
            return self._generate_completion(parsed_args.completion)

        # AI Agents
        if parsed_args.fix:
            auto_apply = getattr(parsed_args, 'apply', False)
            return self._run_auto_fix(parsed_args.fix, auto_apply=auto_apply)

        if parsed_args.generate_tests:
            output_file = getattr(parsed_args, 'output', None)
            return self._run_test_generator(parsed_args.generate_tests, output_file=output_file)

        # Agent mode
        if parsed_args.agent:
            self._agent_mode = True

        if parsed_args.shell or not parsed_args.prompt:
            # Interactive shell mode
            return self._run_shell()
        else:
            # Direct command mode
            return self._run_command(parsed_args.prompt)
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser
        
        Returns:
            Argument parser
        """
        parser = argparse.ArgumentParser(
            prog="nc1709",
            description="NC1709 - A Local-First AI Developer Assistant",
            epilog="Examples:\n"
                   "  nc1709 'create a Python script to parse JSON'\n"
                   "  nc1709 --shell\n"
                   "  nc1709 --config",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            "prompt",
            nargs="?",
            help="Your request or question"
        )
        
        parser.add_argument(
            "-s", "--shell",
            action="store_true",
            help="Start interactive shell mode"
        )
        
        parser.add_argument(
            "-v", "--version",
            action="store_true",
            help="Show version information"
        )
        
        parser.add_argument(
            "-c", "--config",
            action="store_true",
            help="Show current configuration"
        )
        
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output"
        )

        # Session management arguments
        parser.add_argument(
            "--sessions",
            action="store_true",
            help="List saved sessions"
        )

        parser.add_argument(
            "--resume",
            metavar="SESSION_ID",
            help="Resume a previous session"
        )

        # Memory/indexing arguments
        parser.add_argument(
            "--index",
            action="store_true",
            help="Index the current project for semantic search"
        )

        parser.add_argument(
            "--search",
            metavar="QUERY",
            help="Search indexed code semantically"
        )

        # Plugin arguments
        parser.add_argument(
            "--plugins",
            action="store_true",
            help="List available plugins"
        )

        parser.add_argument(
            "--plugin",
            metavar="NAME",
            help="Execute a plugin action (e.g., --plugin git:status)"
        )

        # MCP arguments
        parser.add_argument(
            "--mcp-status",
            action="store_true",
            help="Show MCP server status and available tools"
        )

        parser.add_argument(
            "--mcp-serve",
            action="store_true",
            help="Run NC1709 as an MCP server (stdio transport)"
        )

        parser.add_argument(
            "--mcp-connect",
            metavar="CONFIG",
            help="Connect to MCP servers from config file"
        )

        parser.add_argument(
            "--mcp-tool",
            metavar="TOOL",
            help="Call an MCP tool (e.g., --mcp-tool read_file --args '{\"path\": \"file.txt\"}')"
        )

        parser.add_argument(
            "--args",
            metavar="JSON",
            help="JSON arguments for --mcp-tool"
        )

        # Web Dashboard arguments
        parser.add_argument(
            "--web",
            action="store_true",
            help="Start the web dashboard (default: http://localhost:8709)"
        )

        parser.add_argument(
            "--port",
            type=int,
            default=8709,
            help="Port for web dashboard (default: 8709)"
        )

        # Remote mode arguments
        parser.add_argument(
            "--remote",
            metavar="URL",
            help="Connect to remote NC1709 server (e.g., --remote https://your-server.ngrok.io)"
        )

        parser.add_argument(
            "--api-key",
            metavar="KEY",
            help="API key for remote server authentication"
        )

        parser.add_argument(
            "--serve",
            action="store_true",
            help="Run as a server for remote clients (use with --web)"
        )

        parser.add_argument(
            "--local",
            action="store_true",
            help="Force local mode (use local Ollama instead of remote server)"
        )

        # AI Agents arguments
        parser.add_argument(
            "--fix",
            metavar="FILE",
            help="Auto-fix code errors in a file"
        )

        parser.add_argument(
            "--apply",
            action="store_true",
            help="Auto-apply fixes (use with --fix)"
        )

        parser.add_argument(
            "--generate-tests",
            metavar="FILE",
            help="Generate unit tests for a file"
        )

        parser.add_argument(
            "--output",
            metavar="FILE",
            help="Output file for generated tests (use with --generate-tests)"
        )

        # Shell completions
        parser.add_argument(
            "--completion",
            choices=["bash", "zsh", "fish"],
            help="Generate shell completion script"
        )

        # Agentic mode
        parser.add_argument(
            "--agent", "-a",
            action="store_true",
            help="Enable agentic mode with tool execution (Claude Code-style)"
        )

        parser.add_argument(
            "--permission",
            choices=["strict", "normal", "permissive", "trust"],
            default="normal",
            help="Permission policy for agent tools (default: normal)"
        )

        return parser
    
    def _print_version(self) -> None:
        """Print version information"""
        from . import __version__
        print(f"NC1709 CLI v{__version__}")
        print("A Local-First AI Developer Assistant")

        if self.remote_client:
            print(f"\n🌐 Remote Mode: {self.remote_url}")
            try:
                status = self.remote_client.check_status()
                print(f"   Server: {status.get('server', 'nc1709')}")
                print(f"   Version: {status.get('version', 'unknown')}")
                models = status.get('models', {})
                if models:
                    print("\n   Available Models:")
                    for task, model in models.items():
                        print(f"     {task:12} → {model}")
            except Exception as e:
                print(f"   (Unable to fetch server info: {e})")
        elif self.llm:
            print("\nConfigured Models:")
            for task_type in TaskType:
                model_info = self.llm.get_model_info(task_type)
                print(f"  {task_type.value:12} → {model_info['model']}")
    
    def _show_config(self) -> None:
        """Show current configuration in a user-friendly format"""
        from . import __version__

        C = '\033[36m'   # Cyan
        B = '\033[1m'    # Bold
        G = '\033[32m'   # Green
        Y = '\033[33m'   # Yellow
        D = '\033[2m'    # Dim
        R = '\033[0m'    # Reset

        print(f"\n{B}NC1709 Configuration{R}\n")

        # Connection info
        if self.remote_client:
            print(f"  {C}Mode{R}          Remote (Cloud)")
            print(f"  {C}Server{R}        {self.remote_url}")
        else:
            print(f"  {C}Mode{R}          Local (Ollama)")
            ollama_url = self.config.get("ollama.base_url", "http://localhost:11434")
            print(f"  {C}Ollama{R}        {ollama_url}")

        print(f"  {C}Version{R}       {__version__}")

        # Safety settings (simplified)
        confirm_writes = self.config.get("safety.confirm_writes", True)
        confirm_cmds = self.config.get("safety.confirm_commands", True)
        safety_status = f"{G}On{R}" if (confirm_writes and confirm_cmds) else f"{Y}Partial{R}"
        print(f"  {C}Safety{R}        {safety_status}")

        # Memory
        memory_enabled = self.config.get("memory.enabled", False)
        memory_status = f"{G}Enabled{R}" if memory_enabled else f"{D}Disabled{R}"
        print(f"  {C}Memory{R}        {memory_status}")

        # Agent mode
        agent_status = f"{G}Enabled{R}" if self._agent_mode else f"{D}Disabled{R}"
        print(f"  {C}Agent Mode{R}    {agent_status}")

        print(f"\n{D}Config file: {self.config.config_path}{R}")
        print(f"{D}Use '/config raw' for full JSON, '/config edit' to modify{R}\n")

    def _show_config_raw(self) -> None:
        """Show full configuration as JSON (for advanced users)"""
        import json
        print("\nFull Configuration (JSON):\n")
        print(json.dumps(self.config.config, indent=2))
        print(f"\nConfig file: {self.config.config_path}")

    def _run_shell(self, resume_session: Optional[str] = None) -> int:
        """Run interactive shell mode

        Args:
            resume_session: Session ID to resume

        Returns:
            Exit code
        """
        self._print_banner()

        # Initialize conversation logger for this session
        if HAS_CONVERSATION_LOGGER:
            mode = "remote" if self.remote_client else "local"
            self._conversation_logger = init_logger(mode=mode)
            log_system("Session started", {"mode": mode, "cwd": str(Path.cwd())})

        # Initialize or resume session
        if self.session_manager:
            if resume_session:
                session = self.session_manager.load_session(resume_session)
                if session:
                    self.session_manager.current_session = session
                    print(f"📂 Resumed session: {session.name} ({len(session.messages)} messages)")
                else:
                    print(f"⚠️  Session '{resume_session}' not found, starting new session")
                    self.session_manager.start_session(project_path=str(Path.cwd()))
            else:
                self.session_manager.start_session(project_path=str(Path.cwd()))

        # Show tools count and session ID (Claude Code style)
        if self.remote_client:
            tools_count = getattr(self, '_remote_tools_count', 17)
            print(f"{Color.GREEN}●{Color.RESET} {tools_count} tools available")
        else:
            # Count local tools
            tools_count = 0
            if hasattr(self, '_local_registry') and self._local_registry:
                tools_count = len(self._local_registry.list_names())
            print(f"{Color.GREEN}●{Color.RESET} {tools_count} tools available")

        # Show session ID
        if HAS_CONVERSATION_LOGGER and hasattr(self, '_conversation_logger') and self._conversation_logger:
            session_id = self._conversation_logger.session_id[:16]  # Shortened
            print(f"{Color.GREEN}●{Color.RESET} Session: {Color.DIM}{session_id}{Color.RESET}")

        # Initialize file tracking for this session
        self._session_files_created = []
        self._session_files_modified = []

        print()

        # Set up prompt_toolkit with slash command completion
        prompt_session = self._create_prompt_session()

        while self.running:
            try:
                # Get user input with styled prompt and autocomplete
                prompt = self._get_user_input(prompt_session)

                if not prompt:
                    continue

                # Normalize command (remove leading / for slash commands)
                cmd = prompt[1:] if prompt.startswith('/') else prompt
                cmd_lower = cmd.lower()

                # Handle special commands
                if cmd_lower in ["exit", "quit", "q"]:
                    if self.session_manager and self.session_manager.current_session:
                        self.session_manager.save_session(self.session_manager.current_session)
                        info(f"Session saved: {self.session_manager.current_session.id}")
                    success("Goodbye!")
                    break

                if cmd_lower == "help":
                    self._print_help()
                    continue

                if cmd_lower == "clear":
                    if self.llm:
                        self.llm.clear_history()
                    success("Conversation history cleared")
                    continue

                if cmd_lower == "history":
                    self._show_history()
                    continue

                if cmd_lower == "version":
                    self._print_version()
                    continue

                if cmd_lower == "config":
                    self._show_config()
                    continue

                if cmd_lower == "config raw":
                    self._show_config_raw()
                    continue

                if cmd_lower.startswith("config "):
                    self._handle_config_command(cmd)
                    continue

                # Session management commands
                if cmd_lower == "sessions":
                    self._list_sessions()
                    continue

                # Conversation logs commands
                if cmd_lower == "logs":
                    self._show_conversation_logs()
                    continue

                if cmd_lower.startswith("logs "):
                    session_id = cmd[5:].strip()
                    self._show_conversation_log(session_id)
                    continue

                if cmd_lower == "save":
                    if self.session_manager and self.session_manager.current_session:
                        self.session_manager.save_session(self.session_manager.current_session)
                        success(f"Session saved: {self.session_manager.current_session.id}")
                    else:
                        warning("No active session to save")
                    continue

                if cmd_lower.startswith("search "):
                    query = cmd[7:].strip()
                    self._search_code(query)
                    continue

                if cmd_lower == "index":
                    self._index_project()
                    continue

                # Plugin commands
                if cmd_lower == "plugins":
                    self._list_plugins()
                    continue

                if cmd_lower.startswith("git "):
                    self._run_plugin_action(f"git:{cmd[4:].strip()}")
                    continue

                if cmd_lower.startswith("docker "):
                    self._run_plugin_action(f"docker:{cmd[7:].strip()}")
                    continue

                # MCP commands
                if cmd_lower == "mcp":
                    self._mcp_show_status()
                    continue

                if cmd_lower == "mcp tools":
                    self._mcp_list_tools()
                    continue

                if cmd_lower.startswith("mcp call "):
                    tool_spec = cmd[9:].strip()
                    self._mcp_call_tool_interactive(tool_spec)
                    continue

                # Agent mode commands
                if cmd_lower in ["agent", "agent on"]:
                    if HAS_AGENT:
                        self._agent_mode = True
                        success("Agent mode enabled. Autonomous tool execution active.")
                    else:
                        error("Agent module not available")
                    continue

                if cmd_lower == "agent off":
                    self._agent_mode = False
                    info("Agent mode disabled. Using standard reasoning engine.")
                    continue

                # Cognitive system commands
                if cmd_lower in ["brain", "brain status"]:
                    self._brain_show_status()
                    continue

                if cmd_lower == "brain suggest":
                    self._brain_show_suggestions()
                    continue

                if cmd_lower == "brain index":
                    self._brain_index_project()
                    continue

                if cmd_lower == "brain insights":
                    self._brain_show_insights()
                    continue

                # Checkpoint commands
                if cmd_lower in ["rewind", "undo"]:
                    self._rewind_checkpoint()
                    continue

                if cmd_lower in ["forward", "redo"]:
                    self._forward_checkpoint()
                    continue

                if cmd_lower == "checkpoints":
                    self._list_checkpoints()
                    continue

                # Git autocommit commands
                if cmd_lower == "autocommit":
                    self._toggle_autocommit()
                    continue

                if cmd_lower == "autocommit on":
                    self._set_autocommit(True)
                    continue

                if cmd_lower == "autocommit off":
                    self._set_autocommit(False)
                    continue

                if cmd_lower == "agent tools":
                    self._show_agent_tools()
                    continue

                if cmd_lower == "agent status":
                    self._show_agent_status()
                    continue

                # Model Registry commands
                if cmd_lower in ["models", "models list"]:
                    self._show_models()
                    continue

                if cmd_lower == "models detect":
                    self._detect_models()
                    continue

                if cmd_lower == "models recommend":
                    self._recommend_models()
                    continue

                # Code action commands (these get passed to AI with context)
                if cmd_lower.startswith("fix "):
                    file_path = cmd[4:].strip()
                    self._run_auto_fix(file_path)
                    continue

                if cmd_lower.startswith("test "):
                    file_path = cmd[5:].strip()
                    self._run_test_generator(file_path)
                    continue

                # Quick commands
                if cmd_lower.startswith("run "):
                    shell_cmd = cmd[4:].strip()
                    self._quick_run_command(shell_cmd)
                    continue

                if cmd_lower == "web":
                    self._run_web_dashboard()
                    continue

                # Custom commands
                if cmd_lower == "commands":
                    self._list_custom_commands()
                    continue

                # Image input commands
                if cmd_lower.startswith("image "):
                    image_path = cmd[6:].strip()
                    self._add_image(image_path)
                    continue

                if cmd_lower == "screenshot":
                    self._capture_screenshot()
                    continue

                if cmd_lower == "paste":
                    self._paste_clipboard_image()
                    continue

                if cmd_lower == "images":
                    self._list_pending_images()
                    continue

                if cmd_lower == "clear-images":
                    self._clear_pending_images()
                    continue

                # Plan mode commands
                if cmd_lower == "plan":
                    self._enter_plan_mode()
                    continue

                if cmd_lower == "plan approve":
                    self._approve_plan()
                    continue

                if cmd_lower == "plan reject":
                    self._reject_plan()
                    continue

                if cmd_lower == "plan show":
                    self._show_plan()
                    continue

                if cmd_lower == "plan exit":
                    self._exit_plan_mode()
                    continue

                # Requirements tracking commands
                if cmd_lower in ["requirements", "reqs"]:
                    self._show_requirements()
                    continue

                if cmd_lower.startswith("requirements init ") or cmd_lower.startswith("reqs init "):
                    parts = cmd.split(" ", 2)
                    name = parts[2] if len(parts) > 2 else ""
                    self._init_requirements(name)
                    continue

                if cmd_lower.startswith("requirements add ") or cmd_lower.startswith("reqs add "):
                    parts = cmd.split(" ", 2)
                    title = parts[2] if len(parts) > 2 else ""
                    self._add_requirement(title)
                    continue

                if cmd_lower.startswith("requirements done ") or cmd_lower.startswith("reqs done "):
                    parts = cmd.split(" ", 2)
                    req_id = parts[2] if len(parts) > 2 else ""
                    self._complete_requirement(req_id)
                    continue

                if cmd_lower.startswith("requirements start ") or cmd_lower.startswith("reqs start "):
                    parts = cmd.split(" ", 2)
                    req_id = parts[2] if len(parts) > 2 else ""
                    self._start_requirement(req_id)
                    continue

                if cmd_lower.startswith("requirements note "):
                    parts = cmd.split(" ", 3)
                    if len(parts) >= 4:
                        req_id = parts[2]
                        note = parts[3]
                        self._add_requirement_note(req_id, note)
                    continue

                if cmd_lower in ["requirements all", "reqs all"]:
                    self._show_requirements(include_completed=True)
                    continue

                # GitHub/PR commands
                if cmd_lower == "pr":
                    self._create_pr_interactive()
                    continue

                if cmd_lower == "pr list":
                    self._list_prs()
                    continue

                if cmd_lower.startswith("pr view "):
                    pr_num = cmd[8:].strip()
                    self._view_pr(pr_num)
                    continue

                if cmd_lower == "issues":
                    self._list_issues()
                    continue

                if cmd_lower.startswith("gh "):
                    gh_cmd = cmd[3:].strip()
                    self._run_gh_command(gh_cmd)
                    continue

                # Linting commands
                if cmd_lower == "lint":
                    self._run_lint()
                    continue

                if cmd_lower == "lint linters":
                    self._list_linters()
                    continue

                if cmd_lower.startswith("lint file "):
                    file_path = cmd[10:].strip()
                    self._lint_file(file_path)
                    continue

                if cmd_lower == "lint fix":
                    self._lint_fix()
                    continue

                if cmd_lower.startswith("lint fix "):
                    target = cmd[9:].strip()
                    self._lint_fix(target)
                    continue

                if cmd_lower.startswith("lint "):
                    # Lint specific target
                    target = cmd[5:].strip()
                    self._run_lint(target=target)
                    continue

                # Check if this is a custom command (try to execute it)
                if HAS_CUSTOM_COMMANDS:
                    custom_content = execute_custom_command(cmd)
                    if custom_content:
                        # Execute the custom command by passing its content as a prompt
                        info(f"Running custom command: /{cmd}")
                        self._process_request(custom_content)
                        continue

                # Process the request (either a plain prompt or unrecognized command)
                self._process_request(prompt)

            except KeyboardInterrupt:
                warning("\nUse 'exit' to quit.")
                continue

            except Exception as e:
                error(f"Error: {e}")
                if self.config.get("ui.verbose"):
                    import traceback
                    traceback.print_exc()

        return 0
    
    def _create_prompt_session(self):
        """Create a prompt_toolkit session with slash command completion

        Returns:
            PromptSession configured with completions and styling
        """
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
        from prompt_toolkit.styles import Style

        try:
            from .slash_commands import SlashCommandCompleter
            completer = SlashCommandCompleter()
        except ImportError:
            completer = None

        # Custom style for completions
        style = Style.from_dict({
            'completion-menu.completion': 'bg:#333333 #ffffff',
            'completion-menu.completion.current': 'bg:#00aaaa #ffffff bold',
            'completion-menu.meta.completion': 'bg:#333333 #888888',
            'completion-menu.meta.completion.current': 'bg:#00aaaa #ffffff',
            'scrollbar.background': 'bg:#333333',
            'scrollbar.button': 'bg:#666666',
        })

        return PromptSession(
            history=InMemoryHistory(),
            auto_suggest=AutoSuggestFromHistory(),
            completer=completer,
            complete_while_typing=True,  # Show completions as you type
            style=style,
            multiline=False,
        )

    def _get_user_input(self, session) -> str:
        """Get user input using prompt_toolkit with completions

        Args:
            session: PromptSession instance

        Returns:
            User input string (stripped)
        """
        from prompt_toolkit.formatted_text import HTML

        # Create colored prompt
        prompt_text = HTML('<cyan>❯</cyan> <bold>nc1709&gt;</bold> ')

        try:
            return session.prompt(prompt_text).strip()
        except EOFError:
            return "exit"
        except KeyboardInterrupt:
            return ""

    def _quick_run_command(self, cmd: str) -> None:
        """Quickly run a shell command and show output

        Args:
            cmd: Shell command to run
        """
        import subprocess

        print(f"\n{Color.DIM}$ {cmd}{Color.RESET}\n")

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"{Color.YELLOW}{result.stderr}{Color.RESET}")

            if result.returncode != 0:
                warning(f"Command exited with code {result.returncode}")
            else:
                success("Command completed")

        except subprocess.TimeoutExpired:
            error("Command timed out after 60 seconds")
        except Exception as e:
            error(f"Error running command: {e}")

    def _run_command(self, prompt: str) -> int:
        """Run a single command

        Args:
            prompt: User's prompt

        Returns:
            Exit code
        """
        try:
            self._process_request(prompt)
            return 0
        except Exception as e:
            error(f"Error: {e}")
            return 1
    
    def _process_request(self, prompt: str) -> None:
        """Process a user request

        Args:
            prompt: User's prompt
        """
        # Log user message
        if HAS_CONVERSATION_LOGGER:
            log_user(prompt)

        if self.remote_client:
            # Remote mode with LOCAL tool execution
            # Server only provides LLM thinking, tools run on user's machine
            self._process_request_remote_agent(prompt)
        elif self._agent_mode and HAS_AGENT:
            # Agent mode - use the agent for tool execution
            self._process_request_agent(prompt)
        else:
            # Local mode - use cognitive system if available
            if self.cognitive_system and HAS_COGNITIVE:
                # Use the 5-layer cognitive architecture
                self._process_request_cognitive(prompt)
            else:
                # Fallback to standard reasoning engine
                # Classify the task
                task_type = TaskClassifier.classify(prompt)

                # Get context
                context = {
                    "cwd": str(Path.cwd()),
                    "task_type": task_type.value
                }

                # Use reasoning engine for complex requests
                response = self.reasoning_engine.process_request(prompt, context)

                # Print response with text wrapping
                print_response(response)

    def _process_request_cognitive(self, prompt: str) -> None:
        """Process a user request using the 5-layer cognitive architecture

        This is the core NC1709 differentiator:
        - Layer 1: Intelligent Router - routes to best model
        - Layer 2: Deep Context - provides codebase understanding
        - Layer 3: Multi-Agent Council - experts collaborate on complex tasks
        - Layer 4: Learning Core - learns from user patterns
        - Layer 5: Anticipation - predicts needs before asked

        Args:
            prompt: User's prompt
        """
        from .cli_ui import thinking, info

        thinking("Processing with cognitive architecture...")

        # Create cognitive request
        request = CognitiveRequest(
            prompt=prompt,
            context={"cwd": str(Path.cwd())},
            stream=False,
        )

        # Process through cognitive system
        response = self.cognitive_system.process(request)

        # Print main response with text wrapping
        print_response(response.content)

        # Show cognitive metadata (subtle)
        model_info = f"[{response.category}]"
        if response.council_used and response.council_agents:
            model_info += f" Council: {', '.join(response.council_agents)}"
        else:
            model_info += f" {response.model_used}"

        if response.processing_time_ms:
            model_info += f" ({response.processing_time_ms}ms)"

        info(model_info)

        # Show proactive suggestions if any
        if response.suggestions:
            print()
            info("💡 Suggestions:")
            for suggestion in response.suggestions[:3]:
                confidence = suggestion.get('confidence', 0)
                icon = "🔥" if confidence > 0.8 else "💭" if confidence > 0.5 else "💡"
                print(f"   {icon} {suggestion['title']}")
                if suggestion.get('description'):
                    print(f"      {suggestion['description'][:80]}...")

    def _process_request_remote_agent(self, prompt: str) -> None:
        """Process a user request using remote LLM but LOCAL tool execution

        This is the correct architecture:
        - Server: Only runs LLM (thinking/reasoning)
        - Client: Executes all tools locally on user's machine

        Args:
            prompt: User's prompt
        """
        import json
        import re

        # Initialize local tool registry for executing tools
        if not hasattr(self, '_local_registry') or self._local_registry is None:
            from .agent.tools.base import ToolRegistry
            from .agent.tools.file_tools import register_file_tools
            from .agent.tools.search_tools import register_search_tools
            from .agent.tools.bash_tool import register_bash_tools
            from .agent.tools.web_tools import register_web_tools

            self._local_registry = ToolRegistry()
            register_file_tools(self._local_registry)
            register_search_tools(self._local_registry)
            register_bash_tools(self._local_registry)
            register_web_tools(self._local_registry)

        # Get conversation history from session (if available)
        messages = []
        if self.session_manager and self.session_manager.current_session:
            # Load previous messages for context (last 20 messages)
            messages = self.session_manager.get_current_history(limit=20)

        # Add current user prompt
        messages.append({"role": "user", "content": prompt})

        # Save user message to session
        if self.session_manager:
            self.session_manager.add_message("user", prompt, auto_save=True)

        max_iterations = 50
        iteration = 0
        tool_history = []
        final_response = ""

        # Track files created/modified in this request
        files_created = []
        files_modified = []

        print()  # Add spacing

        # Show analyzing status (Claude Code style)
        print(f"{Color.YELLOW}{Icons.BULLET}{Color.RESET} Analyzing request...")

        while iteration < max_iterations:
            iteration += 1
            if iteration > 1:
                thinking(f"Thinking... (iteration {iteration})")

            try:
                # Call remote server for LLM response (NO tool execution on server)
                result = self.remote_client.agent_chat(
                    messages=messages,
                    cwd=str(Path.cwd()),
                    tools=list(self._local_registry.list_names())
                )

                response = result.get("response", "")

                # Parse tool calls from response
                tool_calls = self._parse_tool_calls_from_response(response)

                if not tool_calls:
                    # No tool calls - LLM is done, show final response
                    # Clean the response (remove any tool markers)
                    clean_response = self._clean_response_text(response)
                    print_response(clean_response)

                    # Log assistant response
                    if HAS_CONVERSATION_LOGGER:
                        log_assistant(clean_response)

                    # Save assistant response to session for memory
                    if self.session_manager:
                        self.session_manager.add_message("assistant", clean_response, auto_save=True)

                    # Show completion summary with file tree (Claude Code style)
                    if files_created or files_modified:
                        self._show_file_summary(files_created, files_modified)

                    # Update session-level file tracking
                    if hasattr(self, '_session_files_created'):
                        self._session_files_created.extend(files_created)
                    if hasattr(self, '_session_files_modified'):
                        self._session_files_modified.extend(files_modified)

                    # Flush any remaining files to index
                    self._flush_index_queue()

                    return

                # Execute tools LOCALLY
                all_results = []
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_params = tool_call["parameters"]

                    tool = self._local_registry.get(tool_name)
                    if not tool:
                        result_text = f"Error: Unknown tool '{tool_name}'"
                        all_results.append(f"[{tool_name}] {result_text}")
                        tool_history.append({"tool": tool_name, "target": "?", "success": False})
                        continue

                    # Get target for display
                    target = tool._get_target(**tool_params) if hasattr(tool, '_get_target') else str(tool_params)[:30]

                    # Check if tool needs approval
                    if self._local_registry.needs_approval(tool_name):
                        print(f"\n{Color.YELLOW}Tool requires approval:{Color.RESET}")
                        print(f"  {Color.BOLD}{tool_name}{Color.RESET}({Color.CYAN}{target}{Color.RESET})")
                        if tool_params:
                            print(f"  Parameters: {json.dumps(tool_params, indent=2)[:200]}")

                        approval = input(f"\n{Color.BOLD}Allow?{Color.RESET} [y/N/always]: ").strip().lower()
                        if approval == "always":
                            self._local_registry.approve_for_session(tool_name)
                        elif approval not in ["y", "yes"]:
                            result_text = "Tool execution denied by user"
                            all_results.append(f"[{tool_name}] {result_text}")
                            tool_history.append({"tool": tool_name, "target": target, "success": False})
                            continue

                    # Execute tool locally with Claude Code-style UI
                    log_action(tool_name, target)

                    try:
                        import time
                        start_time = time.time()
                        tool_result = tool.run(**tool_params)
                        duration_ms = int((time.time() - start_time) * 1000)

                        if tool_result.success:
                            result_text = tool_result.output

                            # Track file operations
                            file_path = tool_params.get("file_path") or tool_params.get("path") or target
                            if tool_name == "Write":
                                # Track new file creation
                                files_created.append(file_path)
                                # Enhanced output for Write - show line count
                                content = tool_params.get("content", "")
                                line_count = content.count('\n') + 1 if content else 0
                                log_output(f"Written {line_count} lines", is_error=False)
                            elif tool_name == "Edit":
                                # Track file modification
                                files_modified.append(file_path)
                                log_output(f"File modified", is_error=False)
                            else:
                                # Show output in Claude Code style (truncated for readability)
                                log_output(result_text, is_error=False)

                            tool_history.append({"tool": tool_name, "target": target, "success": True})

                            # Log tool call
                            if HAS_CONVERSATION_LOGGER:
                                log_tool(tool_name, tool_params, result_text[:1000], success=True, duration_ms=duration_ms)

                            # Auto-index files when Read tool is used
                            if tool_name == "Read" and hasattr(self, '_user_id'):
                                self._queue_file_for_indexing(
                                    file_path=tool_params.get("file_path", target),
                                    content=result_text
                                )
                        else:
                            result_text = f"Error: {tool_result.error}"
                            log_output(result_text, is_error=True)
                            tool_history.append({"tool": tool_name, "target": target, "success": False})

                            # Log failed tool call
                            if HAS_CONVERSATION_LOGGER:
                                log_tool(tool_name, tool_params, result_text, success=False, duration_ms=duration_ms)

                        all_results.append(f"[{tool_name}({target})] {result_text}")

                    except Exception as e:
                        result_text = f"Exception: {str(e)}"
                        log_output(result_text, is_error=True)
                        all_results.append(f"[{tool_name}] {result_text}")
                        tool_history.append({"tool": tool_name, "target": target, "success": False})

                        # Log exception
                        if HAS_CONVERSATION_LOGGER:
                            log_error(result_text, {"tool": tool_name, "params": tool_params})

                # Add assistant response and tool results to conversation
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": f"Tool results:\n\n" + "\n\n".join(all_results) + "\n\nContinue with the task based on these results."
                })

            except Exception as e:
                error(f"Remote request failed: {e}")
                if self.config.get("ui.verbose"):
                    import traceback
                    traceback.print_exc()
                return

        warning(f"Reached maximum iterations ({max_iterations})")

    def _parse_tool_calls_from_response(self, response: str) -> list:
        """Parse tool calls from LLM response

        Args:
            response: LLM response text

        Returns:
            List of tool calls [{"name": ..., "parameters": {...}}, ...]
        """
        import json
        import re

        tool_calls = []

        # Pattern 1: ```tool ... ``` blocks
        pattern = r"```tool\s*\n?(.*?)\n?```"
        matches = re.findall(pattern, response, re.DOTALL)

        for match in matches:
            try:
                data = json.loads(match.strip())
                if "tool" in data:
                    tool_calls.append({
                        "name": data["tool"],
                        "parameters": data.get("parameters", {})
                    })
            except json.JSONDecodeError:
                continue

        # Pattern 2: JSON objects with "tool" key
        json_pattern = r'\{[^{}]*"tool"\s*:\s*"[^"]+"\s*[^{}]*\}'
        json_matches = re.findall(json_pattern, response)

        for match in json_matches:
            # Don't duplicate
            if any(match in tc.get("raw", "") for tc in tool_calls):
                continue
            try:
                data = json.loads(match)
                if "tool" in data:
                    tool_calls.append({
                        "name": data["tool"],
                        "parameters": data.get("parameters", {}),
                        "raw": match
                    })
            except json.JSONDecodeError:
                continue

        return tool_calls

    def _clean_response_text(self, response: str) -> str:
        """Remove tool call markers from final response

        Args:
            response: Raw LLM response

        Returns:
            Cleaned response text
        """
        import re

        # Remove tool blocks
        response = re.sub(r"```tool\s*\n?.*?\n?```", "", response, flags=re.DOTALL)
        # Remove JSON tool calls
        response = re.sub(r'\{[^{}]*"tool"\s*:\s*"[^"]+"\s*[^{}]*\}', "", response)
        return response.strip()

    def _queue_file_for_indexing(self, file_path: str, content: str) -> None:
        """Queue a file for indexing on the server

        Args:
            file_path: Path to the file
            content: File content
        """
        if not hasattr(self, '_files_to_index'):
            self._files_to_index = []
        if not hasattr(self, '_indexed_files'):
            self._indexed_files = set()

        # Don't re-index same file in this session
        if file_path in self._indexed_files:
            return

        # Determine language from extension
        ext_to_lang = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.jsx': 'javascript', '.tsx': 'typescript', '.go': 'go',
            '.rs': 'rust', '.java': 'java', '.c': 'c', '.cpp': 'cpp',
            '.h': 'c', '.hpp': 'cpp', '.rb': 'ruby', '.php': 'php',
            '.swift': 'swift', '.kt': 'kotlin', '.scala': 'scala',
            '.md': 'markdown', '.json': 'json', '.yaml': 'yaml',
            '.yml': 'yaml', '.toml': 'toml', '.html': 'html',
            '.css': 'css', '.sql': 'sql', '.sh': 'shell',
        }
        ext = Path(file_path).suffix.lower()
        language = ext_to_lang.get(ext, 'text')

        self._files_to_index.append({
            "path": file_path,
            "content": content[:50000],  # Limit content size
            "language": language
        })
        self._indexed_files.add(file_path)

        # Batch index every 5 files
        if len(self._files_to_index) >= 5:
            self._flush_index_queue()

    def _flush_index_queue(self) -> None:
        """Send queued files to server for indexing"""
        if not hasattr(self, '_files_to_index') or not self._files_to_index:
            return

        if not self.remote_client or not hasattr(self, '_user_id'):
            return

        try:
            project_name = Path.cwd().name

            result = self.remote_client.index_code(
                user_id=self._user_id,
                files=self._files_to_index,
                project_name=project_name
            )

            # Clear queue on success
            self._files_to_index = []

        except Exception as e:
            # Silently fail - indexing is best-effort
            pass

    def _process_request_agent(self, prompt: str) -> None:
        """Process a user request using the agent

        Args:
            prompt: User's prompt
        """
        if not self.agent:
            error("Agent not available. Check LLM configuration.")
            return

        print()  # Add spacing
        thinking("Processing with agent...")

        try:
            response = self.agent.run(prompt)

            # Show tool execution history
            tool_history = self.agent.get_tool_history()
            if tool_history:
                print(f"\n{Color.DIM}Tools executed: {len(tool_history)}{Color.RESET}")
                for entry in tool_history[-5:]:  # Show last 5
                    icon = Icons.SUCCESS if entry['success'] else Icons.FAILURE
                    duration = f"{entry['duration_ms']:.0f}ms" if entry['duration_ms'] else ""
                    print(f"  {icon} {entry['tool']}({entry['target']}) {Color.DIM}{duration}{Color.RESET}")

            # Print final response with text wrapping
            print_response(response)

        except Exception as e:
            error(f"Agent error: {e}")
            if self.config.get("ui.verbose"):
                import traceback
                traceback.print_exc()

    def _show_agent_tools(self) -> None:
        """Show available agent tools"""
        if not HAS_AGENT:
            error("Agent module not available")
            return

        if not self.agent:
            warning("Agent not initialized. Enable agent mode first with 'agent on'")
            return

        print(f"\n{Color.BOLD}🔧 Agent Tools{Color.RESET}")
        print("=" * 60)

        # Group tools by category
        tools_by_category = {}
        for tool_name in self.agent.registry.list_names():
            tool = self.agent.registry.get(tool_name)
            if tool:
                category = getattr(tool, 'category', 'other')
                if category not in tools_by_category:
                    tools_by_category[category] = []
                tools_by_category[category].append(tool)

        for category, tools in sorted(tools_by_category.items()):
            print(f"\n{Color.CYAN}{category.title()}{Color.RESET}")
            for tool in tools:
                perm = self.agent.registry.get_permission(tool.name)
                perm_icon = {
                    "auto": f"{Color.GREEN}✓{Color.RESET}",
                    "ask": f"{Color.YELLOW}?{Color.RESET}",
                    "deny": f"{Color.RED}✗{Color.RESET}",
                }.get(perm.value, "?")
                print(f"  {perm_icon} {Color.BOLD}{tool.name}{Color.RESET}")
                print(f"      {Color.DIM}{tool.description[:60]}...{Color.RESET}" if len(tool.description) > 60 else f"      {Color.DIM}{tool.description}{Color.RESET}")

        print(f"\n{Color.DIM}Permission key: ✓=auto, ?=ask, ✗=deny{Color.RESET}")
        print(f"Total tools: {len(self.agent.registry.list_names())}")

    def _show_agent_status(self) -> None:
        """Show agent status and tool history"""
        if not HAS_AGENT:
            error("Agent module not available")
            return

        print(f"\n{Color.BOLD}🤖 Agent Status{Color.RESET}")
        print("=" * 60)

        # Mode status
        mode_status = f"{Color.GREEN}Enabled{Color.RESET}" if self._agent_mode else f"{Color.DIM}Disabled{Color.RESET}"
        print(f"\nAgent Mode: {mode_status}")

        if self._agent:
            # Agent state
            print(f"State: {self._agent.state.value}")
            print(f"Iteration: {self._agent.iteration_count}")
            print(f"Registered Tools: {len(self._agent.registry.list_names())}")

            # Tool history
            history = self._agent.get_tool_history()
            if history:
                print(f"\n{Color.BOLD}Recent Tool Executions:{Color.RESET}")
                for entry in history[-10:]:
                    icon = Icons.SUCCESS if entry['success'] else Icons.FAILURE
                    duration = f"{entry['duration_ms']:.0f}ms" if entry['duration_ms'] else ""
                    print(f"  {icon} {entry['tool']}({entry['target']}) {Color.DIM}{duration}{Color.RESET}")
            else:
                print(f"\n{Color.DIM}No tool executions yet{Color.RESET}")
        else:
            print(f"\n{Color.DIM}Agent not initialized. Use 'agent on' to enable.{Color.RESET}")

    def _show_models(self) -> None:
        """Show Model Registry status and available models"""
        try:
            from .models import (
                get_all_models,
                get_model_spec,
                ModelCapability,
                ModelManager,
            )
        except ImportError:
            error("Model Registry not available. Install nc1709 with all features.")
            return

        print(f"\n{Color.BOLD}Model Registry{Color.RESET}")
        print("=" * 70)

        # Get all known models
        all_models = get_all_models()
        print(f"\n{Color.GREEN}Known Models:{Color.RESET} {len(all_models)}")

        # Group by capability
        capability_groups = {}
        for model_name in all_models:
            spec = get_model_spec(model_name)
            if spec:
                for cap in spec.capabilities:
                    if cap.value not in capability_groups:
                        capability_groups[cap.value] = []
                    capability_groups[cap.value].append(spec)

        # Print models by capability
        cap_icons = {
            "code_generation": "  ",
            "reasoning": "  ",
            "fast_inference": "  ",
            "long_context": "  ",
            "instruction_following": "  ",
            "math": "  ",
            "vision": "  ",
            "function_calling": "  ",
        }

        for cap_name in ["code_generation", "reasoning", "fast_inference", "long_context"]:
            if cap_name in capability_groups:
                models = capability_groups[cap_name]
                icon = cap_icons.get(cap_name, "  ")
                print(f"\n{Color.CYAN}{icon} {cap_name.replace('_', ' ').title()}{Color.RESET}")
                seen = set()
                for spec in models:
                    if spec.ollama_name not in seen:
                        seen.add(spec.ollama_name)
                        ctx = f"{spec.context_window // 1024}K" if spec.context_window else "?"
                        print(f"    {Color.BOLD}{spec.ollama_name:<30}{Color.RESET} {Color.DIM}ctx:{ctx}{Color.RESET}")

        # Show tiering configuration
        try:
            from .performance.tiering import DEFAULT_TIERS, ModelTier
            print(f"\n{Color.BOLD}Model Tiering Configuration:{Color.RESET}")
            for tier, config in DEFAULT_TIERS.items():
                if tier != ModelTier.COUNCIL:
                    tier_name = tier.value.replace("_", " ").title()
                    model_name = config.model.replace("ollama/", "")
                    print(f"    {tier_name:<12} -> {Color.GREEN}{model_name}{Color.RESET}")
        except ImportError:
            pass

        print(f"\n{Color.DIM}Use '/models detect' to auto-detect from Ollama{Color.RESET}")
        print(f"{Color.DIM}Use '/models recommend' to get task recommendations{Color.RESET}")

    def _detect_models(self) -> None:
        """Auto-detect models from Ollama"""
        try:
            from .models import ModelDetector
            import asyncio
        except ImportError:
            error("Model Registry not available")
            return

        print(f"\n{Color.BOLD}Detecting Models from Ollama...{Color.RESET}")

        detector = ModelDetector()
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            models = loop.run_until_complete(detector.list_available_models())
            if models:
                print(f"\n{Color.GREEN}Found {len(models)} models:{Color.RESET}\n")
                for model_name in models:
                    spec = loop.run_until_complete(detector.get_model_spec(model_name))
                    if spec:
                        caps = ", ".join(c.value.replace("_", " ") for c in list(spec.capabilities)[:3])
                        ctx = f"{spec.context_window // 1024}K" if spec.context_window else "?"
                        print(f"  {Color.BOLD}{spec.ollama_name:<30}{Color.RESET}")
                        print(f"      {Color.DIM}Capabilities: {caps}{Color.RESET}")
                        print(f"      {Color.DIM}Context: {ctx}, Format: {spec.prompt_format.value}{Color.RESET}")
            else:
                warning("No models found. Is Ollama running?")
        except Exception as e:
            error(f"Failed to detect models: {e}")

    def _recommend_models(self) -> None:
        """Get model recommendations for different tasks"""
        try:
            from .models import ModelManager
        except ImportError:
            error("Model Registry not available")
            return

        print(f"\n{Color.BOLD}Model Recommendations{Color.RESET}")
        print("=" * 60)

        manager = ModelManager()
        tasks = ["coding", "general", "reasoning", "fast"]

        for task in tasks:
            spec = manager.recommend_model(task)
            if spec:
                print(f"\n{Color.CYAN}{task.title()}{Color.RESET}")
                print(f"    Recommended: {Color.GREEN}{spec.ollama_name}{Color.RESET}")
                score = spec.suitability.get(task, 0)
                print(f"    Suitability: {score:.0%}")
                settings = manager.get_recommended_settings(spec.ollama_name, task)
                print(f"    Temperature: {settings.get('temperature', 0.7)}")

        print(f"\n{Color.DIM}Use these models via tiering or set model explicitly{Color.RESET}")

    def _print_auth_screen(self) -> None:
        """Print compact auth screen with API key instructions"""
        from . import __version__

        # Colors that work on both light and dark terminals
        C = '\033[36m'   # Cyan (works on both)
        B = '\033[1m'    # Bold
        G = '\033[32m'   # Green
        Y = '\033[33m'   # Yellow
        M = '\033[35m'   # Magenta
        R = '\033[0m'    # Reset

        print(f'''
{B}{C}        ███╗   ██╗ ██████╗ ██╗███████╗ ██████╗  █████╗ {R}
{B}{C}        ████╗  ██║██╔════╝███║╚════██║██╔═████╗██╔══██╗{R}
{B}{C}        ██╔██╗ ██║██║     ╚██║    ██╔╝██║██╔██║╚██████║{R}
{B}{C}        ██║╚██╗██║██║      ██║   ██╔╝ ████╔╝██║ ╚═══██║{R}
{B}{C}        ██║ ╚████║╚██████╗ ██║   ██║  ╚██████╔╝ █████╔╝{R}
{B}{C}        ╚═╝  ╚═══╝ ╚═════╝ ╚═╝   ╚═╝   ╚═════╝  ╚════╝ {R}
                    {B}Bring your code to life{R}  v{__version__}

        {C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}

          {B}Your AI coding partner that reads, writes, and
          runs code directly on your machine.{R}

          {B}{G}✓{R}{B} Generate & edit code    {G}✓{R}{B} Run shell commands{R}
          {B}{G}✓{R}{B} Debug & fix errors      {G}✓{R}{B} Manage files & projects{R}

          {B}{C}Languages{R}   Python · JavaScript · TypeScript · Go · Rust
          {B}{C}Frameworks{R}  React · Node.js · FastAPI · Django · Express
          {B}{C}DevOps{R}      Docker · Kubernetes · Kafka · Redis · Nginx
          {B}{C}Workflows{R}   CI/CD · Git · Testing · Deployment · APIs

        {C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}

                        {B}{Y}🔐 API Key Required{R}

          {B}{C}→{R} nc1709 --api-key "your-api-key"
          {B}{C}→{R} export NC1709_API_KEY="your-api-key"

        {C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}
              {B}{M}📧 Need a key? support@lafzusa.com{R}
        {C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}
''')
        # Check for updates and show notification even on auth screen
        try:
            from .version_check import check_and_notify
            update_msg = check_and_notify()
            if update_msg:
                print(f"{Y}{update_msg}{R}")
        except Exception:
            pass

    def _print_startup_banner(self) -> None:
        """Print startup banner (kept for compatibility)"""
        from . import __version__

        C = '\033[96m'  # Bright Cyan
        W = '\033[97m'  # Bright White
        D = '\033[2m'   # Dim
        R = '\033[0m'   # Reset

        print(f'''
{C}                        NC1709{R}
{W}                  Bring your code to life{R}
{D}                        v{__version__}{R}

{D}       Your AI coding partner — reads, writes, and
         runs code directly on your machine.{R}
''')

    def _print_banner(self) -> None:
        """Print welcome banner after successful authentication"""
        from . import __version__

        # Colors that work on both light and dark terminals
        C = '\033[36m'   # Cyan
        B = '\033[1m'    # Bold
        G = '\033[32m'   # Green
        Y = '\033[33m'   # Yellow
        D = '\033[2m'    # Dim
        R = '\033[0m'    # Reset

        print(f'''
{B}{C}  ███╗   ██╗ ██████╗ ██╗███████╗ ██████╗  █████╗ {R}   {G}✓{R} Generate & edit code
{B}{C}  ████╗  ██║██╔════╝███║╚════██║██╔═████╗██╔══██╗{R}   {G}✓{R} Run shell commands
{B}{C}  ██╔██╗ ██║██║     ╚██║    ██╔╝██║██╔██║╚██████║{R}   {G}✓{R} Debug & fix errors
{B}{C}  ██║╚██╗██║██║      ██║   ██╔╝ ████╔╝██║ ╚═══██║{R}   {G}✓{R} Multi-agent system
{B}{C}  ██║ ╚████║╚██████╗ ██║   ██║  ╚██████╔╝ █████╔╝{R}   {G}✓{R} Learns your style
{B}{C}  ╚═╝  ╚═══╝ ╚═════╝ ╚═╝   ╚═╝   ╚═════╝  ╚════╝ {R}

  {B}Bring your code to life{R} {D}v{__version__}{R}       {G}●{R} {B}Connected{R}

  {D}Python · JS · TS · Go · Rust │ React · FastAPI · Docker · Git{R}

  {C}›{R} Describe what you want      {C}›{R} Type {Y}/help{R} for commands

  {Y}╭─────────────────────────────────────────────────────────────────╮{R}
  {Y}│{R} {B}{Y}⚡ ADAPTIVE INFERENCE ENGINE{R}                                    {Y}│{R}
  {Y}│{R}                                                                 {Y}│{R}
  {Y}│{R} {C}Multi-model routing{R}, {C}context vectorization{R}, and {C}intelligent{R}   {Y}│{R}
  {Y}│{R} {C}load balancing{R} are active. Initial responses may vary as the   {Y}│{R}
  {Y}│{R} system optimizes for your workflow.                             {Y}│{R}
  {Y}╰─────────────────────────────────────────────────────────────────╯{R}
''')
        # Check for updates (non-blocking, cached)
        try:
            from .version_check import check_and_notify
            update_msg = check_and_notify()
            if update_msg:
                print(f"{Y}{update_msg}{R}")
        except Exception:
            pass  # Never fail startup due to version check
    
    def _print_help(self) -> None:
        """Print help message with slash commands"""
        try:
            from .slash_commands import format_help_text
            print(format_help_text())
        except ImportError:
            # Fallback if slash_commands not available
            print(self._get_fallback_help())

        # Additional tips
        print("""
\033[1mUsage Tips:\033[0m

  • Type / to see all commands with autocomplete
  • Press Tab to complete commands
  • Just describe what you want in plain English
  • The AI will ask before making changes

\033[36mExamples:\033[0m

  • "Read main.py and explain what it does"
  • "Create a Python script to fetch data from an API"
  • /git status  or  /docker ps
  • /search authentication logic
""")

    def _get_fallback_help(self) -> str:
        """Get fallback help text if slash_commands module not available"""
        return """
\033[1mAvailable Commands:\033[0m

  /help          Show this help message
  /exit          Exit NC1709
  /clear         Clear conversation history
  /history       Show command history
  /config        View/modify configuration

\033[36mAgent Mode:\033[0m
  /agent on      Enable agent mode
  /agent off     Disable agent mode
  /agent tools   List available tools
  /agent status  Show agent status

\033[36mGit:\033[0m
  /git status    Show git status
  /git diff      Show changes
  /git log       Show commit history

\033[36mDocker:\033[0m
  /docker ps     List containers
  /docker logs   View logs

\033[36mSearch:\033[0m
  /search <q>    Search code
  /index         Index project

\033[36mCognitive:\033[0m
  /brain status  Show cognitive system status
  /brain suggest Get proactive suggestions
  /brain index   Index project for context awareness

\033[36mRequirements:\033[0m
  /requirements     Show project requirements (/reqs shortcut)
  /reqs add <title> Add a new requirement
  /reqs start <id>  Mark requirement as in-progress
  /reqs done <id>   Mark requirement as complete
  /reqs all         Show all requirements including completed
"""
    
    def _show_history(self) -> None:
        """Show command execution history"""
        history = self.executor.get_execution_history(limit=20)

        if not history:
            print("No command history yet.")
            return

        print("\nRecent Command History:")
        print("="*60)

        for i, entry in enumerate(history, 1):
            status = "✅" if entry["success"] else "❌"
            print(f"{i}. {status} {entry['command']}")
            print(f"   Time: {entry['timestamp']}")
            print(f"   Exit code: {entry['return_code']}")
            print()

    def _rewind_checkpoint(self) -> None:
        """Rewind to previous checkpoint (undo last file change)"""
        if not HAS_CHECKPOINTS:
            warning("Checkpoints module not available")
            return

        manager = get_checkpoint_manager()

        if not manager.can_rewind():
            warning("No checkpoints to rewind to")
            return

        checkpoint = manager.rewind()
        if checkpoint:
            files = list(checkpoint.files.keys())
            file_names = [Path(f).name for f in files]
            success(f"Rewound to checkpoint: {checkpoint.description}")
            info(f"Restored {len(files)} file(s): {', '.join(file_names)}")
        else:
            error("Failed to rewind")

    def _forward_checkpoint(self) -> None:
        """Go forward in checkpoint history (redo after rewind)"""
        if not HAS_CHECKPOINTS:
            warning("Checkpoints module not available")
            return

        manager = get_checkpoint_manager()

        if not manager.can_forward():
            warning("Already at latest checkpoint")
            return

        checkpoint = manager.forward()
        if checkpoint:
            files = list(checkpoint.files.keys())
            file_names = [Path(f).name for f in files]
            success(f"Forward to checkpoint: {checkpoint.description}")
            info(f"Restored {len(files)} file(s): {', '.join(file_names)}")
        else:
            error("Failed to go forward")

    def _list_checkpoints(self) -> None:
        """List recent checkpoints"""
        if not HAS_CHECKPOINTS:
            warning("Checkpoints module not available")
            return

        manager = get_checkpoint_manager()
        checkpoints = manager.list_checkpoints(limit=15)

        if not checkpoints:
            info("No checkpoints yet. Checkpoints are created automatically before file edits.")
            return

        B = Color.BOLD
        C = Color.CYAN
        G = Color.GREEN
        D = Color.DIM
        R = Color.RESET

        print(f"\n{B}Recent Checkpoints{R}")
        print("=" * 60)

        for cp in checkpoints:
            current = f" {G}<-- current{R}" if cp["is_current"] else ""
            files = [Path(f).name for f in cp["files"]]
            file_list = ", ".join(files[:3])
            if len(files) > 3:
                file_list += f", +{len(files) - 3} more"

            print(f"{C}[{cp['index']}]{R} {cp['description']}{current}")
            print(f"    {D}Tool: {cp['tool']} | Files: {file_list}{R}")
            print(f"    {D}{cp['timestamp'][:19]}{R}")
            print()

        print(f"{D}Use /rewind to undo, /forward to redo{R}\n")

    def _toggle_autocommit(self) -> None:
        """Toggle automatic git commits"""
        if not HAS_GIT_INTEGRATION:
            warning("Git integration module not available")
            return

        git = get_git_integration()

        if not git.is_repo:
            warning("Not in a git repository")
            return

        git.auto_commit = not git.auto_commit
        status = "enabled" if git.auto_commit else "disabled"
        success(f"Auto-commit {status}")

    def _set_autocommit(self, enabled: bool) -> None:
        """Set automatic git commits on/off"""
        if not HAS_GIT_INTEGRATION:
            warning("Git integration module not available")
            return

        git = get_git_integration()

        if not git.is_repo:
            warning("Not in a git repository")
            return

        git.auto_commit = enabled
        status = "enabled" if enabled else "disabled"
        success(f"Auto-commit {status}")

    def _list_custom_commands(self) -> None:
        """List available custom slash commands"""
        if not HAS_CUSTOM_COMMANDS:
            warning("Custom commands module not available")
            return

        manager = get_custom_command_manager()
        commands = manager.list_commands()

        if not commands:
            print("\nNo custom commands found.\n")
            print("Create custom commands in:")
            print("  ~/.nc1709/commands/*.md  (personal commands)")
            print("  .nc1709/commands/*.md   (project commands)\n")
            print("Example command file (fix-bug.md):")
            print("  # Fix a bug in the codebase")
            print("  ")
            print("  Look at the error message provided.")
            print("  Find the relevant code files.")
            print("  Analyze the root cause and implement a fix.\n")
            return

        # Group by scope
        personal_cmds = [c for c in commands if c.scope == "personal"]
        project_cmds = [c for c in commands if c.scope == "project"]

        print("\n\033[1mCustom Slash Commands\033[0m\n")

        if personal_cmds:
            print("\033[36mPersonal Commands (~/.nc1709/commands/):\033[0m")
            for cmd in personal_cmds:
                print(f"  \033[1m/{cmd.name:<20}\033[0m {cmd.description}")
            print()

        if project_cmds:
            print("\033[36mProject Commands (.nc1709/commands/):\033[0m")
            for cmd in project_cmds:
                # Remove project: prefix for display
                display_name = cmd.name.replace("project:", "")
                print(f"  \033[1m/{cmd.name:<20}\033[0m {cmd.description}")
            print()

        print("\033[90mTip: Type / and press Tab to autocomplete custom commands\033[0m\n")

    def _add_image(self, image_path: str) -> None:
        """Add an image file for the next prompt"""
        if not HAS_IMAGE_INPUT:
            warning("Image input module not available")
            return

        handler = get_image_handler()
        if handler.add_image(image_path):
            img_info = get_image_info(image_path)
            if img_info:
                dims = ""
                if img_info.get("width") and img_info.get("height"):
                    dims = f" ({img_info['width']}x{img_info['height']})"
                success(f"Added image: {img_info['name']}{dims} - {img_info['size_human']}")
            else:
                success(f"Added image: {image_path}")
            print("\033[90mImage will be included in your next prompt\033[0m")
        else:
            error(f"Failed to load image: {image_path}")
            print("Supported formats: PNG, JPG, GIF, WebP, BMP")

    def _capture_screenshot(self) -> None:
        """Capture a screenshot for the next prompt"""
        if not HAS_IMAGE_INPUT:
            warning("Image input module not available")
            return

        import platform
        if platform.system() != 'Darwin':
            warning("Screenshot capture is only available on macOS")
            return

        info("Capture a screenshot... (drag to select area, ESC to cancel)")

        handler = get_image_handler()
        if handler.add_screenshot():
            success("Screenshot captured and added")
            print("\033[90mScreenshot will be included in your next prompt\033[0m")
        else:
            warning("Screenshot cancelled or failed")

    def _paste_clipboard_image(self) -> None:
        """Paste image from clipboard for the next prompt"""
        if not HAS_IMAGE_INPUT:
            warning("Image input module not available")
            return

        handler = get_image_handler()
        if handler.add_clipboard():
            success("Image pasted from clipboard")
            print("\033[90mImage will be included in your next prompt\033[0m")
        else:
            warning("No image found in clipboard or paste failed")
            print("Tip: Copy an image to clipboard first, or install pngpaste (brew install pngpaste)")

    def _list_pending_images(self) -> None:
        """List pending images for next prompt"""
        if not HAS_IMAGE_INPUT:
            warning("Image input module not available")
            return

        handler = get_image_handler()
        images = handler.get_pending_images()

        if not images:
            print("\nNo pending images.")
            print("\nAdd images with:")
            print("  /image <path>   - Add an image file")
            print("  /screenshot     - Capture a screenshot")
            print("  /paste          - Paste from clipboard\n")
            return

        print(f"\n\033[1mPending Images ({len(images)})\033[0m\n")

        for i, img in enumerate(images, 1):
            from pathlib import Path
            name = Path(img.path).name
            dims = ""
            if img.width and img.height:
                dims = f" ({img.width}x{img.height})"
            size = f"{img.size_bytes / 1024:.1f} KB"
            print(f"  {i}. {name}{dims} - {size}")

        print(f"\n\033[90mThese images will be included in your next prompt\033[0m")
        print(f"\033[90mUse /clear-images to remove them\033[0m\n")

    def _clear_pending_images(self) -> None:
        """Clear pending images"""
        if not HAS_IMAGE_INPUT:
            warning("Image input module not available")
            return

        handler = get_image_handler()
        count = len(handler.get_pending_images())
        handler.clear_pending()
        success(f"Cleared {count} pending image(s)")

    def _enter_plan_mode(self) -> None:
        """Enter plan mode"""
        if not HAS_PLAN_MODE:
            warning("Plan mode module not available")
            return

        manager = get_plan_manager()
        manager.enter_plan_mode()

        print("\n\033[1;36mPlan Mode Activated\033[0m\n")
        print("In plan mode, the AI will:")
        print("  1. Analyze your request thoroughly")
        print("  2. Create a step-by-step plan")
        print("  3. Identify affected files and risks")
        print("  4. Wait for your approval before making changes\n")
        print("Commands:")
        print("  /plan approve  - Approve and execute the plan")
        print("  /plan reject   - Reject the current plan")
        print("  /plan show     - Show the current plan")
        print("  /plan exit     - Exit plan mode\n")
        print("\033[90mDescribe what you want to accomplish...\033[0m\n")

    def _approve_plan(self) -> None:
        """Approve and execute the current plan"""
        if not HAS_PLAN_MODE:
            warning("Plan mode module not available")
            return

        manager = get_plan_manager()

        if not manager.current_plan:
            warning("No plan to approve. Create a plan first.")
            return

        if manager.approve_plan():
            success("Plan approved!")
            manager.start_execution()

            # Get the execution prompt and pass to AI
            execution_prompt = manager.get_execution_prompt()
            if execution_prompt:
                info("Executing plan...")
                self._process_request(execution_prompt)

            manager.complete_plan(success=True)
        else:
            error("Failed to approve plan")

    def _reject_plan(self) -> None:
        """Reject the current plan"""
        if not HAS_PLAN_MODE:
            warning("Plan mode module not available")
            return

        manager = get_plan_manager()

        if not manager.current_plan:
            warning("No plan to reject")
            return

        manager.reject_plan()
        info("Plan rejected. Describe a new approach or use /plan exit to leave plan mode.")

    def _show_plan(self) -> None:
        """Show the current plan"""
        if not HAS_PLAN_MODE:
            warning("Plan mode module not available")
            return

        manager = get_plan_manager()
        summary = manager.get_plan_summary()

        if summary:
            print(summary)
        else:
            print("\nNo current plan.")
            print("Describe what you want to accomplish to generate a plan.\n")

    def _exit_plan_mode(self) -> None:
        """Exit plan mode"""
        if not HAS_PLAN_MODE:
            warning("Plan mode module not available")
            return

        manager = get_plan_manager()
        manager.exit_plan_mode()
        info("Exited plan mode")

    def _create_pr_interactive(self) -> None:
        """Create a PR interactively"""
        if not HAS_GITHUB:
            warning("GitHub integration module not available")
            return

        gh = get_github_integration()

        if not gh.is_available:
            warning("GitHub CLI (gh) not found. Install it with: brew install gh")
            return

        if not gh.is_authenticated:
            warning("Not authenticated with GitHub. Run: gh auth login")
            return

        branch = gh.get_current_branch()
        if not branch:
            error("Not in a git repository or no branch found")
            return

        if branch in ["main", "master"]:
            warning(f"You're on the {branch} branch. Create a feature branch first.")
            return

        print(f"\n\033[1mCreate Pull Request\033[0m")
        print(f"Branch: {branch}\n")

        # Prompt for PR details
        try:
            title = input("\033[36mPR Title: \033[0m").strip()
            if not title:
                warning("PR title is required")
                return

            print("\033[36mPR Description (end with empty line):\033[0m")
            body_lines = []
            while True:
                line = input()
                if not line:
                    break
                body_lines.append(line)
            body = "\n".join(body_lines)

            # Push branch if needed
            info("Pushing branch to remote...")
            if not gh.push_branch():
                warning("Failed to push branch. You may need to push manually.")

            info("Creating PR...")
            pr = gh.create_pr(title=title, body=body)

            if pr:
                success(f"PR created: #{pr.number}")
                print(f"URL: {pr.url}")
            else:
                error("Failed to create PR")

        except KeyboardInterrupt:
            print()
            warning("Cancelled")

    def _list_prs(self) -> None:
        """List open PRs"""
        if not HAS_GITHUB:
            warning("GitHub integration module not available")
            return

        gh = get_github_integration()

        if not gh.is_available:
            warning("GitHub CLI (gh) not found")
            return

        prs = gh.list_prs(state="open")

        if not prs:
            print("\nNo open pull requests.\n")
            return

        print(f"\n\033[1mOpen Pull Requests ({len(prs)})\033[0m\n")

        for pr in prs:
            print(format_pr_summary(pr))
            print()

    def _view_pr(self, pr_num: str) -> None:
        """View a specific PR"""
        if not HAS_GITHUB:
            warning("GitHub integration module not available")
            return

        gh = get_github_integration()

        if not gh.is_available:
            warning("GitHub CLI (gh) not found")
            return

        try:
            number = int(pr_num)
        except ValueError:
            error(f"Invalid PR number: {pr_num}")
            return

        pr = gh.get_pr(number)

        if pr:
            print()
            print(format_pr_summary(pr))
            if pr.body:
                print(f"\n\033[90m{pr.body[:500]}{'...' if len(pr.body) > 500 else ''}\033[0m")
            print()
        else:
            error(f"PR #{number} not found")

    def _list_issues(self) -> None:
        """List open issues"""
        if not HAS_GITHUB:
            warning("GitHub integration module not available")
            return

        gh = get_github_integration()

        if not gh.is_available:
            warning("GitHub CLI (gh) not found")
            return

        issues = gh.list_issues(state="open")

        if not issues:
            print("\nNo open issues.\n")
            return

        print(f"\n\033[1mOpen Issues ({len(issues)})\033[0m\n")

        for issue in issues:
            print(format_issue_summary(issue))
            print()

    def _run_gh_command(self, args: str) -> None:
        """Run a gh CLI command"""
        if not HAS_GITHUB:
            warning("GitHub integration module not available")
            return

        import subprocess
        try:
            result = subprocess.run(
                ["gh"] + args.split(),
                capture_output=False,
                text=True,
                timeout=60
            )
        except subprocess.TimeoutExpired:
            error("Command timed out")
        except FileNotFoundError:
            warning("GitHub CLI (gh) not found. Install it with: brew install gh")
        except Exception as e:
            error(f"Error running gh command: {e}")

    # ==================== Linting Commands ====================

    def _run_lint(self, target: str = None, fix: bool = False) -> None:
        """Run linter on project or specific target"""
        if not HAS_LINTING:
            warning("Linting module not available")
            return

        manager = get_linting_manager()

        if not manager.available_linters:
            warning("No linters detected. Install ruff, eslint, or other linters.")
            return

        if target:
            # Lint specific file
            linter = manager.get_linter_for_file(target)
            if not linter:
                warning(f"No suitable linter found for: {target}")
                return

            info(f"Running {linter} on {target}...")
            result = manager.run_linter(linter, target, fix=fix)
            print(format_lint_result(result))
        else:
            # Lint entire project
            info(f"Running linters on project ({', '.join(manager.available_linters)})...")
            results = manager.lint_project(fix=fix)

            total_errors = 0
            total_warnings = 0

            for linter_name, result in results.items():
                print(format_lint_result(result))
                total_errors += result.error_count
                total_warnings += result.warning_count
                print()

            if total_errors == 0 and total_warnings == 0:
                success("All linters passed with no issues!")
            else:
                info(f"Total: {total_errors} errors, {total_warnings} warnings")

    def _lint_file(self, file_path: str) -> None:
        """Lint a specific file"""
        self._run_lint(target=file_path)

    def _lint_fix(self, target: str = None) -> None:
        """Run linter with auto-fix enabled"""
        self._run_lint(target=target, fix=True)

    def _list_linters(self) -> None:
        """List available linters"""
        if not HAS_LINTING:
            warning("Linting module not available")
            return

        manager = get_linting_manager()

        print("\n\033[1mAvailable Linters\033[0m\n")

        if not manager.available_linters:
            warning("No linters detected.")
            print("\nSupported linters (install any):")
            print("  • ruff - Fast Python linter")
            print("  • flake8 - Python style checker")
            print("  • pylint - Python code analyzer")
            print("  • mypy - Python type checker")
            print("  • eslint - JavaScript/TypeScript linter")
            print("  • tsc - TypeScript compiler")
            print("  • golangci-lint - Go linter")
            print("  • cargo clippy - Rust linter")
            return

        for linter in manager.available_linters:
            from .linting import LINTERS
            config = LINTERS.get(linter)
            if config:
                patterns = ", ".join(config.file_patterns)
                print(f"  \033[32m✓\033[0m \033[1m{linter}\033[0m ({patterns})")

        print(f"\nTotal: {len(manager.available_linters)} linters available")

    def _handle_config_command(self, prompt: str) -> None:
        """Handle config commands
        
        Args:
            prompt: Config command
        """
        parts = prompt.split(maxsplit=2)
        
        if len(parts) < 2:
            self._show_config()
            return
        
        if parts[1] == "get":
            if len(parts) < 3:
                print("Usage: config get <key>")
                return
            key = parts[2]
            value = self.config.get(key)
            print(f"{key} = {value}")
        
        elif parts[1] == "set":
            if len(parts) < 3:
                print("Usage: config set <key> <value>")
                return
            # Parse key=value
            if "=" not in parts[2]:
                print("Usage: config set <key>=<value>")
                return
            key, value = parts[2].split("=", 1)
            self.config.set(key.strip(), value.strip())
            print(f"✅ Set {key} = {value}")
        
        else:
            print("Unknown config command. Use 'config get <key>' or 'config set <key>=<value>'")

    def _list_sessions(self) -> int:
        """List saved sessions

        Returns:
            Exit code
        """
        if not self.session_manager:
            print("⚠️  Session management not available")
            return 1

        sessions = self.session_manager.list_sessions(limit=20)

        if not sessions:
            print("No saved sessions found.")
            return 0

        print("\n📚 Saved Sessions:")
        print("=" * 70)

        for session in sessions:
            msg_count = session.get("message_count", 0)
            project = session.get("project_path", "N/A")
            if project and len(project) > 30:
                project = "..." + project[-27:]

            print(f"  ID: {session['id']}")
            print(f"  Name: {session['name']}")
            print(f"  Messages: {msg_count}")
            print(f"  Updated: {session.get('updated_at', 'N/A')[:19]}")
            print(f"  Project: {project}")
            print("-" * 70)

        print(f"\nTo resume a session: nc1709 --resume <session_id>")
        return 0

    def _index_project(self) -> int:
        """Index the current project for semantic search

        Returns:
            Exit code
        """
        try:
            from .memory.indexer import ProjectIndexer

            print(f"🔍 Indexing project: {Path.cwd()}")
            print("This may take a few minutes for large projects...\n")

            indexer = ProjectIndexer(str(Path.cwd()))
            stats = indexer.index_project(show_progress=True)

            print(f"\n✅ Indexing complete!")
            print(f"   Files indexed: {stats['files_indexed']}")
            print(f"   Total chunks: {stats['chunks_created']}")

            if stats['errors']:
                print(f"   Errors: {len(stats['errors'])}")

            return 0

        except ImportError:
            print("⚠️  Memory module dependencies not installed.")
            print("   Install with: pip install chromadb sentence-transformers")
            return 1
        except Exception as e:
            print(f"❌ Error indexing project: {e}")
            return 1

    def _search_code(self, query: str) -> int:
        """Search indexed code

        Args:
            query: Search query

        Returns:
            Exit code
        """
        if not query:
            print("Usage: search <query>")
            return 1

        try:
            from .memory.indexer import ProjectIndexer

            indexer = ProjectIndexer(str(Path.cwd()))

            # Check if project is indexed
            summary = indexer.get_project_summary()
            if summary['total_files'] == 0:
                print("⚠️  Project not indexed yet. Run 'index' first.")
                return 1

            print(f"\n🔍 Searching for: {query}\n")

            results = indexer.search(query, n_results=5)

            if not results:
                print("No results found.")
                return 0

            print(f"Found {len(results)} results:\n")
            print("=" * 70)

            for i, result in enumerate(results, 1):
                similarity = result.get('similarity', 0) * 100
                location = result.get('location', 'Unknown')
                language = result.get('language', 'unknown')

                print(f"\n📄 Result {i} ({similarity:.1f}% match)")
                print(f"   Location: {location}")
                print(f"   Language: {language}")
                print("-" * 70)

                # Show code preview (first 10 lines)
                code = result.get('content', '')
                lines = code.split('\n')[:10]
                for line in lines:
                    print(f"   {line[:80]}")
                if len(code.split('\n')) > 10:
                    print("   ...")

            print("\n" + "=" * 70)
            return 0

        except ImportError:
            print("⚠️  Memory module dependencies not installed.")
            print("   Install with: pip install chromadb sentence-transformers")
            return 1
        except Exception as e:
            print(f"❌ Error searching: {e}")
            return 1

    def _list_plugins(self) -> int:
        """List available plugins

        Returns:
            Exit code
        """
        if not self.plugin_manager:
            print("⚠️  Plugin system not available")
            return 1

        status = self.plugin_manager.get_status()

        if not status:
            print("No plugins registered.")
            return 0

        print("\n🔌 Available Plugins:")
        print("=" * 70)

        for name, info in status.items():
            status_icon = "✅" if info["status"] == "active" else "❌"
            builtin_tag = " [built-in]" if info.get("builtin") else ""

            print(f"\n  {status_icon} {name} v{info['version']}{builtin_tag}")
            print(f"      Status: {info['status']}")

            if info.get("error"):
                print(f"      Error: {info['error']}")

            # Show actions for loaded plugins
            plugin = self.plugin_manager.get_plugin(name)
            if plugin and plugin.actions:
                actions = ", ".join(plugin.actions.keys())
                print(f"      Actions: {actions}")

        print("\n" + "=" * 70)
        print("\nUsage: nc1709 --plugin <name>:<action>")
        print("Example: nc1709 --plugin git:status")
        return 0

    def _run_plugin_action(self, action_spec: str) -> int:
        """Run a plugin action

        Args:
            action_spec: Plugin:action specification (e.g., "git:status")

        Returns:
            Exit code
        """
        if not self.plugin_manager:
            print("⚠️  Plugin system not available")
            return 1

        # Parse action spec
        if ":" not in action_spec:
            # Try to find a plugin that can handle this as a request
            handlers = self.plugin_manager.find_handler(action_spec)
            if handlers:
                plugin_name = handlers[0][0]
                plugin = self.plugin_manager.get_plugin(plugin_name)
                if plugin and hasattr(plugin, 'handle_request'):
                    result = plugin.handle_request(action_spec)
                    if result:
                        self._print_action_result(result)
                        return 0 if result.success else 1

            print(f"❌ Invalid format. Use: <plugin>:<action>")
            print(f"   Example: git:status, docker:ps")
            return 1

        parts = action_spec.split(":", 1)
        plugin_name = parts[0].strip()
        action_name = parts[1].strip() if len(parts) > 1 else ""

        # Get the plugin
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if not plugin:
            # Try to load it
            if not self.plugin_manager.load_plugin(plugin_name):
                print(f"❌ Plugin '{plugin_name}' not found")
                return 1
            plugin = self.plugin_manager.get_plugin(plugin_name)

        # If no action specified, show plugin help
        if not action_name:
            print(plugin.get_help())
            return 0

        # Check if action exists
        if action_name not in plugin.actions:
            # Try to handle as natural language
            if hasattr(plugin, 'handle_request'):
                result = plugin.handle_request(action_name)
                if result:
                    self._print_action_result(result)
                    return 0 if result.success else 1

            print(f"❌ Unknown action: {action_name}")
            print(f"   Available actions: {', '.join(plugin.actions.keys())}")
            return 1

        # Execute the action
        result = self.plugin_manager.execute_action(plugin_name, action_name)
        self._print_action_result(result)
        return 0 if result.success else 1

    def _print_action_result(self, result) -> None:
        """Print an action result

        Args:
            result: ActionResult to print
        """
        if result.success:
            print(f"\n✅ {result.message}")
        else:
            print(f"\n❌ {result.message}")
            if result.error:
                print(f"   Error: {result.error}")

        # Print data if present
        if result.data:
            if isinstance(result.data, str):
                print(f"\n{result.data}")
            elif isinstance(result.data, list):
                for item in result.data:
                    if hasattr(item, '__dict__'):
                        # Dataclass or object
                        print(f"  - {item}")
                    else:
                        print(f"  - {item}")
            elif hasattr(result.data, '__dict__'):
                # Single object
                for key, value in vars(result.data).items():
                    if not key.startswith('_'):
                        print(f"  {key}: {value}")

    # =========================================================================
    # MCP Methods
    # =========================================================================

    def _mcp_show_status(self) -> int:
        """Show MCP status

        Returns:
            Exit code
        """
        if not self.mcp_manager:
            print("⚠️  MCP module not available")
            return 1

        status = self.mcp_manager.get_status()

        print("\n🔌 MCP Status:")
        print("=" * 60)

        # Server info
        server = status["server"]
        print(f"\n📡 Local Server: {server['name']} v{server['version']}")
        print(f"   Running: {'Yes' if server['running'] else 'No'}")
        print(f"   Tools: {server['tools']}")
        print(f"   Resources: {server['resources']}")
        print(f"   Prompts: {server['prompts']}")

        # Connected servers
        client = status["client"]
        print(f"\n🌐 Connected Servers: {client['connected_servers']}")

        if client["servers"]:
            for srv in client["servers"]:
                status_icon = "✅" if srv["connected"] else "❌"
                print(f"   {status_icon} {srv['name']}: {srv['tools']} tools, {srv['resources']} resources")

        print("\n" + "=" * 60)
        print("\nCommands:")
        print("  mcp tools     - List available tools")
        print("  mcp call <t>  - Call a tool")
        print("  --mcp-serve   - Run as MCP server")
        return 0

    def _mcp_list_tools(self) -> int:
        """List MCP tools

        Returns:
            Exit code
        """
        if not self.mcp_manager:
            print("⚠️  MCP module not available")
            return 1

        all_tools = self.mcp_manager.get_all_tools()

        print("\n🔧 Available MCP Tools:")
        print("=" * 60)

        # Local tools
        if all_tools["local"]:
            print("\n📍 Local Tools:")
            for tool in all_tools["local"]:
                print(f"\n  {tool.name}")
                print(f"    Description: {tool.description}")
                if tool.parameters:
                    params = ", ".join(p.name for p in tool.parameters)
                    print(f"    Parameters: {params}")

        # Remote tools
        if all_tools["remote"]:
            print("\n🌐 Remote Tools:")
            for tool in all_tools["remote"]:
                print(f"\n  {tool.name}")
                print(f"    Description: {tool.description}")

        if not all_tools["local"] and not all_tools["remote"]:
            print("\nNo tools available.")

        print("\n" + "=" * 60)
        return 0

    def _mcp_call_tool_interactive(self, tool_spec: str) -> int:
        """Call an MCP tool from interactive mode

        Args:
            tool_spec: Tool name and args (e.g., "read_file path=main.py")

        Returns:
            Exit code
        """
        import json

        parts = tool_spec.split(maxsplit=1)
        tool_name = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""

        # Parse key=value args
        args = {}
        if args_str:
            for pair in args_str.split():
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    # Try to parse as JSON for complex values
                    try:
                        args[key] = json.loads(value)
                    except json.JSONDecodeError:
                        args[key] = value

        return self._mcp_call_tool(tool_name, json.dumps(args))

    def _mcp_call_tool(self, tool_name: str, args_json: str) -> int:
        """Call an MCP tool

        Args:
            tool_name: Tool name
            args_json: JSON string of arguments

        Returns:
            Exit code
        """
        import json
        import asyncio

        if not self.mcp_manager:
            print("⚠️  MCP module not available")
            return 1

        try:
            args = json.loads(args_json)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON arguments: {e}")
            return 1

        print(f"\n🔧 Calling tool: {tool_name}")
        if args:
            print(f"   Arguments: {args}")

        try:
            # Run async call
            result = asyncio.run(self.mcp_manager.call_tool(tool_name, args))

            if "error" in result:
                print(f"\n❌ Error: {result['error']}")
                return 1

            print("\n✅ Result:")
            print("-" * 40)

            if "content" in result:
                for item in result["content"]:
                    if item.get("type") == "text":
                        print(item.get("text", ""))
            else:
                print(json.dumps(result, indent=2))

            return 0

        except Exception as e:
            print(f"❌ Error calling tool: {e}")
            return 1

    def _mcp_run_server(self) -> int:
        """Run NC1709 as an MCP server

        Returns:
            Exit code (never returns normally)
        """
        import asyncio

        if not self.mcp_manager:
            print("⚠️  MCP module not available", file=sys.stderr)
            return 1

        # Don't print to stdout as it's used for MCP communication
        print("Starting NC1709 MCP server (stdio)...", file=sys.stderr)

        try:
            asyncio.run(self.mcp_manager.server.run_stdio())
        except KeyboardInterrupt:
            print("\nServer stopped.", file=sys.stderr)

        return 0

    def _mcp_connect_servers(self, config_path: str) -> int:
        """Connect to MCP servers from config

        Args:
            config_path: Path to MCP config file

        Returns:
            Exit code
        """
        import asyncio

        if not self.mcp_manager:
            print("⚠️  MCP module not available")
            return 1

        print(f"🔌 Connecting to MCP servers from: {config_path}")

        try:
            count = asyncio.run(self.mcp_manager.auto_discover_servers(config_path))

            if count > 0:
                print(f"\n✅ Connected to {count} server(s)")

                # Show connected servers
                servers = self.mcp_manager.list_connected_servers()
                for srv in servers:
                    print(f"   - {srv['name']}: {srv['tools']} tools")

                return 0
            else:
                print("\n⚠️  No servers connected. Check config file.")
                return 1

        except Exception as e:
            print(f"❌ Error connecting: {e}")
            return 1

    # =========================================================================
    # File Summary Display
    # =========================================================================

    def _show_file_summary(self, files_created: list, files_modified: list) -> None:
        """Show a summary of files created/modified with file tree format.

        Args:
            files_created: List of file paths that were created
            files_modified: List of file paths that were modified
        """
        if not files_created and not files_modified:
            return

        # Deduplicate paths
        created_set = set(files_created)
        modified_set = set(files_modified) - created_set  # Don't show as modified if created

        total_files = len(created_set) + len(modified_set)

        # Show summary header
        print(f"\n{Color.GREEN}{Icons.SUCCESS}{Color.RESET} Done!")

        if created_set:
            print(f"\n{Color.BOLD}Files created:{Color.RESET}")
            self._print_file_tree(list(created_set), "created")

        if modified_set:
            print(f"\n{Color.BOLD}Files modified:{Color.RESET}")
            self._print_file_tree(list(modified_set), "modified")

        print()

    def _print_file_tree(self, file_paths: list, action: str) -> None:
        """Print files in a tree format.

        Args:
            file_paths: List of file paths
            action: Either 'created' or 'modified'
        """
        # Get current working directory for relative paths
        cwd = Path.cwd()

        # Sort and convert to relative paths where possible
        relative_paths = []
        for fp in file_paths:
            try:
                path = Path(fp)
                if path.is_absolute():
                    try:
                        rel = path.relative_to(cwd)
                        relative_paths.append(str(rel))
                    except ValueError:
                        relative_paths.append(fp)
                else:
                    relative_paths.append(fp)
            except Exception:
                relative_paths.append(fp)

        relative_paths.sort()

        # Print with tree structure
        for i, path in enumerate(relative_paths):
            is_last = (i == len(relative_paths) - 1)
            prefix = Icons.TREE_BRANCH if is_last else Icons.TREE_TEE
            color = Color.GREEN if action == "created" else Color.YELLOW
            print(f"{prefix} {color}{path}{Color.RESET}")

    # =========================================================================
    # Conversation Logs Methods
    # =========================================================================

    def _show_conversation_logs(self) -> None:
        """Show recent conversation logs"""
        if not HAS_CONVERSATION_LOGGER:
            warning("Conversation logger not available")
            return

        sessions = ConversationLogger.list_sessions(limit=20)

        if not sessions:
            print("No conversation logs found.")
            print(f"Logs are stored in: ~/.nc1709/logs/")
            return

        print(f"\n{Color.BOLD}Recent Conversation Logs:{Color.RESET}\n")
        for session in sessions:
            session_id = session.get("session_id", "unknown")[:20]
            started = session.get("started_at", "")[:16]
            ip = session.get("ip_address") or "local"
            mode = session.get("mode", "remote")
            count = session.get("entry_count", 0)

            print(f"  {Color.CYAN}{session_id}{Color.RESET}")
            print(f"    Started: {started} | IP: {ip} | Mode: {mode}")
            print(f"    Entries: {count}")
            print()

        print(f"{Color.DIM}Use /logs <session_id> to view a specific log{Color.RESET}")

    def _show_conversation_log(self, session_id: str) -> None:
        """Show a specific conversation log"""
        if not HAS_CONVERSATION_LOGGER:
            warning("Conversation logger not available")
            return

        session_data = ConversationLogger.load_session(session_id)

        if not session_data:
            error(f"Session log not found: {session_id}")
            return

        session = session_data.get("session", {})
        entries = session_data.get("entries", [])

        print(f"\n{Color.BOLD}Session: {session.get('session_id')}{Color.RESET}")
        print(f"Started: {session.get('started_at', '')[:16]}")
        print(f"IP: {session.get('ip_address') or 'local'}")
        print(f"Mode: {session.get('mode', 'remote')}")
        print(f"Working Dir: {session.get('working_directory', 'unknown')}")
        print(f"\n{'─' * 60}\n")

        for entry in entries:
            role = entry.get("role", "unknown")
            timestamp = entry.get("timestamp", "")[:19]
            content = entry.get("content", "")
            metadata = entry.get("metadata", {})

            if role == "user":
                print(f"{Color.GREEN}[{timestamp}] User:{Color.RESET}")
                print(f"  {content[:500]}{'...' if len(content) > 500 else ''}")
            elif role == "assistant":
                print(f"{Color.BLUE}[{timestamp}] Assistant:{Color.RESET}")
                print(f"  {content[:500]}{'...' if len(content) > 500 else ''}")
            elif role == "tool":
                tool_name = metadata.get("tool_name", "unknown")
                success_str = "✓" if metadata.get("success") else "✗"
                duration = metadata.get("duration_ms", 0)
                print(f"{Color.YELLOW}[{timestamp}] Tool: {tool_name} {success_str} ({duration}ms){Color.RESET}")
            elif role == "error":
                print(f"{Color.RED}[{timestamp}] Error: {content}{Color.RESET}")
            elif role == "system":
                print(f"{Color.DIM}[{timestamp}] System: {content}{Color.RESET}")

            print()

        print(f"\n{Color.DIM}Total entries: {len(entries)}{Color.RESET}")

    # =========================================================================
    # Requirements Tracking Methods
    # =========================================================================

    def _show_requirements(self, include_completed: bool = False) -> None:
        """Show project requirements"""
        if not HAS_REQUIREMENTS:
            warning("Requirements tracking module not available")
            return

        tracker = get_tracker()
        print(tracker.format_all(verbose=True, include_completed=include_completed))

    def _init_requirements(self, name: str) -> None:
        """Initialize a new project for requirements tracking"""
        if not HAS_REQUIREMENTS:
            warning("Requirements tracking module not available")
            return

        if not name:
            # Use current directory name
            name = Path.cwd().name

        tracker = get_tracker()
        project = tracker.init_project(name)
        success(f"Initialized requirements for project: {project.name}")
        info(f"Storage: {tracker.storage_path}")

    def _add_requirement(self, title: str) -> None:
        """Add a new requirement"""
        if not HAS_REQUIREMENTS:
            warning("Requirements tracking module not available")
            return

        if not title:
            warning("Please provide a requirement title")
            return

        tracker = get_tracker()
        req = tracker.add_requirement(title)
        success(f"Added requirement: {req.id}")
        print(tracker.format_requirement(req, verbose=True))

    def _complete_requirement(self, req_id: str) -> None:
        """Mark a requirement as complete"""
        if not HAS_REQUIREMENTS:
            warning("Requirements tracking module not available")
            return

        if not req_id:
            warning("Please provide a requirement ID")
            return

        tracker = get_tracker()
        req = tracker.set_status(req_id.upper(), RequirementStatus.COMPLETED)
        if req:
            success(f"Completed: {req.title}")
        else:
            error(f"Requirement not found: {req_id}")

    def _start_requirement(self, req_id: str) -> None:
        """Mark a requirement as in progress"""
        if not HAS_REQUIREMENTS:
            warning("Requirements tracking module not available")
            return

        if not req_id:
            warning("Please provide a requirement ID")
            return

        tracker = get_tracker()
        req = tracker.set_status(req_id.upper(), RequirementStatus.IN_PROGRESS)
        if req:
            success(f"Started: {req.title}")
        else:
            error(f"Requirement not found: {req_id}")

    def _add_requirement_note(self, req_id: str, note: str) -> None:
        """Add a note to a requirement"""
        if not HAS_REQUIREMENTS:
            warning("Requirements tracking module not available")
            return

        tracker = get_tracker()
        req = tracker.add_note(req_id.upper(), note)
        if req:
            success(f"Added note to {req_id}")
        else:
            error(f"Requirement not found: {req_id}")

    # =========================================================================
    # Cognitive System Methods (Brain)
    # =========================================================================

    def _brain_show_status(self) -> None:
        """Show cognitive system status"""
        if not HAS_COGNITIVE:
            warning("Cognitive module not available")
            return

        if not self.cognitive_system:
            warning("Cognitive system not initialized")
            return

        stats = self.cognitive_system.get_system_stats()

        print("\n🧠 NC1709 Cognitive System Status:")
        print("=" * 60)

        # Uptime
        uptime = stats.get("uptime_seconds", 0)
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        print(f"\n⏱️  Uptime: {hours}h {minutes}m")

        # Request stats
        print(f"\n📊 Statistics:")
        print(f"   Total requests: {stats.get('total_requests', 0)}")
        print(f"   Council convenes: {stats.get('council_convenes', 0)}")
        council_rate = stats.get('council_rate', 0) * 100
        print(f"   Council rate: {council_rate:.1f}%")

        # Layer status
        print(f"\n🔧 Layer Status:")
        layers = stats.get("layers_active", {})
        layer_names = {
            "router": "Layer 1: Intelligent Router",
            "context_engine": "Layer 2: Deep Context Engine",
            "council": "Layer 3: Multi-Agent Council",
            "learning": "Layer 4: Learning Core",
            "anticipation": "Layer 5: Anticipation Engine",
        }
        for key, name in layer_names.items():
            status = "✅ Active" if layers.get(key) else "⚪ Inactive"
            print(f"   {status} {name}")

        # Project stats if available
        if "project" in stats:
            project = stats["project"]
            print(f"\n📁 Project Index:")
            print(f"   Files indexed: {project.get('files_indexed', 0)}")
            print(f"   Total lines: {project.get('total_lines', 0):,}")
            print(f"   Patterns detected: {project.get('patterns_detected', 0)}")

    def _brain_show_suggestions(self) -> None:
        """Show proactive suggestions from the anticipation engine"""
        if not HAS_COGNITIVE:
            warning("Cognitive module not available")
            return

        if not self.cognitive_system:
            warning("Cognitive system not initialized")
            return

        suggestions = self.cognitive_system.get_suggestions(limit=5)

        if not suggestions:
            info("No suggestions available yet. Keep using NC1709 to build context!")
            return

        print("\n💡 Proactive Suggestions:")
        print("=" * 60)

        for i, suggestion in enumerate(suggestions, 1):
            confidence = suggestion.get('confidence', 0)
            icon = "🔥" if confidence > 0.8 else "💭" if confidence > 0.5 else "💡"

            print(f"\n{i}. {icon} {suggestion['title']}")
            if suggestion.get('description'):
                print(f"   {suggestion['description']}")
            print(f"   Type: {suggestion['type']} | Confidence: {confidence:.0%}")

            if suggestion.get('action'):
                action = suggestion['action']
                if action.get('type') == 'open_file':
                    print(f"   📂 Open: {action.get('target')}")
                elif action.get('type') == 'suggest_command':
                    print(f"   ⌨️  Command: {action.get('target')}")

    def _brain_index_project(self) -> None:
        """Index the project for context awareness"""
        if not HAS_COGNITIVE:
            warning("Cognitive module not available")
            return

        if not self.cognitive_system:
            warning("Cognitive system not initialized")
            return

        from .cli_ui import thinking

        thinking("Indexing project for context awareness...")

        try:
            result = self.cognitive_system.index_project(incremental=False)
            success(f"Indexed {result.get('files_indexed', 0)} files with {result.get('nodes', 0)} code nodes")
        except Exception as e:
            error(f"Error indexing project: {e}")

    def _brain_show_insights(self) -> None:
        """Show user insights from the learning core"""
        if not HAS_COGNITIVE:
            warning("Cognitive module not available")
            return

        if not self.cognitive_system:
            warning("Cognitive system not initialized")
            return

        insights = self.cognitive_system.get_user_insights()

        if "error" in insights:
            warning(insights["error"])
            return

        print("\n🧠 User Insights:")
        print("=" * 60)

        # Summary stats
        print(f"\n📊 Activity:")
        print(f"   Total interactions: {insights.get('total_interactions', 0)}")
        print(f"   Session count: {insights.get('session_count', 0)}")

        # Top categories
        if insights.get('top_categories'):
            print(f"\n📂 Top Task Categories:")
            for cat, count in insights.get('top_categories', {}).items():
                print(f"   • {cat}: {count} interactions")

        # Preferences
        if insights.get('preferences'):
            print(f"\n⚙️  Learned Preferences:")
            for pref in insights.get('preferences', [])[:5]:
                print(f"   • {pref.get('category', 'general')}: {pref.get('preference', '')}")

        # Patterns
        if insights.get('patterns'):
            print(f"\n🔍 Detected Patterns:")
            for pattern in insights.get('patterns', [])[:3]:
                print(f"   • {pattern.get('description', 'No description')}")

    # =========================================================================
    # Web Dashboard Methods
    # =========================================================================

    def _run_web_dashboard(self, port: int = 8709, serve_remote: bool = False) -> int:
        """Run the web dashboard

        Args:
            port: Port to run on
            serve_remote: If True, bind to 0.0.0.0 for remote clients

        Returns:
            Exit code
        """
        try:
            from .web import run_server
            run_server(host="127.0.0.1", port=port, serve_remote=serve_remote)
            return 0
        except ImportError as e:
            print("⚠️  Web dashboard dependencies not installed.")
            print("   Install with: pip install fastapi uvicorn")
            print(f"   Error: {e}")
            return 1
        except Exception as e:
            error(f"Error starting web dashboard: {e}")
            return 1

    # =========================================================================
    # Shell Completions
    # =========================================================================

    def _generate_completion(self, shell: str) -> int:
        """Generate shell completion script

        Args:
            shell: Shell type (bash, zsh, fish)

        Returns:
            Exit code
        """
        try:
            from .shell_completions import get_completion_script
            script = get_completion_script(shell)
            print(script)
            return 0
        except ImportError:
            error("Shell completions module not available")
            return 1
        except Exception as e:
            error(f"Error generating completions: {e}")
            return 1

    # =========================================================================
    # AI Agents
    # =========================================================================

    def _run_auto_fix(self, file_path: str, auto_apply: bool = False) -> int:
        """Run auto-fix agent on a file

        Args:
            file_path: Path to file to fix
            auto_apply: Whether to auto-apply fixes

        Returns:
            Exit code
        """
        try:
            from .agents.auto_fix import AutoFixAgent

            with action_spinner(f"Analyzing {file_path}") as spinner:
                agent = AutoFixAgent(self.llm)
                spinner.update("Detecting errors")
                errors = agent.analyze_file(file_path)

                if not errors:
                    spinner.success(f"No errors found in {file_path}")
                    return 0

                spinner.update(f"Found {len(errors)} error(s)")
                spinner.add_action("Analyze", file_path)

                # Generate fixes
                fixes = agent.fix_errors(errors)
                spinner.success(f"Found {len(errors)} error(s), generated {len(fixes)} fix(es)")

            # Display errors and fixes
            print(f"\n{Color.BOLD}Auto-Fix Analysis: {file_path}{Color.RESET}")
            print(f"{Color.DIM}{'─'*60}{Color.RESET}")

            for i, err in enumerate(errors, 1):
                print(f"\n{Color.RED}{Icons.FAILURE}{Color.RESET} Error {i}: {err.message}")
                print(f"   {Color.DIM}Line {err.line}: {err.error_type}{Color.RESET}")

            if fixes:
                print(f"\n{Color.BOLD}Generated Fixes:{Color.RESET}")
                for i, fix in enumerate(fixes, 1):
                    confidence = f"{fix.confidence*100:.0f}%" if hasattr(fix, 'confidence') else "N/A"
                    print(f"  {Color.GREEN}{Icons.SUCCESS}{Color.RESET} Fix {i}: {fix.description}")
                    print(f"     {Color.DIM}Confidence: {confidence}{Color.RESET}")

            if auto_apply and fixes:
                print(f"\n{Color.YELLOW}Applying fixes...{Color.RESET}")
                agent.fix_file(file_path, auto_apply=True)
                success(f"Fixes applied to {file_path}")

            return 0

        except ImportError:
            error("Auto-fix agent not available")
            return 1
        except Exception as e:
            error(f"Error running auto-fix: {e}")
            return 1

    def _run_test_generator(self, file_path: str, output_file: Optional[str] = None) -> int:
        """Run test generator agent on a file

        Args:
            file_path: Path to file to generate tests for
            output_file: Optional output file path

        Returns:
            Exit code
        """
        try:
            from .agents.test_generator import TestGeneratorAgent

            with action_spinner(f"Analyzing {file_path}") as spinner:
                agent = TestGeneratorAgent(self.llm)
                spinner.update("Finding functions to test")
                functions = agent.analyze_file(file_path)

                if not functions:
                    spinner.success(f"No testable functions found in {file_path}")
                    return 0

                spinner.update(f"Found {len(functions)} function(s)")
                spinner.add_action("Analyze", file_path)

                # Generate tests
                tests = agent.generate_tests(functions)
                spinner.success(f"Generated {len(tests)} test(s)")

            # Display results
            print(f"\n{Color.BOLD}Test Generator: {file_path}{Color.RESET}")
            print(f"{Color.DIM}{'─'*60}{Color.RESET}")

            print(f"\n{Color.CYAN}Functions found:{Color.RESET}")
            for func in functions:
                print(f"  {Icons.TREE_BRANCH} {func.name}() - line {func.line}")

            print(f"\n{Color.CYAN}Tests generated:{Color.RESET}")
            for test in tests:
                print(f"  {Color.GREEN}{Icons.SUCCESS}{Color.RESET} {test.name}")

            # Write output file
            if output_file:
                agent.generate_test_file(file_path, output_file)
                success(f"Tests written to {output_file}")
            else:
                # Default output file
                from pathlib import Path
                p = Path(file_path)
                default_output = p.parent / f"test_{p.name}"
                agent.generate_test_file(file_path, str(default_output))
                success(f"Tests written to {default_output}")

            return 0

        except ImportError:
            error("Test generator agent not available")
            return 1
        except Exception as e:
            error(f"Error generating tests: {e}")
            return 1


def main():
    """Main entry point"""
    # Track startup (fire-and-forget, non-blocking)
    if HAS_TELEMETRY:
        mode = "remote" if is_remote_mode() else "cli"
        telemetry.track_startup(mode=mode)
        telemetry.track_install()  # Only sends once per machine

    # Pre-parse to get remote args before creating CLI
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--remote", metavar="URL")
    parser.add_argument("--api-key", metavar="KEY")
    parser.add_argument("--local", action="store_true")
    pre_args, _ = parser.parse_known_args()

    # Determine remote URL
    # --local flag disables remote mode entirely
    if pre_args.local:
        remote_url = None
    else:
        remote_url = pre_args.remote  # Will fall back to DEFAULT_API_URL in __init__

    # Create CLI with remote settings if provided
    cli = NC1709CLI(
        remote_url=remote_url,
        api_key=pre_args.api_key
    )

    # Run CLI and track session end
    try:
        exit_code = cli.run()
    finally:
        # Track session end (fire-and-forget)
        if HAS_TELEMETRY:
            model = getattr(cli, 'current_model', None)
            telemetry.track_session_end(model=model)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
