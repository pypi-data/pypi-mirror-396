"""
NC1709 Remote Client
Connects to a remote NC1709 server for LLM access
"""
import os
import json
from typing import Optional, Dict, Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


class RemoteClient:
    """Client for connecting to remote NC1709 server"""

    def __init__(
        self,
        server_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """Initialize remote client

        Args:
            server_url: URL of the NC1709 server (or set NC1709_API_URL env var)
            api_key: API key for authentication (or set NC1709_API_KEY env var)
        """
        self.server_url = (
            server_url or
            os.environ.get("NC1709_API_URL") or
            os.environ.get("NC1709_SERVER_URL")
        )
        self.api_key = (
            api_key or
            os.environ.get("NC1709_API_KEY")
        )

        if not self.server_url:
            raise ValueError(
                "No server URL provided. Set NC1709_API_URL environment variable "
                "or pass server_url parameter."
            )

        # Normalize URL
        self.server_url = self.server_url.rstrip("/")

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to server

        Args:
            endpoint: API endpoint (e.g., "/api/remote/status")
            method: HTTP method
            data: JSON data for POST requests

        Returns:
            Response JSON
        """
        url = f"{self.server_url}{endpoint}"

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "nc1709-client/1.4.0"
        }

        if self.api_key:
            headers["X-API-Key"] = self.api_key

        body = json.dumps(data).encode("utf-8") if data else None

        req = Request(url, data=body, headers=headers, method=method)

        try:
            with urlopen(req, timeout=300) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as e:
            error_body = e.read().decode("utf-8")
            try:
                error_json = json.loads(error_body)
                detail = error_json.get("detail", error_body)
            except json.JSONDecodeError:
                detail = error_body

            if e.code == 401:
                raise ConnectionError(
                    f"Authentication failed: {detail}\n"
                    "Set NC1709_API_KEY environment variable with your API key."
                )
            raise ConnectionError(f"Server error ({e.code}): {detail}")
        except URLError as e:
            raise ConnectionError(
                f"Cannot connect to NC1709 server at {self.server_url}\n"
                f"Error: {e.reason}\n"
                "Make sure the server is running and accessible."
            )

    def check_status(self) -> Dict[str, Any]:
        """Check server status

        Returns:
            Server status information
        """
        return self._make_request("/api/remote/status")

    def complete(
        self,
        prompt: str,
        task_type: str = "general",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Get LLM completion from remote server

        Args:
            prompt: User prompt
            task_type: Task type (reasoning, coding, tools, general, fast)
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            LLM response text
        """
        data = {
            "prompt": prompt,
            "task_type": task_type,
            "temperature": temperature
        }

        if system_prompt:
            data["system_prompt"] = system_prompt
        if max_tokens:
            data["max_tokens"] = max_tokens

        result = self._make_request("/api/remote/complete", method="POST", data=data)
        return result.get("response", "")

    def chat(self, message: str) -> str:
        """Send chat message to remote server (uses full reasoning engine)

        Args:
            message: User message

        Returns:
            Assistant response
        """
        data = {"message": message}
        result = self._make_request("/api/remote/chat", method="POST", data=data)
        return result.get("response", "")

    def agent_chat(
        self,
        messages: list,
        cwd: str,
        tools: list = None
    ) -> Dict[str, Any]:
        """Send agent chat request - returns LLM response for local tool execution

        This is the new architecture where:
        - Server only runs LLM (thinking)
        - Client executes tools locally

        Args:
            messages: Conversation history [{"role": "user/assistant", "content": "..."}]
            cwd: Client's current working directory
            tools: List of available tools on client

        Returns:
            Dict with 'response' (LLM output that may contain tool calls)
        """
        data = {
            "messages": messages,
            "cwd": cwd,
            "tools": tools or []
        }
        return self._make_request("/api/remote/agent", method="POST", data=data)

    def is_connected(self) -> bool:
        """Check if connected to server

        Returns:
            True if server is reachable
        """
        try:
            status = self.check_status()
            return status.get("status") == "ok"
        except Exception:
            return False

    def index_code(
        self,
        user_id: str,
        files: list,
        project_name: str = None
    ) -> Dict[str, Any]:
        """Index code files on the server's vector database

        Args:
            user_id: Unique user/session identifier
            files: List of {"path": "...", "content": "...", "language": "..."}
            project_name: Optional project name for grouping

        Returns:
            Indexing result with stats
        """
        data = {
            "user_id": user_id,
            "files": files,
            "project_name": project_name
        }
        return self._make_request("/api/remote/index", method="POST", data=data)

    def search_code(
        self,
        user_id: str,
        query: str,
        n_results: int = 5,
        project_name: str = None
    ) -> Dict[str, Any]:
        """Search indexed code on the server

        Args:
            user_id: User identifier
            query: Search query
            n_results: Number of results to return
            project_name: Optional project filter

        Returns:
            Search results
        """
        data = {
            "user_id": user_id,
            "query": query,
            "n_results": n_results,
            "project_name": project_name
        }
        return self._make_request("/api/remote/search", method="POST", data=data)


def get_remote_client() -> Optional[RemoteClient]:
    """Get remote client if configured

    Returns:
        RemoteClient instance if NC1709_API_URL is set, None otherwise
    """
    if os.environ.get("NC1709_API_URL") or os.environ.get("NC1709_SERVER_URL"):
        try:
            return RemoteClient()
        except ValueError:
            return None
    return None


def is_remote_mode() -> bool:
    """Check if running in remote mode

    Returns:
        True if NC1709_API_URL is set
    """
    return bool(
        os.environ.get("NC1709_API_URL") or
        os.environ.get("NC1709_SERVER_URL")
    )
