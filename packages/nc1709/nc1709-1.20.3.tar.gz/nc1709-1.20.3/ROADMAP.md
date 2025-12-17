# NC1709 CLI - Development Roadmap

**Version**: 1.0.0 → 2.0.0
**Last Updated**: December 5, 2025
**Status**: Phase 1 ✅ | Phase 2 ✅ | Phase 3 ✅ | Phase 4 ✅ | Phase 5 ✅ COMPLETE

---

## Overview

This document outlines the development roadmap for NC1709 CLI, a local-first AI developer assistant. The roadmap is divided into phases, each building upon the previous to create a powerful, privacy-focused coding assistant.

---

## Phase 1: Foundation ✅ COMPLETE

**Status**: Delivered December 3, 2025

### Completed Features
- [x] Multi-Model Orchestration Engine (DeepSeek-R1, Qwen2.5-Coder, Qwen2.5)
- [x] Safe Filesystem Controller with automatic backups
- [x] Execution Sandbox with command validation
- [x] Multi-Step Reasoning Engine
- [x] Interactive CLI with shell mode
- [x] Configuration System (JSON-based)
- [x] Comprehensive test suite (48 tests)

### Bug Fixes & Improvements (December 4, 2025)
- [x] Fixed streaming return type bug
- [x] Fixed config deep copy issue
- [x] Added Ollama health check at startup
- [x] Added retry logic with exponential backoff
- [x] Improved command executor security
- [x] Fixed JSON parsing fragility in reasoning engine
- [x] Made backup directory configurable
- [x] Added structured logging module

---

## Phase 2: Memory & Context Enhancement ✅ COMPLETE

**Status**: Delivered December 4, 2025

### 2.1 Vector Database Integration ✅
- [x] Integrated ChromaDB as local vector store
- [x] Created embedding pipeline for code/text
- [x] Designed schema for storing code chunks, docs, conversations
- [x] Implemented similarity search API
- [x] Added memory configuration options

### 2.2 Semantic Code Search ✅
- [x] Index project files on startup
- [x] Support natural language queries
- [x] Return relevant code snippets with file locations
- [x] Rank results by relevance

### 2.3 Project Indexing ✅
- [x] Incremental indexing (only changed files via hash check)
- [x] Respect .gitignore patterns
- [x] Index file metadata (size, line count, language)
- [x] Support for 30+ file types

### 2.4 Conversation Persistence ✅
- [x] Save conversation history to disk
- [x] Resume previous sessions (`--resume`)
- [x] List past conversations (`--sessions`)
- [x] Export conversations to markdown
- [x] Session search functionality

---

## Phase 3: Extensibility & Agentic Capabilities ✅ COMPLETE

**Status**: Delivered December 4, 2025
**Goal**: Make NC1709 extensible and capable of autonomous workflows

### 3.1 Plugin System ✅ COMPLETE
- [x] Defined plugin API/interface (`Plugin`, `PluginMetadata`, `PluginAction`)
- [x] Plugin discovery and loading (`PluginRegistry`)
- [x] Plugin configuration support
- [x] Built-in plugin manager (`PluginManager`)
- [x] Capability-based routing
- [x] 36 plugin system tests

**Plugin Structure**:
```
nc1709/plugins/
├── __init__.py
├── base.py          # Plugin, PluginMetadata, ActionResult
├── registry.py      # PluginRegistry
├── manager.py       # PluginManager
└── agents/
    ├── git_agent.py     # Git operations
    └── docker_agent.py  # Docker operations
```

### 3.2 Git Agent ✅ COMPLETE
- [x] Repository status checking
- [x] Diff viewing (staged and unstaged)
- [x] Commit with messages
- [x] Branch management (list, create, delete, switch)
- [x] Push/Pull operations
- [x] Stash management
- [x] Reset functionality
- [x] Log viewing with filtering

**Usage**:
```bash
nc1709 --plugin git:status
nc1709 --plugin git:diff
nc1709 --plugin git:log
# Or in shell mode:
git status
git diff
```

### 3.3 Docker Agent ✅ COMPLETE
- [x] Container listing (`ps`)
- [x] Container start/stop/remove
- [x] Container logs viewing
- [x] Execute commands in containers
- [x] Image management (list, pull, build, remove)
- [x] Docker Compose (up, down, ps)
- [x] Prune unused resources

**Usage**:
```bash
nc1709 --plugin docker:ps
nc1709 --plugin docker:images
nc1709 --plugin docker:compose_up
# Or in shell mode:
docker ps
docker images
```

### 3.4 Framework Agents ✅ COMPLETE
- [x] FastAPI scaffolding, endpoints, and Pydantic models
- [x] Next.js scaffolding, pages, components, and API routes
- [x] Django projects, apps, models, views, and serializers
- [x] 28 framework agent tests

**Supported Frameworks**:
```
FastAPI:
  - Project scaffolding (with DB, auth options)
  - Endpoint generation
  - Pydantic model generation
  - CRUD router generation
  - Project analysis

Next.js:
  - Project scaffolding (TypeScript, Tailwind)
  - Page generation (App Router)
  - Component generation (client/server)
  - API route generation
  - Layout generation

Django:
  - Project scaffolding (with DRF option)
  - App generation
  - Model generation
  - View generation (function, class, viewset)
  - Serializer generation
```

### 3.5 MCP Server Support ✅ COMPLETE
- [x] Full Model Context Protocol implementation
- [x] MCP Server (expose NC1709 as tool provider)
- [x] MCP Client (connect to external MCP servers)
- [x] MCP Manager (high-level API)
- [x] Default tools (read_file, write_file, execute_command, search_code)
- [x] Auto-discovery from config files
- [x] CLI integration (--mcp-status, --mcp-serve, --mcp-tool)
- [x] 60 MCP tests

**MCP Structure**:
```
nc1709/mcp/
├── __init__.py
├── protocol.py    # MCPMessage, MCPTool, MCPResource, MCPErrorCode
├── server.py      # MCPServer - expose NC1709 capabilities
├── client.py      # MCPClient - connect to external servers
└── manager.py     # MCPManager - high-level unified API
```

**Usage**:
```bash
# Show MCP status
nc1709 --mcp-status

# List available tools
# In shell mode: mcp tools

# Call a tool
nc1709 --mcp-tool read_file --args '{"path": "main.py"}'

# Run as MCP server (for other AI tools to connect)
nc1709 --mcp-serve

# Connect to external MCP servers
nc1709 --mcp-connect ./mcp.json
```

---

## Phase 4: UI/UX & Collaboration ✅ COMPLETE

**Status**: Delivered December 4, 2025
**Goal**: Bring NC1709 to more interfaces and enable team usage

### 4.1 Web UI Dashboard ✅ COMPLETE
- [x] Local web server (FastAPI backend)
- [x] Modern responsive dashboard UI
- [x] Conversation view with syntax highlighting
- [x] Session management (view, create, resume)
- [x] Semantic code search interface
- [x] Plugin management panel
- [x] MCP tools browser
- [x] Configuration viewer
- [x] Real-time WebSocket chat support
- [x] 26 dashboard tests

### 4.2 VS Code Extension ✅ COMPLETE
- [x] Inline code suggestions
- [x] Chat panel integration
- [x] Code actions (refactor, explain, test)
- [x] Problem detection and fixes

### 4.3 Desktop App ✅ COMPLETE
- [x] Electron-based desktop application
- [x] System tray integration
- [x] Dark/light mode support

---

## Phase 5: Claude Code Architecture ✅ COMPLETE

**Status**: Delivered December 5, 2025 (v1.8.0)
**Goal**: Split architecture - local tools, remote LLM

### 5.1 Architecture Redesign ✅ COMPLETE
- [x] Tools execute locally on user's machine
- [x] LLM inference on remote server only
- [x] Auto-connect to `nc1709.lafzusa.com` by default
- [x] `--local` flag for offline/self-hosted mode
- [x] Multi-turn agentic loop in CLI

### 5.2 New API Endpoints ✅ COMPLETE
- [x] `POST /api/remote/agent` - Returns tool calls for local execution
- [x] `POST /api/remote/index` - Server-side code indexing
- [x] `POST /api/remote/search` - Semantic search across indexed code
- [x] `GET /api/remote/index/stats` - Indexing statistics

### 5.3 Server-Side Vector Database ✅ COMPLETE
- [x] ChromaDB on server for code embeddings
- [x] Auto-index files when Read tool is used
- [x] Per-user isolation via user_id
- [x] Project-based grouping
- [x] Semantic code search API

