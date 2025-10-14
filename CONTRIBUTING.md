# Contributing to SITR

Thank you for your interest in contributing to SITR (Simple Time Tracker)!

## Project Background

SITR started as a CS50 Final Project that remained unfinished for a long time. After revisiting the design, it became clear that the architecture was solid enough to bring to completion. The project now serves as both a useful tool and a demonstration of clean software engineering practices.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Virtual environment (venv)
- Git

### Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/CS50TimeTracker.git
   cd CS50TimeTracker
   ```

3. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # or: .venv\Scripts\activate on Windows
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run tests:
   ```bash
   pytest tests/
   ```

## Code Structure

```
CS50TimeTracker/
├── sitr_cli.py                    # CLI interface (Typer)
├── sitr_api.py                    # FastAPI server
├── sitr_models.py                 # Domain models (SQLModel)
├── api_client.py                  # HTTP client
├── config_manager.py              # Configuration system
├── server_manager.py              # Server lifecycle
├── time_management_service.py     # Business logic
├── database_repositories.py       # Data access layer
├── database_manager.py            # Database connection
├── enums.py                       # Enumerations
├── tests/                         # Test files
└── docs/                          # Additional documentation
```

## Architecture Principles

SITR follows **Domain-Driven Design (DDD)** with clear layer separation:

1. **Presentation Layer** - CLI interface
2. **API Layer** - FastAPI endpoints
3. **Service Layer** - Business logic
4. **Repository Layer** - Data access
5. **Domain Layer** - Models and entities

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

## Contribution Guidelines

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions focused and small
- Use meaningful variable names

### Commit Messages

Follow conventional commits:

```
feat: Add export to CSV functionality
fix: Correct timezone handling in timestamps
docs: Update API documentation
test: Add tests for break continuation
refactor: Simplify project handover logic
```

### Pull Request Process

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes with clear commits

3. Write/update tests as needed

4. Update documentation if you're changing functionality

5. Run tests and ensure they pass:
   ```bash
   pytest tests/
   ```

6. Push to your fork and submit a pull request

7. Wait for review and address feedback

### What to Contribute

#### 🟢 Great First Issues

- Add more CLI output formatting
- Improve error messages
- Add more unit tests
- Improve documentation
- Add command aliases

#### 🟡 Medium Difficulty

- Export functionality (CSV, JSON)
- Report generation
- Timezone handling improvements
- Additional API endpoints
- Performance optimizations

#### 🔴 Advanced

- Web UI (React/Vue)
- Mobile app integration
- Multi-user support
- Authentication system
- Analytics dashboard

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_time_tracking.py
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names
- Test edge cases and error conditions

Example:

```python
def test_project_handover_ends_previous_project():
    """Test that starting a new project ends the currently active one."""
    # Arrange
    service = TimeManagementService(...)
    
    # Act
    service.start_project(user_id=1, project_name="Project A")
    service.start_project(user_id=1, project_name="Project B")
    
    # Assert
    # Verify Project A was ended automatically
```

## Code Review Process

All contributions go through code review:

1. **Functionality** - Does it work as intended?
2. **Tests** - Are there appropriate tests?
3. **Documentation** - Is it documented?
4. **Code Quality** - Is it clean and maintainable?
5. **Architecture** - Does it fit the design?

## Questions or Issues?

- Check existing [issues](https://github.com/TechPrototyper/CS50TimeTracker/issues)
- Create a new issue if your question isn't answered
- Join discussions in issue comments

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be acknowledged in the project documentation and README.

---

Thank you for helping make SITR better! 🙏
