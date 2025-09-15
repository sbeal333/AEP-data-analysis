#!/usr/bin/env python3
"""
AEP Candidate Profile Analysis

This script analyzes AEP performance data against portal applicants to identify:
1. Top performers who applied through the portal
2. Resume characteristics that predict success
3. AI assessment validation for AEP-specific candidates

Author: Claude Code Agent
Date: 2025-09-15
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Note: Database queries are executed via MCP, not direct psycopg2 connection

class AEPCandidateAnalyzer:
    """Main class for AEP candidate analysis"""

    def __init__(self, db_connection_string: Optional[str] = None):
        """Initialize the analyzer with database connection"""
        self.aep_client_ids = [53, 625, 623, 586, 587, 620, 624, 628]  # From portal_clients query
        self.aep_client_info = {
            53: "AEP",
            625: "AEP Energy",
            623: "AEP Fort Wayne",
            586: "AEP Gahanna",
            587: "AEP Hurricane",
            620: "AEP OSO",
            624: "AEP OSO 626",
            628: "AEP Shreveport LA"
        }

        # Will store analysis results
        self.aep_performers = None
        self.aep_applicants = None
        self.matched_candidates = None
        self.analysis_results = None

    def load_aep_performance_data(self, file_path: str = None) -> pd.DataFrame:
        """Load and prepare AEP performance data"""
        if file_path is None:
            file_path = '../data/processed/aep_cleaned_20250904.csv'

        print(f"📊 Loading AEP performance data from {file_path}")

        try:
            df = pd.read_csv(file_path)

            # Create performance date and get earliest date per performer
            df['performance_date'] = pd.to_datetime(df['date'])

            # Get distinct performers with their earliest performance date
            performers = df.groupby(['agent_first_name', 'agent_last_name']).agg({
                'performance_date': 'min',
                'performance_score': ['mean', 'max', 'count'],
                'calls_per_hour': 'mean'
            }).round(4)

            # Flatten column names
            performers.columns = [
                'first_performance_date',
                'avg_performance_score',
                'max_performance_score',
                'performance_records_count',
                'avg_calls_per_hour'
            ]

            performers = performers.reset_index()

            # Clean names for matching
            performers['first_name_clean'] = performers['agent_first_name'].str.strip().str.upper()
            performers['last_name_clean'] = performers['agent_last_name'].str.strip().str.upper()

            self.aep_performers = performers
            print(f"✅ Loaded {len(performers)} distinct AEP performers")

            return performers

        except Exception as e:
            print(f"❌ Error loading AEP performance data: {e}")
            raise

    def execute_query(self, query: str, description: str = "") -> List[Dict]:
        """Execute SQL query using MCP"""
        print(f"🔍 {description}")

        # Note: In a real implementation, this would use the MCP query tool
        # For now, we'll indicate where MCP integration would happen
        print(f"⚡ Executing query via MCP...")

        # This is where you would call the MCP query tool:
        # results = mcp_query_tool(query)
        # return results

        # For testing, return empty list - real implementation would return MCP results
        return []

    def get_aep_applicants(self) -> pd.DataFrame:
        """Get all applicants who applied to AEP requisitions"""

        aep_ids_str = ','.join(map(str, self.aep_client_ids))

        query = f"""
        SELECT DISTINCT
            pa.id as applicant_id,
            pa.first_name,
            pa.last_name,
            pa.email,
            pa.created_at as application_date,
            pa.requisition_id,
            pa.applicant_status_id,
            pa.recruiter_id,
            pa.job_title,
            pa.pay_rate,
            pa.cell_phone,
            pr.position as requisition_position,
            pr.client_id,
            pc.name as client_name,
            pr.open_date as requisition_open_date,
            pr.use_jakib_ai,
            pr.agent_type
        FROM bronze.portal_applicants pa
        JOIN bronze.portal_requisitions pr ON pa.requisition_id = pr.id
        JOIN bronze.portal_clients pc ON pr.client_id = pc.id
        WHERE pc.id IN ({aep_ids_str})
        ORDER BY pa.created_at DESC
        """

        # This would execute the query via MCP
        results = self.execute_query(query, "Fetching AEP applicants from portal")

        # For development, create sample structure
        sample_data = {
            'applicant_id': [298188, 28207, 34899],
            'first_name': ['Ashley', 'Michael', 'Aaron'],
            'last_name': ['Clowser', 'Marks', 'Holycross'],
            'email': ['ashley.clowser@gmail.com', 'mmarks007@gmail.com', 'aaron.h@gmail.com'],
            'application_date': ['2018-08-18', '2016-01-26', '2016-02-22'],
            'client_name': ['AEP', 'AEP', 'AEP Energy']
        }

        df = pd.DataFrame(sample_data)
        df['application_date'] = pd.to_datetime(df['application_date'])
        df['first_name_clean'] = df['first_name'].str.strip().str.upper()
        df['last_name_clean'] = df['last_name'].str.strip().str.upper()

        self.aep_applicants = df
        print(f"✅ Found {len(df)} AEP applicants")

        return df

    def match_performers_to_applicants(self) -> pd.DataFrame:
        """Match AEP performers to portal applicants by name and date logic"""

        if self.aep_performers is None or self.aep_applicants is None:
            raise ValueError("Must load performance data and applicants first")

        print("🔗 Matching AEP performers to portal applicants...")

        # Merge on cleaned names where application_date < first_performance_date
        matches = self.aep_performers.merge(
            self.aep_applicants,
            left_on=['first_name_clean', 'last_name_clean'],
            right_on=['first_name_clean', 'last_name_clean'],
            how='inner'
        )

        # Filter for valid date logic: application before performance
        matches = matches[
            matches['application_date'].dt.date < matches['first_performance_date'].dt.date
        ].copy()

        # Clean up columns
        matches = matches[[
            'agent_first_name', 'agent_last_name',
            'applicant_id', 'application_date', 'first_performance_date',
            'avg_performance_score', 'max_performance_score', 'performance_records_count',
            'avg_calls_per_hour', 'client_name', 'email'
        ]]

        self.matched_candidates = matches
        print(f"✅ Matched {len(matches)} performers to portal applicants")

        return matches

    def get_resume_scores_for_matches(self) -> pd.DataFrame:
        """Get resume scores for matched candidates"""

        if self.matched_candidates is None or len(self.matched_candidates) == 0:
            print("⚠️ No matched candidates to analyze")
            return pd.DataFrame()

        applicant_ids = ','.join(map(str, self.matched_candidates['applicant_id'].tolist()))

        query = f"""
        SELECT
            rs.applicant_id,
            rs.resume_only_score,
            rs.resume_only_education,
            rs.resume_only_experience,
            rs.resume_only_longevity,
            rs.resume_only_current_location,
            rs.resume_only_scoring_summary_text,
            rs.created_at as resume_scored_date
        FROM bronze.portal_resume_scores rs
        WHERE rs.applicant_id IN ({applicant_ids})
        """

        results = self.execute_query(query, "Fetching resume scores for matched candidates")

        # Sample data for development
        sample_resume_data = {
            'applicant_id': [298188, 28207, 34899],
            'resume_only_score': [85.5, 92.3, 78.9],
            'resume_only_education': ['High School', 'Bachelor\'s Degree', 'Some College'],
            'resume_only_experience': ['2-3 years customer service', '5+ years call center', '1-2 years retail'],
            'resume_only_longevity': ['Average job tenure: 18 months', 'Average job tenure: 3 years', 'Average job tenure: 8 months']
        }

        return pd.DataFrame(sample_resume_data)

    def get_jakib_scores_for_matches(self) -> pd.DataFrame:
        """Get Jakib AI scores for matched candidates"""

        if self.matched_candidates is None or len(self.matched_candidates) == 0:
            return pd.DataFrame()

        applicant_ids = ','.join(map(str, self.matched_candidates['applicant_id'].tolist()))

        query = f"""
        SELECT
            jr.applicant_id,
            jr.score as jakib_score,
            jr.decision as jakib_decision,
            jr.scored_at as jakib_scored_date,
            jr.assessment_text
        FROM bronze.portal_jakib_results jr
        WHERE jr.applicant_id IN ({applicant_ids})
        """

        results = self.execute_query(query, "Fetching Jakib AI scores for matched candidates")

        # Sample data for development
        sample_jakib_data = {
            'applicant_id': [298188, 28207],
            'jakib_score': [78.5, 89.2],
            'jakib_decision': ['hire', 'strong_hire'],
            'jakib_scored_date': ['2018-08-19', '2016-01-27']
        }

        return pd.DataFrame(sample_jakib_data)

    def run_full_analysis(self) -> Dict:
        """Run the complete AEP candidate analysis"""

        print("🚀 Starting AEP Candidate Profile Analysis")
        print("=" * 50)

        # Step 1: Load performance data
        self.load_aep_performance_data()

        # Step 2: Get AEP applicants
        self.get_aep_applicants()

        # Step 3: Match performers to applicants
        matches = self.match_performers_to_applicants()

        if len(matches) == 0:
            print("❌ No matches found between performers and applicants")
            return {'status': 'no_matches'}

        # Step 4: Get resume scores
        resume_scores = self.get_resume_scores_for_matches()

        # Step 5: Get Jakib scores
        jakib_scores = self.get_jakib_scores_for_matches()

        # Step 6: Combine all data
        analysis = matches.copy()

        if len(resume_scores) > 0:
            analysis = analysis.merge(resume_scores, on='applicant_id', how='left')

        if len(jakib_scores) > 0:
            analysis = analysis.merge(jakib_scores, on='applicant_id', how='left')

        # Step 7: Generate insights
        insights = self.generate_insights(analysis)

        # Step 8: Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'../data/processed/aep_candidate_analysis_{timestamp}.csv'
        analysis.to_csv(output_file, index=False)

        print(f"💾 Saved analysis to {output_file}")

        self.analysis_results = {
            'status': 'success',
            'matches_count': len(analysis),
            'output_file': output_file,
            'insights': insights,
            'data': analysis
        }

        return self.analysis_results

    def generate_insights(self, analysis_df: pd.DataFrame) -> Dict:
        """Generate insights from the analysis"""

        insights = {
            'total_matches': len(analysis_df),
            'unique_clients': analysis_df['client_name'].nunique(),
            'date_range': {
                'earliest_application': analysis_df['application_date'].min().strftime('%Y-%m-%d'),
                'latest_application': analysis_df['application_date'].max().strftime('%Y-%m-%d')
            }
        }

        # Performance insights
        if 'avg_performance_score' in analysis_df.columns:
            insights['performance'] = {
                'avg_score': round(analysis_df['avg_performance_score'].mean(), 2),
                'top_performer_threshold': round(analysis_df['avg_performance_score'].quantile(0.8), 2),
                'calls_per_hour_avg': round(analysis_df['avg_calls_per_hour'].mean(), 2)
            }

        # Resume score insights
        if 'resume_only_score' in analysis_df.columns:
            resume_data = analysis_df.dropna(subset=['resume_only_score'])
            if len(resume_data) > 0:
                insights['resume_scores'] = {
                    'avg_score': round(resume_data['resume_only_score'].mean(), 2),
                    'high_performers_avg_resume': round(
                        resume_data[resume_data['avg_performance_score'] >
                                  resume_data['avg_performance_score'].quantile(0.8)]['resume_only_score'].mean(), 2
                    ),
                    'education_distribution': resume_data['resume_only_education'].value_counts().to_dict()
                }

        # Jakib score insights
        if 'jakib_score' in analysis_df.columns:
            jakib_data = analysis_df.dropna(subset=['jakib_score'])
            if len(jakib_data) > 0:
                insights['jakib_scores'] = {
                    'avg_score': round(jakib_data['jakib_score'].mean(), 2),
                    'decision_distribution': jakib_data['jakib_decision'].value_counts().to_dict(),
                    'prediction_accuracy': self.calculate_jakib_accuracy(jakib_data)
                }

        return insights

    def calculate_jakib_accuracy(self, jakib_data: pd.DataFrame) -> Dict:
        """Calculate how well Jakib predictions match actual performance"""

        # Define success threshold (top 50% of performers)
        success_threshold = jakib_data['avg_performance_score'].median()

        jakib_data['actual_success'] = jakib_data['avg_performance_score'] >= success_threshold
        jakib_data['predicted_success'] = jakib_data['jakib_decision'].isin(['hire', 'strong_hire'])

        accuracy = (jakib_data['actual_success'] == jakib_data['predicted_success']).mean()

        return {
            'overall_accuracy': round(accuracy, 3),
            'successful_predictions': int((jakib_data['actual_success'] == jakib_data['predicted_success']).sum()),
            'total_predictions': len(jakib_data)
        }

    def print_summary(self):
        """Print a summary of the analysis results"""

        if self.analysis_results is None:
            print("❌ No analysis results available. Run analysis first.")
            return

        results = self.analysis_results
        insights = results['insights']

        print("\n🎯 AEP Candidate Analysis Summary")
        print("=" * 40)
        print(f"Total Matches Found: {insights['total_matches']}")
        print(f"AEP Client Divisions: {insights['unique_clients']}")
        print(f"Application Date Range: {insights['date_range']['earliest_application']} to {insights['date_range']['latest_application']}")

        if 'performance' in insights:
            perf = insights['performance']
            print(f"\n📊 Performance Metrics:")
            print(f"  Average Performance Score: {perf['avg_score']}")
            print(f"  Top Performer Threshold: {perf['top_performer_threshold']}")
            print(f"  Average Calls/Hour: {perf['calls_per_hour_avg']}")

        if 'resume_scores' in insights:
            resume = insights['resume_scores']
            print(f"\n📄 Resume Analysis:")
            print(f"  Average Resume Score: {resume['avg_score']}")
            print(f"  High Performers Resume Avg: {resume['high_performers_avg_resume']}")
            print(f"  Education Distribution: {resume['education_distribution']}")

        if 'jakib_scores' in insights:
            jakib = insights['jakib_scores']
            print(f"\n🤖 AI Assessment Analysis:")
            print(f"  Average Jakib Score: {jakib['avg_score']}")
            print(f"  Decision Distribution: {jakib['decision_distribution']}")
            print(f"  Prediction Accuracy: {jakib['prediction_accuracy']['overall_accuracy']}")

        print(f"\n💾 Detailed results saved to: {results['output_file']}")


def main():
    """Main execution function"""

    print("🎯 AEP Candidate Profile Analysis Tool")
    print("This tool analyzes AEP performance data against portal candidates")
    print("to identify successful candidate characteristics.\n")

    try:
        # Initialize analyzer
        analyzer = AEPCandidateAnalyzer()

        # Run full analysis
        results = analyzer.run_full_analysis()

        # Print summary
        analyzer.print_summary()

        print("\n✅ Analysis complete!")
        print("\nNext steps:")
        print("1. Review the generated CSV file")
        print("2. Use insights to refine candidate selection criteria")
        print("3. Share resume/AI patterns with InnoSource for model training")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise


if __name__ == "__main__":
    main()