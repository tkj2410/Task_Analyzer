from django.test import TestCase
from .scoring import calculate_task_score, detect_circular_dependencies
from datetime import date, timedelta

class ScoringAlgorithmTests(TestCase):
    
    def test_overdue_task_high_priority(self):
        """Overdue tasks should get very high priority scores"""
        task = {
            'title': 'Overdue task',
            'due_date': (date.today() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 3,
            'importance': 5,
            'dependencies': []
        }
        result = calculate_task_score(task, strategy='smart')
        self.assertGreater(result['priority_score'], 100)
    
    def test_missing_data_handling(self):
        """Algorithm should handle missing optional data"""
        task = {
            'title': 'Minimal task',
            'due_date': date.today().strftime('%Y-%m-%d'),
            'estimated_hours': 1,
            'importance': 5
        }
        result = calculate_task_score(task, strategy='smart')
        self.assertIsNotNone(result['priority_score'])
    
    def test_circular_dependency_detection(self):
        """Should detect circular dependencies"""
        tasks = [
            {'title': 'A', 'dependencies': [1]},
            {'title': 'B', 'dependencies': [2]},
            {'title': 'C', 'dependencies': [0]}
        ]
        circular = detect_circular_dependencies(tasks)
        self.assertTrue(len(circular) > 0)