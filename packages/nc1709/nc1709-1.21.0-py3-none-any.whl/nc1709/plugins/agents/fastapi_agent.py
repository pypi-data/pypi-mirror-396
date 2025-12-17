"""
FastAPI Agent for NC1709
Scaffolds FastAPI projects, endpoints, models, and more
"""
import os
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
class EndpointInfo:
    """Represents an API endpoint"""
    method: str
    path: str
    function_name: str
    description: str
    request_model: Optional[str] = None
    response_model: Optional[str] = None


class FastAPIAgent(Plugin):
    """
    FastAPI scaffolding and development agent.

    Provides:
    - Project scaffolding with best practices
    - Endpoint generation
    - Pydantic model generation
    - CRUD operations scaffolding
    - Database integration (SQLAlchemy)
    - Authentication scaffolding
    """

    METADATA = PluginMetadata(
        name="fastapi",
        version="1.0.0",
        description="FastAPI project scaffolding and development",
        author="NC1709 Team",
        capabilities=[
            PluginCapability.CODE_GENERATION,
            PluginCapability.PROJECT_SCAFFOLDING
        ],
        keywords=[
            "fastapi", "api", "rest", "endpoint", "pydantic",
            "model", "schema", "crud", "router", "uvicorn",
            "async", "python", "backend"
        ],
        config_schema={
            "project_path": {"type": "string", "default": "."},
            "use_async": {"type": "boolean", "default": True},
            "database": {"type": "string", "enum": ["sqlite", "postgresql", "mysql", "none"], "default": "sqlite"}
        }
    )

    @property
    def metadata(self) -> PluginMetadata:
        return self.METADATA

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._project_path: Optional[Path] = None

    def initialize(self) -> bool:
        """Initialize the FastAPI agent"""
        self._project_path = Path(self._config.get("project_path", ".")).resolve()
        return True

    def cleanup(self) -> None:
        """Cleanup resources"""
        pass

    def _register_actions(self) -> None:
        """Register FastAPI actions"""
        self.register_action(
            "scaffold",
            self.scaffold_project,
            "Create a new FastAPI project structure",
            parameters={
                "name": {"type": "string", "required": True},
                "with_db": {"type": "boolean", "default": True},
                "with_auth": {"type": "boolean", "default": False}
            }
        )

        self.register_action(
            "endpoint",
            self.create_endpoint,
            "Generate a new API endpoint",
            parameters={
                "path": {"type": "string", "required": True},
                "method": {"type": "string", "default": "GET"},
                "name": {"type": "string", "required": True}
            }
        )

        self.register_action(
            "model",
            self.create_model,
            "Generate a Pydantic model",
            parameters={
                "name": {"type": "string", "required": True},
                "fields": {"type": "object", "required": True}
            }
        )

        self.register_action(
            "crud",
            self.create_crud,
            "Generate CRUD endpoints for a model",
            parameters={
                "model": {"type": "string", "required": True},
                "prefix": {"type": "string", "default": ""}
            }
        )

        self.register_action(
            "router",
            self.create_router,
            "Generate a new router module",
            parameters={
                "name": {"type": "string", "required": True},
                "prefix": {"type": "string", "default": ""}
            }
        )

        self.register_action(
            "analyze",
            self.analyze_project,
            "Analyze existing FastAPI project structure"
        )

    def scaffold_project(
        self,
        name: str,
        with_db: bool = True,
        with_auth: bool = False
    ) -> ActionResult:
        """Create a new FastAPI project structure

        Args:
            name: Project name
            with_db: Include database setup
            with_auth: Include authentication

        Returns:
            ActionResult
        """
        project_dir = self._project_path / name

        if project_dir.exists():
            return ActionResult.fail(f"Directory '{name}' already exists")

        try:
            # Create directory structure
            dirs = [
                project_dir,
                project_dir / "app",
                project_dir / "app" / "api",
                project_dir / "app" / "api" / "v1",
                project_dir / "app" / "core",
                project_dir / "app" / "models",
                project_dir / "app" / "schemas",
                project_dir / "app" / "services",
                project_dir / "tests",
            ]

            if with_db:
                dirs.append(project_dir / "app" / "db")
                dirs.append(project_dir / "alembic")

            for d in dirs:
                d.mkdir(parents=True, exist_ok=True)

            # Create main.py
            main_content = self._generate_main(name, with_db, with_auth)
            (project_dir / "app" / "main.py").write_text(main_content)

            # Create __init__.py files
            for d in dirs:
                if "app" in str(d) or "tests" in str(d):
                    init_file = d / "__init__.py"
                    if not init_file.exists():
                        init_file.write_text("")

            # Create config
            config_content = self._generate_config(name, with_db)
            (project_dir / "app" / "core" / "config.py").write_text(config_content)

            # Create requirements.txt
            requirements = self._generate_requirements(with_db, with_auth)
            (project_dir / "requirements.txt").write_text(requirements)

            # Create .env.example
            env_content = self._generate_env_example(name, with_db)
            (project_dir / ".env.example").write_text(env_content)

            # Create example router
            router_content = self._generate_example_router()
            (project_dir / "app" / "api" / "v1" / "health.py").write_text(router_content)

            # Create API init
            api_init = self._generate_api_init()
            (project_dir / "app" / "api" / "v1" / "__init__.py").write_text(api_init)

            if with_db:
                # Create database setup
                db_content = self._generate_db_setup()
                (project_dir / "app" / "db" / "database.py").write_text(db_content)

                # Create base model
                base_model = self._generate_base_model()
                (project_dir / "app" / "models" / "base.py").write_text(base_model)

            if with_auth:
                # Create auth module
                auth_content = self._generate_auth_module()
                (project_dir / "app" / "core" / "auth.py").write_text(auth_content)

            files_created = len(list(project_dir.rglob("*")))

            return ActionResult.ok(
                message=f"Created FastAPI project '{name}' with {files_created} files",
                data={
                    "project_path": str(project_dir),
                    "with_db": with_db,
                    "with_auth": with_auth,
                    "next_steps": [
                        f"cd {name}",
                        "python -m venv venv",
                        "source venv/bin/activate",
                        "pip install -r requirements.txt",
                        "uvicorn app.main:app --reload"
                    ]
                }
            )

        except Exception as e:
            return ActionResult.fail(str(e))

    def create_endpoint(
        self,
        path: str,
        method: str = "GET",
        name: str = ""
    ) -> ActionResult:
        """Generate a new API endpoint

        Args:
            path: URL path (e.g., "/users/{user_id}")
            method: HTTP method
            name: Function name

        Returns:
            ActionResult with generated code
        """
        method = method.upper()
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            return ActionResult.fail(f"Invalid HTTP method: {method}")

        # Generate function name if not provided
        if not name:
            name = self._path_to_function_name(path, method)

        # Detect path parameters
        path_params = re.findall(r'\{(\w+)\}', path)

        # Generate endpoint code
        code = self._generate_endpoint_code(path, method, name, path_params)

        return ActionResult.ok(
            message=f"Generated {method} {path} endpoint",
            data={
                "code": code,
                "function_name": name,
                "path_params": path_params
            }
        )

    def create_model(
        self,
        name: str,
        fields: Dict[str, str]
    ) -> ActionResult:
        """Generate a Pydantic model

        Args:
            name: Model name
            fields: Dict of field_name -> field_type

        Returns:
            ActionResult with generated code
        """
        # Generate model code
        code = self._generate_pydantic_model(name, fields)

        return ActionResult.ok(
            message=f"Generated Pydantic model '{name}'",
            data={"code": code, "fields": list(fields.keys())}
        )

    def create_crud(
        self,
        model: str,
        prefix: str = ""
    ) -> ActionResult:
        """Generate CRUD endpoints for a model

        Args:
            model: Model name
            prefix: URL prefix

        Returns:
            ActionResult with generated code
        """
        model_lower = model.lower()
        prefix = prefix or f"/{model_lower}s"

        code = self._generate_crud_router(model, prefix)

        return ActionResult.ok(
            message=f"Generated CRUD router for '{model}'",
            data={
                "code": code,
                "endpoints": [
                    f"GET {prefix}",
                    f"POST {prefix}",
                    f"GET {prefix}/{{id}}",
                    f"PUT {prefix}/{{id}}",
                    f"DELETE {prefix}/{{id}}"
                ]
            }
        )

    def create_router(
        self,
        name: str,
        prefix: str = ""
    ) -> ActionResult:
        """Generate a new router module

        Args:
            name: Router name
            prefix: URL prefix

        Returns:
            ActionResult with generated code
        """
        prefix = prefix or f"/{name}"

        code = f'''"""
{name.title()} Router
"""
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="{prefix}", tags=["{name}"])


@router.get("/")
async def list_{name}():
    """List all {name}"""
    return {{"message": "List {name}"}}


@router.get("/{{item_id}}")
async def get_{name}(item_id: int):
    """Get a single {name}"""
    return {{"id": item_id}}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_{name}():
    """Create a new {name}"""
    return {{"message": "Created"}}


@router.put("/{{item_id}}")
async def update_{name}(item_id: int):
    """Update a {name}"""
    return {{"id": item_id, "updated": True}}


@router.delete("/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{name}(item_id: int):
    """Delete a {name}"""
    return None
'''

        return ActionResult.ok(
            message=f"Generated router '{name}'",
            data={"code": code, "prefix": prefix}
        )

    def analyze_project(self) -> ActionResult:
        """Analyze existing FastAPI project structure

        Returns:
            ActionResult with project analysis
        """
        # Look for FastAPI indicators
        app_dir = self._project_path / "app"
        main_file = self._project_path / "main.py"
        app_main = app_dir / "main.py" if app_dir.exists() else None

        if not (main_file.exists() or (app_main and app_main.exists())):
            return ActionResult.fail("No FastAPI project found in current directory")

        analysis = {
            "project_path": str(self._project_path),
            "structure": [],
            "routers": [],
            "models": [],
            "endpoints": []
        }

        # Scan for Python files
        for py_file in self._project_path.rglob("*.py"):
            rel_path = py_file.relative_to(self._project_path)
            analysis["structure"].append(str(rel_path))

            # Check for routers
            content = py_file.read_text()
            if "APIRouter" in content:
                analysis["routers"].append(str(rel_path))

            # Check for models
            if "BaseModel" in content and "pydantic" in content.lower():
                analysis["models"].append(str(rel_path))

            # Find endpoints
            for match in re.finditer(r'@\w+\.(get|post|put|delete|patch)\(["\']([^"\']+)', content):
                analysis["endpoints"].append({
                    "file": str(rel_path),
                    "method": match.group(1).upper(),
                    "path": match.group(2)
                })

        return ActionResult.ok(
            message=f"Analyzed project with {len(analysis['endpoints'])} endpoints",
            data=analysis
        )

    # Code generation helpers

    def _generate_main(self, name: str, with_db: bool, with_auth: bool) -> str:
        """Generate main.py content"""
        imports = ['from fastapi import FastAPI', 'from fastapi.middleware.cors import CORSMiddleware']

        if with_db:
            imports.append('from app.db.database import engine, Base')

        code = '\n'.join(imports) + '\n'
        code += f'''from app.api.v1 import health

app = FastAPI(
    title="{name.replace('_', ' ').title()} API",
    description="API built with FastAPI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1")
'''

        if with_db:
            code += '''

# Create database tables
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
'''

        code += '''

@app.get("/")
async def root():
    return {"message": "Welcome to the API", "docs": "/docs"}
'''
        return code

    def _generate_config(self, name: str, with_db: bool) -> str:
        """Generate config.py content"""
        code = '''"""
Application configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    app_name: str = "''' + name + '''"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
'''
        if with_db:
            code += '''    database_url: str = "sqlite:///./app.db"
'''
        code += '''
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
'''
        return code

    def _generate_requirements(self, with_db: bool, with_auth: bool) -> str:
        """Generate requirements.txt"""
        reqs = [
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.23.0",
            "pydantic>=2.0.0",
            "pydantic-settings>=2.0.0",
            "python-dotenv>=1.0.0",
        ]

        if with_db:
            reqs.extend([
                "sqlalchemy>=2.0.0",
                "alembic>=1.12.0",
            ])

        if with_auth:
            reqs.extend([
                "python-jose[cryptography]>=3.3.0",
                "passlib[bcrypt]>=1.7.0",
                "python-multipart>=0.0.6",
            ])

        reqs.append("pytest>=7.0.0")
        reqs.append("httpx>=0.24.0")

        return '\n'.join(reqs) + '\n'

    def _generate_env_example(self, name: str, with_db: bool) -> str:
        """Generate .env.example"""
        content = f'''# {name} Environment Variables
DEBUG=true
'''
        if with_db:
            content += 'DATABASE_URL=sqlite:///./app.db\n'
        return content

    def _generate_example_router(self) -> str:
        """Generate example health router"""
        return '''"""
Health check router
"""
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {"status": "ready"}
'''

    def _generate_api_init(self) -> str:
        """Generate API __init__.py"""
        return '''"""
API v1 routers
"""
from . import health

__all__ = ["health"]
'''

    def _generate_db_setup(self) -> str:
        """Generate database setup"""
        return '''"""
Database configuration
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # SQLite only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

    def _generate_base_model(self) -> str:
        """Generate base SQLAlchemy model"""
        return '''"""
Base model with common fields
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from app.db.database import Base


class BaseModel(Base):
    """Abstract base model with common fields"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
