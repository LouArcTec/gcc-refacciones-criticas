# Dashboard Refacciones Criticas

> Predictive Maintenance & Procurement Forecasting for Heavy-Duty Truck Fleets

An enterprise-grade predictive analytics platform that combines **survival analysis**, **machine learning**, and **fleet maintenance intelligence** to forecast component failures before they occur.

The Fleet Health Intelligence Platform enables maintenance teams, reliability engineers, and fleet operators to transition from reactive maintenance schedules toward a proactive, data-driven maintenance strategy that reduces downtime, lowers operating costs, and improves parts procurement planning.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Capabilities](#key-capabilities)
- [Live Application](#live-application)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [Model Configuration](#model-configuration)
- [Model Performance](#model-performance)
- [Local Installation](#local-installation)
- [Data Requirements](#data-requirements)
- [Retraining Workflow](#retraining-workflow)
- [Authentication](#authentication)
- [Business Impact](#business-impact)
- [Known Limitations](#known-limitations)
- [Future Enhancements](#future-enhancements)

---

# Overview

Traditional fleet maintenance programs rely heavily on scheduled inspections or component replacement after failure.

This platform introduces a predictive approach by leveraging a **Random Survival Forest (RSF)** model trained on historical maintenance events, replacement records, vehicle characteristics, and operational usage patterns.

Instead of asking:

> "What failed?"

The platform answers:

> "What is likely to fail next, and when should we prepare for it?"

---

# Key Capabilities

## 🔮 Predictive Component Lifecycle Forecasting

Predicts when individual components are expected to exceed the critical health degradation threshold based on:

- Historical replacement timelines
- Usage frequency
- Vehicle characteristics
- Maintenance behavior patterns
- Operational environments

## 📦 Procurement Planning Intelligence

Provides forward-looking visibility into future parts demand, allowing operators to:

- Forecast inventory needs
- Reduce emergency purchases
- Improve warehouse stocking efficiency
- Optimize procurement cycles

## 📈 Survival Analysis Modeling

Uses a specialized Random Survival Forest architecture capable of:

- Modeling non-linear failure patterns
- Handling censored observations
- Generating component survival probabilities
- Estimating Remaining Useful Life (RUL)

## 🖥 Interactive Dashboard

The Streamlit-based interface enables users to:

- Upload updated fleet datasets
- Retrain predictive models
- Monitor validation metrics
- Explore component forecasts
- Analyze procurement requirements

---

# Live Application

### Production Deployment

```text
https://predictive-maintenance-dashboard.render.com
```

---

# System Architecture

```text
predictive-maintenance-dashboard/
│
├── data/
│   ├── infotec.xlsx
│   ├── consumibles.xlsx
│   └── Master_Procurement_All_Trucks.csv
│
├── model/
│   └── pipeline.py
│
├── app
│   └── app.py
├── requirements.txt
├── Dockerfile
└── README.md
```

---

# Technology Stack

## Machine Learning

- Random Survival Forest (RSF)
- Survival Analysis
- K-Means Clustering
- TF-IDF Vectorization
- Cross Validation

## Data Processing

- Pandas
- NumPy
- Scikit-Learn
- Scikit-Survival

## Frontend

- Streamlit

## Deployment

- Docker
- Render

---

# Machine Learning Pipeline

```text
Raw Fleet Data
        │
        ▼
Data Cleaning
        │
        ▼
Consumable Filtering
        │
        ▼
Text Processing
        │
        ▼
TF-IDF Vectorization
        │
        ▼
Feature Engineering
        │
        ▼
K-Means Clustering
        │
        ▼
Random Survival Forest Training
        │
        ▼
Cross Validation
        │
        ▼
Forecast Generation
```

---

# Model Configuration

## Random Survival Forest Parameters

```python
RandomSurvivalForest(
    n_estimators=150,
    min_samples_split=60,
    min_samples_leaf=20,
    n_jobs=2
)
```

### Additional Configuration

| Parameter | Value |
|------------|--------|
| Time Granularity | 5-Day Intervals |
| Validation Method | 3-Fold Stratified CV |
| Model Type | Random Survival Forest |
| Prediction Target | Component Time-To-Failure |

---

# Model Performance

| Validation Fold | C-Index |
|-----------------|----------|
| Fold 1 | 0.72 |
| Fold 2 | 0.71 |
| Fold 3 | 0.69 |

### Interpretation

A Concordance Index (C-Index) above **0.65** demonstrates meaningful prognostic capability and aligns with accepted reliability engineering standards.

---

# Local Installation

## Prerequisites

### Python

```text
Python 3.11.x
```

### System Dependencies

#### Windows

Install:

- Visual Studio Build Tools
- Desktop Development with C++

#### Linux

```bash
sudo apt install build-essential gfortran pkg-config
```

#### macOS

```bash
brew install gcc pkg-config
```

---

## Clone Repository

```bash
git clone https://github.com/LouArcTec/gcc-refacciones-criticas.git

cd gcc-refacciones-criticas
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install --upgrade pip

pip install -r requirements.txt
```

---

## Generate Procurement Matrix

```bash
python model/pipeline.py
```

---

## Launch Dashboard

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

# Data Requirements

## data/infotec.xlsx

Contains three worksheets:

### Equipos

| Column | Description |
|----------|------------|
| EQUIPO | Asset Identifier |
| MARCA | Vehicle Manufacturer |
| MODELO | Vehicle Model Year |
| ORIGEN | Manufacturing Origin |

### Ordenes de Trabajo

| Column | Description |
|----------|------------|
| Order | Work Order ID |
| Description | Repair Summary |
| Equipment | Asset ID |
| Created On | Start Date |
| Changed On | Completion Date |
| Order Type | Maintenance Category |

### Refacciones

| Column | Description |
|----------|------------|
| Order | Linked Work Order |
| Description | Part Description |
| Material | Part Number |
| Quantity | Units Consumed |
| Posting Date | Installation Date |

---

## data/consumibles.xlsx

Contains a list of low-value consumables automatically excluded from model training.

Examples:

```text
CINTA AISLANTE SUPER 33
SHOP TOWELS
AEROSOL CLEANERS
WORKSHOP SUPPLIES
```

---

# Retraining Workflow

### Step 1

Upload:

- infotec.xlsx
- consumibles.xlsx

### Step 2

Click:

```text
Import Data & Re-run Pipeline
```

### Step 3

The system automatically:

- Saves uploaded files
- Rebuilds training datasets
- Retrains RSF models
- Computes validation metrics
- Updates procurement forecasts
- Refreshes dashboard caches

---

# Authentication

Application access is protected by password authentication.

Environment variable:

```bash
APP_PASSWORD
```

Local fallback:

```text
admin123
```

Production deployments should override this value through secure environment configuration.

---

# Business Impact

Organizations implementing predictive maintenance strategies typically benefit from:

- Reduced unplanned downtime
- Improved vehicle availability
- Lower maintenance debt
- Better spare-parts forecasting
- Reduced emergency procurement costs
- Improved maintenance planning efficiency

---

# Known Limitations

## Render 512 Mib

Re-training the model may crash the live docker due to the random forest model needing more than 4GB of Ram.

## Survival Horizon Limitation

Predictions cannot exceed the maximum observed lifespan present in training data.

When this threshold is reached, the platform displays:

```text
Exceeds Model Limit
```

---

# Future Enhancements

- Real-time telematics integration
- Remaining Useful Life (RUL) visualization
- Automated procurement recommendations
- Fleet-wide risk scoring
- Multi-fleet benchmarking
- REST API access
- Role-based access control
- Inventory optimization engine
- Multi-tenant architecture

---

# License

**Proprietary – Internal Enterprise Use**

All rights reserved.

---

# Author

**Fleet Health Intelligence Platform**

Lou Anthony Arc, Karla Isabel Ortega Esquivel, Anette Ortiz Monzón
Tecnológico de Monterrey School of Engineering and Sciences
