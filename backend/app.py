"""
app.py
======
Flask backend for the Prescription Speech-to-Text system.

Endpoints:
    POST /api/process       — Upload audio → Whisper STT → parse (local only)
    POST /api/process-text  — Submit text → parse → JSON (primary endpoint)
    GET  /api/health        — Health check

Whisper is optional. When deployed to the cloud, the browser's Web Speech
API handles speech-to-text and the server only parses text.
"""

import os
import tempfile
import time
import traceback

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from prescription_parser import parse_prescription

# --------------------------------------------------------------------------
# Optional Whisper support (heavy dependency — skipped on cloud deploys)
# --------------------------------------------------------------------------
WHISPER_AVAILABLE = False
whisper_model = None

try:
    import whisper
    from pydub import AudioSegment
    import subprocess

    def _check_ffmpeg():
        try:
            r = subprocess.run(["ffmpeg", "-version"],
                               capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                return True
        except Exception:
            pass
        # Windows-specific fallback paths
        for d in [
            os.path.expanduser(
                r"~\AppData\Local\Microsoft\WinGet\Packages"
                r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
                r"\ffmpeg-8.1.1-full_build\bin"
            ),
            os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Links"),
            r"C:\ProgramData\chocolatey\bin",
            r"C:\ffmpeg\bin",
        ]:
            if os.path.exists(os.path.join(d, "ffmpeg.exe")):
                os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
                AudioSegment.converter = os.path.join(d, "ffmpeg.exe")
                fp = os.path.join(d, "ffprobe.exe")
                if os.path.exists(fp):
                    AudioSegment.ffprobe = fp
                return True
        return False

    _check_ffmpeg()

    WHISPER_MODEL_SIZE = os.environ.get("WHISPER_MODEL", "base")
    print(f"[INFO] Loading Whisper model '{WHISPER_MODEL_SIZE}'...")
    t0 = time.time()
    whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
    print(f"[INFO] Whisper loaded in {time.time() - t0:.1f}s")
    WHISPER_AVAILABLE = True

except ImportError:
    print("[INFO] Whisper not installed — voice upload disabled.")
    print("[INFO] Text parsing is fully functional.")
except Exception as e:
    print(f"[WARN] Whisper failed to load: {e}")
    print("[INFO] Text parsing is fully functional.")

# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "voice_upload": WHISPER_AVAILABLE,
        "message": "Prescription Speech-to-Text API is running.",
    })


@app.route("/api/process-text", methods=["POST"])
def process_text():
    """Primary endpoint: parse prescription text into structured data."""
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "No text provided."}), 400

    text = data["text"].strip()
    if not text:
        return jsonify({"error": "Empty text provided."}), 400

    print(f'[INFO] Parsing: "{text[:120]}..."')
    parsed = parse_prescription(text)
    print(f"[INFO] Found {parsed['num_medicines']} medicine(s)")

    return jsonify({
        "success": True,
        "transcription": {"text": text, "language": "en", "processing_time": 0},
        "prescription": parsed,
    })


@app.route("/api/process", methods=["POST"])
def process_audio():
    """Upload audio → Whisper transcription → parse. Only works locally."""
    if not WHISPER_AVAILABLE:
        return jsonify({
            "error": "Voice upload not available on this server. Use the microphone button (browser speech recognition) or type text.",
        }), 503

    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided."}), 400

    audio_file = request.files["audio"]
    if audio_file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    temp_dir = tempfile.mkdtemp()
    temp_wav = os.path.join(temp_dir, "audio.wav")
    ext = os.path.splitext(audio_file.filename or "r.webm")[1] or ".webm"
    temp_input = os.path.join(temp_dir, f"input{ext}")

    try:
        audio_file.save(temp_input)
        if os.path.getsize(temp_input) < 100:
            return jsonify({"error": "Audio too short."}), 400

        audio = AudioSegment.from_file(temp_input)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(temp_wav, format="wav")

        t0 = time.time()
        result = whisper_model.transcribe(temp_wav, language="en", fp16=False)
        duration = round(time.time() - t0, 2)
        text = result["text"].strip()

        if not text:
            return jsonify({"error": "Could not transcribe audio."}), 422

        parsed = parse_prescription(text)
        return jsonify({
            "success": True,
            "transcription": {
                "text": text,
                "language": result.get("language", "en"),
                "processing_time": duration,
            },
            "prescription": parsed,
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Processing failed: {e}"}), 500
    finally:
        for f in [temp_input, temp_wav]:
            if os.path.exists(f):
                os.remove(f)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)


# --------------------------------------------------------------------------
# Serve frontend
# --------------------------------------------------------------------------
@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "=" * 60)
    print("  PRESCRIPTION SPEECH-TO-TEXT SERVER")
    print("=" * 60)
    print(f"  Voice Upload : {'Yes' if WHISPER_AVAILABLE else 'No (browser speech used)'}")
    print(f"  URL          : http://localhost:{port}")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
