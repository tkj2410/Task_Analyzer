// API Base URL
const API_URL = 'http://127.0.0.1:8000/api/tasks';

// State
let tasks = [];

// DOM Elements
const taskForm = document.getElementById('taskForm');
const jsonInput = document.getElementById('jsonInput');
const loadJsonBtn = document.getElementById('loadJson');
const analyzeBtn = document.getElementById('analyzeBtn');
const taskList = document.getElementById('taskList');
const taskCount = document.getElementById('taskCount');
const results = document.getElementById('results');
const loading = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const strategySelect = document.getElementById('strategy');

// Event Listeners
taskForm.addEventListener('submit', addTask);
loadJsonBtn.addEventListener('click', loadFromJson);
analyzeBtn.addEventListener('click', analyzeTasks);

// Add individual task
function addTask(e) {
    e.preventDefault();
    
    const task = {
        title: document.getElementById('title').value,
        due_date: document.getElementById('dueDate').value,
        estimated_hours: parseInt(document.getElementById('hours').value),
        importance: parseInt(document.getElementById('importance').value),
        dependencies: []
    };
    
    // Validate
    if (task.importance < 1 || task.importance > 10) {
        showError('Importance must be between 1 and 10');
        return;
    }
    
    tasks.push(task);
    updateTaskList();
    taskForm.reset();
}

// Load tasks from JSON
function loadFromJson() {
    try {
        const jsonData = JSON.parse(jsonInput.value);
        
        if (!Array.isArray(jsonData)) {
            throw new Error('JSON must be an array of tasks');
        }
        
        // Validate each task
        jsonData.forEach(task => {
            if (!task.title || !task.due_date || !task.estimated_hours || !task.importance) {
                throw new Error('Each task must have title, due_date, estimated_hours, and importance');
            }
        });
        
        tasks = jsonData;
        updateTaskList();
        jsonInput.value = '';
        showError('', false);
    } catch (error) {
        showError('Invalid JSON: ' + error.message);
    }
}

// Update task list display
function updateTaskList() {
    taskCount.textContent = tasks.length;
    
    if (tasks.length === 0) {
        taskList.innerHTML = '<p style="color: #999;">No tasks added yet</p>';
        return;
    }
    
    taskList.innerHTML = tasks.map((task, index) => `
        <div class="task-item">
            <span>${task.title} (Due: ${task.due_date})</span>
            <button onclick="removeTask(${index})">Remove</button>
        </div>
    `).join('');
}

// Remove task
function removeTask(index) {
    tasks.splice(index, 1);
    updateTaskList();
}

// Analyze tasks
async function analyzeTasks() {
    if (tasks.length === 0) {
        showError('Please add at least one task');
        return;
    }
    
    loading.classList.remove('hidden');
    results.innerHTML = '';
    showError('', false);
    
    try {
        const strategy = strategySelect.value;
        
        const response = await fetch(`${API_URL}/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks,
                strategy: strategy
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to analyze tasks');
        }
        
        const data = await response.json();
        displayResults(data);
    } catch (error) {
        showError('Error: ' + error.message);
    } finally {
        loading.classList.add('hidden');
    }
}

// Display results
function displayResults(data) {
    const { tasks: sortedTasks, circular_dependencies, strategy_used } = data;
    
    let html = '';
    
    // Show circular dependency warning
    if (circular_dependencies && circular_dependencies.length > 0) {
        html += `
            <div class="error">
                ⚠️ Warning: Circular dependencies detected in tasks: ${circular_dependencies.join(', ')}
            </div>
        `;
    }
    
    // Show strategy used
    html += `<p style="margin-bottom: 15px; color: #667eea; font-weight: bold;">
        Strategy: ${getStrategyName(strategy_used)}
    </p>`;
    
    // Display tasks
    sortedTasks.forEach((task, index) => {
        html += `
            <div class="result-card ${task.priority_level.toLowerCase()}">
                <h3>
                    ${index + 1}. ${task.title}
                    <span class="score-badge">${task.priority_score}</span>
                    <span class="priority-badge ${task.priority_level}">${task.priority_level}</span>
                </h3>
                <div class="task-details">
                    📅 Due: ${task.due_date} | 
                    ⏱️ Effort: ${task.estimated_hours}h | 
                    ⭐ Importance: ${task.importance}/10
                    ${task.dependencies.length > 0 ? ` | 🔗 Blocks ${task.dependencies.length} tasks` : ''}
                </div>
                <div class="explanation">
                    <strong>Why this priority?</strong> ${task.explanation}
                </div>
            </div>
        `;
    });
    
    results.innerHTML = html;
}

// Helper: Get strategy name
function getStrategyName(strategy) {
    const names = {
        'smart': 'Smart Balance',
        'fastest': 'Fastest Wins',
        'impact': 'High Impact',
        'deadline': 'Deadline Driven'
    };
    return names[strategy] || strategy;
}

// Show/hide error
function showError(message, show = true) {
    if (show && message) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    } else {
        errorDiv.classList.add('hidden');
    }
}

// Initialize
updateTaskList();