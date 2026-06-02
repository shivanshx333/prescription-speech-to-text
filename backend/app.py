"""
app.py
======
Flask backend server for the Prescription Speech-to-Text system.

Endpoints:
    POST /api/process       — Upload audio file → Whisper STT → parse → JSON
    POST /api/process-text  — Submit raw text → parse → JSON (for testing)
    GET  /api/health        — Health check

The server loads the Whisper model once on startup and reuses it for all
requests. Audio files are temporarily saved, transcribed, and deleted.
"""

import os
import tempfile
import time
import traceback

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import whisper
from pydub import AudioSegment
import subprocess

from prescription_parser import parse_prescription


# --------------------------------------------------------------------------
# Check ffmpeg availability & add to PATH if needed
# --------------------------------------------------------------------------
def check_ffmpeg():
    """Verify that ffmpeg is installed and accessible."""
    # First check if ffmpeg is already in PATH
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print("[INFO] ffmpeg is available in PATH.")
            return True
    except FileNotFoundError:
        pass
    except Exception:
        pass

    # ffmpeg not in PATH — search common Windows install locations
    print("[INFO] ffmpeg not in PATH, searching common install locations...")
    common_dirs = [
        os.path.expanduser(
            r"~\AppData\Local\Microsoft\WinGet\Packages"
            r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
            r"\ffmpeg-8.1.1-full_build\bin"
        ),
        os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Links"),
        r"C:\ProgramData\chocolatey\bin",
        r"C:\ffmpeg\bin",
    ]
    for bin_dir in common_dirs:
        ffmpeg_path = os.path.join(bin_dir, "ffmpeg.exe")
        if os.path.exists(ffmpeg_path):
            # Add the directory to PATH so pydub/subprocess can find it
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
            # Also explicitly tell pydub
            AudioSegment.converter = ffmpeg_path
            ffprobe_path = os.path.join(bin_dir, "ffprobe.exe")
            if os.path.exists(ffprobe_path):
                AudioSegment.ffprobe = ffprobe_path
            print(f"[INFO] ffmpeg found and added to PATH: {bin_dir}")
            return True

    print("[WARNING] ffmpeg not found! Audio conversion will fail.")
    print("[WARNING] Please restart your terminal and run 'python app.py' again,")
    print("[WARNING] or reinstall ffmpeg: winget install ffmpeg")
    return False


check_ffmpeg()

# --------------------------------------------------------------------------
# App Configuration
# --------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the frontend

# Whisper model size: tiny, base, small, medium, large
# 'base' offers a good balance between accuracy and speed
WHISPER_MODEL_SIZE = os.environ.get("WHISPER_MODEL", "base")

# --------------------------------------------------------------------------
# Load Whisper Model (cached — loaded once at startup)
# --------------------------------------------------------------------------
print(f"[INFO] Loading Whisper model '{WHISPER_MODEL_SIZE}'...")
start_time = time.time()
whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
load_time = time.time() - start_time
print(f"[INFO] Whisper model loaded in {load_time:.2f} seconds.")


# --------------------------------------------------------------------------
# Utility Functions
# --------------------------------------------------------------------------
def convert_audio_to_wav(input_path, output_path):
    """
    Convert any audio format (WebM, OGG, MP3, etc.) to WAV using pydub.

    This is needed because Whisper works best with WAV files.
    pydub uses ffmpeg under the hood for the conversion.
    """
    audio = AudioSegment.from_file(input_path)
    # Convert to mono, 16kHz (Whisper's expected format)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    return output_path


def transcribe_audio(audio_path):
    """
    Transcribe an audio file using Whisper.

    Args:
        audio_path (str): Path to the audio file (WAV format preferred)

    Returns:
        dict: {
            "text": str,           # Full transcription text
            "language": str,       # Detected language
            "duration": float,     # Processing time in seconds
        }
    """
    start_time = time.time()

    # Run Whisper transcription
    result = whisper_model.transcribe(
        audio_path,
        language="en",      # Force English (as per requirement)
        fp16=False,         # Use FP32 for CPU compatibility
    )

    duration = time.time() - start_time

    return {
        "text": result["text"].strip(),
        "language": result.get("language", "en"),
        "duration": round(duration, 2),
    }


# --------------------------------------------------------------------------
# API Endpoints
# --------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify the server is running."""
    return jsonify({
        "status": "healthy",
        "whisper_model": WHISPER_MODEL_SIZE,
        "message": "Prescription Speech-to-Text API is running.",
    })


