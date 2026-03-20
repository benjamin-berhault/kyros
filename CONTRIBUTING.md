# Contributing to Kyros

Thank you for your interest in contributing to Kyros! This guide will help you get started.

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Git

### Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/kyros.git
   cd kyros
   ```

2. **Install development dependencies**
   ```bash
   make install-dev
   # or manually:
   pip install -r requirements-dev.txt
   ```

3. **Run tests to verify setup**
   ```bash
   make test
   ```

4. **Deploy a test environment**
   ```bash
   make level-1
   ```

## Project Structure

```
kyros/
├── services/           # Service YAML definitions
├── presets/            # Environment presets (level-0 to level-4)
├── docker/             # Dockerfiles and configurations
├── tests/              # Test suite
├── poc/                # Web deployment interface
├── data/               # Sample data and workspaces
├── kyros-cli.py        # Interactive CLI
└── generate-docker-compose.sh  # Compose file generator
```

## Making Changes

### Adding a New Service

1. Create a service definition in `services/your-service.yml`:
   ```yaml
   your-service:
     container_name: your-service
     build:
       context: ./docker/your-service
     ports:
       - "8080:8080"
     healthcheck:
       test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
       interval: 30s
       timeout: 10s
       retries: 3
       start_period: 30s
     deploy:
       resources:
         limits:
           memory: 1G
           cpus: "1.0"
     networks:
       - my-network
   ```

2. Create the Dockerfile in `docker/your-service/Dockerfile`

3. Add the service toggle to presets:
   - Add `INCLUDE_YOUR_SERVICE=true/false` to each `presets/level-*.env`

4. Update `kyros-cli.py` to include the new component

5. Add tests for the new service

### Modifying Services

- Always add healthchecks to services
- Include resource limits (memory and CPU)
- Test changes with `make validate` before committing

## Code Style

### Python

- Follow PEP 8 guidelines
- Use type hints where practical
- Keep functions focused and small
- Run `make lint` before committing

### YAML

- Use 2-space indentation
- Include comments for non-obvious configurations
- Validate with `make validate`

### Commit Messages

Format: `<type>: <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat: add Kafka service with healthcheck
fix: correct Superset port mapping
docs: update README with new deployment options
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
python -m pytest tests/test_services.py -v
```

### Writing Tests

- Place tests in `tests/` directory
- Follow naming convention: `test_*.py`
- Use descriptive test names
- Add fixtures to `conftest.py`

Example:
```python
def test_service_has_healthcheck(services_dir):
    """Verify new service has healthcheck defined."""
    service_file = services_dir / "your-service.yml"
    content = service_file.read_text()
    assert "healthcheck" in content
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feat/your-feature
   ```

2. **Make your changes**
   - Keep commits atomic and focused
   - Update tests as needed
   - Update documentation if required

3. **Validate your changes**
   ```bash
   make lint
   make validate
   make test
   ```

4. **Push and create PR**
   ```bash
   git push origin feat/your-feature
   ```

5. **PR Requirements**
   - Tests pass in CI
   - Code follows style guidelines
   - Documentation updated if needed
   - Commits are clean and well-described

## Architecture Decisions

When proposing significant changes, consider:

1. **Does it align with Kyros philosophy?**
   - "Start simple. Scale when justified."
   - Progressive architecture levels
   - Cost transparency

2. **Which level does this belong to?**
   - Level 0: Local development
   - Level 1: Team collaboration
   - Level 2: Data lake capabilities
   - Level 3: Distributed processing
   - Level 4: Enterprise features

3. **Is it cloud-agnostic?**
   - Avoid vendor lock-in
   - Use standard interfaces where possible

## Getting Help

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Join discussions for architectural questions

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
