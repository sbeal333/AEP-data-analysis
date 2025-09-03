# Performance Goals & Standards

> Created: 2025-01-03
> Purpose: Define performance targets for agent evaluation

## Daily Performance Targets

| Metric | Target Value | Unit | Direction |
|--------|-------------|------|-----------|
| Talk Time | ≤279 | seconds | Lower is better |
| Hold Time | ≤10 | seconds | Lower is better |
| After Call Work | ≤41 | seconds | Lower is better |
| Average Handle Time | ≤330 | seconds | Lower is better (sum of above) |

## Performance Evaluation

### Goal Achievement Calculation
- **Meets Goal:** Actual value ≤ Target value
- **Exceeds Goal:** Significantly below target (performance bands TBD)
- **Below Goal:** Actual value > Target value

### Usage in Analysis
These goals will be used to:
- Calculate daily/weekly/monthly goal achievement rates
- Identify top performers who consistently meet targets
- Correlate goal achievement with other performance metrics
- Feed into the InnoSource AI training data for candidate evaluation

## Implementation Notes

### Data Integration
- Goals will be joined with performance data during analysis
- Each agent's daily metrics will be compared against these targets
- Goal achievement will become a calculated field in the dataset

### Future Enhancements
- Goals may be adjusted based on role, experience level, or time period
- Additional metrics may be added as business requirements evolve
- Seasonal or campaign-specific targets may be defined

## Data Format for Scripts

```python
PERFORMANCE_GOALS = {
    'talk_time_seconds': 279,
    'hold_time_seconds': 10, 
    'after_call_work_seconds': 41,
    'average_handle_time_seconds': 330  # Sum of above three
}
```