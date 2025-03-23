# utils/whisper_transcriber.py
import whisper

def transcribe_with_whisper(audio_path: str):
    model = whisper.load_model("base")  # Có thể dùng "small", "medium", "large"
    result = model.transcribe(audio_path, word_timestamps=True)
    
    # Lấy ra các đoạn transcript có thời gian
    segments = []
    for seg in result['segments']:
        segments.append({
            'start': seg['start'],
            'end': seg['end'],
            'text': seg['text'].strip()
        })
    return segments
