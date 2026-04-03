# Data Governance

## Overview

All data used in Atlas JV Planning OS is ynthetic.

The project is designed so that no real operational, financial, commercial, technical, personal, or proprietary dataset is required at any stage.

## Data Source Policy

The sole approved data sources for this repository are:

1. programmatically generated synthetic data

2. manually defined ficticious reference values

3. publicly known, generalized industry benchmark ranges used only to calibrate realism at a high level

No private, confidential, restricted, or internal data is permitted

## Synthetic Data Categories

The synthetic data layer may generate the following categories:

- ventures

- assets

- projects

- planning assumptions

- monthly actuals

- KPI inputs

- scenario cases

- personnel display names

## Generation Method

Data is generated through Python scripts using packages such as:

- `numpy`
- `pandas`
- `faker`
- Python standard library utilities

A fixed random seed may be used to ensure reproducibility.

## Public Benchmark Inspiration

Where realism is needed, broad ranges may be calibrated using publicly known industry concepts such as:

- typical production scale ranges

- generic operating cost ranges

- generic capex ranges

- common economic analysis conventions

- standard reporting concepts used in oil and gas analytics

These ranges are not tied to any specific confidential asset, company, or internal dataset.

## Explicit Exclusions

The following are explicitly prohibited from being used in this repository:

- employer data

- client data

- internal spreadsheets

- screenshots from proprietary systems

- copied database exports

- copied report templates

- internal planning guidelines

- internal asset assumptions

- personal employee information

- non-public operational or financial information

## Governance Rule

All application outputs must be traceable either to:

- synthetic generation logic, or
- clearly documented ficticious assumptions

If a value cannot be explained through one of those two paths, it should not be included.

## Review Standard

Before any data file or feature is committed, the author should be able to answer:

1. Is this synthetic?

2. Is this ficticious?

3. Is this traceable to public/general knowledge or generated logic?

4. Could this be mistaken for real confidential data?

If the answer to question 4 is "yes" or "maybe," the data should be revised or removed.

