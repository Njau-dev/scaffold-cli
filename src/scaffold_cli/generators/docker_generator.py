"""
Docker configuration generation
"""

from pathlib import Path
from typing import Optional
from rich.console import Console

console = Console()


class DockerGenerator:
    """Generates Docker configurations"""

    def __init__(self, project_path: Path, project_type: str, project_name: str):
        self.project_path = project_path
        self.project_type = project_type
        self.project_name = project_name

    def generate_dockerfile(self) -> bool:
        """Generate Dockerfile based on project type"""
        try:
            dockerfile_path = self.project_path / "Dockerfile"

            if self.project_type in ["react", "nextjs", "vue", "nodejs"]:
                content = self._generate_node_dockerfile()
            elif self.project_type in ["django", "fastapi", "flask", "python"]:
                content = self._generate_python_dockerfile()
            else:
                console.print(
                    f"[yellow]⚠[/yellow] No Dockerfile template for {self.project_type}"
                )
                return False

            dockerfile_path.write_text(content)
            console.print(f"[green]✓[/green] Created Dockerfile")

            # Also create .dockerignore
            self._generate_dockerignore()

            return True

        except Exception as e:
            console.print(f"[red]✗[/red] Failed to create Dockerfile: {e}")
            return False

    def generate_docker_compose(self, with_database: bool = False) -> bool:
        """Generate docker-compose.yml"""
        try:
            compose_path = self.project_path / "docker-compose.yml"

            if self.project_type == "monorepo":
                content = self._generate_monorepo_compose(with_database)
            else:
                content = self._generate_single_compose(with_database)

            compose_path.write_text(content)
            console.print(f"[green]✓[/green] Created docker-compose.yml")

            return True

        except Exception as e:
            console.print(f"[red]✗[/red] Failed to create docker-compose.yml: {e}")
            return False

    def _generate_node_dockerfile(self) -> str:
        """Generate Dockerfile for Node.js projects"""
        if self.project_type == "nextjs":
            return f"""# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Build
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy built assets
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
"""
        else:  # React/Vue with Vite
            return f"""# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Build
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"""

    def _generate_python_dockerfile(self) -> str:
        """Generate Dockerfile for Python projects"""
        if self.project_type == "django":
            return f"""FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "{self.project_name}.wsgi:application"]
"""
        elif self.project_type == "fastapi":
            return """FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

EXPOSE 8000

# Run uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        else:  # Generic Python
            return """FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

CMD ["python", "main.py"]
"""

    def _generate_dockerignore(self):
        """Generate .dockerignore file"""
        content = """# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.venv/
*.egg-info/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# Build outputs
dist/
build/
.next/
out/

# OS
.DS_Store
Thumbs.db

# Tests
coverage/
.pytest_cache/
"""
        dockerignore_path = self.project_path / ".dockerignore"
        dockerignore_path.write_text(content)
        console.print(f"[green]✓[/green] Created .dockerignore")

    def _generate_single_compose(self, with_database: bool) -> str:
        """Generate docker-compose.yml for single project"""
        service_name = self.project_name.replace("-", "_")

        compose = f"""version: '3.8'

services:
  {service_name}:
    build: .
    ports:"""

        if self.project_type in ["react", "vue"]:
            compose += '\n      - "80:80"'
        elif self.project_type == "nextjs":
            compose += '\n      - "3000:3000"'
        else:  # Python/Node APIs
            compose += '\n      - "8000:8000"'

        compose += f"""
    env_file:
      - .env
    volumes:
      - .:/app
    restart: unless-stopped
"""

        if with_database:
            compose += """
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  pgdata:
"""

        return compose

    def _generate_monorepo_compose(self, with_database: bool) -> str:
        """Generate docker-compose.yml for monorepo"""
        compose = """version: '3.8'

services:
  web:
    build: ./web
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://api:8000
    volumes:
      - ./web:/app
      - /app/node_modules
    depends_on:
      - api
    restart: unless-stopped

  api:
    build: ./api
    ports:
      - "8000:8000"
    env_file:
      - ./api/.env
    volumes:
      - ./api:/app
    restart: unless-stopped
"""

        if with_database:
            compose += """    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  pgdata:
"""

        return compose

    def generate_nginx_config(self):
        """Generate nginx.conf for React/Vue projects"""
        if self.project_type not in ["react", "vue"]:
            return

        nginx_config = """server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
"""
        nginx_path = self.project_path / "nginx.conf"
        nginx_path.write_text(nginx_config)
        console.print(f"[green]✓[/green] Created nginx.conf")