'''

    def _generate_auth_module(self) -> str:
        """Generate authentication module"""
        return '''"""
Authentication utilities
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"username": username}
'''

    def _path_to_function_name(self, path: str, method: str) -> str:
        """Convert URL path to function name"""
        # Remove path parameters
        clean_path = re.sub(r'\{[^}]+\}', '', path)
        # Convert to snake_case
        name = clean_path.strip('/').replace('/', '_').replace('-', '_')
        prefix = method.lower()
        return f"{prefix}_{name}" if name else prefix

    def _generate_endpoint_code(
        self,
        path: str,
        method: str,
        name: str,
        path_params: List[str]
    ) -> str:
        """Generate endpoint code"""
        decorator = f'@router.{method.lower()}("{path}")'

        # Build function signature
        params = [f"{p}: int" for p in path_params]  # Default to int
        params_str = ", ".join(params) if params else ""

        if method in ["POST", "PUT", "PATCH"]:
            # Add request body parameter
            if params_str:
                params_str += ", "
            params_str += "data: dict"

        code = f'''{decorator}
async def {name}({params_str}):
    """
    {method} {path}
    """
'''
        if method == "GET":
            if path_params:
                code += f'    return {{"id": {path_params[0]}}}\n'
            else:
                code += '    return {"message": "OK"}\n'
        elif method == "POST":
            code += '    return {"message": "Created", "data": data}\n'
        elif method in ["PUT", "PATCH"]:
            code += f'    return {{"id": {path_params[0] if path_params else "1"}, "updated": True}}\n'
        elif method == "DELETE":
            code += '    return None\n'

        return code

    def _generate_pydantic_model(self, name: str, fields: Dict[str, str]) -> str:
        """Generate Pydantic model code"""
        code = f'''from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class {name}Base(BaseModel):
    """Base {name} schema"""
'''
        for field_name, field_type in fields.items():
            code += f'    {field_name}: {field_type}\n'

        code += f'''

class {name}Create({name}Base):
    """Schema for creating {name}"""
    pass


class {name}Update(BaseModel):
    """Schema for updating {name}"""
'''
        for field_name, field_type in fields.items():
            code += f'    {field_name}: Optional[{field_type}] = None\n'

        code += f'''

class {name}({name}Base):
    """Full {name} schema with ID"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
