#!/usr/bin/env python3
"""
Top Performer Analysis for AEP Performance Data.
Identifies the top 5 performing agents based on goal achievement and overall metrics.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TopPerformerAnalyzer:
    """Analyze and identify top performing agents."""
    
    def __init__(self, input_path):
        """
        Initialize the analyzer.
        
        Args:
            input_path: Path to semantic CSV file
        """
        self.input_path = Path(input_path)
        self.df = None
        self.top_performers = None
        
    def load_semantic_data(self):
        """Load the semantically transformed data."""
        logger.info(f"Loading semantic data from {self.input_path}")
        self.df = pd.read_csv(self.input_path)
        logger.info(f"Loaded {len(self.df)} rows and {len(self.df.columns)} columns")
        return self
    
    def calculate_agent_performance_summary(self):
        """Calculate overall performance metrics per agent."""
        logger.info("Calculating agent performance summaries")
        
        # Group by agent and calculate performance metrics
        agent_stats = self.df.groupby(['agent_name', 'agent_first_name', 'agent_last_name']).agg({
            # Basic stats
            'performance_date': ['count', 'min', 'max'],
            'total_interactions': ['sum', 'mean'],
            
            # Goal achievement rates
            'talk_time_goal_met': 'mean',
            'hold_time_goal_met': 'mean', 
            'acw_goal_met': 'mean',
            'aht_goal_met': 'mean',
            'daily_goals_met_rate': 'mean',
            'all_time_goals_met': 'mean',
            
            # Performance scores
            'overall_performance_score': 'mean',
            'hourly_interaction_rate': 'mean',
            
            # Time metrics averages
            'talk_time_seconds': 'mean',
            'hold_time_seconds': 'mean',
            'after_call_work_seconds': 'mean',
            'average_handle_time_seconds': 'mean',
            
            # Quality metrics
            'customer_satisfaction_score': 'mean',
            'first_call_resolution_rate': 'mean',
            'schedule_adherence_rate': 'mean'
        }).round(3)
        
        # Flatten column names
        agent_stats.columns = ['_'.join(col).strip() for col in agent_stats.columns]
        agent_stats = agent_stats.reset_index()
        
        # Rename columns for clarity
        column_mapping = {
            'performance_date_count': 'days_worked',
            'performance_date_min': 'first_performance_date',
            'performance_date_max': 'last_performance_date',
            'total_interactions_sum': 'total_interactions_period',
            'total_interactions_mean': 'avg_daily_interactions',
            'daily_goals_met_rate_mean': 'overall_goal_achievement_rate',
            'all_time_goals_met_mean': 'perfect_days_rate',
            'overall_performance_score_mean': 'avg_performance_score',
            'hourly_interaction_rate_mean': 'avg_hourly_rate'
        }
        
        agent_stats = agent_stats.rename(columns=column_mapping)
        
        # Calculate additional metrics
        agent_stats['avg_interactions_per_day'] = (
            agent_stats['total_interactions_period'] / agent_stats['days_worked']
        ).round(1)
        
        # Create composite performance score
        # Weight: 40% goal achievement, 30% performance score, 20% efficiency, 10% consistency
        agent_stats['composite_performance_score'] = (
            agent_stats['overall_goal_achievement_rate'] * 0.4 +
            (agent_stats['avg_performance_score'] / 100) * 0.3 +  # Normalize to 0-1
            (agent_stats['avg_hourly_rate'] / 20) * 0.2 +  # Normalize assuming max ~20/hour
            (1 - agent_stats['average_handle_time_seconds_mean'] / 600) * 0.1  # Efficiency bonus
        ).round(4)
        
        self.agent_summary = agent_stats
        logger.info(f"Calculated performance summaries for {len(agent_stats)} agents")
        
        return self
    
    def identify_top_performers(self, top_n=5):
        """Identify the top N performers based on composite score."""
        logger.info(f"Identifying top {top_n} performers")
        
        # Filter agents with sufficient data (at least 10 days worked)
        qualified_agents = self.agent_summary[
            self.agent_summary['days_worked'] >= 10
        ].copy()
        
        # Sort by composite performance score
        top_performers = qualified_agents.nlargest(top_n, 'composite_performance_score')
        
        # Add ranking
        top_performers['rank'] = range(1, len(top_performers) + 1)
        
        self.top_performers = top_performers
        
        logger.info(f"Identified top {len(top_performers)} performers")
        return self
    
    def generate_top_performer_report(self):
        """Generate detailed report on top performers."""
        logger.info("Generating top performer report")
        
        if self.top_performers is None:
            logger.error("Top performers not identified yet. Run identify_top_performers first.")
            return self
        
        # Create report content
        report_lines = [
            "# Top Performer Analysis Report",
            f"",
            f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"> Dataset: {self.input_path}",
            f"> Total agents analyzed: {len(self.agent_summary)}",
            f"> Qualified agents (≥10 days): {len(self.agent_summary[self.agent_summary['days_worked'] >= 10])}",
            f"",
            "## Top 5 Performers",
            ""
        ]
        
        # Add top performer details
        for idx, performer in self.top_performers.iterrows():
            report_lines.extend([
                f"### #{performer['rank']}. {performer['agent_first_name']} {performer['agent_last_name']}",
                f"",
                f"**Full Name:** {performer['agent_name']}",
                f"**Composite Score:** {performer['composite_performance_score']:.4f}",
                f"**Days Worked:** {performer['days_worked']}",
                f"**Period:** {performer['first_performance_date']} to {performer['last_performance_date']}",
                f"",
                f"**Goal Achievement:**",
                f"- Overall Goal Rate: {performer['overall_goal_achievement_rate']:.1%}",
                f"- Perfect Days Rate: {performer['perfect_days_rate']:.1%}",
                f"- Talk Time Goals: {performer['talk_time_goal_met_mean']:.1%}",
                f"- Hold Time Goals: {performer['hold_time_goal_met_mean']:.1%}",
                f"- ACW Goals: {performer['acw_goal_met_mean']:.1%}",
                f"- AHT Goals: {performer['aht_goal_met_mean']:.1%}",
                f"",
                f"**Performance Metrics:**",
                f"- Avg Performance Score: {performer['avg_performance_score']:.1f}",
                f"- Avg Daily Interactions: {performer['avg_daily_interactions']:.1f}",
                f"- Avg Hourly Rate: {performer['avg_hourly_rate']:.1f}",
                f"",
                f"**Time Efficiency:**",
                f"- Avg Talk Time: {performer['talk_time_seconds_mean']:.0f}s (Goal: ≤279s)",
                f"- Avg Hold Time: {performer['hold_time_seconds_mean']:.1f}s (Goal: ≤10s)",
                f"- Avg ACW Time: {performer['after_call_work_seconds_mean']:.1f}s (Goal: ≤41s)",
                f"- Avg AHT: {performer['average_handle_time_seconds_mean']:.0f}s (Goal: ≤330s)",
                f"",
                f"**Quality Metrics:**",
                f"- Customer Satisfaction: {performer['customer_satisfaction_score_mean']:.1f}",
                f"- Resolution Rate: {performer['first_call_resolution_rate_mean']:.1f}",
                f"- Schedule Adherence: {performer['schedule_adherence_rate_mean']:.1f}",
                f"",
                "---",
                ""
            ])
        
        # Add summary statistics
        report_lines.extend([
            "## Summary Statistics",
            "",
            "| Metric | Top 5 Average | All Agents Average |",
            "|--------|---------------|-------------------|"
        ])
        
        # Calculate averages for comparison
        top_5_avg = self.top_performers[['overall_goal_achievement_rate', 'avg_performance_score', 'avg_hourly_rate']].mean()
        all_avg = self.agent_summary[['overall_goal_achievement_rate', 'avg_performance_score', 'avg_hourly_rate']].mean()
        
        report_lines.extend([
            f"| Goal Achievement Rate | {top_5_avg['overall_goal_achievement_rate']:.1%} | {all_avg['overall_goal_achievement_rate']:.1%} |",
            f"| Performance Score | {top_5_avg['avg_performance_score']:.1f} | {all_avg['avg_performance_score']:.1f} |",
            f"| Hourly Interaction Rate | {top_5_avg['avg_hourly_rate']:.1f} | {all_avg['avg_hourly_rate']:.1f} |"
        ])
        
        # Save report
        report_file = Path('reports') / f"top_performers_report_{datetime.now().strftime('%Y%m%d')}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Top performer report saved to {report_file}")
        
        return self
    
    def save_top_performer_data(self):
        """Save top performer data for ATS comparison."""
        if self.top_performers is None:
            logger.error("Top performers not identified yet.")
            return self
        
        # Save detailed data
        output_file = Path('data/processed') / f"top_5_performers_{datetime.now().strftime('%Y%m%d')}.csv"
        self.top_performers.to_csv(output_file, index=False)
        
        # Save just the names for ATS matching
        names_file = Path('data/processed') / f"top_5_performer_names_{datetime.now().strftime('%Y%m%d')}.csv"
        name_cols = ['rank', 'agent_first_name', 'agent_last_name', 'agent_name', 'composite_performance_score']
        self.top_performers[name_cols].to_csv(names_file, index=False)
        
        logger.info(f"Top performer data saved to {output_file}")
        logger.info(f"Names for ATS matching saved to {names_file}")
        
        return self
    
    def run_analysis(self):
        """Run the complete top performer analysis."""
        logger.info("Starting top performer analysis")
        
        (self
         .load_semantic_data()
         .calculate_agent_performance_summary()
         .identify_top_performers(top_n=5)
         .generate_top_performer_report()
         .save_top_performer_data())
        
        logger.info("Top performer analysis complete")
        
        return self.top_performers


if __name__ == "__main__":
    # Run the top performer analysis
    analyzer = TopPerformerAnalyzer('data/processed/aep_semantic_20250903.csv')
    top_performers = analyzer.run_analysis()
    
    print(f"\n🏆 Top 5 Performers Identified!")
    print("="*50)
    for idx, performer in top_performers.iterrows():
        print(f"{performer['rank']}. {performer['agent_first_name']} {performer['agent_last_name']}")
        print(f"   Score: {performer['composite_performance_score']:.4f}")
        print(f"   Goal Achievement: {performer['overall_goal_achievement_rate']:.1%}")
        print(f"   Days Worked: {performer['days_worked']}")
        print()