# Changelog

All notable changes to Atlas JV Planning OS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/SPEC.html).

## [Unreleased]

### Added
- Comprehensive documentation suite (README, CONTRIBUTING, etc.)
- Enhanced UI with emoji icons and workflow diagrams
- Improved onboarding flow in Home page
- Better separation between app.py (landing) and Home page (guidance)

### Changed
- Refactored page modules to use src/ modules for better separation
- Updated README with installation instructions and better structure
- Enhanced error handling and user feedback

### Fixed
- Minor type annotation issues
- Improved test coverage

## [1.0.0] - 2026-04-03

### Added
- Initial release of Atlas JV Planning OS
- Complete synthetic planning workflow simulation
- 5 core workflow modules (Planning Intake, Economics, KPI Dashboard, Mid-Year Update, Planning Database)
- 4 supporting transparency pages (Home, Methodology, Data Dictionary, Legal)
- SQLite database with synthetic data generation
- Comprehensive test suite
- Modular Python architecture
- Streamlit-based web interface
- Full documentation and legal disclaimers

### Features
- Planning assumption capture and validation
- Discounted cash flow economic evaluation
- Monthly KPI tracking and reporting
- Mid-year reforecast simulation
- Database exploration and version comparison
- 100% synthetic data with full traceability
- Educational methodology explanations
- Interactive data dictionary
- Legal safety and limitations documentation

### Technical
- Python 3.8+ compatibility
- Streamlit web framework
- SQLite relational database
- Pandas/NumPy for data processing
- Plotly for visualizations
- pytest for testing
- Faker for synthetic data generation
- Modular src/ architecture
- Type hints and documentation

---

**Legend:**
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities