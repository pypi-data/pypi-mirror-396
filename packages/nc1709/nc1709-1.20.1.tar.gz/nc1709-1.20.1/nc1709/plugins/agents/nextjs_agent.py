"""
Next.js Agent for NC1709
Scaffolds Next.js projects, pages, components, and API routes
"""
import os
import json
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


class NextJSAgent(Plugin):
    """
    Next.js scaffolding and development agent.

    Provides:
    - Project scaffolding (App Router or Pages Router)
    - Page generation
    - Component generation (with TypeScript support)
    - API route generation
    - Layout generation
    - Middleware setup
    """

    METADATA = PluginMetadata(
        name="nextjs",
        version="1.0.0",
        description="Next.js project scaffolding and development",
        author="NC1709 Team",
        capabilities=[
            PluginCapability.CODE_GENERATION,
            PluginCapability.PROJECT_SCAFFOLDING
        ],
        keywords=[
            "nextjs", "next", "react", "typescript", "javascript",
            "component", "page", "api", "route", "layout",
            "middleware", "frontend", "ssr", "ssg"
        ],
        config_schema={
            "project_path": {"type": "string", "default": "."},
            "use_typescript": {"type": "boolean", "default": True},
            "use_app_router": {"type": "boolean", "default": True},
            "styling": {"type": "string", "enum": ["tailwind", "css-modules", "styled-components"], "default": "tailwind"}
        }
    )

    @property
    def metadata(self) -> PluginMetadata:
        return self.METADATA

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._project_path: Optional[Path] = None

    def initialize(self) -> bool:
        """Initialize the Next.js agent"""
        self._project_path = Path(self._config.get("project_path", ".")).resolve()
        return True

    def cleanup(self) -> None:
        """Cleanup resources"""
        pass

    def _register_actions(self) -> None:
        """Register Next.js actions"""
        self.register_action(
            "scaffold",
            self.scaffold_project,
            "Create a new Next.js project structure",
            parameters={
                "name": {"type": "string", "required": True},
                "typescript": {"type": "boolean", "default": True},
                "tailwind": {"type": "boolean", "default": True}
            }
        )

        self.register_action(
            "page",
            self.create_page,
            "Generate a new page",
            parameters={
                "path": {"type": "string", "required": True},
                "name": {"type": "string", "required": True}
            }
        )

        self.register_action(
            "component",
            self.create_component,
            "Generate a React component",
            parameters={
                "name": {"type": "string", "required": True},
                "props": {"type": "object", "default": {}},
                "client": {"type": "boolean", "default": False}
            }
        )

        self.register_action(
            "api",
            self.create_api_route,
            "Generate an API route",
            parameters={
                "path": {"type": "string", "required": True},
                "methods": {"type": "array", "default": ["GET"]}
            }
        )

        self.register_action(
            "layout",
            self.create_layout,
            "Generate a layout component",
            parameters={
                "path": {"type": "string", "default": ""},
                "name": {"type": "string", "default": "Layout"}
            }
        )

        self.register_action(
            "analyze",
            self.analyze_project,
            "Analyze existing Next.js project structure"
        )

    def scaffold_project(
        self,
        name: str,
        typescript: bool = True,
        tailwind: bool = True
    ) -> ActionResult:
        """Create a new Next.js project structure

        Args:
            name: Project name
            typescript: Use TypeScript
            tailwind: Include Tailwind CSS

        Returns:
            ActionResult
        """
        project_dir = self._project_path / name
        ext = "tsx" if typescript else "jsx"
        style_ext = "module.css"

        if project_dir.exists():
            return ActionResult.fail(f"Directory '{name}' already exists")

        try:
            # Create directory structure (App Router)
            dirs = [
                project_dir,
                project_dir / "app",
                project_dir / "app" / "api",
                project_dir / "components",
                project_dir / "lib",
                project_dir / "public",
                project_dir / "styles",
            ]

            for d in dirs:
                d.mkdir(parents=True, exist_ok=True)

            # Create package.json
            package_json = self._generate_package_json(name, typescript, tailwind)
            (project_dir / "package.json").write_text(json.dumps(package_json, indent=2))

            # Create root layout
            layout_content = self._generate_root_layout(typescript, tailwind)
            (project_dir / "app" / f"layout.{ext}").write_text(layout_content)

            # Create home page
            page_content = self._generate_home_page(typescript)
            (project_dir / "app" / f"page.{ext}").write_text(page_content)

            # Create global styles
            if tailwind:
                globals_css = self._generate_tailwind_globals()
                (project_dir / "app" / "globals.css").write_text(globals_css)

                # Create tailwind config
                tailwind_config = self._generate_tailwind_config(typescript)
                config_ext = "ts" if typescript else "js"
                (project_dir / f"tailwind.config.{config_ext}").write_text(tailwind_config)

                # Create postcss config
                postcss_config = self._generate_postcss_config()
                (project_dir / "postcss.config.js").write_text(postcss_config)
            else:
                globals_css = self._generate_basic_globals()
                (project_dir / "app" / "globals.css").write_text(globals_css)

            # Create next.config
            next_config = self._generate_next_config(typescript)
            config_ext = "mjs"
            (project_dir / f"next.config.{config_ext}").write_text(next_config)

            if typescript:
                # Create tsconfig
                tsconfig = self._generate_tsconfig()
                (project_dir / "tsconfig.json").write_text(json.dumps(tsconfig, indent=2))

            # Create example component
            component_content = self._generate_example_component(typescript)
            (project_dir / "components" / f"Button.{ext}").write_text(component_content)

            # Create example API route
            api_content = self._generate_example_api(typescript)
            api_dir = project_dir / "app" / "api" / "hello"
            api_dir.mkdir(exist_ok=True)
            (api_dir / f"route.{ext[:2]}").write_text(api_content)

            # Create .gitignore
            gitignore = self._generate_gitignore()
            (project_dir / ".gitignore").write_text(gitignore)

            # Create README
            readme = self._generate_readme(name)
            (project_dir / "README.md").write_text(readme)

            files_created = len(list(project_dir.rglob("*")))

            return ActionResult.ok(
                message=f"Created Next.js project '{name}' with {files_created} files",
                data={
                    "project_path": str(project_dir),
                    "typescript": typescript,
                    "tailwind": tailwind,
                    "next_steps": [
                        f"cd {name}",
                        "npm install",
                        "npm run dev"
                    ]
                }
            )

        except Exception as e:
            return ActionResult.fail(str(e))

    def create_page(
        self,
        path: str,
        name: str
    ) -> ActionResult:
        """Generate a new page

        Args:
            path: Page path (e.g., "dashboard" or "users/[id]")
            name: Page component name

        Returns:
            ActionResult with generated code
        """
        use_ts = self._config.get("use_typescript", True)
        ext = "tsx" if use_ts else "jsx"

        # Detect dynamic segments
        is_dynamic = "[" in path

        code = self._generate_page_code(name, path, is_dynamic, use_ts)

        return ActionResult.ok(
            message=f"Generated page at app/{path}/page.{ext}",
            data={
                "code": code,
                "path": f"app/{path}/page.{ext}",
                "dynamic": is_dynamic
            }
        )

    def create_component(
        self,
        name: str,
        props: Dict[str, str] = None,
        client: bool = False
    ) -> ActionResult:
        """Generate a React component

        Args:
            name: Component name
            props: Props definition
            client: Whether it's a client component

        Returns:
            ActionResult with generated code
        """
        props = props or {}
        use_ts = self._config.get("use_typescript", True)
        ext = "tsx" if use_ts else "jsx"

        code = self._generate_component_code(name, props, client, use_ts)

        return ActionResult.ok(
            message=f"Generated component '{name}'",
            data={
                "code": code,
                "path": f"components/{name}.{ext}",
                "client": client
            }
        )

    def create_api_route(
        self,
        path: str,
        methods: List[str] = None
    ) -> ActionResult:
        """Generate an API route

        Args:
            path: Route path
            methods: HTTP methods to handle

        Returns:
            ActionResult with generated code
        """
        methods = methods or ["GET"]
        use_ts = self._config.get("use_typescript", True)
        ext = "ts" if use_ts else "js"

        code = self._generate_api_route_code(path, methods, use_ts)

        return ActionResult.ok(
            message=f"Generated API route at app/api/{path}/route.{ext}",
            data={
                "code": code,
                "path": f"app/api/{path}/route.{ext}",
                "methods": methods
            }
        )

    def create_layout(
        self,
        path: str = "",
        name: str = "Layout"
    ) -> ActionResult:
        """Generate a layout component

        Args:
            path: Layout path
            name: Layout name

        Returns:
            ActionResult with generated code
        """
        use_ts = self._config.get("use_typescript", True)
        ext = "tsx" if use_ts else "jsx"

        code = self._generate_layout_code(name, use_ts)

        layout_path = f"app/{path}/layout.{ext}" if path else f"app/layout.{ext}"

        return ActionResult.ok(
            message=f"Generated layout at {layout_path}",
            data={
                "code": code,
                "path": layout_path
            }
        )

    def analyze_project(self) -> ActionResult:
        """Analyze existing Next.js project structure

        Returns:
            ActionResult with project analysis
        """
        # Look for Next.js indicators
        package_json = self._project_path / "package.json"

        if not package_json.exists():
            return ActionResult.fail("No package.json found")

        try:
            pkg = json.loads(package_json.read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

            if "next" not in deps:
                return ActionResult.fail("Not a Next.js project (next not in dependencies)")
        except Exception:
            return ActionResult.fail("Could not parse package.json")

        analysis = {
            "project_path": str(self._project_path),
            "next_version": deps.get("next", "unknown"),
            "typescript": "typescript" in deps,
            "tailwind": "tailwindcss" in deps,
            "app_router": (self._project_path / "app").exists(),
            "pages_router": (self._project_path / "pages").exists(),
            "pages": [],
            "components": [],
            "api_routes": []
        }

        # Scan for pages
        app_dir = self._project_path / "app"
        if app_dir.exists():
            for page in app_dir.rglob("page.*"):
                rel_path = page.relative_to(app_dir)
                route = "/" + str(rel_path.parent).replace("\\", "/")
                if route == "/.":
                    route = "/"
                analysis["pages"].append(route)

            # Scan for API routes
            api_dir = app_dir / "api"
            if api_dir.exists():
                for route in api_dir.rglob("route.*"):
                    rel_path = route.relative_to(api_dir)
                    api_path = "/api/" + str(rel_path.parent).replace("\\", "/")
                    analysis["api_routes"].append(api_path)

        # Scan for components
        components_dir = self._project_path / "components"
        if components_dir.exists():
            for comp in components_dir.rglob("*.tsx"):
                analysis["components"].append(comp.stem)
            for comp in components_dir.rglob("*.jsx"):
                analysis["components"].append(comp.stem)

        return ActionResult.ok(
            message=f"Analyzed Next.js project with {len(analysis['pages'])} pages",
            data=analysis
        )

    # Code generation helpers

    def _generate_package_json(self, name: str, typescript: bool, tailwind: bool) -> dict:
        """Generate package.json"""
        pkg = {
            "name": name,
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "14.0.0",
                "react": "^18",
                "react-dom": "^18"
            },
            "devDependencies": {
                "eslint": "^8",
                "eslint-config-next": "14.0.0"
            }
        }

        if typescript:
            pkg["devDependencies"].update({
                "typescript": "^5",
                "@types/node": "^20",
                "@types/react": "^18",
                "@types/react-dom": "^18"
            })

        if tailwind:
            pkg["devDependencies"].update({
                "tailwindcss": "^3.3.0",
                "autoprefixer": "^10.0.1",
                "postcss": "^8"
            })

        return pkg

    def _generate_root_layout(self, typescript: bool, tailwind: bool) -> str:
        """Generate root layout"""
        props_type = ": { children: React.ReactNode }" if typescript else ""

        return f'''import type {{ Metadata }} from 'next'
import './globals.css'

export const metadata: Metadata = {{
  title: 'My App',
  description: 'Built with Next.js',
}}

export default function RootLayout({{
  children,
}}{props_type}) {{
  return (
    <html lang="en">
      <body{' className="antialiased"' if tailwind else ''}>{{children}}</body>
    </html>
  )
}}
'''

    def _generate_home_page(self, typescript: bool) -> str:
        """Generate home page"""
        return '''export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold">Welcome to Next.js</h1>
      <p className="mt-4 text-lg text-gray-600">
        Get started by editing app/page.tsx
      </p>
    </main>
  )
}
'''

    def _generate_tailwind_globals(self) -> str:
        """Generate Tailwind CSS globals"""
        return '''@tailwind base;
@tailwind components;
@tailwind utilities;
'''

    def _generate_basic_globals(self) -> str:
        """Generate basic CSS globals"""
        return '''* {
  box-sizing: border-box;
  padding: 0;
  margin: 0;
}

html,
body {
  max-width: 100vw;
  overflow-x: hidden;
}

a {
  color: inherit;
  text-decoration: none;
}
'''

    def _generate_tailwind_config(self, typescript: bool) -> str:
        """Generate Tailwind config"""
        if typescript:
            return '''import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
export default config
'''
        return '''/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
'''

    def _generate_postcss_config(self) -> str:
        """Generate PostCSS config"""
        return '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'''

    def _generate_next_config(self, typescript: bool) -> str:
        """Generate next.config"""
        return '''/** @type {import('next').NextConfig} */
const nextConfig = {}

export default nextConfig
'''

    def _generate_tsconfig(self) -> dict:
        """Generate tsconfig.json"""
        return {
            "compilerOptions": {
                "lib": ["dom", "dom.iterable", "esnext"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [{"name": "next"}],
                "paths": {"@/*": ["./*"]}
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }

    def _generate_example_component(self, typescript: bool) -> str:
        """Generate example component"""
        props_interface = '''
interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  variant?: 'primary' | 'secondary'
}
''' if typescript else ''

        props_type = ": ButtonProps" if typescript else ""

        return f'''"use client"
{props_interface}
export default function Button({{ children, onClick, variant = 'primary' }}{props_type}) {{
  const baseStyles = "px-4 py-2 rounded-lg font-medium transition-colors"
  const variants = {{
    primary: "bg-blue-500 text-white hover:bg-blue-600",
    secondary: "bg-gray-200 text-gray-800 hover:bg-gray-300"
  }}

  return (
    <button
      onClick={{onClick}}
      className={{`${{baseStyles}} ${{variants[variant]}}`}}
    >
      {{children}}
    </button>
  )
}}
'''

    def _generate_example_api(self, typescript: bool) -> str:
        """Generate example API route"""
        type_import = "import { NextRequest, NextResponse } from 'next/server'\n\n" if typescript else ""

        return f'''{type_import}export async function GET() {{
  return Response.json({{ message: 'Hello from API' }})
}}

export async function POST(request{': NextRequest' if typescript else ''}) {{
  const data = await request.json()
  return Response.json({{ received: data }})
}}
'''

    def _generate_gitignore(self) -> str:
        """Generate .gitignore"""
        return '''# dependencies
/node_modules
/.pnp
.pnp.js

# testing
/coverage

# next.js
/.next/
/out/

# production
/build

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# local env files
.env*.local

# typescript
*.tsbuildinfo
next-env.d.ts
'''

    def _generate_readme(self, name: str) -> str:
        """Generate README.md"""
        return f'''# {name}

This is a [Next.js](https://nextjs.org/) project.

## Getting Started

First, install dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

## Project Structure

```
├── app/
│   ├── layout.tsx    # Root layout
│   ├── page.tsx      # Home page
│   └── api/          # API routes
├── components/       # React components
├── lib/             # Utility functions
└── public/          # Static files
```

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Learn Next.js](https://nextjs.org/learn)
'''

    def _generate_page_code(self, name: str, path: str, is_dynamic: bool, typescript: bool) -> str:
        """Generate page code"""
        props = ""
        if is_dynamic and typescript:
            # Extract param name
            import re
            params = re.findall(r'\[(\w+)\]', path)
            if params:
                props = f"{{ params }}: {{ params: {{ {params[0]}: string }} }}"

        return f'''export default function {name}Page({props}) {{
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">{name}</h1>
      {f'<p>ID: {{params.{params[0]}}}</p>' if is_dynamic and 'params' in locals() else ''}
    </div>
  )
}}
'''

    def _generate_component_code(
        self,
        name: str,
        props: Dict[str, str],
        client: bool,
        typescript: bool
    ) -> str:
        """Generate component code"""
        use_client = '"use client"\n\n' if client else ''

        if typescript and props:
            interface = f"interface {name}Props {{\n"
            for prop_name, prop_type in props.items():
                interface += f"  {prop_name}: {prop_type}\n"
            interface += "}\n\n"
        else:
            interface = ""

        props_destructure = ", ".join(props.keys()) if props else ""
        props_type = f": {name}Props" if typescript and props else ""

        return f'''{use_client}{interface}export default function {name}({{ {props_destructure} }}{props_type}) {{
  return (
    <div>
      <h2>{name} Component</h2>
    </div>
  )
}}
'''

    def _generate_api_route_code(self, path: str, methods: List[str], typescript: bool) -> str:
        """Generate API route code"""
        code = ""

        if typescript:
            code += "import { NextRequest, NextResponse } from 'next/server'\n\n"

        for method in methods:
            method_upper = method.upper()
            if method_upper == "GET":
                code += f'''export async function GET() {{
  return Response.json({{ message: 'GET /{path}' }})
}}

'''
            elif method_upper == "POST":
                code += f'''export async function POST(request{': NextRequest' if typescript else ''}) {{
  const data = await request.json()
  return Response.json({{ message: 'POST /{path}', data }})
}}

'''
            elif method_upper == "PUT":
                code += f'''export async function PUT(request{': NextRequest' if typescript else ''}) {{
  const data = await request.json()
  return Response.json({{ message: 'PUT /{path}', data }})
}}

'''
            elif method_upper == "DELETE":
                code += f'''export async function DELETE() {{
  return Response.json({{ message: 'DELETE /{path}' }})
}}

'''

        return code.strip() + '\n'

    def _generate_layout_code(self, name: str, typescript: bool) -> str:
        """Generate layout code"""
        props_type = ": { children: React.ReactNode }" if typescript else ""

        return f'''export default function {name}({{
  children,
}}{props_type}) {{
  return (
    <div>
      <header className="p-4 border-b">
        <nav>Navigation</nav>
      </header>
      <main>{{children}}</main>
      <footer className="p-4 border-t">
        Footer
      </footer>
    </div>
  )
}}
'''

    def can_handle(self, request: str) -> float:
        """Check if request is Next.js-related"""
        request_lower = request.lower()

        high_conf = ["nextjs", "next.js", "next js", "react component", "app router"]
        for kw in high_conf:
            if kw in request_lower:
                return 0.9

        med_conf = ["react", "component", "page", "layout", "typescript"]
        for kw in med_conf:
            if kw in request_lower:
                return 0.5

        return super().can_handle(request)

    def handle_request(self, request: str, **kwargs) -> Optional[ActionResult]:
        """Handle a natural language request"""
        request_lower = request.lower()

        if "scaffold" in request_lower or "new project" in request_lower:
            words = request.split()
            name = "my_app"
            for i, word in enumerate(words):
                if word.lower() in ["project", "called", "named"]:
                    if i + 1 < len(words):
                        name = words[i + 1].strip("'\"")
                        break
            return self.scaffold_project(name=name)

        if "analyze" in request_lower:
            return self.analyze_project()

        return None
