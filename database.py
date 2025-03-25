import sqlite3

def init_db():
    with sqlite3.connect('tasks.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            status TEXT,
            docx_path TEXT,
            audio_path TEXT,
            srt_path TEXT
        )''')
        conn.commit()

def update_task_status(task_id, status, srt_path=None):
    with sqlite3.connect('tasks.db') as conn:
        if srt_path:
            conn.execute(
                "UPDATE tasks SET status = ?, srt_path = ? WHERE id = ?",
                (status, srt_path, task_id)
            )
        else:
            conn.execute(
                "UPDATE tasks SET status = ? WHERE id = ?",
                (status, task_id)
            )
        conn.commit()

def insert_task(task_id, status, docx_path, audio_path, srt_path):
    with sqlite3.connect('tasks.db') as conn:
        conn.execute("INSERT INTO tasks (id, status, docx_path, audio_path, srt_path) VALUES (?, ?, ?, ?, ?)",
                     (task_id, status, docx_path, audio_path, srt_path))
        conn.commit()

def get_all_tasks():
    with sqlite3.connect('tasks.db') as conn:
        cur = conn.execute("SELECT id, status, docx_path, audio_path, srt_path FROM tasks ORDER BY id DESC")
        return [
            {
                'task_id': row[0],
                'status': row[1],
                'docx': row[2],
                'audio': row[3],
                'srt': row[4]
            } for row in cur.fetchall()
        ]

def delete_task(task_id):
    with sqlite3.connect('tasks.db') as conn:
        cur = conn.execute("SELECT docx_path, audio_path, srt_path FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        if row:
            for path in row:
                if path and os.path.exists(path):
                    os.remove(path)
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return True
    return False