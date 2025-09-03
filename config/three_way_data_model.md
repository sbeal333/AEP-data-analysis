# Three-Way Comparison Data Model

> Created: 2025-01-03
> Purpose: Define data structure for InnoSource AI feedback loop

## Overview

This document defines the data model for comparing three rating systems:
1. **InnoSource AI Ratings** - AI-generated candidate scores
2. **AEP Candidate Ratings** - Human ratings using AEP's scale (Superior, etc.)
3. **Actual Performance Data** - Real performance metrics from AEP systems

## Core Entities

### 1. Candidate Profile
```
candidate_id (Primary Key)
first_name
last_name
hire_date
position
department
manager_hierarchy (from performance data)
status (active/inactive/terminated)
```

### 2. InnoSource AI Ratings
```
candidate_id (Foreign Key)
ai_rating_id (Primary Key)
overall_score (0-100)
rating_date
model_version
confidence_score
category_scores:
  - technical_skills
  - communication_skills
  - experience_relevance
  - culture_fit
  - growth_potential
```

### 3. AEP Candidate Ratings
```
candidate_id (Foreign Key)
aep_rating_id (Primary Key)
overall_rating (Superior/Good/Average/Below Average)
rating_date
rater_id
interview_type
detailed_scores:
  - technical_competency
  - communication_skills  
  - problem_solving
  - team_fit
  - motivation
notes
```

### 4. Resume Data
```
candidate_id (Foreign Key)
resume_id (Primary Key)
education_level
years_experience
previous_industries
certifications
skills_mentioned
employment_gaps
location
salary_history
```

### 5. Performance Data
```
candidate_id (Foreign Key)
performance_date
manager_hierarchy_manager
manager_hierarchy_location
manager_hierarchy_supervisor
daily_metrics:
  - talk_time
  - hold_time
  - acw_time
  - aht
  - interaction_count
  - paperless_conversion
  - homeserve_transfers
  - allconnect_transfers
  - osat_with_agent
  - resolution_rate
  - talk_available_pct
  - off_phone_pct
  - conformance
calculated_metrics:
  - performance_score
  - calls_per_hour
  - efficiency_rating
```

## Aggregated Views

### Performance Summary by Candidate
```
candidate_id
performance_period (30/90/180 days)
avg_performance_score
performance_tier (Top/High/Medium/Low)
retention_status
days_employed
trend_direction (improving/stable/declining)
```

### Three-Way Comparison Dataset
```
candidate_id
hire_date
ai_overall_score
ai_confidence_score
aep_overall_rating
aep_rating_score (numerical conversion)
performance_tier
avg_performance_score
90_day_retention
resume_characteristics:
  - education_score
  - experience_score
  - skills_match_score
prediction_accuracy:
  - ai_accuracy (how well AI predicted performance)
  - aep_accuracy (how well AEP rating predicted performance)
```

## Data Quality Requirements

### Completeness
- All candidates must have performance data for at least 30 days
- Minimum viable dataset: 100 candidates with all three rating types

### Data Linkage
- Candidate matching across systems via:
  - Primary: candidate_id (if standardized)
  - Secondary: first_name + last_name + hire_date
  - Fallback: fuzzy matching algorithm

### Time Windows
- Performance evaluation period: 90 days post-hire
- Rating recency: Within 30 days of hire date
- Minimum employment duration: 30 days (for retention analysis)

## Export Formats for InnoSource

### AI Training Dataset
```json
{
  "candidates": [
    {
      "candidate_id": "string",
      "resume_features": {
        "education_level": "string",
        "years_experience": "number",
        "relevant_skills": ["array"],
        "certifications": ["array"]
      },
      "performance_outcome": {
        "performance_tier": "string",
        "retention_90_days": "boolean",
        "avg_performance_score": "number"
      },
      "original_ai_rating": {
        "overall_score": "number",
        "confidence": "number"
      },
      "validation_metrics": {
        "prediction_accuracy": "number",
        "recommendation": "string"
      }
    }
  ],
  "metadata": {
    "export_date": "date",
    "total_candidates": "number",
    "performance_period": "string",
    "data_quality_score": "number"
  }
}
```

## Data Governance

### Privacy & Security
- Remove PII before export to InnoSource
- Use hashed candidate IDs for external sharing
- Aggregate sensitive performance details

### Data Retention
- Raw performance data: 2 years
- Processed comparison datasets: 5 years
- Exported training data: Permanent (de-identified)

### Update Frequency
- Performance data: Daily
- Three-way comparison: Monthly
- InnoSource export: Quarterly (or as requested)

## Success Metrics

### Data Quality Metrics
- Completeness rate: >95% for all three rating types
- Linkage accuracy: >98% candidate matching
- Data freshness: <7 days lag from performance systems

### Analysis Metrics
- Prediction correlation: R² > 0.4 for rating-to-performance
- Sample size: >200 candidates per quarterly export
- Rating system accuracy comparison: Statistical significance p < 0.05

## Implementation Notes

### Phase 1: Foundation
- Focus on performance data cleaning and standardization
- Establish candidate ID matching across systems

### Phase 2: Integration
- Import and structure AI and AEP rating data
- Build three-way linking framework

### Phase 3: Analysis & Export
- Implement comparison algorithms
- Create export pipeline for InnoSource

### Data Sources Required
1. **From InnoSource:**
   - AI rating datasets with candidate identifiers
   - Data format specifications for exports
   - Model version information

2. **From AEP:**
   - Candidate rating data (Superior/Good/etc. scale)
   - Resume/application data
   - Hiring date information
   - Current performance dashboard data access

3. **Resume Analysis:**
   - Structured resume data extraction
   - Skills and experience categorization
   - Education and certification parsing