import logging
import datetime
from typing import Dict, Any, List, Tuple
from collections import defaultdict
from app.database.db_manager import db_manager

# Get a logger for the data processor module
logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Handles aggregation and processing of historical PPE compliance data
    from the database to generate insights and reports.
    """

    def __init__(self):
        logger.info("DataProcessor initialized.")

    def get_hourly_violation_trends(self, days: int = 7) -> Dict[int, int]:
        """
        Aggregates violation counts by hour of the day over a specified number of days.
        Useful for identifying peak hours of non-compliance.

        Args:
            days (int): The number of past days to consider for the trend.

        Returns:
            Dict[int, int]: A dictionary where keys are hours (0-23) and values are
                            the total violation counts for that hour across all days.
        """
        logger.info(f"Calculating hourly violation trends for last {days} days.")
        end_date = datetime.datetime.utcnow()
        start_date = end_date - datetime.timedelta(days=days)

        all_violations = db_manager.get_all_violation_events(limit=None) # Fetch all, then filter
        
        hourly_counts = defaultdict(int)
        
        for event in all_violations:
            if start_date <= event['timestamp'] <= end_date:
                hour = event['timestamp'].hour
                hourly_counts[hour] += 1
        
        # Ensure all 24 hours are present, even if no violations occurred
        for i in range(24):
            if i not in hourly_counts:
                hourly_counts[i] = 0
                
        sorted_hourly_counts = dict(sorted(hourly_counts.items()))
        logger.info(f"Hourly violation trends: {sorted_hourly_counts}")
        return sorted_hourly_counts

    def get_daily_compliance_summary(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Generates a daily summary of compliance metrics over a specified period.

        Args:
            days (int): The number of past days to include in the summary.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a day's summary.
                                  Example: [{'date': 'YYYY-MM-DD', 'total_persons': N, 'violations': M, 'compliance_rate': X.XX}]
        """
        logger.info(f"Calculating daily compliance summary for last {days} days.")
        daily_summary = defaultdict(lambda: {'total_persons': 0, 'total_violations': 0, 'total_logs': 0})
        
        end_date = datetime.datetime.utcnow().date()
        
        # Fetch all logs for efficient processing, then filter by date
        all_logs = db_manager.get_all_compliance_logs(limit=None) 

        for log in all_logs:
            log_date = log['timestamp'].date()
            if log_date >= (end_date - datetime.timedelta(days=days)):
                daily_summary[log_date]['total_persons'] += log['person_count']
                daily_summary[log_date]['total_violations'] += log['violations_count']
                daily_summary[log_date]['total_logs'] += 1
        
        results = []
        for i in range(days):
            current_date = end_date - datetime.timedelta(days=i)
            day_data = daily_summary[current_date]
            
            total_p = day_data['total_persons']
            total_v = day_data['total_violations']
            
            compliance_rate = 100.0
            if total_p > 0:
                compliance_rate = ((total_p - total_v) / total_p) * 100
                compliance_rate = max(0, compliance_rate)
            
            results.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'total_persons': total_p,
                'total_violations': total_v,
                'compliance_rate': round(compliance_rate, 2),
                'total_logs': day_data['total_logs']
            })
            
        # Sort results by date in ascending order
        results.sort(key=lambda x: x['date'])
        logger.info(f"Generated daily compliance summary for {len(results)} days.")
        return results

    def get_violation_type_distribution(self, days: int = 30) -> Dict[str, int]:
        """
        Calculates the distribution of different violation types over a period.

        Args:
            days (int): The number of past days to consider.

        Returns:
            Dict[str, int]: A dictionary where keys are violation types and values are their counts.
        """
        logger.info(f"Calculating violation type distribution for last {days} days.")
        end_date = datetime.datetime.utcnow()
        start_date = end_date - datetime.timedelta(days=days)

        all_violations = db_manager.get_all_violation_events(limit=None)
        
        type_counts = defaultdict(int)
        for event in all_violations:
            if start_date <= event['timestamp'] <= end_date:
                type_counts[event['violation_type']] += 1
        
        sorted_type_counts = dict(sorted(type_counts.items()))
        logger.info(f"Violation type distribution: {sorted_type_counts}")
        return sorted_type_counts


data_processor = DataProcessor()