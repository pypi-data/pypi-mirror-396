import click
import yaml
from pathlib import Path
from .generators.microservice import MicroserviceGenerator
from .validators import ConfigValidator


@click.group()
@click.version_option()
def cli():
    """ND-SDK - Enterprise Framework & Code Generator"""
    pass


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True), required=True,
              help='Path to configuration YAML file')
@click.option('--output', '-o', type=click.Path(), default='.',
              help='Output directory for generated project')
@click.option('--force', '-f', is_flag=True,
              help='Force overwrite if project exists')
def generate(config, output, force):
    """Generate project from configuration file"""

    try:
        # Load and validate config
        click.echo(f"Loading configuration from {config}...")
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)

        # Validate configuration
        validator = ConfigValidator()
        is_valid, errors = validator.validate(config_data)

        if not is_valid:
            click.echo(click.style("Configuration validation failed:", fg='red'))
            for error in errors:
                click.echo(click.style(f"  • {error}", fg='red'))
            return

        project_type = config_data['project']['type']
        project_name = config_data['project']['name']

        # Check if project exists
        output_path = Path(output) / project_name
        if output_path.exists() and not force:
            click.confirm(
                f"Project '{project_name}' already exists. Overwrite?",
                abort=True
            )

        # Select appropriate generator
        if project_type == 'microservice':
            generator = MicroserviceGenerator(config_data, output)
        else:
            raise ValueError(f"Unknown project type: {project_type}")

        # Generate code
        click.echo(f"Generating {project_type} project '{project_name}'...")
        generator.generate()

        click.echo(click.style(f"\n✓ Project generated successfully!", fg='green'))
        click.echo(f"\nNext steps:")
        click.echo(f"  cd {output_path}")
        click.echo(f"  pip install -r requirements.txt")
        click.echo(f"  python main.py")

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'))
        raise


@cli.command()
@click.option('--type', '-t',
              type=click.Choice(['microservice', 'batch-job', 'worker']),
              default='microservice',
              help='Project type')
@click.option('--output', '-o', default='nd-config.yaml',
              help='Output configuration file name')
def init(type, output):
    """Create a sample configuration file"""

    templates = {
        'microservice': MICROSERVICE_TEMPLATE,
        'batch-job': BATCH_JOB_TEMPLATE,
        'worker': WORKER_TEMPLATE,
    }

    config_path = Path(output)
    if config_path.exists():
        click.confirm(f'{output} already exists. Overwrite?', abort=True)

    with open(config_path, 'w') as f:
        f.write(templates[type].strip())

    click.echo(click.style(f"✓ Created {output}", fg='green'))
    click.echo(f"\nEdit the configuration file and run:")
    click.echo(f"  nd-sdk generate -c {output}")


@cli.command()
def validate(config):
    """Validate a configuration file"""

    try:
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)

        validator = ConfigValidator()
        is_valid, errors = validator.validate(config_data)

        if is_valid:
            click.echo(click.style("✓ Configuration is valid", fg='green'))
        else:
            click.echo(click.style("✗ Configuration has errors:", fg='red'))
            for error in errors:
                click.echo(click.style(f"  • {error}", fg='red'))
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'))


# Configuration templates
MICROSERVICE_TEMPLATE = """
project:
  name: "my-microservice"
  type: "microservice"
  description: "Sample microservice with ND-SDK"
  version: "1.0.0"

modules:
  observability:
    enabled: true
    logging:
      enabled: true
      level: "INFO"
    tracing:
      enabled: true
      provider: "jaeger"
    metrics:
      enabled: true
      provider: "prometheus"

  caching:
    enabled: true
    default_provider: "redis"
    providers:
      redis:
        host: "localhost"
        port: 6379
      inmemory:
        max_size: 1000

  storage:
    enabled: false
    providers:
      - s3

  web_framework: "fastapi"

  exception_handler:
    enabled: true
    include_traceback: true

endpoints:
  - name: "health_check"
    path: "/health"
    method: "GET"
    description: "Health check endpoint"
    params: []
    cache:
      enabled: false

  - name: "create_user"
    path: "/users"
    method: "POST"
    description: "Create a new user"
    params:
      - name: "username"
        type: "str"
        required: true
        min_length: 3
        max_length: 50
      - name: "email"
        type: "str"
        required: true
        pattern: '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$'
      - name: "age"
        type: "int"
        required: false
        default: 0
        min: 0
        max: 150
    cache:
      enabled: false

  - name: "get_user"
    path: "/users/{user_id}"
    method: "GET"
    description: "Get user by ID"
    params:
      - name: "user_id"
        type: "str"
        in: "path"
        required: true
    cache:
      enabled: true
      ttl: 300

  - name: "list_users"
    path: "/users"
    method: "GET"
    description: "List all users with pagination"
    params:
      - name: "page"
        type: "int"
        required: false
        default: 1
        min: 1
      - name: "limit"
        type: "int"
        required: false
        default: 10
        min: 1
        max: 100
    cache:
      enabled: true
      ttl: 60
"""

BATCH_JOB_TEMPLATE = """
project:
  name: "my-batch-job"
  type: "batch-job"
  description: "Sample batch job with ND-SDK"
  version: "1.0.0"

modules:
  observability:
    enabled: true
    logging:
      enabled: true
      level: "INFO"

  storage:
    enabled: true
    providers:
      - s3

jobs:
  - name: "data_processor"
    schedule: "0 0 * * *"  # Daily at midnight
    description: "Process daily data"
    steps:
      - name: "extract"
        type: "extract"
      - name: "transform"
        type: "transform"
      - name: "load"
        type: "load"
"""

WORKER_TEMPLATE = """
project:
  name: "my-worker"
  type: "worker"
  description: "Sample worker service with ND-SDK"
  version: "1.0.0"

modules:
  observability:
    enabled: true

  queue:
    enabled: true
    provider: "rabbitmq"

tasks:
  - name: "process_email"
    queue: "emails"
    retry: 3

  - name: "generate_report"
    queue: "reports"
    retry: 5
"""
