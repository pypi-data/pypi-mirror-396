# createsonline/cli/commands/project.py
"""
CREATESONLINE Project Commands

Create new projects with AI features.
"""
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def new_command(
    name: str = typer.Argument(..., help="Project name"),
    template: str = typer.Option("basic", "--template", "-t", help="Project template (basic, ai-full, api-only)"),
    directory: str = typer.Option(None, "--dir", "-d", help="Directory to create project in"),
):
    """✨ Create new CREATESONLINE project with AI features"""
    
    # Determine project directory
    if directory:
        project_dir = Path(directory) / name
    else:
        project_dir = Path.cwd() / name
    
    console.print(Panel(
        f"[bold green]Creating CREATESONLINE Project[/bold green]\n\n"
        f"[cyan]Name:[/cyan] {name}\n"
        f"[cyan]Template:[/cyan] {template}\n"
        f"[cyan]Directory:[/cyan] {project_dir}\n"
        f"[cyan]Features:[/cyan] AI Fields, Admin Interface, CLI",
        title="✨ Project Generator",
        border_style="green"
    ))
    
    # Check if directory exists
    if project_dir.exists():
        console.print(f"[red]Error: Directory {project_dir} already exists![/red]")
        raise typer.Exit(1)
    
    # Create project with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Create directories
        task = progress.add_task("Creating project structure...", total=None)
        try:
            create_project_structure(project_dir, name, template)
            progress.update(task, description=" Project structure created")
            
            # Generate files
            progress.update(task, description="Generating project files...")
            generate_project_files(project_dir, name, template)
            progress.update(task, description=" Project files generated")
            
            # Create virtual environment suggestion
            progress.update(task, description=" Project created successfully!")
            
        except Exception as e:
            console.print(f"[red]Error creating project: {e}[/red]")
            raise typer.Exit(1)
    
    # Success message
    success_panel = Panel(
        f"[bold green] Project '{name}' created successfully![/bold green]\n\n"
        "[cyan]Next steps:[/cyan]\n"
        f"1. [yellow]cd {name}[/yellow]\n"
        "2. [yellow]python -m venv venv[/yellow]\n"
        "3. [yellow]source venv/bin/activate[/yellow]  # or venv\\Scripts\\activate on Windows\n"
        "4. [yellow]pip install -r requirements.txt[/yellow]\n"
        "5. [yellow]createsonline serve[/yellow]\n\n"
        "[green]Visit:[/green] http://localhost:8000",
        title=" Ready to Go!",
        border_style="green"
    )
    console.print(success_panel)

def create_project_structure(project_dir: Path, name: str, template: str):
    """Create the project directory structure"""
    
    # Create main project directory
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories based on template
    directories = [
        "static",
        "templates", 
        "models",
        "api",
        "tests"
    ]
    
    if template in ["ai-full", "full"]:
        directories.extend([
            "ai",
            "ml_models",
            "data"
        ])
    
    for dir_name in directories:
        (project_dir / dir_name).mkdir(exist_ok=True)
        # Create __init__.py for Python packages
        if dir_name in ["models", "api", "ai"]:
            (project_dir / dir_name / "__init__.py").write_text("")

def generate_project_files(project_dir: Path, name: str, template: str):
    """Generate project files based on template"""
    
    # Generate main.py
    main_py_content = generate_main_py(name, template)
    (project_dir / "main.py").write_text(main_py_content)
    
    # Generate requirements.txt
    requirements_content = generate_requirements(template)
    (project_dir / "requirements.txt").write_text(requirements_content)
    
    # Generate .env
    env_content = generate_env_file(name)
    (project_dir / ".env").write_text(env_content)
    
    # Generate README.md
    readme_content = generate_readme(name, template)
    (project_dir / "README.md").write_text(readme_content)
    
    # Generate .gitignore
    gitignore_content = generate_gitignore()
    (project_dir / ".gitignore").write_text(gitignore_content)
    
    # Template-specific files
    if template in ["ai-full", "full"]:
        # Generate AI model examples
        ai_models_content = generate_ai_models(name)
        (project_dir / "models" / "ai_models.py").write_text(ai_models_content)
        
        # Generate AI routes
        ai_routes_content = generate_ai_routes()
        (project_dir / "api" / "ai_routes.py").write_text(ai_routes_content)

