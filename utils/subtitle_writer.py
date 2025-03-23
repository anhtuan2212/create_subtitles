# utils/subtitle_writer.py
import srt
from datetime import timedelta

def ms(seconds): return timedelta(seconds=seconds)

def generate_srt_from_whisper(segments, output_path):
    subs = []
    for i, seg in enumerate(segments):
        sub = srt.Subtitle(
            index=i + 1,
            start=ms(seg["start"]),
            end=ms(seg["end"]),
            content=seg["text"]
        )
        subs.append(sub)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(srt.compose(subs))
