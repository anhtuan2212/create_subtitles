import threading
from task_queue import task_queue, queue_map
from utils.docx_parser import parse_docx
from utils.whisper_transcriber import transcribe_with_whisper
from utils.subtitle_writer import generate_srt_from_whisper
from database import update_task_status

def split_text_to_lines(text, max_chars=40):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        if sum(len(w) + 1 for w in current_line + [word]) <= max_chars:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)

def worker():
    while True:
        task_id = task_queue.get()
        task = queue_map.get(task_id)
        if not task:
            continue

        update_task_status(task_id, 'processing')
        try:
            # Lấy nội dung văn bản gốc từ file docx
            docx_text = " ".join(parse_docx(task['docx_path']))

            # Nhận diện âm thanh từ Whisper (có timestamp)
            whisper_segments = transcribe_with_whisper(task['audio_path'])

            # Tính toán tổng độ dài & chuẩn bị danh sách từ
            total_audio_duration = sum(seg['end'] - seg['start'] for seg in whisper_segments)
            words = docx_text.split()
            total_words = len(words)

            mapped_segments = []
            start_word = 0

            for seg in whisper_segments:
                proportion = (seg['end'] - seg['start']) / total_audio_duration
                chunk_word_count = round(proportion * total_words)
                text_chunk_raw = " ".join(words[start_word:start_word + chunk_word_count]).strip()
                text_chunk = split_text_to_lines(text_chunk_raw, max_chars=40)

                mapped_segments.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": text_chunk
                })

                start_word += chunk_word_count

            # Ghi ra file SRT
            generate_srt_from_whisper(mapped_segments, task['srt_path'])
            update_task_status(task_id, 'done')
        except Exception as e:
            print(f"Task {task_id} failed: {str(e)}")
            update_task_status(task_id, 'error')

def start_worker():
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
