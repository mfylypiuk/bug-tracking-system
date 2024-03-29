
"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from flask import request
from flask import abort
from flask import redirect
from flask import url_for
from bug_tracking_system import app
import pyodbc
from flask import jsonify

server = 'bts-dm.database.windows.net'
database = 'bts-dm'
username = 'devmaks'
password = '121212Web'
driver= 'ODBC Driver 17 for SQL Server'
conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)

def generate_tasks_list(cursor):
    tasksList = []
    for task in cursor:
        task = {
            'id' : task.id,
            'type' : task.type,
            'title' : task.title,
            'description' : task.description,
            'priority' : task.priority,
            'status' : task.status}
        tasksList.append(task)
    return tasksList;

def generate_task(cursor):
    for item in cursor:
        task = {
            'id': item.id,
            'type': item.type,
            'title': item.title,
            'description': item.description,
            'priority': item.priority,
            'status': item.status
        }
    return task;

@app.route('/', methods=['GET'])
@app.route('/tasks-list', methods=['GET'])
def generate_tasks_list_page():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dbo.Tasks')
    tasksList = generate_tasks_list(cursor)
    return render_template(
        'tasks-list.html',
        title='Tasks list',
        year=datetime.now().year,
        tasks=tasksList,
    )

@app.route('/tasks', methods=['GET'])
def get_tasks():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dbo.Tasks')
    tasksList = generate_tasks_list(cursor)
    return jsonify(tasksList), 200

@app.route('/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    cursor = conn.cursor()
    query = "SELECT * FROM dbo.Tasks WHERE id = %s" % task_id;
    cursor.execute(query)

    if cursor.rowcount == 0:
        abort(404)
    
    task = generate_task(cursor);
    return jsonify(task), 200

@app.route('/create-task', methods=['POST'])
def create_task():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dbo.Tasks')
    tasksList = generate_tasks_list(cursor)

    if not tasksList:
        id = 1
    else:
        id = tasksList[-1]['id'] + 1

    cursor.execute("INSERT INTO dbo.Tasks(id, type, title, description, priority, status) VALUES (?, ?, ?, ?, ?, ?)", 
        id, request.form['taskType'], request.form['taskTitle'], request.form.get('taskDescription', ""), request.form['taskPriority'], 1)
    cursor.commit()

    return redirect(url_for('generate_tasks_list_page')), 201

@app.route('/new-task', methods=['GET'])
def generate_new_task_page():
    return render_template(
        "new-task.html",
        year=datetime.now().year
    )

@app.route('/edit-task/<int:task_id>', methods=['GET'])
def generate_edit_task_page(task_id):
    cursor = conn.cursor()
    query = "SELECT * FROM dbo.Tasks WHERE id = %s" % task_id;
    cursor.execute(query)

    if cursor.rowcount == 0:
        abort(404)
    
    task = generate_task(cursor);

    return render_template(
        "edit-task.html",
        year=datetime.now().year,
        task=task
    )

@app.route('/save-task/<int:task_id>', methods=['POST', 'GET'])
def save_task(task_id):

    cursor = conn.cursor()
    cursor.execute("UPDATE Tasks SET type = ?, title = ?, description = ?, priority = ?, status = ? WHERE id = ?", 
        request.form['taskType'], request.form['taskTitle'], request.form.get('taskDescription', ""), request.form['taskPriority'], request.form['taskStatus'], task_id)
    cursor.commit()

    cursor.execute('SELECT * FROM dbo.Tasks')
    tasksList = generate_tasks_list(cursor)

    return redirect(url_for('generate_tasks_list_page')), 200
