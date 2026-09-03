import importlib.util, shutil, sys
mods=['fastapi','streamlit','whisper','faster_whisper','chromadb','langchain','sentence_transformers','rank_bm25']
print('Python:', sys.version.split()[0])
print('FFmpeg:', shutil.which('ffmpeg') or 'NOT FOUND')
for m in mods:
    print(f'{m}:', 'OK' if importlib.util.find_spec(m) else 'MISSING')
