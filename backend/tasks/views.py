from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .scoring import calculate_task_score, detect_circular_dependencies
from datetime import datetime

@api_view(['POST'])
def analyze_tasks(request):
    """
    Analyze and sort tasks by priority.
    
    Request body:
    {
        "tasks": [...],
        "strategy": "smart" (optional)
    }
    """
    try:
        tasks = request.data.get('tasks', [])
        strategy = request.data.get('strategy', 'smart')
        
        if not tasks:
            return Response(
                {'error': 'No tasks provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate and score each task
        scored_tasks = []
        for task in tasks:
            # Validate required fields
            if not all(k in task for k in ['title', 'due_date', 'estimated_hours', 'importance']):
                return Response(
                    {'error': f'Missing required fields in task: {task.get("title", "Unknown")}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            scored_task = calculate_task_score(task, tasks, strategy)
            scored_tasks.append(scored_task)
        
        # Sort by priority score (highest first)
        scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Detect circular dependencies
        circular_deps = detect_circular_dependencies(tasks)
        
        return Response({
            'tasks': scored_tasks,
            'circular_dependencies': circular_deps,
            'strategy_used': strategy
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def suggest_tasks(request):
    """
    Suggest top 3 tasks to work on today.
    """
    try:
        tasks = request.data.get('tasks', [])
        strategy = request.data.get('strategy', 'smart')
        
        if not tasks:
            return Response({'suggestions': []})
        
        # Score all tasks
        scored_tasks = [calculate_task_score(task, tasks, strategy) for task in tasks]
        
        # Sort and get top 3
        scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
        top_3 = scored_tasks[:3]
        
        suggestions = []
        for i, task in enumerate(top_3, 1):
            suggestions.append({
                'rank': i,
                'task': task,
                'reason': f"Score: {task['priority_score']} - {task['explanation']}"
            })
        
        return Response({'suggestions': suggestions})
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )