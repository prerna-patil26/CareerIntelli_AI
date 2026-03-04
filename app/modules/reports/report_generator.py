"""Report generator module for creating comprehensive reports."""

from typing import Dict, Any
from datetime import datetime
import json


class ReportGenerator:
    """Generate comprehensive reports for users."""
    
    def __init__(self):
        """Initialize report generator."""
        pass
    
    def generate_comprehensive_report(self, 
                                     user_id: str,
                                     interview_data: Dict[str, Any],
                                     resume_data: Dict[str, Any],
                                     feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive user report.
        
        Args:
            user_id: User ID
            interview_data: Interview results
            resume_data: Resume analysis
            feedback: Feedback and recommendations
        
        Returns:
            Comprehensive report dictionary
        """
        report = {
            'report_id': f'RPT_{user_id}_{datetime.now().timestamp()}',
            'generated_date': datetime.now().isoformat(),
            'user_id': user_id,
            'interview_summary': interview_data,
            'resume_summary': resume_data,
            'feedback': feedback,
            'recommendations': self._generate_recommendations(interview_data, resume_data)
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_path: str) -> bool:
        """
        Save report to file.
        
        Args:
            report: Report dictionary
            output_path: Path to save report
        
        Returns:
            Success status
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False
    
    def _generate_recommendations(self, 
                                 interview_data: Dict[str, Any],
                                 resume_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if interview_data.get('overall_score', 0) < 70:
            recommendations.append('Practice more interview questions to improve response quality')
        
        if resume_data.get('score', 0) < 70:
            recommendations.append('Update resume with more specific experience details')
        
        recommendations.append('Build projects relevant to your target role')
        
        return recommendations