def generate_main_py(name: str, template: str) -> str:
    """Generate main.py file - Pure Independence Version"""
    
    if template == "basic":
        return f'''#!/usr/bin/env python3
"""
{name} - Pure CREATESONLINE Application

Pure independence CREATESONLINE application with internal implementations only.
Zero external web framework dependencies - Pure ASGI implementation.
"""
from createsonline.config.app import CreatesonlineApp
from createsonline.database import Database
import os

# Create pure CREATESONLINE application (no external frameworks)
app = CreatesonlineApp(
    title="{name.title()}",
    description="A pure CREATESONLINE application - Zero external dependencies",
    version="1.0.0",
    debug=False
)

# Initialize database with internal abstraction
db = Database(os.getenv("DATABASE_URL", "sqlite:///./app.db"))

@app.route("/", methods=["GET"])
async def home(request):
    """Home page - Pure internal implementation"""
    return {{
        "message": "Welcome to {name.title()}!",
        "framework": "CREATESONLINE",
        "template": "basic",
        "independence": "Pure - Zero external web frameworks",
        "dependencies": "Only 5 core essentials"
    }}

@app.route("/health", methods=["GET"])
async def health(request):
    """Health check - Internal monitoring"""
    return {{
        "status": "healthy",
        "framework": "CREATESONLINE Pure",
        "database": "connected" if db.is_connected() else "disconnected"
    }}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
'''
    
    elif template in ["ai-full", "full"]:
        return f'''#!/usr/bin/env python3
"""
{name} - Pure AI-Native CREATESONLINE Application

Pure independence AI application with internal ML implementations.
Zero external ML framework dependencies - Native CREATESONLINE AI stack.
"""
from createsonline.config.app import CreatesonlineApp
from createsonline.database import Database
from createsonline.ai.services import AIService
from createsonline.ai.fields import AIComputedField, LLMField, VectorField
from createsonline.ai.orm import AIBaseModel
from createsonline.ml.neural import NeuralNetwork
from createsonline.ml.classification import Classifier
import os

# Create pure CREATESONLINE AI application (no external frameworks)
app = CreatesonlineApp(
    title="{name.title()} AI",
    description="Pure AI-native CREATESONLINE application - Zero external ML dependencies",
    version="1.0.0",
    debug=False
)

# Initialize with internal implementations only
db = Database(os.getenv("DATABASE_URL", "sqlite:///./app.db"))
ai = AIService()  # Pure internal AI - no TensorFlow/PyTorch

@app.route("/", methods=["GET"])
async def home(request):
    """AI-powered home page - Pure internal implementation"""
    return {{
        "message": "Welcome to {name.title()} AI!",
        "framework": "CREATESONLINE Pure AI",
        "template": "ai-full",
        "ai_features": [
            "Internal AI-Computed Fields",
            "Pure LLM Content Generation",
            "Native Vector Embeddings",
            "Internal Text Analysis"
        ],
        "independence": "Pure - Zero external AI/ML dependencies"
    }}

@app.route("/ai/demo", methods=["GET"])
async def ai_demo(request):
    """Demonstrate AI capabilities - Internal implementations"""
    try:
        # Use internal AI generation
        sample_text = await ai.generate_text(
            f"Write a tagline for {{name.title()}}",
            max_tokens=50
        )
        
        # Get internal embedding
        embedding = await ai.get_embedding("CREATESONLINE Pure AI Framework")
        
        return {{
            "ai_status": " Working - Pure Internal",
            "sample_text": sample_text,
            "embedding_size": len(embedding),
            "framework": "CREATESONLINE Pure AI"
        }}
    except Exception as e:
        return {{
            "ai_status": " Limited Mode",
            "error": str(e),
            "framework": "CREATESONLINE Pure AI"
        }}

@app.route("/ai/predict", methods=["POST"])
async def ai_predict(request):
    """AI prediction endpoint - Pure internal ML"""
    try:
        data = await request.json()
        # Use internal neural network implementation
        model = NeuralNetwork(layers=[10, 5, 1])
        prediction = await ai.predict(model, data.get("features", []))
        
        return {{
            "prediction": prediction,
            "model": "Internal Neural Network",
            "framework": "CREATESONLINE Pure ML"
        }}
    except Exception as e:
        return {{"error": str(e)}}, 400

@app.route("/health", methods=["GET"])
async def health(request):
    """AI system health check"""
    return {{
        "status": "healthy",
        "framework": "CREATESONLINE Pure AI",
        "ai_service": "active",
        "database": "connected" if db.is_connected() else "disconnected",
        "ai_enabled": True
    }}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
'''
    
    else:  # api-only
        return f'''#!/usr/bin/env python3
"""
{name} - Pure CREATESONLINE API

API-only CREATESONLINE application with pure internal implementation.
Zero external framework dependencies - Pure ASGI implementation.
"""
from createsonline.config.app import CreatesonlineApp
from createsonline.database import Database
import os

# Create pure CREATESONLINE API application (no external frameworks)
app = CreatesonlineApp(
    title="{name.title()} API",
    description="Pure API built with CREATESONLINE - Zero external dependencies",
    version="1.0.0",
    debug=False
)

# Initialize database with internal abstraction
db = Database(os.getenv("DATABASE_URL", "sqlite:///./app.db"))

@app.route("/api/v1/status", methods=["GET"])
async def api_status(request):
    """API status - Pure internal implementation"""
    return {{
        "service": "{name.title()} API",
        "status": "operational",
        "version": "1.0.0",
        "framework": "CREATESONLINE Pure API",
        "independence": "Pure - Zero external web frameworks"
    }}

@app.route("/api/v1/health", methods=["GET"])
async def api_health(request):
    """API health check - Internal monitoring"""
    return {{
        "status": "healthy",
        "framework": "CREATESONLINE Pure API",
        "database": "connected" if db.is_connected() else "disconnected",
        "dependencies": "Only 5 core essentials"
    }}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

def generate_requirements(template: str) -> str:
    """Generate requirements.txt - Pure Independence Version"""
    
    base_requirements = [
        "# CREATESONLINE Framework - Pure Independence Requirements",
        "# Only the absolute essentials that are too complex to rebuild",
        "",
        "# ========================================",
        "# CORE ESSENTIALS (Cannot reasonably rebuild)",
        "# ========================================",
        "",
        "# ASGI Server (minimal - no extras)",
        "uvicorn>=0.24.0,<1.0.0",
        "",
        "# Database ORM (too complex to rebuild)",
        "sqlalchemy>=2.0.0,<3.0.0",
        "alembic>=1.12.0,<2.0.0            # Database migrations",
        "",
        "# Math/AI Foundation (essential for vectors/AI)",
        "numpy>=1.24.0,<2.0.0",
        "",
        "# Environment Variables (simple utility)",
        "python-dotenv>=1.0.0,<2.0.0",
        "",
        "# ========================================",
        "# TOTAL: 5 CORE DEPENDENCIES",
        "# ========================================",
        ""
    ]
    
    if template in ["ai-full", "full"]:
        ai_requirements = [
            "# ========================================",
            "# OPTIONAL AI ENHANCEMENTS",
            "# ========================================",
            "",
            "# External AI APIs (optional)",
            "# openai>=1.0.0                # Uncomment if using OpenAI",
            "# anthropic>=0.18.0            # Uncomment if using Claude",
            "",
            "# ========================================",
            "# EVERYTHING ELSE: BUILT INTERNALLY",
            "# ========================================",
            "#  REMOVED: pydantic (internal validation)",
            "#  REMOVED: pandas (internal data structures)",
            "#  REMOVED: scikit-learn (internal ML)",
            "#  REMOVED: requests/httpx (internal HTTP client)",
            "#  REMOVED: typer/rich (internal CLI with fallbacks)",
            ""
        ]
        base_requirements.extend(ai_requirements)
    
    dev_requirements = [
        "# Development",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "black>=23.0.0",
        "isort>=5.12.0"
    ]
    base_requirements.extend(dev_requirements)
    
    return "\n".join(base_requirements)

def generate_env_file(name: str) -> str:
    """Generate .env file"""
    return f'''# {name.title()} Environment Configuration

