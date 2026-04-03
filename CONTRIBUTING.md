# Contributing to Atlas JV Planning OS

Thank you for your interest in contributing to Atlas JV Planning OS! This project is designed as a portfolio demonstration piece, but we welcome educational contributions that align with the project's goals.

## Code of Conduct

This project follows a simple code of conduct:
- Be respectful and constructive
- Focus on educational and portfolio value
- Maintain data safety and synthetic-only approach
- Keep discussions professional

## How to Contribute

### 1. Reporting Issues

If you find bugs or have suggestions:
- Check existing issues first
- Use clear, descriptive titles
- Provide steps to reproduce
- Include relevant screenshots/logs

### 2. Feature Requests

For new features:
- Explain the educational value
- Consider alignment with synthetic data approach
- Provide use case examples
- Think about portfolio demonstration impact

### 3. Code Contributions

#### Prerequisites
- Python 3.8+
- Familiarity with Streamlit, Pandas, SQLite
- Understanding of synthetic data practices

#### Development Setup
```bash
# Clone and setup
git clone https://github.com/yourusername/atlas_jv_planning_os.git
cd atlas_jv_planning_os
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run tests
pytest

# Run the app
streamlit run app.py
```

#### Coding Standards
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write descriptive commit messages
- Add tests for new functionality
- Document complex logic

#### Data Safety Rules
- **Never** introduce real data or entities
- All additions must be synthetic/fictitious
- Maintain traceability to generation logic
- Update documentation for any data changes

### 4. Documentation

Help improve documentation by:
- Fixing typos or unclear explanations
- Adding code examples
- Improving installation instructions
- Enhancing API documentation

## Development Workflow

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Make** your changes with tests
4. **Run** the full test suite: `pytest`
5. **Commit** with clear messages
6. **Push** to your fork
7. **Submit** a pull request

## Testing

- Run `pytest` to execute all tests
- Aim for high test coverage on business logic
- Test both success and error cases
- Verify UI functionality manually

## Areas for Contribution

### High Priority
- Bug fixes
- Performance improvements
- Documentation enhancements
- Test coverage expansion

### Medium Priority
- New synthetic data scenarios
- Additional KPI calculations
- Enhanced visualizations
- Mobile responsiveness

### Low Priority (Advanced)
- Multi-user support concepts
- Advanced forecasting models
- Integration with external APIs (synthetic only)
- Performance optimization

## Review Process

Pull requests will be reviewed for:
- Code quality and style
- Test coverage
- Documentation updates
- Data safety compliance
- Educational/portfolio value

## Questions?

For questions about contributing:
- Check existing issues and documentation first
- Create a discussion issue if needed
- Respect the educational focus of the project

Thank you for helping make Atlas JV Planning OS better! 🎯