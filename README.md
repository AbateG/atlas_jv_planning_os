# Atlas JV Planning OS

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Synthetic Upstream JV Planning, Economics, and Performance Reporting**

Atlas JV Planning OS is an educational, portfolio-grade web application that simulates selected upstream oil & gas joint venture planning workflows. It uses entirely fictitious entities and 100% synthetic data to demonstrate how structured planning systems can connect business assumption capture, version management, economic evaluation, KPI reporting, and reforecasting.

This project is intentionally simplified for educational purposes but built as a coherent analytical product rather than a static mock-up. It's designed to showcase Python application development skills, modular architecture, and safe synthetic data practices.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Workflow Overview](#workflow-overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Data Governance](#data-governance)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)
- [Disclaimer](#disclaimer)

## Features

### Core Workflow Modules

#### 📝 Planning Intake & Consolidation
- Interactive assumption capture by asset and plan version
- Version management with copy-from functionality
- Real-time business rule validation
- SQLite persistence with issue tracking
- Consolidated planning summaries

#### 💰 Economic Evaluation
- Project-level discounted cash flow (DCF) modeling
- NPV, IRR, and payback period calculations
- Sensitivity analysis with downside/base/upside scenarios
- Editable economic assumptions (oil price, costs, taxes, etc.)
- Results persistence and export

#### 📊 KPI Dashboard
- Monthly production and financial performance tracking
- Venture and asset filtering with interactive charts
- Derived efficiency metrics (unit costs, margins)
- Asset ranking and comparison views
- CSV export functionality

#### 🔄 Mid-Year Update / Reforecast
- YTD actuals vs. H2 assumptions splitting
- Adjustable reforecast parameters
- Original vs. reforecast comparison
- Simplified reforecast workflow simulation

#### 🗄️ Planning Database Explorer
- Direct inspection of synthetic database tables
- Plan version comparison tools
- Validation issue signal review
- Transparent data model exploration

### Supporting Pages

- **🏠 Home**: Guided onboarding and module walkthrough
- **📖 Methodology**: Workflow logic and assumptions explanation
- **📚 Data Dictionary**: Interactive reference for synthetic data model
- **⚖️ Legal & Limitations**: Safe use guidelines and constraints

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/atlas_jv_planning_os.git
   cd atlas_jv_planning_os
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the app**
   Open your browser to `http://localhost:8501`

### First Time Setup

The application will automatically:
- Create the SQLite database
- Generate synthetic data
- Seed initial tables
- Set up default scenarios

No manual configuration required!

## Workflow Overview

Atlas JV Planning OS simulates a connected planning workflow:

1. **Planning Intake** → Capture and validate business assumptions
2. **Economic Evaluation** → Run DCF analysis on synthetic projects
3. **KPI Monitoring** → Track monthly performance against plans
4. **Mid-Year Reforcast** → Adjust H2 assumptions based on YTD actuals
5. **Database Inspection** → Review stored data and validation signals

Each module builds on the previous, demonstrating end-to-end planning system connectivity.

## Technology Stack

- **Frontend**: Streamlit (web UI framework)
- **Backend**: Python 3.8+
- **Database**: SQLite (relational persistence)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Financial Calculations**: numpy-financial
- **Testing**: pytest
- **Synthetic Data**: Faker library
- **Spreadsheet Support**: OpenPyXL

## Project Structure

```
atlas_jv_planning_os/
├── app.py                    # Main Streamlit entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── LICENSE                   # MIT license
├── LEGAL_DISCLAIMER.md       # Legal safety information
├── LIMITATIONS.md            # Model limitations and scope
├── DATA_PROVENANCE.md        # Data governance policies
├── .streamlit/config.toml    # Streamlit configuration
├── assets/                   # Static assets (diagrams, etc.)
├── pages/                    # Streamlit multi-page modules
│   ├── 1_Home.py
│   ├── 2_Planning_Intake.py
│   ├── 3_Economics.py
│   ├── 4_Planning_Database.py
│   ├── 5_KPI_Dashboard.py
│   ├── 6_Mid_Year_Update.py
│   ├── 7_Methodology.py
│   ├── 8_Data_Dictionary.py
│   └── 9_Legal_and_Limitations.py
├── src/                      # Business logic modules
│   ├── __init__.py
│   ├── config.py             # Application configuration
│   ├── constants.py          # App constants and settings
│   ├── db.py                 # Database connection utilities
│   ├── schema.sql            # SQLite schema definition
│   ├── seed.py               # Database seeding logic
│   ├── synthetic_data.py     # Synthetic data generation
│   ├── validation.py         # Business rule validation
│   ├── planning.py           # Planning workflow logic
│   ├── economics.py          # DCF modeling and calculations
│   ├── forecasting.py        # Reforcast and forecasting logic
│   ├── kpi.py                # KPI calculation and aggregation
│   ├── reporting.py          # Report generation utilities
│   ├── ui_helpers.py         # Streamlit UI components
│   └── utils.py              # General utilities
├── data/                     # Data storage
│   ├── atlas_jv_planning.db  # SQLite database
│   └── generated/            # Generated CSV exports
└── tests/                    # Test suite
    ├── test_economics.py
    ├── test_forecasting.py
    ├── test_kpis.py
    ├── test_reporting.py
    └── test_validation.py
```

## Data Governance

All data in Atlas JV Planning OS is 100% synthetic and fictitious:

- **No real entities**: All companies, assets, ventures are invented
- **No confidential data**: No proprietary or internal information used
- **Traceable generation**: All data can be traced to Python generation scripts
- **Safe for portfolio**: Legally clean for professional presentation

See [DATA_PROVENANCE.md](DATA_PROVENANCE.md) for detailed data governance policies.

## Limitations

This is an educational simulation, not a production system:

- Simplified economic models (no depreciation, complex taxes, etc.)
- High-level operational assumptions
- Generic KPI definitions
- Educational forecasting logic

See [LIMITATIONS.md](LIMITATIONS.md) for comprehensive limitations and scope.

## Contributing

This is a portfolio project for demonstration purposes. For educational use:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass: `pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

Atlas JV Planning OS contains entirely fictitious data and is for educational/portfolio purposes only. It should not be used for any real-world decision making, operational planning, or financial analysis.

See [LEGAL_DISCLAIMER.md](LEGAL_DISCLAIMER.md) for complete legal information.

---

**Built with ❤️ for portfolio demonstration and educational purposes.**