### 5.4 Session Memory ✅ COMPLETE
- [x] Local session storage (`~/.nc1709/sessions/`)
- [x] Conversation history sent for LLM context
- [x] Resume sessions with `--resume`
- [x] List sessions with `--sessions`

### 5.5 Tool Execution Framework ✅ COMPLETE
- [x] Tool registry for local execution
- [x] Permission system with approval prompts
- [x] Tool history tracking
- [x] Automatic file indexing on read

**Architecture Diagram**:
```
┌─────────────────────────────────────┐     ┌──────────────────────────────────┐
│  User's Machine (CLI)               │     │  nc1709.lafzusa.com (Server)     │
│                                     │     │                                  │
│  ✅ Tools execute HERE              │     │  ✅ LLM inference HERE           │
│  • Read/Write/Edit files            │◀───▶│  • Ollama models                 │
│  • Run bash commands                │     │  • Reasoning engine              │
│  • Search code (grep/glob)          │     │  • Vector DB (code indexing)     │
│  • Web search/fetch                 │     │                                  │
│                                     │     │                                  │
│  📁 Your files STAY HERE            │     │  🧠 Only "thinking" happens here │
└─────────────────────────────────────┘     └──────────────────────────────────┘
```

---

## Phase 6: Future Enhancements ⏳ PLANNED

**Target**: Q1-Q2 2026

### 6.1 Team Collaboration
- [ ] Shared project context
- [ ] Team memory/knowledge base
- [ ] Access controls and audit logging

### 6.2 Advanced Features
- [ ] Multi-file editing support
- [ ] Code generation from images/screenshots
- [ ] Voice input/output
- [ ] Mobile app

---

## Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| Basic (config, classifier, file) | 9 | ✅ |
| Executor | 12 | ✅ |
| LLM Adapter | 14 | ✅ |
| Reasoning Engine | 16 | ✅ |
| Memory Module | 23 | ✅ |
| Plugin System | 36 | ✅ |
| Framework Agents | 28 | ✅ |
| MCP Support | 60 | ✅ |
| Web Dashboard | 26 | ✅ |
| **Total** | **221** | ✅ |

---

## Quick Wins (Can be done anytime)

| Feature | Complexity | Impact | Status |
|---------|------------|--------|--------|
| LLM-based Task Classifier | Low | High | ⏳ |
| Context Window Management | Low | Medium | ⏳ |
| Progress Indicators | Low | Medium | ⏳ |
| Shell Completions (bash/zsh) | Low | Low | ⏳ |
| Config Validation | Low | Low | ⏳ |

---

## Dependencies

```txt
# Core
ollama>=0.1.0
litellm>=1.0.0
rich>=13.0.0
prompt_toolkit>=3.0.0

# Phase 2 - Memory
chromadb>=0.4.0
sentence-transformers>=2.2.0
watchdog>=3.0.0

# Development
pytest>=7.0.0
```

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.0.0 | Dec 3, 2025 | Initial release - Phase 1 complete |
| 1.0.1 | Dec 4, 2025 | Bug fixes, security improvements |
| 1.1.0 | Dec 4, 2025 | Phase 2 - Memory & Context complete |
| 1.2.0 | Dec 4, 2025 | Phase 3 - Plugin system, Git & Docker agents |
| 1.3.0 | Dec 4, 2025 | Phase 3 complete - Framework agents, MCP support |
| 1.4.0 | Dec 4, 2025 | Phase 4 web dashboard - Full browser-based UI |
| 1.5.0 | Dec 4, 2025 | Smart Task Classifier, Progress Indicators |
| 1.6.0 | Dec 4, 2025 | Agentic architecture with tool execution |
| 1.7.0 | Dec 4, 2025 | NotebookEdit, WebSearch, WebScreenshot tools |
| 1.7.1 | Dec 4, 2025 | Platform-specific installation docs |
| 1.7.2 | Dec 5, 2025 | Remote-first prerequisites clarification |
| 1.7.3 | Dec 5, 2025 | Default server URL (nc1709.lafzusa.com) |
| **1.8.0** | **Dec 5, 2025** | **Phase 5 - Claude Code architecture: local tools + remote LLM** |

---

*Built with passion for developers who value privacy and control*
