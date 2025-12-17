"""
Docker Agent for NC1709
Handles Docker and Docker Compose operations
"""
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

try:
    from ..base import (
        Plugin, PluginMetadata, PluginCapability,
        ActionResult
    )
except ImportError:
    # When loaded dynamically via importlib
    from nc1709.plugins.base import (
        Plugin, PluginMetadata, PluginCapability,
        ActionResult
    )


@dataclass
class ContainerInfo:
    """Represents a Docker container"""
    id: str
    name: str
    image: str
    status: str
    ports: str
    created: str

    @property
    def is_running(self) -> bool:
        return "Up" in self.status


@dataclass
class ImageInfo:
    """Represents a Docker image"""
    id: str
    repository: str
    tag: str
    size: str
    created: str


class DockerAgent(Plugin):
    """
    Docker operations agent.

    Provides Docker and Docker Compose operations:
    - Container management (list, start, stop, remove)
    - Image management (list, pull, build, remove)
    - Docker Compose operations
    - Log viewing and inspection
    """

    METADATA = PluginMetadata(
        name="docker",
        version="1.0.0",
        description="Docker container management",
        author="NC1709 Team",
        capabilities=[
            PluginCapability.CONTAINER_MANAGEMENT,
            PluginCapability.COMMAND_EXECUTION
        ],
        keywords=[
            "docker", "container", "image", "compose", "build",
            "pull", "push", "run", "stop", "start", "logs",
            "dockerfile", "docker-compose", "volume", "network"
        ],
        config_schema={
            "compose_file": {"type": "string", "default": "docker-compose.yml"},
            "default_registry": {"type": "string", "default": ""},
            "build_context": {"type": "string", "default": "."}
        }
    )

    @property
    def metadata(self) -> PluginMetadata:
        return self.METADATA

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._docker_available = False
        self._compose_available = False

    def initialize(self) -> bool:
        """Initialize the Docker agent"""
        # Check Docker
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True
            )
            self._docker_available = result.returncode == 0
        except FileNotFoundError:
            self._error = "Docker is not installed"
            return False

        # Check Docker Compose
        try:
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True
            )
            self._compose_available = result.returncode == 0
        except Exception:
            # Try legacy docker-compose
            try:
                result = subprocess.run(
                    ["docker-compose", "--version"],
                    capture_output=True,
                    text=True
                )
                self._compose_available = result.returncode == 0
            except Exception:
                pass

        return self._docker_available

    def cleanup(self) -> None:
        """Cleanup resources"""
        pass

    def _register_actions(self) -> None:
        """Register Docker actions"""
        # Container actions
        self.register_action(
            "ps",
            self.list_containers,
            "List containers",
            parameters={"all": {"type": "boolean", "default": False}}
        )

        self.register_action(
            "start",
            self.start_container,
            "Start a container",
            parameters={"container": {"type": "string", "required": True}}
        )

        self.register_action(
            "stop",
            self.stop_container,
            "Stop a container",
            parameters={"container": {"type": "string", "required": True}},
            requires_confirmation=True
        )

        self.register_action(
            "remove",
            self.remove_container,
            "Remove a container",
            parameters={
                "container": {"type": "string", "required": True},
                "force": {"type": "boolean", "default": False}
            },
            requires_confirmation=True,
            dangerous=True
        )

        self.register_action(
            "logs",
            self.get_logs,
            "View container logs",
            parameters={
                "container": {"type": "string", "required": True},
                "tail": {"type": "integer", "default": 100},
                "follow": {"type": "boolean", "default": False}
            }
        )

        self.register_action(
            "exec",
            self.exec_in_container,
            "Execute command in container",
            parameters={
                "container": {"type": "string", "required": True},
                "command": {"type": "string", "required": True}
            }
        )

        # Image actions
        self.register_action(
            "images",
            self.list_images,
            "List images"
        )

        self.register_action(
            "pull",
            self.pull_image,
            "Pull an image",
            parameters={"image": {"type": "string", "required": True}}
        )

        self.register_action(
            "build",
            self.build_image,
            "Build an image",
            parameters={
                "tag": {"type": "string", "required": True},
                "dockerfile": {"type": "string", "default": "Dockerfile"},
                "context": {"type": "string", "default": "."}
            }
        )

        self.register_action(
            "rmi",
            self.remove_image,
            "Remove an image",
            parameters={
                "image": {"type": "string", "required": True},
                "force": {"type": "boolean", "default": False}
            },
            requires_confirmation=True,
            dangerous=True
        )

        # Compose actions
        self.register_action(
            "compose_up",
            self.compose_up,
            "Start services with docker-compose",
            parameters={
                "detach": {"type": "boolean", "default": True},
                "build": {"type": "boolean", "default": False},
                "services": {"type": "array", "optional": True}
            }
        )

        self.register_action(
            "compose_down",
            self.compose_down,
            "Stop services with docker-compose",
            parameters={
                "volumes": {"type": "boolean", "default": False},
                "remove_orphans": {"type": "boolean", "default": False}
            },
            requires_confirmation=True
        )

        self.register_action(
            "compose_ps",
            self.compose_ps,
            "List compose services"
        )

        # Utility actions
        self.register_action(
            "prune",
            self.prune,
            "Remove unused resources",
            parameters={
                "type": {"type": "string", "enum": ["containers", "images", "volumes", "all"]}
            },
            requires_confirmation=True,
            dangerous=True
        )

    def _run_docker(self, *args, timeout: int = 60) -> subprocess.CompletedProcess:
        """Run a docker command"""
        cmd = ["docker"] + list(args)
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

    def _run_compose(self, *args, timeout: int = 120) -> subprocess.CompletedProcess:
        """Run a docker-compose command"""
        compose_file = self._config.get("compose_file", "docker-compose.yml")

        # Try new syntax first
        cmd = ["docker", "compose", "-f", compose_file] + list(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0 or "unknown docker command" not in result.stderr.lower():
                return result
        except Exception:
            pass

        # Fall back to docker-compose
        cmd = ["docker-compose", "-f", compose_file] + list(args)
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

    # Container operations

    def list_containers(self, all: bool = False) -> ActionResult:
        """List Docker containers

        Args:
            all: Include stopped containers

        Returns:
            ActionResult with container list
        """
        args = ["ps", "--format", "{{.ID}}|{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}|{{.CreatedAt}}"]

        if all:
            args.append("-a")

        result = self._run_docker(*args)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        containers = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 6:
                containers.append(ContainerInfo(
                    id=parts[0],
                    name=parts[1],
                    image=parts[2],
                    status=parts[3],
                    ports=parts[4],
                    created=parts[5]
                ))

        running = sum(1 for c in containers if c.is_running)

        return ActionResult.ok(
            message=f"{len(containers)} containers ({running} running)",
            data=containers
        )

    def start_container(self, container: str) -> ActionResult:
        """Start a container"""
        result = self._run_docker("start", container)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        return ActionResult.ok(f"Started container: {container}")

    def stop_container(self, container: str) -> ActionResult:
        """Stop a container"""
        result = self._run_docker("stop", container)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        return ActionResult.ok(f"Stopped container: {container}")

    def remove_container(self, container: str, force: bool = False) -> ActionResult:
        """Remove a container"""
        args = ["rm"]
        if force:
            args.append("-f")
        args.append(container)

        result = self._run_docker(*args)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        return ActionResult.ok(f"Removed container: {container}")

    def get_logs(
        self,
        container: str,
        tail: int = 100,
        follow: bool = False
    ) -> ActionResult:
        """Get container logs"""
        args = ["logs", f"--tail={tail}"]

        if follow:
            # For follow, we'd need streaming - just get latest
            pass

        args.append(container)

        result = self._run_docker(*args)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        # Combine stdout and stderr (logs can go to either)
        logs = result.stdout + result.stderr

        return ActionResult.ok(
            message=f"Logs for {container} (last {tail} lines)",
            data=logs
        )

    def exec_in_container(self, container: str, command: str) -> ActionResult:
        """Execute command in container"""
        args = ["exec", container] + command.split()

        result = self._run_docker(*args)

        return ActionResult.ok(
            message=f"Executed in {container}",
            data={"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode}
        )

    # Image operations

    def list_images(self) -> ActionResult:
        """List Docker images"""
        result = self._run_docker(
            "images",
            "--format", "{{.ID}}|{{.Repository}}|{{.Tag}}|{{.Size}}|{{.CreatedAt}}"
        )

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        images = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 5:
                images.append(ImageInfo(
                    id=parts[0],
                    repository=parts[1],
                    tag=parts[2],
                    size=parts[3],
                    created=parts[4]
                ))

        return ActionResult.ok(
            message=f"{len(images)} images",
            data=images
        )

    def pull_image(self, image: str) -> ActionResult:
        """Pull an image"""
        result = self._run_docker("pull", image, timeout=300)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        return ActionResult.ok(
            message=f"Pulled image: {image}",
            data=result.stdout
        )

    def build_image(
        self,
        tag: str,
        dockerfile: str = "Dockerfile",
        context: str = "."
    ) -> ActionResult:
        """Build a Docker image"""
        args = ["build", "-t", tag, "-f", dockerfile, context]

        result = self._run_docker(*args, timeout=600)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        return ActionResult.ok(
            message=f"Built image: {tag}",
            data=result.stdout
        )

    def remove_image(self, image: str, force: bool = False) -> ActionResult:
        """Remove an image"""
        args = ["rmi"]
        if force:
            args.append("-f")
        args.append(image)

        result = self._run_docker(*args)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        return ActionResult.ok(f"Removed image: {image}")

    # Docker Compose operations

    def compose_up(
        self,
        detach: bool = True,
        build: bool = False,
        services: Optional[List[str]] = None
    ) -> ActionResult:
        """Start docker-compose services"""
        if not self._compose_available:
            return ActionResult.fail("Docker Compose not available")

        args = ["up"]

        if detach:
            args.append("-d")
        if build:
            args.append("--build")

        if services:
            args.extend(services)

        result = self._run_compose(*args, timeout=300)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        return ActionResult.ok(
            message="Services started",
            data=result.stdout
        )

    def compose_down(
        self,
        volumes: bool = False,
        remove_orphans: bool = False
    ) -> ActionResult:
        """Stop docker-compose services"""
        if not self._compose_available:
            return ActionResult.fail("Docker Compose not available")

        args = ["down"]

        if volumes:
            args.append("-v")
        if remove_orphans:
            args.append("--remove-orphans")

        result = self._run_compose(*args)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        return ActionResult.ok(
            message="Services stopped",
            data=result.stdout
        )

    def compose_ps(self) -> ActionResult:
        """List docker-compose services"""
        if not self._compose_available:
            return ActionResult.fail("Docker Compose not available")

        result = self._run_compose("ps")

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        return ActionResult.ok(
            message="Compose services",
            data=result.stdout
        )

    # Utility operations

    def prune(self, type: str = "containers") -> ActionResult:
        """Remove unused Docker resources"""
        if type == "containers":
            result = self._run_docker("container", "prune", "-f")
        elif type == "images":
            result = self._run_docker("image", "prune", "-f")
        elif type == "volumes":
            result = self._run_docker("volume", "prune", "-f")
        elif type == "all":
            result = self._run_docker("system", "prune", "-f")
        else:
            return ActionResult.fail(f"Unknown prune type: {type}")

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        return ActionResult.ok(
            message=f"Pruned {type}",
            data=result.stdout
        )

    def can_handle(self, request: str) -> float:
        """Check if request is Docker-related"""
        request_lower = request.lower()

        # High confidence
        high_conf = ["docker", "container", "compose", "dockerfile"]
        for kw in high_conf:
            if kw in request_lower:
                return 0.9

        # Medium confidence
        med_conf = ["image", "build", "deploy", "service"]
        for kw in med_conf:
            if kw in request_lower:
                return 0.5

        return super().can_handle(request)

    def handle_request(self, request: str, **kwargs) -> Optional[ActionResult]:
        """Handle a natural language request"""
        request_lower = request.lower()

        # Container list
        if any(kw in request_lower for kw in ["list containers", "ps", "running containers"]):
            all_containers = "all" in request_lower or "stopped" in request_lower
            return self.list_containers(all=all_containers)

        # Images
        if "list images" in request_lower or "show images" in request_lower:
            return self.list_images()

        # Compose
        if "compose" in request_lower:
            if "up" in request_lower or "start" in request_lower:
                return self.compose_up()
            if "down" in request_lower or "stop" in request_lower:
                return self.compose_down()
            if "ps" in request_lower or "status" in request_lower:
                return self.compose_ps()

        return None
