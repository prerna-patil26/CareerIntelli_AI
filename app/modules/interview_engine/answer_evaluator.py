"""Answer evaluator module for evaluating interview answers."""

from typing import Dict, Any, List
import re


class AnswerEvaluator:
    """Evaluate interview answers for quality and relevance."""
    
    def __init__(self):
        """Initialize the answer evaluator."""
        self.min_answer_length = 50
    
    def evaluate_answer(self, 
                       answer: str, 
                       question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an interview answer.
        
        Args:
            answer: User's answer
            question: Question details
        
        Returns:
            Evaluation results
        """
        evaluation = {
            'relevance_score': 0,
            'completeness_score': 0,
            'clarity_score': 0,
            'length_score': 0,
            'keyword_coverage': 0
        }
        
        # Evaluate length
        evaluation['length_score'] = self._evaluate_length(answer)
        
        # Evaluate keyword coverage
        expected_keywords = question.get('expected_keywords', [])
        evaluation['keyword_coverage'] = self._evaluate_keywords(answer, expected_keywords)
        
        # Evaluate clarity
        evaluation['clarity_score'] = self._evaluate_clarity(answer)
        
        # Calculate overall score
        overall_score = (
            evaluation['length_score'] * 0.2 +
            evaluation['keyword_coverage'] * 0.4 +
            evaluation['clarity_score'] * 0.3 +
            evaluation['relevance_score'] * 0.1
        )
        
        evaluation['overall_score'] = overall_score
        
        return evaluation
    
    def _evaluate_length(self, answer: str) -> float:
        """Evaluate answer length appropriateness."""
        words = len(answer.split())
        if words < 50:
            return 0.3
        elif words < 100:
            return 0.6
        elif words < 300:
            return 1.0
        else:
            return 0.8
    
    def _evaluate_keywords(self, answer: str, keywords: List[str]) -> float:
        """Evaluate presence of expected keywords."""
        if not keywords:
            return 0.5
        
        answer_lower = answer.lower()
        found = sum(1 for keyword in keywords if keyword.lower() in answer_lower)
        
        return min(found / len(keywords), 1.0)
    
    def _evaluate_clarity(self, answer: str) -> float:
        """Evaluate answer clarity."""
        # Simple clarity check based on punctuation and structure
        sentences = len([s for s in answer.split('.') if s.strip()])
        
        if sentences < 2:
            return 0.4
        elif sentences < 5:
            return 0.7
        else:
            return 1.0
