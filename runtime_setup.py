#!/usr/bin/env python3
"""Download pinned model assets and verify the isolated recap runtime."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.request
import wave

MODEL_BASE = 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/'
ASSETS = {
    'kokoro-v1.0.onnx': (325532387, '7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5'),
    'voices-v1.0.bin': (28214398, 'bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d'),
}
WHISPER_REPO = 'Systran/faster-whisper-base.en'
WHISPER_REVISION = '3d3d5dee26484f91867d81cb899cfcf72b96be6c'
SOURCE_WHISPER_REPO = 'Systran/faster-whisper-base'
SOURCE_WHISPER_REVISION = 'ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66'


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def download_asset(path, size, digest):
    if path.is_file() and path.stat().st_size == size and sha256(path) == digest:
        print(f'Verified cached model: {path.name}', flush=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + '.part')
    for attempt in range(3):
        try:
            print(f'Downloading {path.name} ({size / 1e6:.0f} MB), attempt {attempt + 1}/3', flush=True)
            request = urllib.request.Request(MODEL_BASE + path.name, headers={'User-Agent': 'movie-recap-installer/1'})
            with urllib.request.urlopen(request, timeout=60) as response, partial.open('wb') as output:
                received = 0
                last_report = time.monotonic()
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
                    received += len(chunk)
                    if received > size:
                        raise RuntimeError(f'Unexpected download size for {path.name}')
                    if time.monotonic() - last_report >= 10:
                        print(f'  {received / 1e6:.0f}/{size / 1e6:.0f} MB', flush=True)
                        last_report = time.monotonic()
            if partial.stat().st_size != size or sha256(partial) != digest:
                raise RuntimeError(f'Checksum mismatch for {path.name}; refusing to load it')
            partial.replace(path)
            return
        except (OSError, RuntimeError) as exc:
            if attempt == 2:
                raise RuntimeError(f'Could not obtain {path.name}: {exc}') from exc
            time.sleep(2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-dir', required=True, type=Path)
    parser.add_argument('--requirements-sha256', required=True)
    args = parser.parse_args()
    root = args.runtime_dir.expanduser().resolve()
    os.environ['OMP_NUM_THREADS'] = '4'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
    import av
    import imageio_ffmpeg
    import numpy as np
    import onnxruntime as ort
    import kokoro_onnx
    from PIL import Image
    from huggingface_hub import snapshot_download
    from faster_whisper import WhisperModel

    kokoro_dir = root / 'models' / 'kokoro'
    for name, (size, digest) in ASSETS.items():
        download_asset(kokoro_dir / name, size, digest)
    print('Downloading/reusing pinned English Whisper model...', flush=True)
    whisper_dir = Path(snapshot_download(
        repo_id=WHISPER_REPO, revision=WHISPER_REVISION,
        local_dir=str(root / 'models' / 'whisper-base.en'),
        allow_patterns=['config.json', 'model.bin', 'tokenizer.json', 'vocabulary.txt'],
    )).resolve()
    for name in ['config.json', 'model.bin', 'tokenizer.json', 'vocabulary.txt']:
        if not (whisper_dir / name).is_file():
            raise RuntimeError(f'Whisper download is incomplete: {name}')
    print('Downloading/reusing pinned multilingual source-film model...', flush=True)
    source_whisper_dir = Path(snapshot_download(
        repo_id=SOURCE_WHISPER_REPO, revision=SOURCE_WHISPER_REVISION,
        local_dir=str(root / 'models' / 'whisper-base'),
        allow_patterns=['config.json', 'model.bin', 'tokenizer.json', 'vocabulary.txt'],
    )).resolve()

    ffmpeg = str(Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve())
    subprocess.run([ffmpeg, '-version'], check=True, stdout=subprocess.DEVNULL)
    checks = root / 'checks'
    checks.mkdir(exist_ok=True)
    print('Testing Kokoro am_michael on CPU...', flush=True)

    def cpu_session(path):
        options = ort.SessionOptions()
        options.intra_op_num_threads = 4
        options.inter_op_num_threads = 1
        return ort.InferenceSession(path, options, providers=['CPUExecutionProvider'])

    kokoro_onnx.create_session = cpu_session
    narrator = kokoro_onnx.Kokoro(str(kokoro_dir / 'kokoro-v1.0.onnx'), str(kokoro_dir / 'voices-v1.0.bin'))
    samples, rate = narrator.create('This is a movie recap. The narrator is ready to tell the story.', voice='am_michael', speed=1.0, lang='en-us')
    if len(samples) < rate or not np.isfinite(samples).all() or float(np.max(np.abs(samples))) < .01:
        raise RuntimeError('TTS did not produce valid audible speech')
    speech = checks / 'narrator.wav'
    with wave.open(str(speech), 'wb') as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes((np.clip(samples, -.999, .999) * 32767).astype('<i2').tobytes())
    print('Testing H.264/AAC export and PyAV decoding...', flush=True)
    video = checks / 'narrated-test.mp4'
    subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=640x360:r=24', '-i', str(speech), '-af', 'atempo=1.1', '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '48000', '-ac', '2', '-shortest', '-movflags', '+faststart', str(video)], check=True)
    with av.open(str(video)) as container:
        v = container.streams.video[0]
        a = container.streams.audio[0]
        if v.codec_context.name != 'h264' or v.codec_context.format.name != 'yuv420p' or a.codec_context.name != 'aac':
            raise RuntimeError('Unexpected encoded media format')
        count = sum(1 for _ in container.decode(video=0))
        if count < 24:
            raise RuntimeError('Test video is truncated')
    subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-i', str(video), '-f', 'null', '-'], check=True)
    # Use PCM arrays to avoid decoder API differences across PyAV versions.
    pcm_path = checks / 'asr-16k.wav'
    subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(speech), '-ac', '1', '-ar', '16000', str(pcm_path)], check=True)
    with wave.open(str(pcm_path), 'rb') as stream:
        pcm = np.frombuffer(stream.readframes(stream.getnframes()), dtype='<i2').astype(np.float32) / 32768
    print('Testing Whisper transcription on CPU...', flush=True)
    recognizer = WhisperModel(str(whisper_dir), device='cpu', compute_type='int8', cpu_threads=4, local_files_only=True)
    segments, _ = recognizer.transcribe(pcm, language='en', word_timestamps=True, condition_on_previous_text=False)
    segments = list(segments)
    transcript = ' '.join(segment.text.strip() for segment in segments)
    tokens = set(re.findall(r'[a-z]+', transcript.lower()))
    if not {'movie', 'story'} <= tokens or not any(segment.words for segment in segments):
        raise RuntimeError(f'Speech-recognition smoke test failed: {transcript!r}')
    del recognizer
    print('Testing multilingual source recognizer...', flush=True)
    source_recognizer = WhisperModel(str(source_whisper_dir), device='cpu', compute_type='int8', cpu_threads=4, local_files_only=True)
    source_segments, _ = source_recognizer.transcribe(pcm, language='en', condition_on_previous_text=False)
    source_text = ' '.join(s.text for s in source_segments)
    if 'movie' not in source_text.lower():
        raise RuntimeError('Multilingual recognizer smoke test did not recover the test sentence')
    Image.new('RGB', (1280, 720), 'black').save(checks / 'thumbnail-test.png')
    manifest = {
        'status': 'ready', 'verified_at': datetime.now(timezone.utc).isoformat(),
        'manifest_path': str(root / 'runtime.json'), 'runtime_dir': str(root),
        'python': sys.executable, 'python_version': sys.version.split()[0],
        'ffmpeg': ffmpeg, 'media_probe': 'PyAV (no separate ffprobe executable required)',
        'kokoro_model': str(kokoro_dir / 'kokoro-v1.0.onnx'),
        'kokoro_voices': str(kokoro_dir / 'voices-v1.0.bin'), 'voice': 'am_michael',
        'whisper_model': str(whisper_dir), 'whisper_revision': WHISPER_REVISION,
        'source_whisper_model': str(source_whisper_dir), 'source_whisper_revision': SOURCE_WHISPER_REVISION,
        'default_compute': 'cpu', 'requirements_sha256': args.requirements_sha256,
        'packages': {d.metadata['Name']: d.version for d in importlib.metadata.distributions()},
        'checks': {'tts': 'passed', 'h264_aac_decode': 'passed', 'asr_word_timing': 'passed', 'multilingual_model_load_and_english_smoke': 'passed', 'transcript': transcript},
    }
    temporary = root / 'runtime.json.part'
    temporary.write_text(json.dumps(manifest, indent=2), encoding='utf8')
    temporary.replace(root / 'runtime.json')
    print('Runtime ready:', root / 'runtime.json', flush=True)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(f'Runtime setup failed: {exc}', file=sys.stderr)
        sys.exit(1)
