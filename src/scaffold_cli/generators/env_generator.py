"""
Environment variable setup and generation
"""

from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
import questionary

console = Console()


class EnvGenerator:
    """Handles .env file generation and configuration"""

    # Predefined service configurations
    SERVICES = {
        "database": {
            "postgres": {
                "DATABASE_URL": "postgresql://user:password@localhost:5432/dbname",
                "DB_HOST": "localhost",
                "DB_PORT": "5432",
                "DB_NAME": "mydb",
                "DB_USER": "user",
                "DB_PASSWORD": "password",
            },
            "mysql": {
                "DATABASE_URL": "mysql://user:password@localhost:3306/dbname",
                "DB_HOST": "localhost",
                "DB_PORT": "3306",
                "DB_NAME": "mydb",
                "DB_USER": "user",
                "DB_PASSWORD": "password",
            },
            "mongodb": {
                "MONGODB_URL": "mongodb://localhost:27017/mydb",
                "MONGO_HOST": "localhost",
                "MONGO_PORT": "27017",
                "MONGO_DB": "mydb",
            },
            "sqlite": {"DATABASE_URL": "sqlite:///./app.db"},
        },
        "email": {
            "smtp": {
                "EMAIL_HOST": "smtp.gmail.com",
                "EMAIL_PORT": "587",
                "EMAIL_USER": "your-email@gmail.com",
                "EMAIL_PASSWORD": "your-app-password",
                "EMAIL_USE_TLS": "True",
            },
            "sendgrid": {
                "SENDGRID_API_KEY": "your-sendgrid-api-key",
                "FROM_EMAIL": "noreply@yourdomain.com",
            },
        },
        "payment": {
            "mpesa": {
                "MPESA_CONSUMER_KEY": "your-consumer-key",
                "MPESA_CONSUMER_SECRET": "your-consumer-secret",
                "MPESA_SHORTCODE": "your-shortcode",
                "MPESA_PASSKEY": "your-passkey",
                "MPESA_ENVIRONMENT": "sandbox",  # or 'production'
            },
            "stripe": {
                "STRIPE_PUBLIC_KEY": "pk_test_...",
                "STRIPE_SECRET_KEY": "sk_test_...",
                "STRIPE_WEBHOOK_SECRET": "whsec_...",
            },
        },
        "storage": {
            "s3": {
                "AWS_ACCESS_KEY_ID": "your-access-key",
                "AWS_SECRET_ACCESS_KEY": "your-secret-key",
                "AWS_BUCKET_NAME": "your-bucket",
                "AWS_REGION": "us-east-1",
            }
        },
    }

    # Base variables by project type
    BASE_VARS = {
        "react": {
            "VITE_API_URL": "http://localhost:8000",
            "VITE_APP_NAME": "{project_name}",
        },
        "nextjs": {
            "NEXT_PUBLIC_API_URL": "http://localhost:8000",
            "NEXTAUTH_SECRET": "your-secret-key-here",
            "NEXTAUTH_URL": "http://localhost:3000",
        },
        "django": {
            "SECRET_KEY": "django-insecure-change-this-in-production",
            "DEBUG": "True",
            "ALLOWED_HOSTS": "localhost,127.0.0.1",
            "CORS_ALLOWED_ORIGINS": "http://localhost:3000,http://localhost:5173",
        },
        "fastapi": {
            "SECRET_KEY": "your-secret-key-here",
            "DEBUG": "True",
            "CORS_ORIGINS": "http://localhost:3000,http://localhost:5173",
        },
        "express": {
            "PORT": "3001",
            "NODE_ENV": "development",
            "JWT_SECRET": "your-jwt-secret",
        },
    }

    def __init__(self, project_path: Path, project_type: str, project_name: str):
        self.project_path = project_path
        self.project_type = project_type
        self.project_name = project_name
        self.env_vars: Dict[str, str] = {}

    def interactive_setup(self) -> bool:
        """Interactive environment setup"""
        console.print("\n[bold cyan]🔧 Environment Configuration[/bold cyan]")
        console.print(
            "[dim]Configure services and integrations for your project[/dim]\n"
        )

        # Start with base variables
        self._add_base_variables()

        # Ask about services
        if questionary.confirm(
            "Would you like to configure additional services?", default=True
        ).ask():
            self._configure_services()

        return True

    def _add_base_variables(self):
        """Add base environment variables for the project type"""
        base_vars = self.BASE_VARS.get(self.project_type, {})
        for key, value in base_vars.items():
            formatted_value = value.replace("{project_name}", self.project_name)
            self.env_vars[key] = formatted_value

    def _configure_services(self):
        """Interactive service configuration"""
        # Database
        if questionary.confirm("🗄️  Configure database?", default=False).ask():
            db_type = questionary.select(
                "Select database:",
                choices=["PostgreSQL", "MySQL", "MongoDB", "SQLite", "Skip"],
            ).ask()

            if db_type != "Skip":
                db_key = db_type.lower().replace("sql", "")
                if db_key in self.SERVICES["database"]:
                    self._add_service_vars("database", db_key)

        # Email
        if questionary.confirm("📧 Configure email service?", default=False).ask():
            email_type = questionary.select(
                "Select email provider:", choices=["SMTP", "SendGrid", "Skip"]
            ).ask()

            if email_type != "Skip":
                self._add_service_vars("email", email_type.lower())

        # Payment
        if questionary.confirm("💳 Configure payment gateway?", default=False).ask():
            payment_type = questionary.select(
                "Select payment provider:", choices=["M-Pesa", "Stripe", "Skip"]
            ).ask()

            if payment_type != "Skip":
                payment_key = payment_type.lower().replace("-", "")
                if payment_key in self.SERVICES["payment"]:
                    self._add_service_vars("payment", payment_key)

        # Storage
        if questionary.confirm("☁️  Configure cloud storage?", default=False).ask():
            storage_type = questionary.select(
                "Select storage provider:", choices=["AWS S3", "Skip"]
            ).ask()

            if storage_type != "Skip":
                self._add_service_vars("storage", "s3")

    def _add_service_vars(self, category: str, service: str):
        """Add service-specific variables"""
        service_vars = self.SERVICES[category][service]
        self.env_vars.update(service_vars)
        console.print(f"[green]✓[/green] Added {service.upper()} configuration")

    def generate_files(self) -> bool:
        """Generate .env and .env.example files"""
        try:
            # Generate .env.example with all variables
            example_path = self.project_path / ".env.example"
            example_content = self._format_env_content(show_values=False)
            example_path.write_text(example_content)
            console.print(f"[green]✓[/green] Created .env.example")

            # Generate .env with actual values
            env_path = self.project_path / ".env"
            if env_path.exists():
                if not questionary.confirm(
                    ".env already exists. Overwrite?", default=False
                ).ask():
                    console.print("[yellow]⚠[/yellow] Skipped .env creation")
                    return True

            env_content = self._format_env_content(show_values=True)
            env_path.write_text(env_content)
            console.print(f"[green]✓[/green] Created .env")

            return True

        except Exception as e:
            console.print(f"[red]✗[/red] Failed to create env files: {e}")
            return False

    def _format_env_content(self, show_values: bool = True) -> str:
        """Format environment variables as file content"""
        lines = [
            "# Environment Configuration",
            f"# Project: {self.project_name}",
            "# Generated by Scaffold CLI",
            "",
        ]

        # Group by category
        current_category = None
        for key in sorted(self.env_vars.keys()):
            # Detect category from key prefix
            if key.startswith(("DATABASE", "DB_", "MONGO", "POSTGRES", "MYSQL")):
                category = "Database"
            elif key.startswith(("EMAIL", "SENDGRID", "SMTP")):
                category = "Email"
            elif key.startswith(("MPESA", "STRIPE")):
                category = "Payment"
            elif key.startswith(("AWS", "S3")):
                category = "Storage"
            else:
                category = "Application"

            if category != current_category:
                lines.append(f"\n# {category}")
                current_category = category

            value = self.env_vars[key] if show_values else ""
            lines.append(f"{key}={value}")

        return "\n".join(lines) + "\n"

    def get_summary(self) -> Dict[str, any]:
        """Get summary of configured environment"""
        categories = set()
        for key in self.env_vars.keys():
            if key.startswith(("DATABASE", "DB_")):
                categories.add("Database")
            elif key.startswith("EMAIL"):
                categories.add("Email")
            elif key.startswith(("MPESA", "STRIPE")):
                categories.add("Payment")
            elif key.startswith("AWS"):
                categories.add("Storage")

        return {"total_vars": len(self.env_vars), "categories": list(categories)}
