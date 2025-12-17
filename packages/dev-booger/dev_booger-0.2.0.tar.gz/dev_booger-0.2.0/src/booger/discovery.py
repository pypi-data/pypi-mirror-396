"""Auto-discover commands for ports from various config files."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml


ConfidenceLevel = Literal["explicit", "high", "medium", "low"]


@dataclass
class DiscoveryResult:
    """Result of port discovery with metadata."""
    command: str
    source: str
    confidence: ConfidenceLevel
    framework: str | None = None

    def __str__(self) -> str:
        if self.framework:
            return f"{self.command} (from: {self.source}, framework: {self.framework})"
        return f"{self.command} (from: {self.source})"


# Framework defaults when no explicit port is found
FRAMEWORK_DEFAULTS = {
    # Node.js
    "next": {"port": 3000, "cmd": "npm run dev"},
    "vite": {"port": 5173, "cmd": "npm run dev"},
    "react-scripts": {"port": 3000, "cmd": "npm start"},
    "nuxt": {"port": 3000, "cmd": "npm run dev"},
    "gatsby": {"port": 8000, "cmd": "npm run develop"},
    "svelte": {"port": 5173, "cmd": "npm run dev"},
    "remix": {"port": 3000, "cmd": "npm run dev"},
    # Python
    "fastapi": {"port": 8000, "cmd": "uvicorn main:app --reload"},
    "uvicorn": {"port": 8000, "cmd": "uvicorn main:app --reload"},
    "flask": {"port": 5000, "cmd": "flask run"},
    "django": {"port": 8000, "cmd": "python manage.py runserver"},
    "streamlit": {"port": 8501, "cmd": "streamlit run app.py"},
}


def discover_command(port: int, cwd: Path | None = None) -> DiscoveryResult | None:
    """
    Discover the command to run for a given port.

    Checks sources in priority order:
    1. booger.json (explicit config)
    2. docker-compose.yml (service port mappings)
    3. Dockerfile (EXPOSE directive)
    4. .env files (PORT variables)
    5. package.json (npm scripts with port patterns)
    6. pyproject.toml (Python framework detection)
    7. Procfile (Heroku-style)
    8. Makefile (dev/run targets)
    """
    if cwd is None:
        cwd = Path.cwd()

    # 1. Explicit config (highest priority)
    if result := _check_booger_json(port, cwd):
        return result

    # 2. Docker Compose
    if result := _check_docker_compose(port, cwd):
        return result

    # 3. Dockerfile
    if result := _check_dockerfile(port, cwd):
        return result

    # 4. Environment files
    if result := _check_env_files(port, cwd):
        return result

    # 5. package.json scripts
    if result := _check_package_json(port, cwd):
        return result

    # 6. Python project
    if result := _check_python_project(port, cwd):
        return result

    # 7. Procfile
    if result := _check_procfile(port, cwd):
        return result

    # 8. Makefile
    if result := _check_makefile(port, cwd):
        return result

    return None


def _check_booger_json(port: int, cwd: Path) -> DiscoveryResult | None:
    """Check booger.json for explicit port mapping."""
    config_file = cwd / "booger.json"
    if not config_file.exists():
        return None

    try:
        config = json.loads(config_file.read_text())
        ports = config.get("ports", {})
        cmd = ports.get(str(port)) or ports.get(port)
        if cmd:
            return DiscoveryResult(
                command=cmd,
                source="booger.json",
                confidence="explicit",
            )
    except (json.JSONDecodeError, OSError):
        pass
    return None


def _check_docker_compose(port: int, cwd: Path) -> DiscoveryResult | None:
    """Check docker-compose.yml for service with matching port."""
    for filename in ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]:
        compose_file = cwd / filename
        if not compose_file.exists():
            continue

        try:
            config = yaml.safe_load(compose_file.read_text())
            services = config.get("services", {})

            for service_name, service_config in services.items():
                ports_config = service_config.get("ports", [])
                for port_spec in ports_config:
                    # Parse "8000:8000" or "8000:8000/tcp"
                    port_str = str(port_spec).split("/")[0]  # Remove protocol
                    if ":" in port_str:
                        host_port = port_str.split(":")[0].strip('"\'')
                    else:
                        host_port = port_str.strip('"\'')

                    if int(host_port) == port:
                        return DiscoveryResult(
                            command=f"docker compose up {service_name}",
                            source=filename,
                            confidence="high",
                        )
        except (yaml.YAMLError, OSError, ValueError):
            pass
    return None


def _check_dockerfile(port: int, cwd: Path) -> DiscoveryResult | None:
    """Check Dockerfile for EXPOSE directive matching port."""
    dockerfile = cwd / "Dockerfile"
    if not dockerfile.exists():
        return None

    try:
        content = dockerfile.read_text()

        # Check EXPOSE directive
        expose_match = re.search(rf"^EXPOSE\s+{port}\b", content, re.MULTILINE)
        if not expose_match:
            return None

        # Try to extract CMD
        cmd_match = re.search(r'^CMD\s+\[([^\]]+)\]', content, re.MULTILINE)
        if cmd_match:
            # Parse JSON-style CMD ["python", "-m", "uvicorn", ...]
            try:
                cmd_parts = json.loads(f"[{cmd_match.group(1)}]")
                cmd = " ".join(cmd_parts)
            except json.JSONDecodeError:
                cmd = f"docker build -t app . && docker run -p {port}:{port} app"
        else:
            # Check for shell-style CMD
            shell_cmd = re.search(r'^CMD\s+(.+)$', content, re.MULTILINE)
            if shell_cmd:
                cmd = shell_cmd.group(1).strip()
            else:
                cmd = f"docker build -t app . && docker run -p {port}:{port} app"

        return DiscoveryResult(
            command=cmd,
            source="Dockerfile",
            confidence="high",
        )
    except OSError:
        pass
    return None


def _check_env_files(port: int, cwd: Path) -> DiscoveryResult | None:
    """Check .env files for PORT variable matching."""
    for env_file in [".env", ".env.local", ".env.development"]:
        env_path = cwd / env_file
        if not env_path.exists():
            continue

        try:
            content = env_path.read_text()
            # Match PORT=3000 or APP_PORT=3000
            pattern = rf'^([A-Z_]*PORT[A-Z_]*)\s*=\s*["\']?{port}["\']?'
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                var_name = match.group(1)
                # We found the port but need to infer the command
                # Check for common patterns
                if (cwd / "package.json").exists():
                    return DiscoveryResult(
                        command="npm run dev",
                        source=f"{env_file} ({var_name}={port})",
                        confidence="medium",
                    )
                elif (cwd / "pyproject.toml").exists():
                    use_uv = _is_uv_project(cwd)
                    prefix = "uv run " if use_uv else ""
                    app_path = _find_python_main(cwd)
                    return DiscoveryResult(
                        command=f"{prefix}uvicorn {app_path} --port {port} --reload --log-level debug",
                        source=f"{env_file} ({var_name}={port})",
                        confidence="medium",
                    )
        except OSError:
            pass
    return None


def _check_package_json(port: int, cwd: Path) -> DiscoveryResult | None:
    """Check package.json scripts for commands with matching port."""
    package_file = cwd / "package.json"
    if not package_file.exists():
        return None

    try:
        package = json.loads(package_file.read_text())
        scripts = package.get("scripts", {})
        deps = {
            **package.get("dependencies", {}),
            **package.get("devDependencies", {}),
        }

        # First, look for scripts with explicit port
        port_patterns = [
            rf"--port[=\s]+{port}\b",
            rf"-p[=\s]+{port}\b",
            rf"PORT={port}\b",
            rf":{port}\b",
        ]

        for script_name, script_cmd in scripts.items():
            for pattern in port_patterns:
                if re.search(pattern, script_cmd):
                    return DiscoveryResult(
                        command=f"npm run {script_name}",
                        source="package.json",
                        confidence="high",
                    )

        # Second, check framework defaults
        for framework, config in FRAMEWORK_DEFAULTS.items():
            if framework in deps and config["port"] == port:
                # Find the appropriate script
                if "dev" in scripts:
                    cmd = "npm run dev"
                elif "start" in scripts:
                    cmd = "npm start"
                else:
                    cmd = config["cmd"]

                return DiscoveryResult(
                    command=cmd,
                    source="package.json",
                    confidence="medium",
                    framework=framework,
                )

    except (json.JSONDecodeError, OSError):
        pass
    return None


def _check_python_project(port: int, cwd: Path) -> DiscoveryResult | None:
    """Check pyproject.toml for Python framework dependencies."""
    pyproject = cwd / "pyproject.toml"
    if not pyproject.exists():
        return None

    try:
        content = pyproject.read_text()

        # Determine if we should use uv run
        use_uv = _is_uv_project(cwd)
        prefix = "uv run " if use_uv else ""

        # Check for framework dependencies - detect framework regardless of port
        # For ASGI frameworks (fastapi, starlette, litestar) - generate uvicorn command
        # Always use --reload and --log-level debug for maximum visibility
        if re.search(r'["\']?fastapi["\']?\s*[>=<,\]]', content, re.IGNORECASE):
            app_path = _find_python_main(cwd)
            return DiscoveryResult(
                command=f"{prefix}uvicorn {app_path} --port {port} --reload --log-level debug",
                source="pyproject.toml",
                confidence="medium",
                framework="fastapi",
            )

        if re.search(r'["\']?starlette["\']?\s*[>=<,\]]', content, re.IGNORECASE):
            app_path = _find_python_main(cwd)
            return DiscoveryResult(
                command=f"{prefix}uvicorn {app_path} --port {port} --reload --log-level debug",
                source="pyproject.toml",
                confidence="medium",
                framework="starlette",
            )

        if re.search(r'["\']?litestar["\']?\s*[>=<,\]]', content, re.IGNORECASE):
            app_path = _find_python_main(cwd)
            return DiscoveryResult(
                command=f"{prefix}litestar run --port {port} --reload --debug",
                source="pyproject.toml",
                confidence="medium",
                framework="litestar",
            )

        if re.search(r'["\']?flask["\']?\s*[>=<,\]]', content, re.IGNORECASE):
            app_path = _find_python_main(cwd)
            return DiscoveryResult(
                command=f"{prefix}flask --app {app_path} run --port {port} --reload --debug",
                source="pyproject.toml",
                confidence="medium",
                framework="flask",
            )

        if re.search(r'["\']?django["\']?\s*[>=<,\]]', content, re.IGNORECASE):
            return DiscoveryResult(
                command=f"{prefix}python manage.py runserver {port}",
                source="pyproject.toml",
                confidence="medium",
                framework="django",
            )

        if re.search(r'["\']?streamlit["\']?\s*[>=<,\]]', content, re.IGNORECASE):
            result = _find_python_app_path(cwd)
            if result:
                module_path, _ = result
                file_path = module_path.replace(".", "/") + ".py"
            else:
                file_path = "app.py"
            return DiscoveryResult(
                command=f"{prefix}streamlit run {file_path} --server.port {port}",
                source="pyproject.toml",
                confidence="medium",
                framework="streamlit",
            )

        if re.search(r'["\']?gradio["\']?\s*[>=<,\]]', content, re.IGNORECASE):
            result = _find_python_app_path(cwd)
            if result:
                module_path, _ = result
                file_path = module_path.replace(".", "/") + ".py"
            else:
                file_path = "app.py"
            return DiscoveryResult(
                command=f"{prefix}python {file_path}",
                source="pyproject.toml",
                confidence="medium",
                framework="gradio",
            )

    except OSError:
        pass
    return None


def _find_app_variable(file_path: Path) -> str | None:
    """
    Parse a Python file to find the ASGI/WSGI app variable name.

    Looks for patterns like:
    - app = FastAPI()
    - application = Flask(__name__)
    - api = Starlette()
    - app = create_app()  (factory pattern)
    """
    try:
        content = file_path.read_text()

        # Direct instantiation patterns (with optional indentation)
        frameworks = ["FastAPI", "Flask", "Starlette", "Litestar"]
        for framework in frameworks:
            # Match both module-level and indented: app = FastAPI(...)
            match = re.search(rf'^\s*(\w+)\s*=\s*{framework}\s*\(', content, re.MULTILINE)
            if match:
                return match.group(1)

        # Factory pattern: app = create_app() at module level (no indentation)
        # Look for def create_app() -> FastAPI: ... then app = create_app()
        if re.search(r'def\s+create_app\s*\([^)]*\)\s*->\s*FastAPI', content):
            match = re.search(r'^(\w+)\s*=\s*create_app\s*\(', content, re.MULTILINE)
            if match:
                return match.group(1)

        # Generic factory: app = something() at module level where something returns FastAPI
        # Check for common patterns like get_app(), make_app(), build_app()
        for factory in ["create_app", "get_app", "make_app", "build_app", "get_application"]:
            match = re.search(rf'^(\w+)\s*=\s*{factory}\s*\(', content, re.MULTILINE)
            if match:
                return match.group(1)

    except OSError:
        pass

    return None


def _get_project_module_name(cwd: Path) -> str | None:
    """
    Extract the Python module name from pyproject.toml project name.

    Converts 'ai-gateway' -> 'ai_gateway', 'my-cool-app' -> 'my_cool_app'
    """
    pyproject = cwd / "pyproject.toml"
    if not pyproject.exists():
        return None

    try:
        content = pyproject.read_text()
        # Match name = "project-name" in [project] section
        match = re.search(r'^\s*name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        if match:
            project_name = match.group(1)
            # Convert to valid Python module name (hyphens -> underscores)
            return project_name.replace("-", "_")
    except OSError:
        pass

    return None


def _is_uv_project(cwd: Path) -> bool:
    """Check if this is a uv-managed project."""
    # Check for uv.lock file
    if (cwd / "uv.lock").exists():
        return True

    # Check for [tool.uv] in pyproject.toml
    pyproject = cwd / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            if "[tool.uv]" in content:
                return True
        except OSError:
            pass

    return False


def _find_python_app_path(cwd: Path) -> tuple[str, str] | None:
    """
    Discover the Python app path for uvicorn (e.g., 'ai_gateway.main:app').

    Returns tuple of (module_path, app_var) or None.

    Strategy:
    1. Check pyproject.toml project name -> infer module directory
    2. Scan root for Python packages with main.py/app.py containing FastAPI/Flask
    3. Check common patterns (main.py, app.py in root)
    """
    # Strategy 1: Use project name from pyproject.toml
    module_name = _get_project_module_name(cwd)
    if module_name:
        # Check if module directory exists in root
        module_dir = cwd / module_name
        if module_dir.is_dir() and (module_dir / "__init__.py").exists():
            # Check main.py
            main_py = module_dir / "main.py"
            if main_py.exists():
                app_var = _find_app_variable(main_py)
                if app_var:
                    return (f"{module_name}.main", app_var)

            # Check app.py
            app_py = module_dir / "app.py"
            if app_py.exists():
                app_var = _find_app_variable(app_py)
                if app_var:
                    return (f"{module_name}.app", app_var)

        # Check src/{module}/
        src_module = cwd / "src" / module_name
        if src_module.is_dir() and (src_module / "__init__.py").exists():
            main_py = src_module / "main.py"
            if main_py.exists():
                app_var = _find_app_variable(main_py)
                if app_var:
                    return (f"{module_name}.main", app_var)

    # Strategy 2: Scan root for any Python package with FastAPI/Flask app
    for item in cwd.iterdir():
        if item.is_dir() and not item.name.startswith((".", "_", "test")):
            if (item / "__init__.py").exists():
                # Check main.py
                main_py = item / "main.py"
                if main_py.exists():
                    app_var = _find_app_variable(main_py)
                    if app_var:
                        return (f"{item.name}.main", app_var)

                # Check app.py
                app_py = item / "app.py"
                if app_py.exists():
                    app_var = _find_app_variable(app_py)
                    if app_var:
                        return (f"{item.name}.app", app_var)

    # Strategy 3: Check src/ directory
    src_dir = cwd / "src"
    if src_dir.exists():
        for item in src_dir.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                main_py = item / "main.py"
                if main_py.exists():
                    app_var = _find_app_variable(main_py)
                    if app_var:
                        return (f"{item.name}.main", app_var)

                app_py = item / "app.py"
                if app_py.exists():
                    app_var = _find_app_variable(app_py)
                    if app_var:
                        return (f"{item.name}.app", app_var)

    # Strategy 4: Check root main.py or app.py
    root_main = cwd / "main.py"
    if root_main.exists():
        app_var = _find_app_variable(root_main)
        if app_var:
            return ("main", app_var)

    root_app = cwd / "app.py"
    if root_app.exists():
        app_var = _find_app_variable(root_app)
        if app_var:
            return ("app", app_var)

    return None


def _find_python_main(cwd: Path) -> str:
    """Find the main Python module for a project (legacy, returns module:app format)."""
    result = _find_python_app_path(cwd)
    if result:
        module_path, app_var = result
        return f"{module_path}:{app_var}"

    # Fallback to simple detection
    candidates = ["main", "app", "server", "api"]

    for candidate in candidates:
        if (cwd / f"{candidate}.py").exists():
            return f"{candidate}:app"
        if (cwd / "src" / f"{candidate}.py").exists():
            return f"src.{candidate}:app"

    # Check for src/package structure
    src_dir = cwd / "src"
    if src_dir.exists():
        for item in src_dir.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                if (item / "main.py").exists():
                    return f"{item.name}.main:app"
                if (item / "app.py").exists():
                    return f"{item.name}.app:app"

    return "main:app"


def _check_procfile(port: int, cwd: Path) -> DiscoveryResult | None:
    """Check Procfile for process definitions."""
    procfile = cwd / "Procfile"
    if not procfile.exists():
        return None

    try:
        content = procfile.read_text()
        for line in content.strip().split("\n"):
            match = re.match(r"^(\w+):\s*(.+)$", line.strip())
            if match:
                process_name, command = match.groups()
                # Check if command contains the port
                if str(port) in command:
                    return DiscoveryResult(
                        command=command,
                        source=f"Procfile ({process_name})",
                        confidence="high",
                    )
    except OSError:
        pass
    return None


def _check_makefile(port: int, cwd: Path) -> DiscoveryResult | None:
    """Check Makefile for dev/run targets."""
    makefile = cwd / "Makefile"
    if not makefile.exists():
        return None

    try:
        content = makefile.read_text()

        # Look for targets that might run dev servers
        target_pattern = r"^(dev|run|serve|start|server):\s*\n\t(.+)"
        for match in re.finditer(target_pattern, content, re.MULTILINE):
            target_name, command = match.groups()
            # Check if command references the port
            if str(port) in command:
                return DiscoveryResult(
                    command=f"make {target_name}",
                    source=f"Makefile ({target_name})",
                    confidence="low",
                )
    except OSError:
        pass
    return None


def discover_all(ports: list[int], cwd: Path | None = None) -> dict[int, DiscoveryResult | None]:
    """Discover commands for multiple ports."""
    if cwd is None:
        cwd = Path.cwd()
    return {port: discover_command(port, cwd) for port in ports}


def list_discoverable_ports(cwd: Path | None = None) -> list[tuple[int, DiscoveryResult]]:
    """Scan project and list all discoverable ports with their commands."""
    if cwd is None:
        cwd = Path.cwd()

    discovered = []

    # Scan docker-compose for all ports
    for filename in ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]:
        compose_file = cwd / filename
        if compose_file.exists():
            try:
                config = yaml.safe_load(compose_file.read_text())
                for service_name, service_config in config.get("services", {}).items():
                    for port_spec in service_config.get("ports", []):
                        port_str = str(port_spec).split("/")[0].split(":")[0].strip('"\'')
                        try:
                            port = int(port_str)
                            result = discover_command(port, cwd)
                            if result:
                                discovered.append((port, result))
                        except ValueError:
                            pass
            except (yaml.YAMLError, OSError):
                pass

    # Scan package.json for framework defaults
    package_file = cwd / "package.json"
    if package_file.exists():
        try:
            package = json.loads(package_file.read_text())
            deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
            for framework, config in FRAMEWORK_DEFAULTS.items():
                if framework in deps:
                    result = discover_command(config["port"], cwd)
                    if result and (config["port"], result) not in discovered:
                        discovered.append((config["port"], result))
        except (json.JSONDecodeError, OSError):
            pass

    # Scan pyproject.toml for Python frameworks
    pyproject = cwd / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            for framework in ["fastapi", "flask", "django", "streamlit", "gradio"]:
                if framework in content.lower():
                    port = FRAMEWORK_DEFAULTS.get(framework, {}).get("port")
                    if port:
                        result = discover_command(port, cwd)
                        if result and (port, result) not in discovered:
                            discovered.append((port, result))
        except OSError:
            pass

    return discovered