'''
        return code

    def _generate_crud_router(self, model: str, prefix: str) -> str:
        """Generate CRUD router code"""
        model_lower = model.lower()

        return f'''"""
{model} CRUD Router
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
# from app.models.{model_lower} import {model}
# from app.schemas.{model_lower} import {model}Create, {model}Update, {model} as {model}Schema

router = APIRouter(prefix="{prefix}", tags=["{model_lower}s"])


@router.get("/")
async def list_{model_lower}s(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all {model_lower}s"""
    # items = db.query({model}).offset(skip).limit(limit).all()
    return {{"items": [], "total": 0}}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_{model_lower}(data: dict, db: Session = Depends(get_db)):
    """Create a new {model_lower}"""
    # db_item = {model}(**data)
    # db.add(db_item)
    # db.commit()
    # db.refresh(db_item)
    return {{"message": "Created", "data": data}}


@router.get("/{{item_id}}")
async def get_{model_lower}(item_id: int, db: Session = Depends(get_db)):
    """Get a {model_lower} by ID"""
    # item = db.query({model}).filter({model}.id == item_id).first()
    # if not item:
    #     raise HTTPException(status_code=404, detail="{model} not found")
    return {{"id": item_id}}


@router.put("/{{item_id}}")
async def update_{model_lower}(item_id: int, data: dict, db: Session = Depends(get_db)):
    """Update a {model_lower}"""
    # item = db.query({model}).filter({model}.id == item_id).first()
    # if not item:
    #     raise HTTPException(status_code=404, detail="{model} not found")
    return {{"id": item_id, "updated": True}}


@router.delete("/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{model_lower}(item_id: int, db: Session = Depends(get_db)):
    """Delete a {model_lower}"""
    # item = db.query({model}).filter({model}.id == item_id).first()
    # if not item:
    #     raise HTTPException(status_code=404, detail="{model} not found")
    # db.delete(item)
    # db.commit()
    return None
'''

    def can_handle(self, request: str) -> float:
        """Check if request is FastAPI-related"""
        request_lower = request.lower()

        # High confidence
        high_conf = ["fastapi", "pydantic", "uvicorn", "api endpoint"]
        for kw in high_conf:
            if kw in request_lower:
                return 0.9

        # Medium confidence
        med_conf = ["rest api", "endpoint", "router", "crud", "schema"]
        for kw in med_conf:
            if kw in request_lower:
                return 0.6

        return super().can_handle(request)

    def handle_request(self, request: str, **kwargs) -> Optional[ActionResult]:
        """Handle a natural language request"""
        request_lower = request.lower()

        if "scaffold" in request_lower or "new project" in request_lower:
            # Extract project name
            words = request.split()
            name = "my_api"
            for i, word in enumerate(words):
                if word.lower() in ["project", "called", "named"]:
                    if i + 1 < len(words):
                        name = words[i + 1].strip("'\"")
                        break
            return self.scaffold_project(name=name)

        if "analyze" in request_lower:
            return self.analyze_project()

        return None