@app.route("/api/process", methods=["POST"])
def process_audio():
    """
    Process an uploaded audio file:
    1. Receive audio file from the frontend
    2. Convert to WAV if necessary
    3. Transcribe using Whisper
    4. Parse the transcription to extract prescription details
    5. Return structured JSON

    Expects: multipart/form-data with an 'audio' file field
    Returns: JSON with transcription and parsed prescription data
    """
    # --- Validate input ---
    if "audio" not in request.files:
        return jsonify({
            "error": "No audio file provided. Please upload an audio file.",
            "hint": "Send a POST request with a file field named 'audio'.",
        }), 400

    audio_file = request.files["audio"]

    if audio_file.filename == "":
        return jsonify({"error": "Empty filename. Please select a file."}), 400

    # --- Save and process audio ---
    temp_dir = tempfile.mkdtemp()
    temp_wav = os.path.join(temp_dir, "audio.wav")

    try:
        # Save uploaded file with proper extension (pydub needs this)
        original_filename = audio_file.filename or "recording.webm"
        ext = os.path.splitext(original_filename)[1] or ".webm"
        temp_input = os.path.join(temp_dir, f"input_audio{ext}")

        audio_file.save(temp_input)
        file_size = os.path.getsize(temp_input)
        print(f"[INFO] Received audio file: {original_filename} ({file_size} bytes, ext={ext})")

        if file_size < 100:
            return jsonify({
                "error": "Audio file is too small. Please record for at least 2-3 seconds.",
            }), 400

        # Convert to WAV
        print("[INFO] Converting audio to WAV format...")
        convert_audio_to_wav(temp_input, temp_wav)

        # Transcribe with Whisper
        print("[INFO] Transcribing audio with Whisper...")
        transcription = transcribe_audio(temp_wav)
        print(f"[INFO] Transcription: \"{transcription['text']}\"")
        print(f"[INFO] Transcription took {transcription['duration']}s")

        # Check if transcription is empty
        if not transcription["text"]:
            return jsonify({
                "error": "Could not transcribe audio. The recording may be too short or unclear.",
                "hint": "Try speaking more clearly and closer to the microphone.",
            }), 422

        # Parse prescription
        print("[INFO] Parsing prescription text...")
        parsed = parse_prescription(transcription["text"])

        # Build response
        response = {
            "success": True,
            "transcription": {
                "text": transcription["text"],
                "language": transcription["language"],
                "processing_time": transcription["duration"],
            },
            "prescription": parsed,
        }

        print(f"[INFO] Found {parsed['num_medicines']} medicine(s)")
        return jsonify(response), 200

    except Exception as e:
        print(f"[ERROR] Processing failed: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "error": f"Processing failed: {str(e)}",
            "hint": "Please try again. Make sure ffmpeg is installed.",
        }), 500

    finally:
        # Clean up temporary files
        for f in [temp_input, temp_wav]:
            if os.path.exists(f):
                os.remove(f)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)


@app.route("/api/process-text", methods=["POST"])
def process_text():
    """
    Process raw text input (for testing without microphone).

    Expects: JSON body with a 'text' field
    Returns: JSON with parsed prescription data
    """
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({
            "error": "No text provided.",
            "hint": "Send a JSON body with a 'text' field.",
        }), 400

    text = data["text"].strip()

    if not text:
        return jsonify({"error": "Empty text provided."}), 400

    print(f"[INFO] Processing text input: \"{text}\"")

    # Parse prescription
    parsed = parse_prescription(text)

    response = {
        "success": True,
        "transcription": {
            "text": text,
            "language": "en",
            "processing_time": 0,
        },
        "prescription": parsed,
    }

    print(f"[INFO] Found {parsed['num_medicines']} medicine(s)")
    return jsonify(response), 200


# --------------------------------------------------------------------------
# Serve Frontend (optional — for convenience)
# --------------------------------------------------------------------------
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")


@app.route("/")
def serve_frontend():
    """Serve the frontend index.html from the frontend directory."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static frontend files (CSS, JS, images)."""
    return send_from_directory(FRONTEND_DIR, filename)


# --------------------------------------------------------------------------
# Main Entry Point
# --------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  PRESCRIPTION SPEECH-TO-TEXT SERVER")
    print("=" * 60)
    print(f"  Whisper Model : {WHISPER_MODEL_SIZE}")
    print(f"  API Endpoint  : http://localhost:5000")
    print(f"  Frontend      : http://localhost:5000")
    print(f"  Health Check  : http://localhost:5000/api/health")
    print("=" * 60 + "\n")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,   # Disable reloader to avoid re-loading Whisper model
    )
