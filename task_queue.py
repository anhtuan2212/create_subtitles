from queue import Queue
import threading
import sqlite3
from database import update_task_status
import os
import glob

# Hàng đợi toàn cục
task_queue = Queue()

# Lưu thông tin task vào hàng đợi
queue_map = {}


def add_task(task_id, docx_path, audio_path, srt_path):
    task_data = {
        'task_id': task_id,
        'docx_path': docx_path,
        'audio_path': audio_path,
        'srt_path': srt_path,
        'status': 'pending'
    }
    queue_map[task_id] = task_data
    task_queue.put(task_id)

    with sqlite3.connect('tasks.db') as conn:
        conn.execute("INSERT INTO tasks (id, status) VALUES (?, ?)", (task_id, 'pending'))
        conn.commit()


def get_task_status(task_id):
    with sqlite3.connect('tasks.db') as conn:
        cur = conn.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        return {'task_id': task_id, 'status': row[0] if row else 'not_found'}


def cancel_task(task_id):
    if task_id in queue_map:
        update_task_status(task_id, 'cancelled')
        return {'status': 'cancelled'}
    return {'status': 'not_found'}


def delete_task_file(task_id):
    try:
        # Xoá file .srt
        srt_path = f"outputs/{task_id}.srt"
        if os.path.exists(srt_path):
            os.remove(srt_path)

        # Xoá tất cả file trong uploads/ bắt đầu bằng task_id
        for file in glob.glob(f"uploads/{task_id}.*"):
            os.remove(file)

        update_task_status(task_id, 'deleted')
        return {'status': 'deleted'}
    except Exception as e:
        return {'error': str(e)}