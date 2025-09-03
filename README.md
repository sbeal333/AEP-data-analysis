# AEP Performance Analytics

Agent performance analytics platform for AEP that analyzes performance data, identifies top performers, and discovers common success factors.

## Project Structure

```
.
├── data/
│   ├── raw/           # Original data files
│   ├── processed/     # Cleaned and processed data
│   └── external/      # Additional data sources (goals, resumes)
├── scripts/           # Python analysis scripts
├── analysis/          # Analysis notebooks and exploratory work
├── reports/           # Generated reports and visualizations
├── config/            # Configuration files
└── .agent-os/         # Agent OS documentation
```

## Setup

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Data Files

- **Primary dataset:** `data/raw/aep-performance-data.csv`
- Additional datasets will be added to `data/external/`

## Key Metrics in Dataset

- **Performance Metrics:** Talk time, Hold time, ACW (After Call Work), AHT (Average Handle Time)
- **Quality Metrics:** OSAT with Agent, Resolution Rate
- **Availability Metrics:** Talk Available %, Off Phone %, Conformance
- **Sales Metrics:** Paperless Conversion, HomeServe Transfers, Allconnect Transfers

## Development Workflow

1. Check roadmap: `@.agent-os/product/roadmap.md`
2. For new features: `@~/.agent-os/instructions/create-spec.md`
3. For task execution: `@~/.agent-os/instructions/execute-tasks.md`

## Next Steps

The project is set up and ready for data cleaning and analysis. Phase 1 of the roadmap focuses on establishing a clean, reliable data pipeline.