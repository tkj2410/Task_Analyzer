from datetime import date, datetime
from typing import Dict, List, Any

def calculate_task_score(task: Dict[str, Any], all_tasks: List[Dict] = None, strategy: str = 'smart') -> Dict[str, Any]:
    """
    Calculate priority score for a task.
    Higher score = Higher priority
    
    Args:
        task: Dictionary containing task data
        all_tasks: List of all tasks (for dependency calculation)
        strategy: Scoring strategy ('smart', 'fastest', 'impact', 'deadline')
    
    Returns:
        Dictionary with task and calculated score
    """
    score = 0
    explanation_parts = []
    
    # Parse due date
    if isinstance(task.get('due_date'), str):
        due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
    else:
        due_date = task.get('due_date', date.today())
    
    # Get other values with defaults
    importance = task.get('importance', 5)
    estimated_hours = task.get('estimated_hours', 1)
    dependencies = task.get('dependencies', [])
    
    # Calculate days until due
    today = date.today()
    days_until_due = (due_date - today).days
    
    # === URGENCY CALCULATION ===
    urgency_score = 0
    if days_until_due < 0:
        # Overdue - highest urgency
        urgency_score = 100 + abs(days_until_due) * 5
        explanation_parts.append(f"OVERDUE by {abs(days_until_due)} days (+{urgency_score} urgency)")
    elif days_until_due == 0:
        urgency_score = 80
        explanation_parts.append(f"Due TODAY (+{urgency_score} urgency)")
    elif days_until_due <= 1:
        urgency_score = 60
        explanation_parts.append(f"Due tomorrow (+{urgency_score} urgency)")
    elif days_until_due <= 3:
        urgency_score = 40
        explanation_parts.append(f"Due in {days_until_due} days (+{urgency_score} urgency)")
    elif days_until_due <= 7:
        urgency_score = 20
        explanation_parts.append(f"Due this week (+{urgency_score} urgency)")
    else:
        urgency_score = max(0, 100 - days_until_due * 2)
    
    # === STRATEGY-BASED SCORING ===
    if strategy == 'smart':
        # Balanced approach
        importance_weight = importance * 5
        effort_penalty = estimated_hours * 2
        dependency_bonus = len(dependencies) * 10 if all_tasks else 0
        
        score = urgency_score + importance_weight + dependency_bonus - effort_penalty
        
        if importance >= 8:
            explanation_parts.append(f"High importance ({importance}/10)")
        if estimated_hours <= 2:
            explanation_parts.append(f"Quick win ({estimated_hours}h)")
        if dependency_bonus > 0:
            explanation_parts.append(f"Blocks {len(dependencies)} tasks")
    
    elif strategy == 'fastest':
        # Prioritize low-effort tasks
        score = urgency_score + (importance * 2) - (estimated_hours * 10)
        explanation_parts.append(f"Low effort prioritized ({estimated_hours}h)")
    
    elif strategy == 'impact':
        # Prioritize importance
        score = (importance * 10) + urgency_score
        explanation_parts.append(f"High impact focus (importance: {importance}/10)")
    
    elif strategy == 'deadline':
        # Prioritize by deadline
        score = urgency_score + (importance * 2)
        explanation_parts.append(f"Deadline focused")
    
    return {
        **task,
        'priority_score': round(score, 2),
        'explanation': ' | '.join(explanation_parts),
        'priority_level': 'HIGH' if score > 80 else 'MEDIUM' if score > 40 else 'LOW'
    }


def detect_circular_dependencies(tasks: List[Dict]) -> List[str]:
    """
    Detect circular dependencies in task list.
    Returns list of task IDs involved in circular dependencies.
    """
    def has_cycle(task_id, visited, rec_stack, adjacency):
        visited.add(task_id)
        rec_stack.add(task_id)
        
        for neighbor in adjacency.get(task_id, []):
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack, adjacency):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(task_id)
        return False
    
    # Build adjacency list
    adjacency = {}
    for i, task in enumerate(tasks):
        adjacency[i] = task.get('dependencies', [])
    
    visited = set()
    circular = []
    
    for i in range(len(tasks)):
        if i not in visited:
            if has_cycle(i, visited, set(), adjacency):
                circular.append(i)
    
    return circular