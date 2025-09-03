# AEP Performance Data - Applied Filters

> Documentation for: aep performance data.csv
> Created: 2025-01-03

## Source Data Filters Applied

The raw performance CSV data was pre-filtered using the following criteria:

### Performance Metrics
- **Paperless Conversion:** ≤ 100.00%

### Actions Excluded
- **Action Taken:** Excluded HmWar_Clicked and HSWX_Clicked

### Date Range
- **Primary Range:** 1/1/2025 to 8/22/2025
- **Extended Range:** 9/3/2022 to 9/2/2025
- **Year Filter:** ≥ 2022

### Role Exclusions
Excluded the following administrative and supervisory roles:
- Admin
- Admin Assoc
- BILLER
- BILLING LEAD
- C&I Lead
- Supervisor
- Admn
- Billing Coordinator
- Billing Supervisor

### Manager Inclusion
Data includes only these managers:
- Dunbar
- Harris
- Johnson
- Kolevski
- Regoli
- Tierney
- Wright

## Data Quality Impact

These filters ensure the dataset contains:
- Only frontline agent performance data (no supervisory roles)
- Recent performance data (2022 onwards, focus on 2025)
- Valid performance metrics within expected ranges
- Relevant managers for the analysis scope

## Notes for Analysis

- The date range discrepancy (1/1/2025-8/22/2025 vs 9/3/2022-9/2/2025) may indicate overlapping filter criteria
- Role exclusions focus the analysis on direct customer service agents
- Manager filtering suggests this is a subset of the full AEP organization
