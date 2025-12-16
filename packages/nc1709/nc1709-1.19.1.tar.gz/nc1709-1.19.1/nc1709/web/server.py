"""
NC1709 Web Dashboard Server
FastAPI-based local web server for the dashboard
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Header, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import conversation logger
try:
    from ..conversation_logger import ConversationLogger
    HAS_CONVERSATION_LOGGER = True
except ImportError:
    HAS_CONVERSATION_LOGGER = False

# Session loggers by client IP
_session_loggers: Dict[str, ConversationLogger] = {}

# Get the directory where this file is located
WEB_DIR = Path(__file__).parent
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    session_id: Optional[str] = None


class PluginActionRequest(BaseModel):
    """Plugin action request model"""
    plugin: str
    action: str
    params: Optional[Dict[str, Any]] = None


class MCPToolRequest(BaseModel):
    """MCP tool request model"""
    tool: str
    arguments: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    """Search request model"""
    query: str
    n_results: Optional[int] = 5


class RemoteLLMRequest(BaseModel):
    """Remote LLM request model for API access"""
    prompt: str
    task_type: Optional[str] = "general"
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False


class AgentChatRequest(BaseModel):
    """Agent chat request - for local tool execution architecture"""
    messages: List[Dict[str, str]]  # Conversation history
    cwd: str  # Client's current working directory
    tools: Optional[List[str]] = None  # List of available tools on client


class IndexCodeRequest(BaseModel):
    """Request to index code in the server's vector database"""
    user_id: str  # Unique user/session identifier
    files: List[Dict[str, str]]  # List of {"path": "...", "content": "...", "language": "..."}
    project_name: Optional[str] = None


class SearchCodeRequest(BaseModel):
    """Request to search indexed code"""
    user_id: str  # User identifier to search within their indexed code
    query: str
    n_results: Optional[int] = 5
    project_name: Optional[str] = None  # Optional: filter by project


