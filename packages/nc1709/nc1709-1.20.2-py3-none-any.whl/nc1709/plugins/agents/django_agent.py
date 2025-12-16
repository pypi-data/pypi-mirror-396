"""
Django Agent for NC1709
Scaffolds Django projects, apps, models, views, and more
"""
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

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


class DjangoAgent(Plugin):
    """
    Django scaffolding and development agent.

    Provides:
    - Project scaffolding
    - App generation
    - Model generation
    - View generation (function and class-based)
    - URL configuration
    - Admin registration
    - Serializer generation (DRF)
    """

    METADATA = PluginMetadata(
        name="django",
        version="1.0.0",
        description="Django project scaffolding and development",
        author="NC1709 Team",
        capabilities=[
            PluginCapability.CODE_GENERATION,
            PluginCapability.PROJECT_SCAFFOLDING
        ],
        keywords=[
            "django", "python", "model", "view", "template",
            "admin", "orm", "rest", "drf", "serializer",
            "migration", "backend", "web"
        ],
        config_schema={
            "project_path": {"type": "string", "default": "."},
            "use_drf": {"type": "boolean", "default": True},
            "database": {"type": "string", "enum": ["sqlite", "postgresql", "mysql"], "default": "sqlite"}
        }
    )

    @property
    def metadata(self) -> PluginMetadata:
        return self.METADATA

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._project_path: Optional[Path] = None

    def initialize(self) -> bool:
        """Initialize the Django agent"""
        self._project_path = Path(self._config.get("project_path", ".")).resolve()
        return True

    def cleanup(self) -> None:
        """Cleanup resources"""
        pass

    def _register_actions(self) -> None:
        """Register Django actions"""
        self.register_action(
            "scaffold",
            self.scaffold_project,
            "Create a new Django project structure",
            parameters={
                "name": {"type": "string", "required": True},
                "with_drf": {"type": "boolean", "default": True}
            }
        )

        self.register_action(
            "app",
            self.create_app,
            "Generate a new Django app",
            parameters={
                "name": {"type": "string", "required": True}
            }
        )

        self.register_action(
            "model",
            self.create_model,
            "Generate a Django model",
            parameters={
                "app": {"type": "string", "required": True},
                "name": {"type": "string", "required": True},
                "fields": {"type": "object", "required": True}
            }
        )

        self.register_action(
            "view",
            self.create_view,
            "Generate a Django view",
            parameters={
                "app": {"type": "string", "required": True},
                "name": {"type": "string", "required": True},
                "view_type": {"type": "string", "enum": ["function", "class", "viewset"], "default": "class"}
            }
        )

        self.register_action(
            "serializer",
            self.create_serializer,
            "Generate a DRF serializer",
            parameters={
                "app": {"type": "string", "required": True},
                "model": {"type": "string", "required": True}
            }
        )

        self.register_action(
            "analyze",
            self.analyze_project,
            "Analyze existing Django project structure"
        )

    def scaffold_project(
        self,
        name: str,
        with_drf: bool = True
    ) -> ActionResult:
        """Create a new Django project structure

        Args:
            name: Project name
            with_drf: Include Django REST Framework

        Returns:
            ActionResult
        """
        project_dir = self._project_path / name

        if project_dir.exists():
            return ActionResult.fail(f"Directory '{name}' already exists")

        try:
            # Create directory structure
            config_dir = project_dir / name  # Django puts config in project_name/project_name
            dirs = [
                project_dir,
                config_dir,
                project_dir / "apps",
                project_dir / "templates",
                project_dir / "static",
                project_dir / "media",
            ]

            for d in dirs:
                d.mkdir(parents=True, exist_ok=True)

            # Create __init__.py files
            (config_dir / "__init__.py").write_text("")
            (project_dir / "apps" / "__init__.py").write_text("")

            # Create manage.py
            manage_content = self._generate_manage_py(name)
            (project_dir / "manage.py").write_text(manage_content)

            # Create settings.py
            settings_content = self._generate_settings(name, with_drf)
            (config_dir / "settings.py").write_text(settings_content)

            # Create urls.py
            urls_content = self._generate_urls(name, with_drf)
            (config_dir / "urls.py").write_text(urls_content)

            # Create wsgi.py
            wsgi_content = self._generate_wsgi(name)
            (config_dir / "wsgi.py").write_text(wsgi_content)

            # Create asgi.py
            asgi_content = self._generate_asgi(name)
            (config_dir / "asgi.py").write_text(asgi_content)

            # Create requirements.txt
            requirements = self._generate_requirements(with_drf)
            (project_dir / "requirements.txt").write_text(requirements)

            # Create .env.example
            env_content = self._generate_env_example(name)
            (project_dir / ".env.example").write_text(env_content)

            # Create .gitignore
            gitignore = self._generate_gitignore()
            (project_dir / ".gitignore").write_text(gitignore)

            files_created = len(list(project_dir.rglob("*")))

            return ActionResult.ok(
                message=f"Created Django project '{name}' with {files_created} files",
                data={
                    "project_path": str(project_dir),
                    "with_drf": with_drf,
                    "next_steps": [
                        f"cd {name}",
                        "python -m venv venv",
                        "source venv/bin/activate",
                        "pip install -r requirements.txt",
                        "python manage.py migrate",
                        "python manage.py runserver"
                    ]
                }
            )

        except Exception as e:
            return ActionResult.fail(str(e))

    def create_app(self, name: str) -> ActionResult:
        """Generate a new Django app

        Args:
            name: App name

        Returns:
            ActionResult with generated structure
        """
        app_dir = self._project_path / "apps" / name

        if app_dir.exists():
            return ActionResult.fail(f"App '{name}' already exists")

        try:
            # Create app directory
            app_dir.mkdir(parents=True, exist_ok=True)
            (app_dir / "migrations").mkdir()

            # Create __init__.py files
            (app_dir / "__init__.py").write_text("")
            (app_dir / "migrations" / "__init__.py").write_text("")

            # Create models.py
            models_content = self._generate_models_py()
            (app_dir / "models.py").write_text(models_content)

            # Create views.py
            views_content = self._generate_views_py()
            (app_dir / "views.py").write_text(views_content)

            # Create urls.py
            urls_content = self._generate_app_urls(name)
            (app_dir / "urls.py").write_text(urls_content)

            # Create admin.py
            admin_content = self._generate_admin_py()
            (app_dir / "admin.py").write_text(admin_content)

            # Create apps.py
            apps_content = self._generate_apps_py(name)
            (app_dir / "apps.py").write_text(apps_content)

            # Create serializers.py (for DRF)
            serializers_content = self._generate_serializers_py()
            (app_dir / "serializers.py").write_text(serializers_content)

            # Create tests.py
            tests_content = self._generate_tests_py(name)
            (app_dir / "tests.py").write_text(tests_content)

            return ActionResult.ok(
                message=f"Created Django app '{name}'",
                data={
                    "app_path": str(app_dir),
                    "files": [
                        "models.py",
                        "views.py",
                        "urls.py",
                        "admin.py",
                        "serializers.py",
                        "tests.py"
                    ],
                    "note": f"Add 'apps.{name}' to INSTALLED_APPS in settings.py"
                }
            )

        except Exception as e:
            return ActionResult.fail(str(e))

    def create_model(
        self,
        app: str,
        name: str,
        fields: Dict[str, str]
    ) -> ActionResult:
        """Generate a Django model

        Args:
            app: App name
            name: Model name
            fields: Dict of field_name -> field_type

        Returns:
            ActionResult with generated code
        """
        code = self._generate_model_code(name, fields)

        return ActionResult.ok(
            message=f"Generated model '{name}' for app '{app}'",
            data={
                "code": code,
                "path": f"apps/{app}/models.py",
                "migrations_note": "Run: python manage.py makemigrations && python manage.py migrate"
            }
        )

    def create_view(
        self,
        app: str,
        name: str,
        view_type: str = "class"
    ) -> ActionResult:
        """Generate a Django view

        Args:
            app: App name
            name: View name
            view_type: Type of view (function, class, viewset)

        Returns:
            ActionResult with generated code
        """
        if view_type == "function":
            code = self._generate_function_view(name)
        elif view_type == "viewset":
            code = self._generate_viewset(name)
        else:
            code = self._generate_class_view(name)

        return ActionResult.ok(
            message=f"Generated {view_type} view '{name}'",
            data={
                "code": code,
                "path": f"apps/{app}/views.py",
                "type": view_type
            }
        )

    def create_serializer(
        self,
        app: str,
        model: str
    ) -> ActionResult:
        """Generate a DRF serializer

        Args:
            app: App name
            model: Model name

        Returns:
            ActionResult with generated code
        """
        code = self._generate_serializer_code(model)

        return ActionResult.ok(
            message=f"Generated serializer for '{model}'",
            data={
                "code": code,
                "path": f"apps/{app}/serializers.py"
            }
        )

    def analyze_project(self) -> ActionResult:
        """Analyze existing Django project structure

        Returns:
            ActionResult with project analysis
        """
        manage_py = self._project_path / "manage.py"

        if not manage_py.exists():
            return ActionResult.fail("No Django project found (manage.py not found)")

        analysis = {
            "project_path": str(self._project_path),
            "apps": [],
            "models": [],
            "views": [],
            "urls": []
        }

        # Find apps
        for apps_dir in [self._project_path / "apps", self._project_path]:
            if apps_dir.exists():
                for item in apps_dir.iterdir():
                    if item.is_dir() and (item / "models.py").exists():
                        app_name = item.name
                        analysis["apps"].append(app_name)

                        # Find models in this app
                        models_file = item / "models.py"
                        if models_file.exists():
                            content = models_file.read_text()
                            for match in re.finditer(r'class\s+(\w+)\s*\([^)]*Model[^)]*\)', content):
                                analysis["models"].append({
                                    "app": app_name,
                                    "name": match.group(1)
                                })

                        # Find views
                        views_file = item / "views.py"
                        if views_file.exists():
                            content = views_file.read_text()
                            for match in re.finditer(r'(?:def|class)\s+(\w+)', content):
                                analysis["views"].append({
                                    "app": app_name,
                                    "name": match.group(1)
                                })

        return ActionResult.ok(
            message=f"Analyzed Django project with {len(analysis['apps'])} apps",
            data=analysis
        )

    # Code generation helpers

    def _generate_manage_py(self, name: str) -> str:
        """Generate manage.py"""
        return f'''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{name}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
'''

    def _generate_settings(self, name: str, with_drf: bool) -> str:
        """Generate settings.py"""
        drf_apps = "'rest_framework'," if with_drf else ""
        drf_settings = '''
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
''' if with_drf else ""

        return f'''"""
Django settings for {name} project.
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    {drf_apps}
    # Add your apps here
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{name}.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = '{name}.wsgi.application'

# Database
DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
{drf_settings}
'''

    def _generate_urls(self, name: str, with_drf: bool) -> str:
        """Generate urls.py"""
        drf_imports = "from rest_framework import routers" if with_drf else ""
        drf_urls = '''
router = routers.DefaultRouter()
# Register your viewsets here
# router.register(r'items', ItemViewSet)
''' if with_drf else ""
        drf_include = "path('api/', include(router.urls))," if with_drf else ""

        return f'''"""
URL configuration for {name} project.
"""
from django.contrib import admin
from django.urls import path, include
{drf_imports}
{drf_urls}
urlpatterns = [
    path('admin/', admin.site.urls),
    {drf_include}
]
'''

    def _generate_wsgi(self, name: str) -> str:
        """Generate wsgi.py"""
        return f'''"""
WSGI config for {name} project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{name}.settings')
application = get_wsgi_application()
'''

    def _generate_asgi(self, name: str) -> str:
        """Generate asgi.py"""
        return f'''"""
ASGI config for {name} project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{name}.settings')
application = get_asgi_application()
'''

    def _generate_requirements(self, with_drf: bool) -> str:
        """Generate requirements.txt"""
        reqs = [
            "Django>=4.2",
            "python-dotenv>=1.0.0",
            "gunicorn>=21.0.0",
        ]
        if with_drf:
            reqs.append("djangorestframework>=3.14.0")

        reqs.extend([
            "pytest>=7.0.0",
            "pytest-django>=4.5.0",
        ])

        return '\n'.join(reqs) + '\n'

    def _generate_env_example(self, name: str) -> str:
        """Generate .env.example"""
        return f'''# {name} Environment Variables
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
'''

    def _generate_gitignore(self) -> str:
        """Generate .gitignore"""
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
ENV/

