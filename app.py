import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables (useful for local testing)
load_dotenv()

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
# Render uses 'postgres://', but SQLAlchemy 1.4+ requires 'postgresql://'
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODEL ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

# Initialize the database (creates tables if they don't exist)
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def index():
    """Serves the main HTML page"""
    return render_template('index.html')

@app.route('/tasks', methods=['GET', 'POST'])
def handle_tasks():
    """Handles fetching all tasks (GET) and creating new ones (POST)"""
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({"error": "Missing title"}), 400
            
        new_task = Task(title=data['title'])
        db.session.add(new_task)
        db.session.commit()
        return jsonify({"id": new_task.id, "title": new_task.title}), 201
    
    # GET method: return all tasks
    tasks = Task.query.order_by(Task.id.desc()).all()
    return jsonify([{"id": t.id, "title": t.title} for t in tasks])

@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    """Handles deleting a specific task by its ID"""
    task = Task.query.get(id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": f"Task {id} deleted successfully"}), 200
    
    return jsonify({"error": "Task not found"}), 404

# --- START SERVER ---
if __name__ == "__main__":
    # Local development settings
    app.run(debug=True)
