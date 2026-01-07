"""
Project installation logic
"""

import subprocess
from pathlib import Path
from typing import Optional
from rich.console import Console

from .project_types import ProjectConfig
from ..utils.command_runner import CommandRunner

console = Console()


class Installer:
    """Handles actual project creation"""

    def __init__(self):
        self.console = console
        self.runner = CommandRunner()

    def install(
        self,
        config: ProjectConfig,
        project_name: str,
        parent_dir: Optional[Path] = None,
        skip_post_install: bool = False,
    ) -> bool:
        """
        Install a project based on its configuration

        Args:
            config: Project configuration
            project_name: Name of the project to create
            parent_dir: Parent directory (defaults to current directory)
            skip_post_install: Skip post-installation steps

        Returns:
            True if installation succeeded
        """
        if parent_dir is None:
            parent_dir = Path.cwd()

        project_path = parent_dir / project_name

        # Handle custom installers
        if config.command.startswith("custom:"):
            return self._handle_custom_install(config, project_path)

        # Run the main installation command
        console.print(
            f"\n[bold cyan]📦 Creating {config.display_name} project...[/bold cyan]"
        )

        # Format the command with project name
        command = config.command.format(name=project_name)

        # For interactive tools, show output. Otherwise use spinner.
        success = self.runner.run(
            command=command,
            cwd=parent_dir,
            description=f"Installing {config.display_name}",
            show_output=config.interactive,
        )

        if not success:
            console.print(f"[red]✗ Failed to create project[/red]")
            return False

        # Run post-install commands (unless skipped)
        if config.post_install and not skip_post_install:
            return self._run_post_install(config, project_path)

        return True

    def _run_post_install(self, config: ProjectConfig, project_path: Path) -> bool:
        """Run post-installation commands"""
        console.print(f"\n[yellow]⚙️  Running post-install steps...[/yellow]")

        for cmd in config.post_install:
            # Change to project directory for post-install commands
            success = self.runner.run(
                command=cmd,
                cwd=project_path,
                description=f"Running: {cmd}",
                show_output=False,
            )

            if not success:
                console.print(f"[yellow]⚠ Post-install step failed: {cmd}[/yellow]")
                console.print("[dim]You may need to run this manually[/dim]")
                # Don't fail the whole installation for post-install failures

        return True

    def _handle_custom_install(self, config: ProjectConfig, project_path: Path) -> bool:
        """Handle custom installation types"""
        custom_type = config.command.split(":")[1]

        handlers = {
            "fastapi": self._create_fastapi_project,
            "flask": self._create_flask_project,
            "django-drf": self._create_django_drf_project,
            "express-ts": self._create_express_ts_project,
            "go-gin": self._create_go_gin_project,
            "go-fiber": self._create_go_fiber_project,
            "go-echo": self._create_go_echo_project,
            "rust-axum": self._create_rust_axum_project,
            "rust-actix": self._create_rust_actix_project,
            "python-cli-typer": self._create_python_cli_typer,
            "python-cli-click": self._create_python_cli_click,
            "node-cli": self._create_node_cli,
            "node-cli-ts": self._create_node_cli_ts,
            "go-cli-cobra": self._create_go_cli_cobra,
            "rust-cli-clap": self._create_rust_cli_clap,
        }

        handler = handlers.get(custom_type)
        if handler:
            return handler(project_path)

        console.print(f"[red]Unknown custom installer: {custom_type}[/red]")
        return False

    def _create_fastapi_project(self, project_path: Path) -> bool:
        """Create a minimal FastAPI project"""
        console.print(f"\n[bold cyan]📦 Creating FastAPI project...[/bold cyan]")

        try:
            # Create project structure
            project_path.mkdir(parents=True, exist_ok=True)

            # Create main.py
            main_py = project_path / "main.py"
            main_py.write_text(
                '''"""
FastAPI application
"""
from fastapi import FastAPI

app = FastAPI(title="My API")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello World", "status": "ok"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
'''
            )

            # Create requirements.txt
            requirements = project_path / "requirements.txt"
            requirements.write_text(
                """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
"""
            )

            # Create README.md
            readme = project_path / "README.md"
            readme.write_text(
                f"""# {project_path.name}

FastAPI project created with Scaffold CLI.

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

Visit: http://127.0.0.1:8000
API Docs: http://127.0.0.1:8000/docs

## Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
"""
            )

            # Create .gitignore
            gitignore = project_path / ".gitignore"
            gitignore.write_text(
                """__pycache__/
*.py[cod]
*$py.class
venv/
.env
.venv
.pytest_cache/
.coverage
*.log
"""
            )

            console.print(f"[green]✓ FastAPI project created successfully[/green]")
            return True

        except Exception as e:
            console.print(f"[red]✗ Error creating FastAPI project: {e}[/red]")
            return False

    def _create_flask_project(self, project_path: Path) -> bool:
        """Create Flask project"""
        console.print(f"\n[bold cyan]📦 Creating Flask project...[/bold cyan]")
        try:
            project_path.mkdir(parents=True, exist_ok=True)

            (project_path / "app.py").write_text(
                """from flask import Flask, jsonify

    app = Flask(__name__)

    @app.route('/')
    def home():
        return jsonify({'message': 'Hello World', 'status': 'ok'})

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})

    if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0', port=5000)
    """
            )

            (project_path / "requirements.txt").write_text(
                """Flask==3.0.0
    python-dotenv==1.0.0
    """
            )

            (project_path / "README.md").write_text(
                f"""# {project_path.name}

    Flask API created with Scaffold CLI.

    ## Setup
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

    ## Run
    ```bash
    python app.py
    ```
    Visit: http://127.0.0.1:5000
    """
            )

            console.print(f"[green]✓ Flask project created[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def _create_django_drf_project(self, project_path: Path) -> bool:
        """Create Django REST Framework project"""
        console.print(
            f"\n[bold cyan]📦 Creating Django REST Framework project...[/bold cyan]"
        )
        try:
            project_path.mkdir(parents=True, exist_ok=True)

            (project_path / "requirements.txt").write_text(
                """Django==5.0.0
    djangorestframework==3.14.0
    django-cors-headers==4.3.1
    python-dotenv==1.0.0
    """
            )

            (project_path / "README.md").write_text(
                f"""# {project_path.name}

    Django REST Framework project.

    ## Setup
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    django-admin startproject config .
    python manage.py startapp api
    python manage.py migrate
    python manage.py runserver
    ```
    """
            )

            console.print(f"[green]✓ Django DRF project created[/green]")
            console.print(f"[yellow]→ Run setup commands from README[/yellow]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def _create_express_ts_project(self, project_path: Path) -> bool:
        """Create Express TypeScript project"""
        console.print(
            f"\n[bold cyan]📦 Creating Express + TypeScript project...[/bold cyan]"
        )
        try:
            project_path.mkdir(parents=True, exist_ok=True)

            (project_path / "package.json").write_text(
                f"""{{"name": "{project_path.name}",
    "version": "1.0.0",
    "scripts": {{
        "dev": "ts-node-dev src/index.ts",
        "build": "tsc",
        "start": "node dist/index.js"
    }},
    "dependencies": {{
        "express": "^4.18.2"
    }},
    "devDependencies": {{
        "@types/express": "^4.17.21",
        "@types/node": "^20.0.0",
        "ts-node-dev": "^2.0.0",
        "typescript": "^5.3.0"
    }}
    }}"""
            )

            src_dir = project_path / "src"
            src_dir.mkdir()

            (src_dir / "index.ts").write_text(
                """import express from 'express';

    const app = express();
    app.use(express.json());

    app.get('/', (req, res) => {
    res.json({ message: 'Hello World', status: 'ok' });
    });

    app.get('/health', (req, res) => {
    res.json({ status: 'healthy' });
    });

    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    });
    """
            )

            (project_path / "tsconfig.json").write_text(
                """{
    "compilerOptions": {
        "target": "ES2020",
        "module": "commonjs",
        "outDir": "./dist",
        "rootDir": "./src",
        "strict": true,
        "esModuleInterop": true
    }
    }"""
            )

            console.print(f"[green]✓ Express TypeScript project created[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def _create_go_gin_project(self, project_path: Path) -> bool:
        """Create Go Gin project"""
        console.print(f"\n[bold cyan]📦 Creating Go (Gin) project...[/bold cyan]")
        try:
            project_path.mkdir(parents=True, exist_ok=True)

            (project_path / "main.go").write_text(
                """package main

    import (
        "github.com/gin-gonic/gin"
        "net/http"
    )

    func main() {
        r := gin.Default()

        r.GET("/", func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{"message": "Hello World", "status": "ok"})
        })

        r.GET("/health", func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{"status": "healthy"})
        })

        r.Run(":8080")
    }
    """
            )

            (project_path / "go.mod").write_text(
                f"""module {project_path.name}

    go 1.21

    require github.com/gin-gonic/gin v1.9.1
    """
            )

            (project_path / "README.md").write_text(
                f"""# {project_path.name}

    Go Gin API.

    ## Setup
    ```bash
    go mod download
    ```

    ## Run
    ```bash
    go run main.go
    ```
    Visit: http://localhost:8080
    """
            )

            console.print(f"[green]✓ Go Gin project created[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def _create_go_fiber_project(self, project_path: Path) -> bool:
        """Create Go Fiber project"""
        console.print(f"\n[bold cyan]📦 Creating Go (Fiber) project...[/bold cyan]")
        try:
            project_path.mkdir(parents=True, exist_ok=True)

            (project_path / "main.go").write_text(
                """package main

    import (
        "github.com/gofiber/fiber/v2"
        "log"
    )

    func main() {
        app := fiber.New()

        app.Get("/", func(c *fiber.Ctx) error {
            return c.JSON(fiber.Map{"message": "Hello World", "status": "ok"})
        })

        app.Get("/health", func(c *fiber.Ctx) error {
            return c.JSON(fiber.Map{"status": "healthy"})
        })

        log.Fatal(app.Listen(":8080"))
    }
    """
            )

            (project_path / "go.mod").write_text(
                f"""module {project_path.name}

    go 1.21

    require github.com/gofiber/fiber/v2 v2.51.0
    """
            )

            console.print(f"[green]✓ Go Fiber project created[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def _create_go_echo_project(self, project_path: Path) -> bool:
        """Create Go Echo project"""
        console.print(f"\n[bold cyan]📦 Creating Go (Echo) project...[/bold cyan]")
        try:
            project_path.mkdir(parents=True, exist_ok=True)

            (project_path / "main.go").write_text(
                """package main

    import (
        "github.com/labstack/echo/v4"
        "net/http"
    )

    func main() {
        e := echo.New()

        e.GET("/", func(c echo.Context) error {
            return c.JSON(http.StatusOK, map[string]string{"message": "Hello World", "status": "ok"})
        })

        e.GET("/health", func(c echo.Context) error {
            return c.JSON(http.StatusOK, map[string]string{"status": "healthy"})
        })

        e.Start(":8080")
    }
    """
            )

            (project_path / "go.mod").write_text(
                f"""module {project_path.name}

    go 1.21

    require github.com/labstack/echo/v4 v4.11.4
    """
            )

            console.print(f"[green]✓ Go Echo project created[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def _create_rust_axum_project(self, project_path: Path) -> bool:
        """Create Rust Axum project"""
        console.print(f"\n[bold cyan]📦 Creating Rust (Axum) project...[/bold cyan]")
        try:

            result = subprocess.run(
                ["cargo", "new", project_path.name, "--bin"],
                cwd=project_path.parent,
                capture_output=True,
            )
            if result.returncode != 0:
                console.print(f"[red]✗ Cargo init failed[/red]")
                return False

            cargo_toml = project_path / "Cargo.toml"
            content = cargo_toml.read_text()
            content += '\n[dependencies]\naxum = "0.7"\ntokio = { version = "1", features = ["full"] }\nserde = { version = "1.0", features = ["derive"] }\nserde_json = "1.0"\n'
            cargo_toml.write_text(content)

            (project_path / "src" / "main.rs").write_text(
                """use axum::{routing::get, Json, Router};
    use serde::{Deserialize, Serialize};

    #[derive(Serialize, Deserialize)]
    struct Response {
        message: String,
        status: String,
    }

    async fn root() -> Json<Response> {
        Json(Response { message: "Hello World".to_string(), status: "ok".to_string() })
    }

    async fn health() -> Json<Response> {
        Json(Response { message: "".to_string(), status: "healthy".to_string() })
    }

    #[tokio::main]
    async fn main() {
        let app = Router::new()
            .route("/", get(root))
            .route("/health", get(health));
        
        let listener = tokio::net::TcpListener::bind("0.0.0.0:8000").await.unwrap();
        println!("Server running on http://localhost:8000");
        axum::serve(listener, app).await.unwrap();
    }
    """
            )

            console.print(f"[green]✓ Rust Axum project created[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def _create_rust_actix_project(self, project_path: Path) -> bool:
        """Create Rust Actix-web project"""
        console.print(
            f"\n[bold cyan]📦 Creating Rust (Actix-web) project...[/bold cyan]"
        )
        try:

            result = subprocess.run(
                ["cargo", "new", project_path.name, "--bin"],
                cwd=project_path.parent,
                capture_output=True,
            )
            if result.returncode != 0:
                console.print(f"[red]✗ Cargo init failed[/red]")
                return False

            cargo_toml = project_path / "Cargo.toml"
            content = cargo_toml.read_text()
            content += '\n[dependencies]\nactix-web = "4"\nserde = { version = "1.0", features = ["derive"] }\n'
            cargo_toml.write_text(content)

            (project_path / "src" / "main.rs").write_text(
                """use actix_web::{get, web, App, HttpServer, Responder};
    use serde::{Deserialize, Serialize};

    #[derive(Serialize, Deserialize)]
    struct Response {
        message: String,
        status: String,
    }

    #[get("/")]
    async fn root() -> impl Responder {
        web::Json(Response { message: "Hello World".to_string(), status: "ok".to_string() })
    }

    #[get("/health")]
    async fn health() -> impl Responder {
        web::Json(Response { message: "".to_string(), status: "healthy".to_string() })
    }

    #[actix_web::main]
    async fn main() -> std::io::Result<()> {
        println!("Server running on http://localhost:8000");
        HttpServer::new(|| App::new().service(root).service(health))
            .bind(("0.0.0.0", 8000))?
            .run()
            .await
    }
    """
            )

            console.print(f"[green]✓ Rust Actix-web project created[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    # CLI APP INSTALLERS

    def _create_python_cli_typer(self, project_path: Path) -> bool:
        """Create Python CLI with Typer"""
        console.print(f"\n[bold cyan]📦 Creating Python CLI (Typer)...[/bold cyan]")
        try:
            project_path.mkdir(parents=True, exist_ok=True)

            (project_path / "cli.py").write_text(
                '''import typer
    from rich.console import Console

    app = typer.Typer()
    console = Console()

    @app.command()
    def hello(name: str = typer.Option("World", help="Name to greet")):
        """Say hello"""
        console.print(f"[green]Hello {name}![/green]")

    @app.command()
    def goodbye(name: str = "World"):
        """Say goodbye"""
        console.print(f"[yellow]Goodbye {name}![/yellow]")

    if __name__ == "__main__":
        app()
    '''
            )

            (project_path / "requirements.txt").write_text(
                """typer[all]==0.12.0
    rich==13.7.0
    """
            )

            (project_path / "README.md").write_text(
                f"""# {project_path.name}

    Python CLI app using Typer.

    ## Setup
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

    ## Run
    ```bash
    python cli.py hello --name "Your Name"
    python cli.py goodbye
    ```
    """
            )

            console.print(f"[green]✓ Python CLI (Typer) created[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def _create_python_cli_click(self, project_path: Path) -> bool:
        """Create Python CLI with Click"""
        console.print(f"\n[bold cyan]📦 Creating Python CLI (Click)...[/bold cyan]")
        try:
            project_path.mkdir(parents=True, exist_ok=True)

            (project_path / "cli.py").write_text(
                '''import click

    @click.group()
    def cli():
        """My CLI application"""
        pass

    @cli.command()
    @click.option('--name', default='World', help='Name to greet')
    def hello(name):
        """Say hello"""
        click.echo(f'Hello {name}!')

    @cli.command()
    @click.argument('name', default='World')
    def goodbye(name):
        """Say goodbye"""
        click.echo(f'Goodbye {name}!')

    if __name__ == '__main__':
        cli()
    '''
            )

            (project_path / "requirements.txt").write_text(
                """click==8.1.7
    """
            )

            console.print(f"[green]✓ Python CLI (Click) created[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def _create_node_cli(self, project_path: Path) -> bool:
        """Create Node.js CLI"""
        console.print(f"\n[bold cyan]📦 Creating Node.js CLI...[/bold cyan]")
        try:
            project_path.mkdir(parents=True, exist_ok=True)

            (project_path / "package.json").write_text(
                f"""{{"name": "{project_path.name}",
    "version": "1.0.0",
    "bin": {{
        "{project_path.name}": "./cli.js"
    }},
    "dependencies": {{
        "commander": "^11.1.0",
        "chalk": "^4.1.2"
    }}
    }}"""
            )

            (project_path / "cli.js").write_text(
                """#!/usr/bin/env node
    const { program } = require('commander');
    const chalk = require('chalk');

    program
    .name('mycli')
    .description('My CLI application')
    .version('1.0.0');

    program
    .command('hello')
    .description('Say hello')
    .option('-n, --name <name>', 'name to greet', 'World')
    .action((options) => {
        console.log(chalk.green(`Hello ${options.name}!`));
    });

    program
    .command('goodbye')
    .description('Say goodbye')
    .argument('[name]', 'name', 'World')
    .action((name) => {
        console.log(chalk.yellow(`Goodbye ${name}!`));
    });

    program.parse();
    """
            )

            console.print(f"[green]✓ Node.js CLI created[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def _create_node_cli_ts(self, project_path: Path) -> bool:
        """Create Node.js CLI with TypeScript"""
        console.print(
            f"\n[bold cyan]📦 Creating Node.js CLI (TypeScript)...[/bold cyan]"
        )
        try:
            project_path.mkdir(parents=True, exist_ok=True)

            (project_path / "package.json").write_text(
                f"""{{"name": "{project_path.name}",
    "version": "1.0.0",
    "bin": {{
        "{project_path.name}": "./dist/cli.js"
    }},
    "scripts": {{
        "build": "tsc",
        "dev": "ts-node src/cli.ts"
    }},
    "dependencies": {{
        "commander": "^11.1.0",
        "chalk": "^4.1.2"
    }},
    "devDependencies": {{
        "@types/node": "^20.0.0",
        "ts-node": "^10.9.2",
        "typescript": "^5.3.0"
    }}
    }}"""
            )

            src_dir = project_path / "src"
            src_dir.mkdir()

            (src_dir / "cli.ts").write_text(
                """#!/usr/bin/env node
    import { program } from 'commander';
    import chalk from 'chalk';

    program
    .name('mycli')
    .description('My CLI application')
    .version('1.0.0');

    program
    .command('hello')
    .description('Say hello')
    .option('-n, --name <name>', 'name to greet', 'World')
    .action((options: { name: string }) => {
        console.log(chalk.green(`Hello ${options.name}!`));
    });

    program.parse();
    """
            )

            (project_path / "tsconfig.json").write_text(
                """{
    "compilerOptions": {
        "target": "ES2020",
        "module": "commonjs",
        "outDir": "./dist",
        "rootDir": "./src",
        "strict": true
    }
    }"""
            )

            console.print(f"[green]✓ Node.js CLI (TypeScript) created[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def _create_go_cli_cobra(self, project_path: Path) -> bool:
        """Create Go CLI with Cobra"""
        console.print(f"\n[bold cyan]📦 Creating Go CLI (Cobra)...[/bold cyan]")
        try:
            project_path.mkdir(parents=True, exist_ok=True)

            (project_path / "main.go").write_text(
                """package main

    import (
        "fmt"
        "github.com/spf13/cobra"
        "os"
    )

    var rootCmd = &cobra.Command{
        Use:   "mycli",
        Short: "My CLI application",
    }

    var helloCmd = &cobra.Command{
        Use:   "hello",
        Short: "Say hello",
        Run: func(cmd *cobra.Command, args []string) {
            name, _ := cmd.Flags().GetString("name")
            fmt.Printf("Hello %s!\\n", name)
        },
    }

    func init() {
        helloCmd.Flags().StringP("name", "n", "World", "Name to greet")
        rootCmd.AddCommand(helloCmd)
    }

    func main() {
        if err := rootCmd.Execute(); err != nil {
            os.Exit(1)
        }
    }
    """
            )

            (project_path / "go.mod").write_text(
                f"""module {project_path.name}

    go 1.21

    require github.com/spf13/cobra v1.8.0
    """
            )

            console.print(f"[green]✓ Go CLI (Cobra) created[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def _create_rust_cli_clap(self, project_path: Path) -> bool:
        """Create Rust CLI with Clap"""
        console.print(f"\n[bold cyan]📦 Creating Rust CLI (Clap)...[/bold cyan]")
        try:

            result = subprocess.run(
                ["cargo", "new", project_path.name, "--bin"],
                cwd=project_path.parent,
                capture_output=True,
            )
            if result.returncode != 0:
                console.print(f"[red]✗ Cargo init failed[/red]")
                return False

            cargo_toml = project_path / "Cargo.toml"
            content = cargo_toml.read_text()
            content += (
                '\n[dependencies]\nclap = { version = "4.4", features = ["derive"] }\n'
            )
            cargo_toml.write_text(content)

            (project_path / "src" / "main.rs").write_text(
                """use clap::{Parser, Subcommand};

    #[derive(Parser)]
    #[command(name = "mycli")]
    #[command(about = "My CLI application", long_about = None)]
    struct Cli {
        #[command(subcommand)]
        command: Commands,
    }

    #[derive(Subcommand)]
    enum Commands {
        /// Say hello
        Hello {
            /// Name to greet
            #[arg(short, long, default_value = "World")]
            name: String,
        },
    }

    fn main() {
        let cli = Cli::parse();

        match cli.command {
            Commands::Hello { name } => {
                println!("Hello {}!", name);
            }
        }
    }
    """
            )

            console.print(f"[green]✓ Rust CLI (Clap) created[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False