# Django
*.log
local_settings.py
db.sqlite3
*.pot
*.pyc
staticfiles/
media/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment
.env
.env.local

# Testing
.coverage
htmlcov/
.pytest_cache/
'''

    def _generate_models_py(self) -> str:
        """Generate models.py"""
        return '''"""
Models for this app.
"""
from django.db import models


# Create your models here.
class BaseModel(models.Model):
    """Abstract base model with common fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
'''

    def _generate_views_py(self) -> str:
        """Generate views.py"""
        return '''"""
Views for this app.
"""
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView


# Create your views here.
'''

    def _generate_app_urls(self, name: str) -> str:
        """Generate app urls.py"""
        return f'''"""
URL patterns for {name} app.
"""
from django.urls import path
from . import views

app_name = '{name}'

urlpatterns = [
    # Add your URL patterns here
]
'''

    def _generate_admin_py(self) -> str:
        """Generate admin.py"""
        return '''"""
Admin configuration for this app.
"""
from django.contrib import admin

# Register your models here.
'''

    def _generate_apps_py(self, name: str) -> str:
        """Generate apps.py"""
        return f'''"""
App configuration.
"""
from django.apps import AppConfig


class {name.title().replace("_", "")}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{name}'
'''

    def _generate_serializers_py(self) -> str:
        """Generate serializers.py"""
        return '''"""
