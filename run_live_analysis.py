#!/usr/bin/env python3
"""
Run live AEP candidate analysis with real MCP data
"""

import pandas as pd
from datetime import datetime
import sys
import os

# Add scripts directory to path to import our analyzer
sys.path.append('scripts')
from aep_candidate_analysis import AEPCandidateAnalyzer

def main():
    print("🚀 Running Live AEP Candidate Analysis")
    print("=" * 50)

    # Create our analyzer
    analyzer = AEPCandidateAnalyzer()

    # Step 1: Load AEP performance data (this works already)
    print("📊 Loading AEP performance data...")
    performers = analyzer.load_aep_performance_data('data/processed/aep_cleaned_20250904.csv')
    print(f"✅ Loaded {len(performers)} AEP performers")

    # Step 2: Create real AEP applicants data from our MCP query results
    print("🔍 Using live AEP applicant data...")

    # These are our confirmed matches from the MCP queries
    real_matches = [
        {
            'applicant_id': 1142652,
            'first_name': 'Amanda',
            'last_name': 'Harris',
            'email': 'amanda.w.harris@outlook.com',
            'application_date': '2024-01-23',
            'client_name': 'AEP OSO 626',
            'requisition_position': 'CSR'
        },
        {
            'applicant_id': 920830,
            'first_name': 'Adrienne',
            'last_name': 'Stevenson',
            'email': 'adriennes320@yahoo.com',
            'application_date': '2022-11-11',
            'client_name': 'AEP Gahanna',
            'requisition_position': 'CSR'
        },
        {
            'applicant_id': 450585,
            'first_name': 'Michael',
            'last_name': 'Marks',
            'email': 'bizzycomp@outlook.com',
            'application_date': '2020-01-25',
            'client_name': 'AEP Hurricane',
            'requisition_position': 'Customer Service Representative'
        },
        {
            'applicant_id': 298188,
            'first_name': 'Ashley',
            'last_name': 'Clowser',
            'email': 'Ashley.l.clowser@gmail.com',
            'application_date': '2018-08-18',
            'client_name': 'AEP',
            'requisition_position': 'WV Customer Service Representative'
        },
        {
            'applicant_id': 34899,
            'first_name': 'Aaron',
            'last_name': 'Holycross',
            'email': 'Crossfade92@Gmail.com',
            'application_date': '2016-02-22',
            'client_name': 'AEP',
            'requisition_position': 'CSR'
        },
        {
            'applicant_id': 28207,
            'first_name': 'Michael',
            'last_name': 'Marks',
            'email': 'mmarks007@gmail.com',
            'application_date': '2016-01-26',
            'client_name': 'AEP',
            'requisition_position': 'CSR'
        }
    ]

    # Convert to DataFrame with proper data types
    aep_applicants = pd.DataFrame(real_matches)
    aep_applicants['application_date'] = pd.to_datetime(aep_applicants['application_date'])
    aep_applicants['first_name_clean'] = aep_applicants['first_name'].str.strip().str.upper()
    aep_applicants['last_name_clean'] = aep_applicants['last_name'].str.strip().str.upper()

    analyzer.aep_applicants = aep_applicants
    print(f"✅ Found {len(aep_applicants)} confirmed AEP matches")

    # Step 3: Match performers to applicants
    print("🔗 Matching performers to applicants...")
    matches = analyzer.match_performers_to_applicants()
    print(f"✅ Successfully matched {len(matches)} performers")

    if len(matches) == 0:
        print("❌ No matches found!")
        return

    # Step 4: Since we know there are no resume/Jakib scores for these historical candidates,
    # let's create the analysis with just the performance correlation
    print("📈 Analyzing performance correlation...")

    # Add some analysis
    matches['years_since_application'] = (
        matches['first_performance_date'].dt.year - matches['application_date'].dt.year
    )

    # Generate insights
    insights = {
        'total_matches': len(matches),
        'unique_clients': matches['client_name'].nunique(),
        'date_range': {
            'earliest_application': matches['application_date'].min().strftime('%Y-%m-%d'),
            'latest_application': matches['application_date'].max().strftime('%Y-%m-%d')
        },
        'performance_metrics': {
            'avg_performance_score': round(matches['avg_performance_score'].mean(), 2),
            'top_performer_threshold': round(matches['avg_performance_score'].quantile(0.8), 2),
            'avg_calls_per_hour': round(matches['avg_calls_per_hour'].mean(), 2)
        },
        'client_distribution': matches['client_name'].value_counts().to_dict(),
        'time_to_performance': {
            'avg_years': round(matches['years_since_application'].mean(), 1),
            'range': f"{matches['years_since_application'].min()}-{matches['years_since_application'].max()} years"
        }
    }

    # Step 5: Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/processed/live_aep_candidate_analysis_{timestamp}.csv'
    matches.to_csv(output_file, index=False)

    # Step 6: Print comprehensive summary
    print("\n🎯 Live AEP Candidate Analysis Results")
    print("=" * 45)
    print(f"✅ Total Confirmed Matches: {insights['total_matches']}")
    print(f"📍 AEP Client Divisions: {insights['unique_clients']}")
    print(f"📅 Application Period: {insights['date_range']['earliest_application']} to {insights['date_range']['latest_application']}")

    print(f"\n📊 Performance Insights:")
    perf = insights['performance_metrics']
    print(f"  • Average Performance Score: {perf['avg_performance_score']}")
    print(f"  • Top Performer Threshold (80th percentile): {perf['top_performer_threshold']}")
    print(f"  • Average Calls per Hour: {perf['avg_calls_per_hour']}")

    print(f"\n🏢 Client Distribution:")
    for client, count in insights['client_distribution'].items():
        print(f"  • {client}: {count} matches")

    print(f"\n⏰ Time Analysis:")
    time_metrics = insights['time_to_performance']
    print(f"  • Average years from application to performance data: {time_metrics['avg_years']}")
    print(f"  • Range: {time_metrics['range']}")

    print(f"\n👥 Individual Results:")
    for _, row in matches.iterrows():
        print(f"  • {row['agent_first_name']} {row['agent_last_name']}: "
              f"Score {row['avg_performance_score']:.1f}, "
              f"Applied to {row['client_name']} in {row['application_date'].year}")

    print(f"\n💾 Detailed data saved to: {output_file}")

    print(f"\n🎯 Key Findings:")
    print(f"  1. Successfully linked {len(matches)} AEP performers to their original applications")
    print(f"  2. These candidates applied {time_metrics['avg_years']} years before performance measurement")
    print(f"  3. Average performance score of matched candidates: {perf['avg_performance_score']}")
    print(f"  4. Coverage across {insights['unique_clients']} different AEP divisions")

    top_performer = matches.loc[matches['avg_performance_score'].idxmax()]
    print(f"  5. Top performer: {top_performer['agent_first_name']} {top_performer['agent_last_name']} "
          f"(Score: {top_performer['avg_performance_score']:.1f})")

    print(f"\n📈 Implications for InnoSource:")
    print(f"  • We can now track candidate journey from application → hire → performance")
    print(f"  • No AI scores available for these historical candidates (system likely newer)")
    print(f"  • Future candidates will have resume + AI scores for full 'trifecta' analysis")
    print(f"  • This baseline establishes the methodology for ongoing analysis")

    return matches, insights

if __name__ == "__main__":
    results = main()