# Server Configuration
HOST=0.0.0.0
PORT=3000
ENV=development
WORKERS=1

# Database Configuration  
DATABASE_URL=sqlite:///./app.db

# AI Configuration (Optional - for real AI features)
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# Debug
DEBUG=true
'''

def generate_readme(name: str, template: str) -> str:
    """Generate README.md"""
    
    ai_section = ""
    if template in ["ai-full", "full"]:
        ai_section = f'''
## Ｃ⎯● AI Features

This project includes AI capabilities:

- **AI-Computed Fields**: Automatic ML predictions
- **LLM Content Generation**: GPT/Claude integration  
- **Vector Embeddings**: Semantic similarity search
- **Smart Text Analysis**: Sentiment, keywords, language detection

### Configure AI Services

Add your API keys to `.env`:

```bash
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### AI Endpoints

- `GET /ai/demo` - Demonstrate AI capabilities
- `POST /ai/generate` - Generate content with LLM
- `POST /ai/analyze` - Analyze text with AI
'''
    
    return f'''# {name.title()}

A powerful application built with **CREATESONLINE** - The AI-Native Web Framework.

##  Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\\Scripts\\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install CREATESONLINE CLI (if not already installed)
pip install -e .

# 4. Start development server
createsonline serve
# or
python main.py

# 5. Visit your app
open http://localhost:8000
```

##  Project Structure

```
{name}/
├── main.py              # Main application
├── requirements.txt     # Dependencies
├── .env                # Environment configuration
├── models/             # Data models
├── api/               # API routes
├── static/            # Static files
├── templates/         # HTML templates
└── tests/             # Test files
```

##  Development Commands

```bash
# Development server with auto-reload
createsonline dev

# Production server
createsonline prod --workers 4

# Framework information
createsonline info

# Interactive shell
createsonline shell

# Create admin user
createsonline createsuperuser
```
{ai_section}
## 📚 Documentation

- [CREATESONLINE Docs](https://docs.createsonline.com)
- [API Documentation](http://localhost:8000/createsonline/docs) (when running)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

Built with ❤ using [CREATESONLINE](https://createsonline.com) - Build Intelligence Into Everything.
'''