DRF Serializers for this app.
"""
from rest_framework import serializers

# Create your serializers here.
'''

    def _generate_tests_py(self, name: str) -> str:
        """Generate tests.py"""
        return f'''"""
Tests for {name} app.
"""
from django.test import TestCase


class {name.title().replace("_", "")}Tests(TestCase):
    """Tests for {name} app."""

    def test_placeholder(self):
        """Placeholder test."""
        self.assertTrue(True)
'''

    def _generate_model_code(self, name: str, fields: Dict[str, str]) -> str:
        """Generate model code"""
        field_mappings = {
            "str": "CharField(max_length=255)",
            "string": "CharField(max_length=255)",
            "text": "TextField()",
            "int": "IntegerField()",
            "integer": "IntegerField()",
            "float": "FloatField()",
            "decimal": "DecimalField(max_digits=10, decimal_places=2)",
            "bool": "BooleanField(default=False)",
            "boolean": "BooleanField(default=False)",
            "date": "DateField()",
            "datetime": "DateTimeField()",
            "email": "EmailField()",
            "url": "URLField()",
            "file": "FileField(upload_to='files/')",
            "image": "ImageField(upload_to='images/')",
        }

        code = f'''class {name}(BaseModel):
    """{name} model."""
'''
        for field_name, field_type in fields.items():
            django_field = field_mappings.get(field_type.lower(), f"CharField(max_length=255)  # {field_type}")
            code += f'    {field_name} = models.{django_field}\n'

        code += f'''
    class Meta:
        ordering = ['-created_at']
        verbose_name = '{name}'
        verbose_name_plural = '{name}s'

    def __str__(self):
        return f"{name} {{self.id}}"
'''
        return code

    def _generate_function_view(self, name: str) -> str:
        """Generate function-based view"""
        return f'''def {name.lower()}_view(request):
    """{name} view."""
    context = {{}}
    return render(request, '{name.lower()}.html', context)
'''

    def _generate_class_view(self, name: str) -> str:
        """Generate class-based view"""
        return f'''class {name}View(ListView):
    """{name} list view."""
    # model = {name}
    template_name = '{name.lower()}_list.html'
    context_object_name = 'items'
    paginate_by = 10


class {name}DetailView(DetailView):
    """{name} detail view."""
    # model = {name}
    template_name = '{name.lower()}_detail.html'
    context_object_name = 'item'


class {name}CreateView(CreateView):
    """{name} create view."""
    # model = {name}
    # fields = ['field1', 'field2']
    template_name = '{name.lower()}_form.html'
    success_url = '/'
'''

    def _generate_viewset(self, name: str) -> str:
        """Generate DRF ViewSet"""
        return f'''from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
# from .models import {name}
# from .serializers import {name}Serializer


class {name}ViewSet(viewsets.ModelViewSet):
    """{name} API ViewSet."""
    # queryset = {name}.objects.all()
    # serializer_class = {name}Serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset based on user."""
        return super().get_queryset()
