"""
WeWork CLI Commands
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional
import click
import json


def safe_echo(message: str):
    """Safely echo message, handling Unicode encoding errors on Windows"""
    try:
        click.echo(message)
    except UnicodeEncodeError:
        # Fallback: remove emojis and special characters for Windows console
        import re
        # Remove emojis and other problematic Unicode characters
        safe_message = re.sub(r'[^\x00-\x7F]+', '', message)
        click.echo(safe_message if safe_message.strip() else message.encode('ascii', 'ignore').decode('ascii'))


def get_project_root():
    """Find project root by looking for .wework or pyproject.toml"""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".wework").exists() or (parent / "pyproject.toml").exists():
            return parent
    return current


def get_framework_version():
    """Get installed framework version"""
    try:
        import pkg_resources
        return pkg_resources.get_distribution("wework-framework").version
    except:
        return "unknown"


@click.command()
@click.option("--name", prompt="Project name", help="Name of the project")
@click.option("--path", default=".", help="Path to create project")
def init_project(name: str, path: str):
    """Initialize a new WeWork project"""
    project_path = Path(path) / name
    project_path.mkdir(parents=True, exist_ok=True)
    
    click.echo(f"Creating WeWork project '{name}' at {project_path}")
    
    # Create .wework config file
    config = {
        "name": name,
        "version": "1.0.7",
        "framework_version": get_framework_version(),
    }
    (project_path / ".wework").write_text(json.dumps(config, indent=2))
    
    click.echo(f"✓ Project '{name}' initialized successfully!")
    click.echo(f"  Run 'cd {name}' to get started")


@click.command()
@click.argument("name")
@click.option("--path", default="src/api", help="Path to create API file")
@click.option("--prefix", default=None, help="API prefix (default: /api/{name})")
def make_api(name: str, path: str, prefix: Optional[str]):
    """Generate a new API router"""
    project_root = get_project_root()
    api_path = project_root / path
    api_path.mkdir(parents=True, exist_ok=True)
    
    api_prefix = prefix or f"/api/{name}"
    api_file = api_path / f"{name}_api.py"
    
    template = f'''"""
{name.title()} API Router
"""
from fastapi import APIRouter, Depends, HTTPException
from src.api.auth_api import get_current_active_user
from src.db.models import User
from src.db.base import AsyncSessionLocal
from sqlalchemy import select
from pydantic import BaseModel

router = APIRouter(prefix="{api_prefix}", tags=["{name}"])


class {name.title()}Create(BaseModel):
    """Create {name} request model"""
    name: str
    description: str = None


class {name.title()}Update(BaseModel):
    """Update {name} request model"""
    name: str = None
    description: str = None


class {name.title()}Out(BaseModel):
    """{name.title()} response model"""
    id: int
    name: str
    description: str = None
    
    class Config:
        orm_mode = True


@router.get("", response_model=list[{name.title()}Out])
async def list_{name}s(current_user: User = Depends(get_current_active_user)):
    """List all {name}s"""
    async with AsyncSessionLocal() as session:
        # TODO: Implement your query
        return []


@router.get("/{{item_id}}", response_model={name.title()}Out)
async def get_{name}(item_id: int, current_user: User = Depends(get_current_active_user)):
    """Get {name} by ID"""
    async with AsyncSessionLocal() as session:
        # TODO: Implement your query
        raise HTTPException(status_code=404, detail="{name.title()} not found")


@router.post("", response_model={name.title()}Out)
async def create_{name}(
    item: {name.title()}Create,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new {name}"""
    async with AsyncSessionLocal() as session:
        # TODO: Implement creation logic
        raise HTTPException(status_code=501, detail="Not implemented")


@router.patch("/{{item_id}}", response_model={name.title()}Out)
async def update_{name}(
    item_id: int,
    item: {name.title()}Update,
    current_user: User = Depends(get_current_active_user)
):
    """Update {name}"""
    async with AsyncSessionLocal() as session:
        # TODO: Implement update logic
        raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{{item_id}}")
async def delete_{name}(item_id: int, current_user: User = Depends(get_current_active_user)):
    """Delete {name}"""
    async with AsyncSessionLocal() as session:
        # TODO: Implement delete logic
        raise HTTPException(status_code=501, detail="Not implemented")
