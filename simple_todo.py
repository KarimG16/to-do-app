"""
Simple Todo App using built-in Python HTTP server
No external dependencies required!
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs
import webbrowser
import threading

class TodoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✨ Todo App</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
    <style>
        body { padding: 2rem; max-width: 800px; margin: 0 auto; }
        .todo-item { 
            display: flex; 
            align-items: center; 
            padding: 1rem; 
            margin: 0.5rem 0;
            background: var(--card-background-color);
            border-radius: 0.5rem;
            border: 1px solid var(--muted-border-color);
            transition: all 0.2s;
        }
        .todo-item:hover { 
            border-color: #4f46e5;
            box-shadow: 0 2px 8px rgba(79, 70, 229, 0.1);
        }
        .todo-item.completed { opacity: 0.6; }
        .todo-item input[type="checkbox"] { 
            margin-right: 1rem;
            width: 1.25rem;
            height: 1.25rem;
            cursor: pointer;
        }
        .todo-text { 
            flex: 1; 
            font-size: 1rem;
        }
        .todo-text.completed { 
            text-decoration: line-through;
            color: var(--muted-color);
        }
        .delete-btn {
            background: #ef4444;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            cursor: pointer;
            font-size: 0.875rem;
        }
        .delete-btn:hover { background: #dc2626; }
        .add-form { 
            display: flex; 
            flex-direction: column;
            gap: 0.75rem;
            margin-bottom: 2rem;
        }
        .add-form input { 
            width: 100%;
            margin: 0;
            padding: 1rem;
            font-size: 1.1rem;
            border-radius: 0.5rem;
        }
        .add-form button {
            width: 100%;
            margin: 0;
            padding: 1rem;
            font-size: 1.1rem;
            font-weight: 600;
            background: #4f46e5;
            border-radius: 0.5rem;
        }
        .add-form button:hover {
            background: #4338ca;
        }
        .stats {
            display: flex;
            gap: 2rem;
            justify-content: center;
            margin: 2rem 0;
            padding: 1rem;
            background: var(--card-background-color);
            border-radius: 0.5rem;
        }
        .stat-item { text-align: center; }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #4f46e5;
        }
        .stat-label {
            font-size: 0.875rem;
            color: var(--muted-color);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        #todo-list { list-style: none; padding: 0; }
        .empty-state {
            text-align: center;
            padding: 3rem 1rem;
            color: var(--muted-color);
        }
    </style>
</head>
<body>
    <main class="container">
        <h1>✨ My Todo List</h1>
        
        <form class="add-form" onsubmit="handleAdd(event)">
            <input type="text" id="todo-input" placeholder="What needs to be done?" required autofocus>
            <button type="submit">Add Todo</button>
        </form>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number" id="stat-total">0</div>
                <div class="stat-label">Total</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="stat-completed">0</div>
                <div class="stat-label">Completed</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="stat-remaining">0</div>
                <div class="stat-label">Remaining</div>
            </div>
        </div>
        
        <ul id="todo-list"></ul>
    </main>

    <script>
        function getTodos() {
            return JSON.parse(localStorage.getItem('todos') || '[]');
        }
        
        function saveTodos(todos) {
            localStorage.setItem('todos', JSON.stringify(todos));
            updateStats();
        }
        
        function addTodo(title) {
            const todos = getTodos();
            const newTodo = {
                id: Date.now(),
                title: title,
                completed: false
            };
            todos.push(newTodo);
            saveTodos(todos);
            return newTodo;
        }
        
        function toggleTodo(id) {
            const todos = getTodos();
            const todo = todos.find(t => t.id === parseInt(id));
            if (todo) {
                todo.completed = !todo.completed;
                saveTodos(todos);
            }
            return todo;
        }
        
        function deleteTodo(id) {
            let todos = getTodos();
            todos = todos.filter(t => t.id !== parseInt(id));
            saveTodos(todos);
        }
        
        function updateStats() {
            const todos = getTodos();
            const total = todos.length;
            const completed = todos.filter(t => t.completed).length;
            const remaining = total - completed;
            
            document.getElementById('stat-total').textContent = total;
            document.getElementById('stat-completed').textContent = completed;
            document.getElementById('stat-remaining').textContent = remaining;
        }
        
        document.addEventListener('DOMContentLoaded', () => {
            loadTodos();
            updateStats();
        });
        
        function loadTodos() {
            const todos = getTodos();
            const todoList = document.getElementById('todo-list');
            
            if (todos.length === 0) {
                todoList.innerHTML = '<div class="empty-state"><p>No todos yet. Add one to get started!</p></div>';
                return;
            }
            
            todoList.innerHTML = todos.map(todo => createTodoHTML(todo)).join('');
        }
        
        function createTodoHTML(todo) {
            return `
                <li class="todo-item ${todo.completed ? 'completed' : ''}" id="todo-${todo.id}">
                    <input type="checkbox" 
                           ${todo.completed ? 'checked' : ''}
                           onchange="handleToggle(${todo.id})">
                    <span class="todo-text ${todo.completed ? 'completed' : ''}">${todo.title}</span>
                    <button class="delete-btn" onclick="handleDelete(${todo.id})">Delete</button>
                </li>
            `;
        }
        
        function handleAdd(event) {
            event.preventDefault();
            const input = document.getElementById('todo-input');
            const title = input.value.trim();
            
            if (title) {
                addTodo(title);
                input.value = '';
                loadTodos();
            }
        }
        
        function handleToggle(id) {
            toggleTodo(id);
            loadTodos();
        }
        
        function handleDelete(id) {
            if (confirm('Are you sure you want to delete this todo?')) {
                deleteTodo(id);
                loadTodos();
            }
        }
    </script>
</body>
</html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_server(port=5001):
    server_address = ('', port)
    httpd = HTTPServer(server_address, TodoHandler)
    print(f"\n✨ Todo App is running!")
    print(f"🌐 Open your browser to: http://localhost:{port}")
    print(f"⚡ Press Ctrl+C to stop the server\n")
    
    # Auto-open browser after a short delay
    def open_browser():
        import time
        time.sleep(1)
        webbrowser.open(f'http://localhost:{port}')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()