def create_app() -> FastAPI:
    """Create the FastAPI application

    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="NC1709 Dashboard",
        description="Local web dashboard for NC1709 AI assistant",
        version="1.0.0"
    )

    # CORS for local development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Lazy-loaded components
    _components = {}

    def get_config():
        if "config" not in _components:
            from ..config import get_config
            _components["config"] = get_config()
        return _components["config"]

    def get_session_manager():
        if "session_manager" not in _components:
            try:
                from ..memory.sessions import SessionManager
                _components["session_manager"] = SessionManager()
            except ImportError:
                _components["session_manager"] = None
        return _components["session_manager"]

    def get_project_indexer():
        if "indexer" not in _components:
            try:
                from ..memory.indexer import ProjectIndexer
                _components["indexer"] = ProjectIndexer(str(Path.cwd()))
            except (ImportError, Exception):
                _components["indexer"] = None
        return _components["indexer"]

    def get_plugin_manager():
        if "plugin_manager" not in _components:
            try:
                from ..plugins import PluginManager
                pm = PluginManager()
                pm.discover_plugins()
                pm.load_all()
                _components["plugin_manager"] = pm
            except ImportError:
                _components["plugin_manager"] = None
        return _components["plugin_manager"]

    def get_mcp_manager():
        if "mcp_manager" not in _components:
            try:
                from ..mcp import MCPManager
                mm = MCPManager(name="nc1709", version="1.0.0")
                mm.setup_default_tools()
                _components["mcp_manager"] = mm
            except ImportError:
                _components["mcp_manager"] = None
        return _components["mcp_manager"]

    def get_global_vector_store():
        """Get or create a global vector store for all users' code"""
        if "global_vector_store" not in _components:
            try:
                from ..memory.vector_store import VectorStore
                # Store in server's data directory
                import os
                data_dir = os.path.expanduser("~/.nc1709_server/vector_db")
                os.makedirs(data_dir, exist_ok=True)
                _components["global_vector_store"] = VectorStore(persist_directory=data_dir)
            except ImportError:
                _components["global_vector_store"] = None
        return _components["global_vector_store"]

    def get_code_chunker():
        """Get code chunker for splitting code into indexable chunks"""
        if "code_chunker" not in _components:
            try:
                from ..memory.embeddings import CodeChunker
                _components["code_chunker"] = CodeChunker()
            except ImportError:
                _components["code_chunker"] = None
        return _components["code_chunker"]

    def get_reasoning_engine():
        if "reasoning" not in _components:
            try:
                from ..reasoning_engine import ReasoningEngine
                _components["reasoning"] = ReasoningEngine()
            except ImportError:
                _components["reasoning"] = None
        return _components["reasoning"]

    # =========================================================================
    # Static files and main page
    # =========================================================================

    # Mount static files
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index():
        """Serve the main dashboard page"""
        index_file = TEMPLATES_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return HTMLResponse(content=get_fallback_html(), status_code=200)

    # =========================================================================
    # API Routes - System
    # =========================================================================

    @app.get("/api/status")
    async def get_status():
        """Get system status"""
        from .. import __version__
        config = get_config()

        return {
            "status": "ok",
            "version": __version__,
            "project": str(Path.cwd()),
            "memory_enabled": config.get("memory.enabled", False),
            "timestamp": datetime.now().isoformat()
        }

    @app.get("/api/config")
    async def get_configuration():
        """Get current configuration"""
        config = get_config()
        return {
            "config": config.config,
            "config_path": str(config.config_path)
        }

    @app.post("/api/config")
    async def update_config(updates: Dict[str, Any]):
        """Update configuration"""
        config = get_config()
        for key, value in updates.items():
            config.set(key, value)
        return {"status": "ok", "updated": list(updates.keys())}

    # =========================================================================
    # API Routes - Chat
    # =========================================================================

    @app.post("/api/chat")
    async def chat(request: ChatRequest):
        """Send a chat message and get a response"""
        reasoning = get_reasoning_engine()
        if not reasoning:
            raise HTTPException(status_code=503, detail="Reasoning engine not available")

        context = {
            "cwd": str(Path.cwd()),
            "task_type": "general"
        }

        try:
            response = reasoning.process_request(request.message, context)

            # Save to session if available
            session_mgr = get_session_manager()
            if session_mgr and request.session_id:
                session = session_mgr.load_session(request.session_id)
                if session:
                    session_mgr.add_message(session, "user", request.message)
                    session_mgr.add_message(session, "assistant", response)
                    session_mgr.save_session(session)

            return {
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================================
    # API Routes - Sessions
    # =========================================================================

    @app.get("/api/sessions")
    async def list_sessions():
        """List all sessions"""
        session_mgr = get_session_manager()
        if not session_mgr:
            return {"sessions": [], "error": "Session manager not available"}

        sessions = session_mgr.list_sessions(limit=50)
        return {"sessions": sessions}

    @app.get("/api/sessions/{session_id}")
    async def get_session(session_id: str):
        """Get a specific session"""
        session_mgr = get_session_manager()
        if not session_mgr:
            raise HTTPException(status_code=503, detail="Session manager not available")

        session = session_mgr.load_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "id": session.id,
            "name": session.name,
            "messages": [
                {"role": m.role, "content": m.content, "timestamp": m.timestamp}
                for m in session.messages
            ],
            "created_at": session.created_at,
            "updated_at": session.updated_at
        }

    @app.post("/api/sessions")
    async def create_session():
        """Create a new session"""
        session_mgr = get_session_manager()
        if not session_mgr:
            raise HTTPException(status_code=503, detail="Session manager not available")

        session = session_mgr.start_session(project_path=str(Path.cwd()))
        return {
            "id": session.id,
            "name": session.name,
            "created_at": session.created_at
        }

    @app.delete("/api/sessions/{session_id}")
    async def delete_session(session_id: str):
        """Delete a session"""
        session_mgr = get_session_manager()
        if not session_mgr:
            raise HTTPException(status_code=503, detail="Session manager not available")

        success = session_mgr.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"status": "ok", "deleted": session_id}

    # =========================================================================
    # API Routes - Search/Index
    # =========================================================================

    @app.get("/api/index/status")
    async def get_index_status():
        """Get project index status"""
        try:
            indexer = get_project_indexer()
            if not indexer:
                return {"indexed": False, "error": "Indexer not available"}

            summary = indexer.get_project_summary()
            return {
                "indexed": summary["total_files"] > 0,
                "total_files": summary["total_files"],
                "total_chunks": summary["total_chunks"],
                "languages": summary["languages"]
            }
        except Exception as e:
            return {"indexed": False, "error": str(e)}

    @app.post("/api/index")
    async def index_project():
        """Index the current project"""
        indexer = get_project_indexer()
        if not indexer:
            raise HTTPException(status_code=503, detail="Indexer not available")

        try:
            stats = indexer.index_project(show_progress=False)
            return {
                "status": "ok",
                "files_indexed": stats["files_indexed"],
                "chunks_created": stats["chunks_created"],
                "errors": len(stats.get("errors", []))
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/search")
    async def search_code(request: SearchRequest):
        """Search indexed code"""
        try:
            indexer = get_project_indexer()
            if not indexer:
                raise HTTPException(status_code=503, detail="Indexer not available")

            results = indexer.search(request.query, n_results=request.n_results)

            return {
                "query": request.query,
                "results": [
                    {
                        "content": r.get("content", ""),
                        "location": r.get("location", ""),
                        "language": r.get("language", ""),
                        "similarity": r.get("similarity", 0)
                    }
                    for r in results
                ]
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=503, detail=str(e))

    # =========================================================================
    # API Routes - Plugins
    # =========================================================================

    @app.get("/api/plugins")
    async def list_plugins():
        """List available plugins"""
        pm = get_plugin_manager()
        if not pm:
            return {"plugins": [], "error": "Plugin manager not available"}

        status = pm.get_status()
        plugins = []

        for name, info in status.items():
            plugin = pm.get_plugin(name)
            actions = list(plugin.actions.keys()) if plugin else []

            plugins.append({
                "name": name,
                "version": info["version"],
                "status": info["status"],
                "builtin": info.get("builtin", False),
                "actions": actions,
                "error": info.get("error")
            })

        return {"plugins": plugins}

    @app.post("/api/plugins/execute")
    async def execute_plugin_action(request: PluginActionRequest):
        """Execute a plugin action"""
        pm = get_plugin_manager()
        if not pm:
            raise HTTPException(status_code=503, detail="Plugin manager not available")

        plugin = pm.get_plugin(request.plugin)
        if not plugin:
            raise HTTPException(status_code=404, detail=f"Plugin not found: {request.plugin}")

        if request.action not in plugin.actions:
            raise HTTPException(status_code=404, detail=f"Action not found: {request.action}")

        result = pm.execute_action(request.plugin, request.action, **(request.params or {}))

        return {
            "success": result.success,
            "message": result.message,
            "data": result.data,
            "error": result.error
        }

    # =========================================================================
    # API Routes - MCP
    # =========================================================================

    @app.get("/api/mcp/status")
    async def get_mcp_status():
        """Get MCP status"""
        mm = get_mcp_manager()
        if not mm:
            return {"available": False, "error": "MCP not available"}

        status = mm.get_status()
        return {
            "available": True,
            "server": status["server"],
            "client": status["client"]
        }

    @app.get("/api/mcp/tools")
    async def list_mcp_tools():
        """List MCP tools"""
        mm = get_mcp_manager()
        if not mm:
            return {"tools": [], "error": "MCP not available"}

        all_tools = mm.get_all_tools()

        local_tools = [
            {
                "name": t.name,
                "description": t.description,
                "parameters": [
                    {"name": p.name, "type": p.type, "required": p.required}
                    for p in t.parameters
                ]
            }
            for t in all_tools["local"]
        ]

        remote_tools = [
            {"name": t.name, "description": t.description}
            for t in all_tools["remote"]
        ]

        return {
            "local": local_tools,
            "remote": remote_tools
        }

    @app.post("/api/mcp/call")
    async def call_mcp_tool(request: MCPToolRequest):
        """Call an MCP tool"""
        mm = get_mcp_manager()
        if not mm:
            raise HTTPException(status_code=503, detail="MCP not available")

        result = await mm.call_tool(request.tool, request.arguments)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    # =========================================================================
    # API Routes - Remote LLM Access (for remote clients)
    # =========================================================================

    def verify_api_key(x_api_key: Optional[str] = Header(None)):
        """Verify API key for remote access"""
        config = get_config()
        server_api_key = config.get("remote.api_key", None)

        # If no API key is configured, allow access (open mode)
        if not server_api_key:
            return True

        # If API key is configured, require it
        if not x_api_key or x_api_key != server_api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key. Set X-API-Key header."
            )
        return True

    @app.get("/api/remote/status")
    async def remote_status(authorized: bool = Depends(verify_api_key)):
        """Check remote API status and available models"""
        from .. import __version__
        config = get_config()

        # Count available tools (tools that client can execute locally)
        tools_count = 17  # Default count
        try:
            from ..agent.tools.base import ToolRegistry
            from ..agent.tools.file_tools import register_file_tools
            from ..agent.tools.search_tools import register_search_tools
            from ..agent.tools.bash_tool import register_bash_tools
            from ..agent.tools.web_tools import register_web_tools

            registry = ToolRegistry()
            register_file_tools(registry)
            register_search_tools(registry)
            register_bash_tools(registry)
            register_web_tools(registry)
            tools_count = len(registry.list_names())
        except ImportError:
            pass

        return {
            "status": "ok",
            "server": "nc1709",
            "version": __version__,
            "tools_count": tools_count,
            "models": config.get("models", {}),
            "ollama_url": config.get("ollama.base_url", "http://localhost:11434"),
            "auth_required": bool(config.get("remote.api_key")),
            "timestamp": datetime.now().isoformat()
        }

    @app.post("/api/remote/complete")
    async def remote_complete(
        request: RemoteLLMRequest,
        authorized: bool = Depends(verify_api_key)
    ):
        """Remote LLM completion endpoint - allows remote clients to use your LLMs"""
        try:
            from ..llm_adapter import LLMAdapter, TaskType

            llm = LLMAdapter(skip_health_check=True)

            # Map task type string to enum
            task_type_map = {
                "reasoning": TaskType.REASONING,
                "coding": TaskType.CODING,
                "tools": TaskType.TOOLS,
                "general": TaskType.GENERAL,
                "fast": TaskType.FAST
            }
            task_type = task_type_map.get(request.task_type, TaskType.GENERAL)

            response = llm.complete(
                prompt=request.prompt,
                task_type=task_type,
                system_prompt=request.system_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=False  # Streaming not supported over HTTP yet
            )

            return {
                "response": response,
                "model": llm.get_model_info(task_type),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/remote/chat")
    async def remote_chat(
        request: ChatRequest,
        authorized: bool = Depends(verify_api_key)
    ):
        """Remote chat endpoint - uses full reasoning engine (legacy)"""
        reasoning = get_reasoning_engine()
        if not reasoning:
            raise HTTPException(status_code=503, detail="Reasoning engine not available")

        try:
            response = reasoning.process_request(request.message)
            return {
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================================
    # API Routes - Server-Side Vector Database (Code Intelligence)
    # =========================================================================

    @app.post("/api/remote/index")
    async def remote_index_code(
        request: IndexCodeRequest,
        authorized: bool = Depends(verify_api_key)
    ):
        """
        Index user's code in the server's vector database.
        This allows the server to learn from code patterns and provide better assistance.
        """
        vector_store = get_global_vector_store()
        chunker = get_code_chunker()

        if not vector_store or not chunker:
            raise HTTPException(
                status_code=503,
                detail="Vector database not available. Install chromadb and sentence-transformers."
            )

        try:
            indexed_count = 0
            chunk_count = 0

            for file_info in request.files:
                file_path = file_info.get("path", "unknown")
                content = file_info.get("content", "")
                language = file_info.get("language", "text")

                if not content:
                    continue

                # Chunk the code
                chunks = chunker.chunk_code(content, language=language)

                # Add each chunk to vector store with user_id prefix for isolation
                for i, chunk in enumerate(chunks):
                    doc_id = f"{request.user_id}:{file_path}:{i}"
                    metadata = {
                        "user_id": request.user_id,
                        "file_path": file_path,
                        "language": language,
                        "chunk_index": i,
                        "project_name": request.project_name or "default",
                        "indexed_at": datetime.now().isoformat()
                    }
                    vector_store.add(
                        documents=[chunk],
                        ids=[doc_id],
                        metadatas=[metadata]
                    )
                    chunk_count += 1

                indexed_count += 1

            return {
                "status": "ok",
                "files_indexed": indexed_count,
                "chunks_created": chunk_count,
                "user_id": request.user_id,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/remote/search")
    async def remote_search_code(
        request: SearchCodeRequest,
        authorized: bool = Depends(verify_api_key)
    ):
        """
        Search user's indexed code using semantic similarity.
        Only searches within the user's own indexed code.
        """
        vector_store = get_global_vector_store()

        if not vector_store:
            raise HTTPException(
                status_code=503,
                detail="Vector database not available"
            )

        try:
            # Build filter for user's code only
            where_filter = {"user_id": request.user_id}
            if request.project_name:
                where_filter["project_name"] = request.project_name

            # Search
            results = vector_store.query(
                query_texts=[request.query],
                n_results=request.n_results,
                where=where_filter
            )

            # Format results
            formatted_results = []
            if results and results.get("documents"):
                docs = results["documents"][0] if results["documents"] else []
                metadatas = results["metadatas"][0] if results.get("metadatas") else []
                distances = results["distances"][0] if results.get("distances") else []

                for i, doc in enumerate(docs):
                    formatted_results.append({
                        "content": doc,
                        "file_path": metadatas[i].get("file_path", "unknown") if i < len(metadatas) else "unknown",
                        "language": metadatas[i].get("language", "text") if i < len(metadatas) else "text",
                        "similarity": 1 - (distances[i] if i < len(distances) else 0),  # Convert distance to similarity
                    })

            return {
                "query": request.query,
                "results": formatted_results,
                "count": len(formatted_results),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/remote/index/stats")
    async def remote_index_stats(
        user_id: str,
        authorized: bool = Depends(verify_api_key)
    ):
        """Get indexing statistics for a user"""
        vector_store = get_global_vector_store()

        if not vector_store:
            return {"indexed": False, "error": "Vector database not available"}

        try:
            # Get count of documents for this user
            # Note: This is a simplified implementation
            return {
                "user_id": user_id,
                "indexed": True,
                "status": "active",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"indexed": False, "error": str(e)}

    @app.post("/api/remote/agent")
    async def remote_agent_chat(
        request: AgentChatRequest,
        http_request: Request,
        authorized: bool = Depends(verify_api_key)
    ):
        """
        Agent chat endpoint - returns LLM response with tool calls for LOCAL execution.

        This is the correct architecture:
        1. Client sends conversation history + context
        2. Server runs LLM to generate response (may include tool calls)
        3. Server returns raw LLM response (does NOT execute tools)
        4. Client parses tool calls and executes them LOCALLY
        5. Client sends tool results back for next iteration
        """
        # Get client IP for logging
        client_ip = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("user-agent", "unknown")

        # Get or create logger for this client
        if HAS_CONVERSATION_LOGGER:
            if client_ip not in _session_loggers:
                _session_loggers[client_ip] = ConversationLogger(
                    ip_address=client_ip,
                    user_agent=user_agent,
                    mode="server"
                )
            logger = _session_loggers[client_ip]

            # Log the last user message if present
            if request.messages:
                last_msg = request.messages[-1]
                if last_msg.get("role") == "user":
                    logger.log_user_message(last_msg.get("content", ""), {"cwd": request.cwd})

        try:
            from ..llm_adapter import LLMAdapter
            from ..prompts.unified_prompt import get_unified_prompt

            llm = LLMAdapter(skip_health_check=True)

            # Build unified system prompt - no keyword detection needed
            # The LLM understands user intent from natural language
            system_prompt = get_unified_prompt(request.cwd)

            # Build messages - prepend system prompt
            messages = [{"role": "system", "content": system_prompt}] + request.messages

            # Get LLM response (just thinking, no execution)
            response = llm.chat(messages)

            # Log assistant response
            if HAS_CONVERSATION_LOGGER and client_ip in _session_loggers:
                _session_loggers[client_ip].log_assistant_message(response[:2000])

            return {
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "type": "agent_response"
            }
        except Exception as e:
            # Log error
            if HAS_CONVERSATION_LOGGER and client_ip in _session_loggers:
                _session_loggers[client_ip].log_error(str(e))
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================================
    # WebSocket for real-time chat
    # =========================================================================

    @app.websocket("/ws/chat")
    async def websocket_chat(websocket: WebSocket):
        """WebSocket endpoint for real-time chat"""
        await websocket.accept()

        reasoning = get_reasoning_engine()

        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                if message.get("type") == "chat":
                    user_msg = message.get("content", "")

                    # Send acknowledgment
                    await websocket.send_json({
                        "type": "ack",
                        "content": user_msg
                    })

                    if reasoning:
                        context = {"cwd": str(Path.cwd()), "task_type": "general"}
                        response = reasoning.process_request(user_msg, context)

                        await websocket.send_json({
                            "type": "response",
                            "content": response,
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "content": "Reasoning engine not available"
                        })

        except WebSocketDisconnect:
            pass
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "content": str(e)
            })

    return app


def get_fallback_html() -> str:
    """Get fallback HTML if template not found"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NC1709 Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            text-align: center;
        }
        h1 { color: #00d9ff; }
        p { color: #888; }
        a { color: #00d9ff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>NC1709 Dashboard</h1>
        <p>Dashboard is loading...</p>
        <p>If this message persists, the frontend assets may not be installed.</p>
        <p><a href="/api/status">Check API Status</a></p>
    </div>
</body>
</html>
"""


def run_server(host: str = "127.0.0.1", port: int = 8709, reload: bool = False, serve_remote: bool = False):
    """Run the web server

    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
        serve_remote: If True, bind to 0.0.0.0 for remote access
    """
    import uvicorn

    # If serving remote, bind to all interfaces
    if serve_remote:
        host = "0.0.0.0"

    if serve_remote:
        print(f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              NC1709 Remote Server                         ║
║                                                           ║
║  🌐 API Server running on port {port}                       ║
║  📁 Project: {str(Path.cwd())[:40]}
║                                                           ║
║  Remote clients can connect using:                        ║
║    NC1709_API_URL=http://YOUR_IP:{port}                     ║
║                                                           ║
║  For public access, use a tunnel like ngrok:              ║
║    ngrok http {port}                                        ║
║                                                           ║
║  Press Ctrl+C to stop                                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    else:
        print(f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              NC1709 Web Dashboard                         ║
║                                                           ║
║  🌐 Running at: http://{host}:{port}                      ║
║  📁 Project: {str(Path.cwd())[:40]}
║                                                           ║
║  Press Ctrl+C to stop                                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")

    uvicorn.run(
        "nc1709.web.server:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
        log_level="info"
    )


if __name__ == "__main__":
    run_server()