'''
    
    api_file.write_text(template)
    click.echo(f"✓ Created API router: {api_file}")
    click.echo(f"  Don't forget to add it to src/api/app.py:")
    click.echo(f"  from src.api.{name}_api import router as {name}_router")
    click.echo(f"  app.include_router({name}_router)")


@click.command()
@click.argument("name")
@click.option("--path", default="src/db", help="Path to models file")
def make_model(name: str, path: str):
    """Generate a new database model"""
    project_root = get_project_root()
    models_file = project_root / path / "models.py"
    
    if not models_file.exists():
        click.echo(f"✗ Models file not found at {models_file}")
        return
    
    model_name = name.title().replace("_", "")
    table_name = f"{name}s"
    
    template = f'''
class {model_name}(Base):
    """{model_name} model"""
    
    __tablename__ = "{table_name}"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
'''
    
    # Append to models file
    with open(models_file, "a", encoding="utf-8") as f:
        f.write(template)
    
    click.echo(f"✓ Added model {model_name} to {models_file}")
    click.echo(f"  Don't forget to create migration:")
    click.echo(f"  wework make:migration add_{name}_table")


@click.command()
@click.argument("name")
@click.option("--path", default="frontend/src/components", help="Path to create component")
@click.option("--type", type=click.Choice(["functional", "class"]), default="functional", help="Component type")
def make_component(name: str, path: str, type: str):
    """Generate a new React component"""
    project_root = get_project_root()
    component_path = project_root / path
    component_path.mkdir(parents=True, exist_ok=True)
    
    component_name = name.title().replace("_", "")
    component_file = component_path / f"{component_name}.jsx"
    css_file = component_path / f"{component_name}.css"
    
    if type == "functional":
        template = f'''import React from 'react'
import './{component_name}.css'

/**
 * {component_name} Component
 */
export default function {component_name}() {{
  return (
    <div className="{name.lower().replace('_', '-')}">
      <h2>{component_name}</h2>
      {{/* Your component content */}}
    </div>
  )
}}
'''
    else:
        template = f'''import React, {{ Component }} from 'react'
import './{component_name}.css'

/**
 * {component_name} Component
 */
export default class {component_name} extends Component {{
  render() {{
    return (
      <div className="{name.lower().replace('_', '-')}">
        <h2>{component_name}</h2>
        {{/* Your component content */}}
      </div>
    )
  }}
}}
'''
    
    css_template = f'''.{name.lower().replace('_', '-')} {{
  /* Styles for {component_name} */
}}
'''
    
    component_file.write_text(template)
    css_file.write_text(css_template)
    
    click.echo(f"✓ Created component: {component_file}")
    click.echo(f"✓ Created styles: {css_file}")


@click.command()
@click.argument("name")
@click.option("--path", default="frontend/src/hooks", help="Path to create hook")
def make_hook(name: str, path: str):
    """Generate a new React hook"""
    project_root = get_project_root()
    hook_path = project_root / path
    hook_path.mkdir(parents=True, exist_ok=True)
    
    hook_name = f"use{name.title().replace('_', '')}"
    hook_file = hook_path / f"{hook_name}.js"
    
    template = f'''import {{ useState, useEffect }} from 'react'

/**
 * {hook_name} Hook
 * 
 * @returns {{data, loading, error, refetch}}
 */
export function {hook_name}() {{
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  const fetchData = async () => {{
    try {{
      setLoading(true)
      setError(null)
      // TODO: Implement your data fetching logic
      // const response = await fetch('/api/endpoint')
      // const result = await response.json()
      // setData(result)
    }} catch (err) {{
      setError(err.message)
    }} finally {{
      setLoading(false)
    }}
  }}
  
  useEffect(() => {{
    fetchData()
  }}, [])
  
  return {{
    data,
    loading,
    error,
    refetch: fetchData
  }}
}}
'''
    
    hook_file.write_text(template)
    click.echo(f"✓ Created hook: {hook_file}")


@click.command()
@click.argument("name")
@click.option("--path", default="src/db", help="Path to migrations")
def make_migration(name: str, path: str):
    """Generate a new database migration"""
    project_root = get_project_root()
    migration_path = project_root / path
    migration_path.mkdir(parents=True, exist_ok=True)
    
    migration_file = migration_path / f"migrate_{name}.py"
    
    template = f'''"""
Migration: {name}
"""
from src.db.base import Base, engine
from src.db.models import *


async def migrate():
    """Run migration"""
    async with engine.begin() as conn:
        # TODO: Implement your migration
        # Example:
        # await conn.run_sync(Base.metadata.create_all)
        pass


async def rollback():
    """Rollback migration"""
    async with engine.begin() as conn:
        # TODO: Implement rollback
        pass


if __name__ == "__main__":
    import asyncio
    asyncio.run(migrate())
'''
    
    migration_file.write_text(template)
    click.echo(f"✓ Created migration: {migration_file}")
    click.echo(f"  Run with: python -m src.db.migrate_{name}")


@click.command()
def update_framework():
    """Update WeWork framework to latest version"""
    click.echo("Checking for updates...")
    
    try:
        # Check current version
        current_version = get_framework_version()
        click.echo(f"Current version: {current_version}")
        
        # Update via pip
        click.echo("Updating wework-framework...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "wework-framework"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            new_version = get_framework_version()
            click.echo(f"✓ Framework updated to version {new_version}")
        else:
            click.echo(f"✗ Update failed: {result.stderr}")
            
    except Exception as e:
        click.echo(f"✗ Error: {e}")


@click.command()
@click.argument("new_version", required=False)
def set_version(new_version: Optional[str]):
    """Set project version centrally and update all files
    
    Usage:
        wework set:version 1.0.2    - Set version to 1.0.2
        wework set:version          - Sync all files with current version from version.json
    """
    project_root = get_project_root()
    version_file = project_root / "version.json"
    update_script = project_root / "scripts" / "update_version.py"
    
    if not update_script.exists():
        click.echo("✗ اسکریپت update_version.py پیدا نشد!")
        return
    
    try:
        if new_version:
            # Set new version
            import subprocess
            result = subprocess.run(
                [sys.executable, str(update_script), new_version],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                click.echo(result.stdout)
                click.echo(f"✓ نسخه به {new_version} تغییر کرد و همه فایل‌ها به‌روزرسانی شدند")
            else:
                click.echo(f"✗ خطا: {result.stderr}")
        else:
            # Sync with current version
            if not version_file.exists():
                click.echo("✗ فایل version.json پیدا نشد!")
                return
            
            import subprocess
            result = subprocess.run(
                [sys.executable, str(update_script)],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                click.echo(result.stdout)
            else:
                click.echo(f"✗ خطا: {result.stderr}")
    except Exception as e:
        click.echo(f"✗ خطا: {e}")


@click.command()
def version_info():
    """Show WeWork framework version information"""
    version = get_framework_version()
    project_root = get_project_root()
    
    click.echo("WeWork Framework")
    click.echo(f"  Framework version: {version}")
    
    # Check project version from version.json
    version_file = project_root / "version.json"
    if version_file.exists():
        try:
            version_data = json.loads(version_file.read_text())
            project_version = version_data.get("version", "unknown")
            click.echo(f"  Project version: {project_version}")
        except:
            pass
    
    # Check project version from .wework
    wework_config = project_root / ".wework"
    if wework_config.exists():
        config = json.loads(wework_config.read_text())
        click.echo(f"  Project: {config.get('name', 'unknown')}")
        click.echo(f"  Project version (legacy): {config.get('version', 'unknown')}")
        click.echo(f"  Framework version (project): {config.get('framework_version', 'unknown')}")
        
        if config.get('framework_version') != version:
            click.echo("  ⚠ Framework version mismatch! Run 'wework update' to update.")


@click.command()
@click.argument("project_name")
@click.option("--path", default=".", help="Path to create project (default: current directory)")
def create(project_name: str, path: str):
    """Create a new WeWork project from template
    
    This command creates a new project with a complete structure including:
    - Backend (FastAPI) with database setup
    - Frontend (React) with Vite
    - Docker configuration
    - Environment files
    
    Example:
        wework create my-awesome-app
        wework create my-awesome-app --path /path/to/projects
    """
    import re
    from pathlib import Path
    
    # Validate project name
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', project_name):
        click.echo("✗ Invalid project name! Use only letters, numbers, hyphens, and underscores. Must start with a letter.")
        return
    
    # Get template path
    # Try to find template in installed package first
    template_path = None
    try:
        import pkg_resources
        template_path = Path(pkg_resources.resource_filename('src.cli.templates', 'project_template'))
        if not template_path.exists():
            template_path = None
    except:
        pass
    
    # Fallback: use relative path from this file (for development)
    if template_path is None or not template_path.exists():
        template_path = Path(__file__).parent / 'templates' / 'project_template'
    
    if not template_path.exists():
        click.echo(f"✗ Template not found at {template_path}")
        click.echo("  Please ensure wework-framework is properly installed.")
        return
    
    # Create project directory
    project_path = Path(path).resolve() / project_name
    
    if project_path.exists():
        if not click.confirm(f"Directory {project_path} already exists. Overwrite?"):
            click.echo("✗ Cancelled.")
            return
        shutil.rmtree(project_path)
    
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Prepare template variables
    project_name_snake = re.sub(r'[^a-zA-Z0-9]', '_', project_name).lower()
    framework_version = get_framework_version()
    
    replacements = {
        '{{PROJECT_NAME}}': project_name,
        '{{PROJECT_NAME_SNAKE}}': project_name_snake,
        '{{FRAMEWORK_VERSION}}': framework_version,
    }
    
    safe_echo(f"🚀 Creating new WeWork project '{project_name}'...")
    click.echo(f"   Location: {project_path}")
    
    # Copy template files
    def process_file(src_file: Path, dst_file: Path):
        """Copy and process template file"""
        # Create parent directories
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Try to read as text file with different encodings
        content = None
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                content = src_file.read_text(encoding=encoding)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        # If all text encodings failed, treat as binary file
        if content is None:
            # Copy binary file as-is
            shutil.copy2(src_file, dst_file)
            return
        
        # Replace template variables
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Write to destination
        dst_file.write_text(content, encoding='utf-8')
    
    # Copy all files from template
    for src_file in template_path.rglob('*'):
        if src_file.is_file():
            # Get relative path
            rel_path = src_file.relative_to(template_path)
            dst_file = project_path / rel_path
            
            # Skip .env.example if .env exists (we'll create it separately)
            if rel_path.name == '.env.example':
                continue
            
            # Skip __pycache__ and .pyc files
            if '__pycache__' in rel_path.parts or rel_path.suffix == '.pyc':
                continue
            
            process_file(src_file, dst_file)
    
    # Create .env from .env.example
    env_example = template_path / '.env.example'
    if env_example.exists():
        # Try different encodings
        env_content = None
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                env_content = env_example.read_text(encoding=encoding)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if env_content is not None:
            for old, new in replacements.items():
                env_content = env_content.replace(old, new)
            (project_path / '.env.example').write_text(env_content, encoding='utf-8')
    
    # Make docker-entrypoint.sh executable
    entrypoint = project_path / 'docker-entrypoint.sh'
    if entrypoint.exists():
        try:
            import stat
            entrypoint.chmod(entrypoint.stat().st_mode | stat.S_IEXEC)
        except:
            pass  # Windows doesn't support chmod
    
    safe_echo("✅ Project created successfully!")
    click.echo("")
    safe_echo("📝 Next steps:")
    click.echo(f"  1. cd {project_name}")
    click.echo("  2. cp .env.example .env")
    click.echo("  3. Edit .env with your configuration")
    click.echo("  4. python -m venv venv")
    click.echo("  5. source venv/bin/activate  # Windows: venv\\Scripts\\activate")
    click.echo("  6. pip install -r requirements.txt")
    click.echo("  7. cd frontend && npm install")
    click.echo("  8. cd .. && docker-compose up -d postgres redis")
    click.echo("  9. python -m src.db.create_tables")
    click.echo("  10. uvicorn src.api.app:app --reload")
    click.echo("  11. In another terminal: cd frontend && npm run dev")
    click.echo("")
    safe_echo("📚 Documentation: https://github.com/wecanco/WeWork")