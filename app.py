import os
import random
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template
from task_queue import task_queue, add_task, get_task_status, cancel_task, delete_task_file
from database import init_db, get_all_tasks , delete_task

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(
    __name__,
    static_folder=os.path.join(basedir, 'static'),
    template_folder=os.path.join(basedir, 'templates')
)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    docx_file = request.files.get('docx')
    audio_file = request.files.get('audio')

    if not docx_file or not audio_file:
        return jsonify({'error': 'Missing file'}), 400

    task_id = datetime.now().strftime('%Y%m%d%H%M%S') + f"_{random.randint(1000,9999)}"
    docx_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}.docx")
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}.mp3")
    srt_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{task_id}.srt")

    docx_file.save(docx_path)
    audio_file.save(audio_path)

    add_task(task_id, docx_path, audio_path, srt_path)

    return jsonify({'task_id': task_id})

@app.route('/tasks', methods=['GET'])
def list_tasks():
    return jsonify(get_all_tasks())

@app.route('/status/<task_id>', methods=['GET'])
def task_status(task_id):
    return jsonify(get_task_status(task_id))

@app.route('/download/<task_id>', methods=['GET'])
def download(task_id):
    srt_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{task_id}.srt")
    if os.path.exists(srt_path):
        return send_file(srt_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/cancel/<task_id>', methods=['POST'])
def cancel(task_id):
    delete_task_file(task_id)
    return jsonify(cancel_task(task_id))

@app.route('/delete/<task_id>', methods=['POST'])
def delete_file(task_id):
    delete_task_file(task_id)
    if delete_task(task_id):
        return jsonify({'status': 'deleted'})
    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    from task_worker import start_worker
    start_worker()
    app.run(debug=True)
