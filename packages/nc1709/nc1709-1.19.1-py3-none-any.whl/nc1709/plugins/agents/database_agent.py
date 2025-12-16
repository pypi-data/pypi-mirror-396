"""
Database Agent for NC1709
Handles database operations across PostgreSQL, MySQL, SQLite, MongoDB, Redis
"""
import subprocess
import json
import re
import os
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
class TableInfo:
    """Represents a database table"""
    name: str
    schema: str = "public"
    rows: int = 0
    size: str = ""


@dataclass
class ConnectionInfo:
    """Database connection information"""
    host: str = "localhost"
    port: int = 5432
    database: str = ""
    user: str = ""
    # Password should come from environment


class DatabaseAgent(Plugin):
    """
    Database operations agent.

    Provides database operations:
    - Connection testing
    - Schema inspection (tables, columns)
    - Query execution (read-only by default)
    - Backup/restore helpers
    - Migration status
    """

    METADATA = PluginMetadata(
        name="database",
        version="1.0.0",
        description="Database operations and management",
        author="NC1709 Team",
        capabilities=[
            PluginCapability.COMMAND_EXECUTION
        ],
        keywords=[
            "database", "sql", "postgres", "postgresql", "mysql", "sqlite",
            "mongodb", "redis", "psql", "query", "schema", "migration",
            "backup", "restore", "table", "column"
        ],
        config_schema={
            "default_database": {"type": "string", "default": "postgres"},
            "connection_timeout": {"type": "integer", "default": 10},
            "query_timeout": {"type": "integer", "default": 30},
        }
    )

    # Supported databases and their CLI tools
    DATABASE_TOOLS = {
        "postgres": {
            "cli": "psql",
            "version_cmd": "psql --version",
            "list_dbs": "psql -l",
            "list_tables": "psql -c '\\dt'",
            "describe_table": "psql -c '\\d {table}'",
            "default_port": 5432,
        },
        "mysql": {
            "cli": "mysql",
            "version_cmd": "mysql --version",
            "list_dbs": "mysql -e 'SHOW DATABASES'",
            "list_tables": "mysql -e 'SHOW TABLES'",
            "describe_table": "mysql -e 'DESCRIBE {table}'",
            "default_port": 3306,
        },
        "sqlite": {
            "cli": "sqlite3",
            "version_cmd": "sqlite3 --version",
            "list_tables": "sqlite3 {db} '.tables'",
            "describe_table": "sqlite3 {db} '.schema {table}'",
            "default_port": None,
        },
        "mongodb": {
            "cli": "mongosh",
            "version_cmd": "mongosh --version",
            "list_dbs": "mongosh --eval 'show dbs'",
            "list_collections": "mongosh --eval 'show collections'",
            "default_port": 27017,
        },
        "redis": {
            "cli": "redis-cli",
            "version_cmd": "redis-cli --version",
            "ping": "redis-cli ping",
            "info": "redis-cli info",
            "default_port": 6379,
        },
    }

    @property
    def metadata(self) -> PluginMetadata:
        return self.METADATA

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._available_databases = {}

    def initialize(self) -> bool:
        """Initialize the database agent"""
        # Detect available database CLIs
        for db, config in self.DATABASE_TOOLS.items():
            try:
                result = subprocess.run(
                    config["version_cmd"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                self._available_databases[db] = result.returncode == 0
            except Exception:
                self._available_databases[db] = False

        return any(self._available_databases.values())

    def cleanup(self) -> None:
        """Cleanup resources"""
        pass

    def _register_actions(self) -> None:
        """Register database actions"""
        self.register_action(
            "status",
            self.check_status,
            "Check database availability",
            parameters={
                "database": {"type": "string", "optional": True},
            }
        )

        self.register_action(
            "list_tables",
            self.list_tables,
            "List database tables",
            parameters={
                "database": {"type": "string", "optional": True},
                "db_name": {"type": "string", "optional": True},
            }
        )

        self.register_action(
            "describe",
            self.describe_table,
            "Describe a table's structure",
            parameters={
                "table": {"type": "string", "required": True},
                "database": {"type": "string", "optional": True},
            }
        )

        self.register_action(
            "query",
            self.run_query,
            "Run a read-only query",
            parameters={
                "sql": {"type": "string", "required": True},
                "database": {"type": "string", "optional": True},
                "db_name": {"type": "string", "optional": True},
            }
        )

        self.register_action(
            "connect_test",
            self.test_connection,
            "Test database connection",
            parameters={
                "database": {"type": "string", "optional": True},
                "host": {"type": "string", "optional": True},
                "port": {"type": "integer", "optional": True},
            }
        )

        self.register_action(
            "backup",
            self.create_backup,
            "Create database backup",
            parameters={
                "database": {"type": "string", "optional": True},
                "db_name": {"type": "string", "required": True},
                "output": {"type": "string", "optional": True},
            },
            requires_confirmation=True
        )

        self.register_action(
            "migrations",
            self.check_migrations,
            "Check migration status",
            parameters={
                "framework": {"type": "string", "optional": True},
            }
        )

    def _run_command(self, cmd: str, timeout: int = 30) -> subprocess.CompletedProcess:
        """Run a database command"""
        return subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PGPASSWORD": os.environ.get("PGPASSWORD", "")}
        )

    def _get_database_type(self, specified: Optional[str] = None) -> Optional[str]:
        """Get the database type to use"""
        if specified and specified in self._available_databases:
            if self._available_databases[specified]:
                return specified
            return None

        # Auto-detect based on project files
        cwd = Path.cwd()

        # Check for database config files
        if (cwd / "prisma").exists() or (cwd / "schema.prisma").exists():
            # Could be any, check prisma schema
            pass

        # Check for Django
        if (cwd / "manage.py").exists():
            # Likely postgres or sqlite
            if self._available_databases.get("postgres"):
                return "postgres"
            if self._available_databases.get("sqlite"):
                return "sqlite"

        # Return first available
        for db, available in self._available_databases.items():
            if available:
                return db

        return None

    def check_status(self, database: Optional[str] = None) -> ActionResult:
        """Check database availability

        Args:
            database: Specific database type to check

        Returns:
            ActionResult with status information
        """
        if database:
            if database not in self.DATABASE_TOOLS:
                return ActionResult.fail(f"Unknown database: {database}")

            available = self._available_databases.get(database, False)
            config = self.DATABASE_TOOLS[database]

            if available:
                # Get version
                try:
                    result = self._run_command(config["version_cmd"])
                    version = result.stdout.strip()
                except Exception:
                    version = "unknown"

                return ActionResult.ok(
                    message=f"{database} is available",
                    data={
                        "database": database,
                        "available": True,
                        "version": version,
                        "cli": config["cli"],
                    }
                )
            else:
                return ActionResult.fail(
                    f"{database} CLI ({config['cli']}) not found. "
                    f"Install it to use {database} features."
                )

        # Check all databases
        status = {}
        for db, available in self._available_databases.items():
            status[db] = "available" if available else "not installed"

        available_list = [db for db, avail in self._available_databases.items() if avail]

        return ActionResult.ok(
            message=f"{len(available_list)} database CLIs available",
            data={
                "databases": status,
                "available": available_list,
            }
        )

    def list_tables(
        self,
        database: Optional[str] = None,
        db_name: Optional[str] = None
    ) -> ActionResult:
        """List database tables

        Args:
            database: Database type (postgres, mysql, sqlite)
            db_name: Database name to connect to

        Returns:
            ActionResult with table list
        """
        db_type = self._get_database_type(database)
        if not db_type:
            return ActionResult.fail("No database CLI available")

        config = self.DATABASE_TOOLS[db_type]

        if db_type == "postgres":
            cmd = f"psql {db_name or ''} -c '\\dt'"
        elif db_type == "mysql":
            cmd = f"mysql {db_name or ''} -e 'SHOW TABLES'"
        elif db_type == "sqlite":
            if not db_name:
                return ActionResult.fail("SQLite requires a database file path")
            cmd = f"sqlite3 {db_name} '.tables'"
        elif db_type == "mongodb":
            cmd = f"mongosh {db_name or 'test'} --eval 'db.getCollectionNames()'"
        elif db_type == "redis":
            cmd = "redis-cli KEYS '*'"
        else:
            return ActionResult.fail(f"List tables not supported for {db_type}")

        try:
            result = self._run_command(cmd)

            if result.returncode != 0:
                return ActionResult.fail(f"Error listing tables:\n{result.stderr}")

            return ActionResult.ok(
                message=f"Tables in {db_name or 'default'} ({db_type})",
                data={
                    "database_type": db_type,
                    "database_name": db_name,
                    "output": result.stdout,
                }
            )

        except subprocess.TimeoutExpired:
            return ActionResult.fail("Query timed out")
        except Exception as e:
            return ActionResult.fail(f"Error: {e}")

    def describe_table(
        self,
        table: str,
        database: Optional[str] = None,
        db_name: Optional[str] = None
    ) -> ActionResult:
        """Describe a table's structure

        Args:
            table: Table name
            database: Database type
            db_name: Database name

        Returns:
            ActionResult with table structure
        """
        db_type = self._get_database_type(database)
        if not db_type:
            return ActionResult.fail("No database CLI available")

        if db_type == "postgres":
            cmd = f"psql {db_name or ''} -c '\\d {table}'"
        elif db_type == "mysql":
            cmd = f"mysql {db_name or ''} -e 'DESCRIBE {table}'"
        elif db_type == "sqlite":
            if not db_name:
                return ActionResult.fail("SQLite requires a database file path")
            cmd = f"sqlite3 {db_name} '.schema {table}'"
        else:
            return ActionResult.fail(f"Describe not supported for {db_type}")

        try:
            result = self._run_command(cmd)

            if result.returncode != 0:
                return ActionResult.fail(f"Error describing table:\n{result.stderr}")

            return ActionResult.ok(
                message=f"Structure of {table}",
                data={
                    "table": table,
                    "database_type": db_type,
                    "output": result.stdout,
                }
            )

        except Exception as e:
            return ActionResult.fail(f"Error: {e}")

    def run_query(
        self,
        sql: str,
        database: Optional[str] = None,
        db_name: Optional[str] = None
    ) -> ActionResult:
        """Run a read-only SQL query

        Args:
            sql: SQL query to run
            database: Database type
            db_name: Database name

        Returns:
            ActionResult with query results
        """
        db_type = self._get_database_type(database)
        if not db_type:
            return ActionResult.fail("No database CLI available")

        # Safety check: only allow SELECT, SHOW, DESCRIBE, EXPLAIN
        sql_upper = sql.strip().upper()
        allowed_starts = ("SELECT", "SHOW", "DESCRIBE", "EXPLAIN", "WITH")

        if not any(sql_upper.startswith(start) for start in allowed_starts):
            return ActionResult.fail(
                "Only read-only queries allowed (SELECT, SHOW, DESCRIBE, EXPLAIN). "
                "Use database tools directly for write operations."
            )

        if db_type == "postgres":
            cmd = f"psql {db_name or ''} -c \"{sql}\""
        elif db_type == "mysql":
            cmd = f"mysql {db_name or ''} -e \"{sql}\""
        elif db_type == "sqlite":
            if not db_name:
                return ActionResult.fail("SQLite requires a database file path")
            cmd = f"sqlite3 {db_name} \"{sql}\""
        else:
            return ActionResult.fail(f"Query not supported for {db_type}")

        try:
            result = self._run_command(cmd)

            if result.returncode != 0:
                return ActionResult.fail(f"Query error:\n{result.stderr}")

            return ActionResult.ok(
                message="Query executed",
                data={
                    "query": sql,
                    "database_type": db_type,
                    "output": result.stdout,
                }
            )

        except subprocess.TimeoutExpired:
            return ActionResult.fail("Query timed out")
        except Exception as e:
            return ActionResult.fail(f"Error: {e}")

    def test_connection(
        self,
        database: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None
    ) -> ActionResult:
        """Test database connection

        Args:
            database: Database type
            host: Database host
            port: Database port

        Returns:
            ActionResult with connection status
        """
        db_type = self._get_database_type(database)
        if not db_type:
            return ActionResult.fail("No database CLI available")

        config = self.DATABASE_TOOLS[db_type]
        host = host or "localhost"
        port = port or config["default_port"]

        if db_type == "postgres":
            cmd = f"pg_isready -h {host} -p {port}"
        elif db_type == "mysql":
            cmd = f"mysqladmin -h {host} -P {port} ping"
        elif db_type == "redis":
            cmd = f"redis-cli -h {host} -p {port} ping"
        elif db_type == "mongodb":
            cmd = f"mongosh --host {host}:{port} --eval 'db.runCommand({{ping: 1}})'"
        else:
            return ActionResult.fail(f"Connection test not supported for {db_type}")

        try:
            result = self._run_command(cmd, timeout=10)

            if result.returncode == 0:
                return ActionResult.ok(
                    message=f"Connected to {db_type} at {host}:{port}",
                    data={
                        "database_type": db_type,
                        "host": host,
                        "port": port,
                        "connected": True,
                    }
                )
            else:
                return ActionResult.fail(
                    f"Could not connect to {db_type} at {host}:{port}\n{result.stderr}"
                )

        except subprocess.TimeoutExpired:
            return ActionResult.fail(f"Connection to {db_type} timed out")
        except Exception as e:
            return ActionResult.fail(f"Connection error: {e}")

    def create_backup(
        self,
        db_name: str,
        database: Optional[str] = None,
        output: Optional[str] = None
    ) -> ActionResult:
        """Create database backup

        Args:
            db_name: Database name to backup
            database: Database type
            output: Output file path

        Returns:
            ActionResult with backup info
        """
        db_type = self._get_database_type(database)
        if not db_type:
            return ActionResult.fail("No database CLI available")

        output = output or f"{db_name}_backup.sql"

        if db_type == "postgres":
            cmd = f"pg_dump {db_name} > {output}"
        elif db_type == "mysql":
            cmd = f"mysqldump {db_name} > {output}"
        elif db_type == "sqlite":
            cmd = f"sqlite3 {db_name} '.dump' > {output}"
        elif db_type == "mongodb":
            cmd = f"mongodump --db {db_name} --out {output}"
        else:
            return ActionResult.fail(f"Backup not supported for {db_type}")

        try:
            result = self._run_command(cmd, timeout=1800)  # 30 min timeout

            if result.returncode == 0:
                return ActionResult.ok(
                    message=f"Backup created: {output}",
                    data={
                        "database_type": db_type,
                        "database_name": db_name,
                        "output_file": output,
                    }
                )
            else:
                return ActionResult.fail(f"Backup failed:\n{result.stderr}")

        except subprocess.TimeoutExpired:
            return ActionResult.fail("Backup timed out")
        except Exception as e:
            return ActionResult.fail(f"Backup error: {e}")

    def check_migrations(self, framework: Optional[str] = None) -> ActionResult:
        """Check migration status

        Args:
            framework: ORM/migration framework (alembic, django, prisma, etc.)

        Returns:
            ActionResult with migration status
        """
        cwd = Path.cwd()

        # Auto-detect framework
        if not framework:
            if (cwd / "alembic.ini").exists() or (cwd / "alembic").exists():
                framework = "alembic"
            elif (cwd / "manage.py").exists():
                framework = "django"
            elif (cwd / "prisma").exists():
                framework = "prisma"
            elif (cwd / "db" / "migrate").exists():
                framework = "rails"

        if not framework:
            return ActionResult.fail(
                "Could not detect migration framework. "
                "Supported: alembic, django, prisma, rails"
            )

        migration_commands = {
            "alembic": "alembic current",
            "django": "python manage.py showmigrations",
            "prisma": "npx prisma migrate status",
            "rails": "rails db:migrate:status",
            "sequelize": "npx sequelize-cli db:migrate:status",
        }

        if framework not in migration_commands:
            return ActionResult.fail(f"Unknown migration framework: {framework}")

        try:
            result = self._run_command(migration_commands[framework])

            return ActionResult.ok(
                message=f"Migration status ({framework})",
                data={
                    "framework": framework,
                    "output": result.stdout + result.stderr,
                    "return_code": result.returncode,
                }
            )

        except Exception as e:
            return ActionResult.fail(f"Error checking migrations: {e}")

    def can_handle(self, request: str) -> float:
        """Check if request is database-related"""
        request_lower = request.lower()

        # High confidence
        high_conf = [
            "database", "sql", "postgres", "mysql", "sqlite", "mongodb",
            "redis", "psql", "table", "schema", "migration", "query"
        ]
        for kw in high_conf:
            if kw in request_lower:
                return 0.85

        # Medium confidence
        med_conf = ["backup", "restore", "dump", "select", "show tables"]
        for kw in med_conf:
            if kw in request_lower:
                return 0.6

        return super().can_handle(request)

    def handle_request(self, request: str, **kwargs) -> Optional[ActionResult]:
        """Handle a natural language request"""
        request_lower = request.lower()

        # Status check
        if any(kw in request_lower for kw in ["database status", "db status", "check database"]):
            return self.check_status()

        # List tables
        if any(kw in request_lower for kw in ["list table", "show table", "what table"]):
            return self.list_tables()

        # Describe table
        if any(kw in request_lower for kw in ["describe", "schema", "structure"]):
            # Extract table name
            match = re.search(r"(?:describe|schema|structure)\s+(?:of\s+)?(\w+)", request_lower)
            if match:
                return self.describe_table(match.group(1))

        # Migration status
        if "migration" in request_lower:
            return self.check_migrations()

        # Connection test
        if any(kw in request_lower for kw in ["connect", "connection", "ping"]):
            return self.test_connection()

        return None
