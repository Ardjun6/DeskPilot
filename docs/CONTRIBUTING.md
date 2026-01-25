# 🤝 Contributing to DeskPilot

Thank you for your interest in contributing to DeskPilot!

---

## 🚀 Quick Start

1. Fork the repository
2. Clone your fork
3. Create a branch for your feature
4. Make your changes
5. Test thoroughly
6. Submit a pull request

---

## 📋 Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/DeskPilot.git
cd DeskPilot

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest black flake8 mypy

# Run the app
python -m deskpilot.main
```

---

## 📁 Project Structure

```
DeskPilot/
├── deskpilot/
│   ├── actions/          # Action execution
│   │   ├── engine.py     # Main action engine
│   │   ├── steps.py      # Step implementations
│   │   └── ...
│   ├── config/           # Configuration
│   │   ├── models.py     # Pydantic models
│   │   └── config_manager.py
│   ├── ui/               # User interface
│   │   ├── views/        # Main views (tabs)
│   │   ├── widgets/      # Reusable widgets
│   │   ├── main_window.py
│   │   └── theme_manager.py
│   ├── utils/            # Utilities
│   └── main.py           # Entry point
├── docs/                 # Documentation
├── tests/                # Tests (coming soon)
└── requirements.txt
```

---

## 🎯 What to Contribute

### Good First Issues
- Fix typos in documentation
- Add more themes
- Improve error messages
- Add step type icons

### Medium Difficulty
- New step types
- UI improvements
- Bug fixes
- Test coverage

### Advanced
- New major features
- Performance optimization
- Plugin system
- Cross-platform support

---

## 📝 Coding Standards

### Python Style
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use Black for formatting

```bash
# Format code
black deskpilot/

# Check style
flake8 deskpilot/

# Check types
mypy deskpilot/
```

### Naming Conventions
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

### Documentation
- Docstrings for all public classes and functions
- Comments for complex logic
- Update docs/ when adding features

---

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=deskpilot
```

### Writing Tests
- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use pytest fixtures

---

## 🔀 Pull Request Process

### Before Submitting
1. Update documentation if needed
2. Add/update tests
3. Run formatters and linters
4. Test manually on Windows

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
How did you test this?

## Screenshots (if UI change)
Before/after screenshots
```

### Review Process
1. Automated checks must pass
2. Code review by maintainer
3. Address feedback
4. Merge!

---

## 🐛 Bug Reports

### Good Bug Report Includes:
1. **Title**: Clear, concise description
2. **Steps to reproduce**: Numbered list
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: Windows version, Python version
6. **Screenshots/logs**: If applicable

### Template
```markdown
**Describe the bug**
A clear description of the bug.

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable.

**Environment:**
- OS: Windows 11
- Python: 3.11.5
- DeskPilot: 1.0.0
```

---

## 💡 Feature Requests

### Good Feature Request Includes:
1. **Problem**: What problem does this solve?
2. **Solution**: Your proposed solution
3. **Alternatives**: Other solutions considered
4. **Context**: Why is this important?

---

## 📜 Code of Conduct

### Be Respectful
- Treat everyone with respect
- No harassment or discrimination
- Constructive criticism only

### Be Collaborative
- Help others learn
- Share knowledge
- Welcome newcomers

### Be Professional
- Stay on topic
- Keep discussions productive
- Accept feedback gracefully

---

## 📞 Getting Help

- **Questions**: Open a Discussion
- **Bugs**: Open an Issue
- **Features**: Open an Issue with "feature" label

---

## 🏆 Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- CHANGELOG.md

---

Thank you for contributing! 🎉

[← Back to README](../README.md)