'''

    def _generate_serializer_code(self, model: str) -> str:
        """Generate serializer code"""
        return f'''from rest_framework import serializers
# from .models import {model}


class {model}Serializer(serializers.ModelSerializer):
    """{model} serializer."""

    class Meta:
        # model = {model}
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class {model}CreateSerializer(serializers.ModelSerializer):
    """Serializer for creating {model}."""

    class Meta:
        # model = {model}
        exclude = ['id', 'created_at', 'updated_at']
'''

    def can_handle(self, request: str) -> float:
        """Check if request is Django-related"""
        request_lower = request.lower()

        high_conf = ["django", "drf", "django rest", "manage.py"]
        for kw in high_conf:
            if kw in request_lower:
                return 0.9

        med_conf = ["model", "view", "serializer", "migration", "admin"]
        for kw in med_conf:
            if kw in request_lower:
                return 0.5

        return super().can_handle(request)

    def handle_request(self, request: str, **kwargs) -> Optional[ActionResult]:
        """Handle a natural language request"""
        request_lower = request.lower()

        if "scaffold" in request_lower or "new project" in request_lower:
            words = request.split()
            name = "myproject"
            for i, word in enumerate(words):
                if word.lower() in ["project", "called", "named"]:
                    if i + 1 < len(words):
                        name = words[i + 1].strip("'\"")
                        break
            return self.scaffold_project(name=name)

        if "analyze" in request_lower:
            return self.analyze_project()

        return None
