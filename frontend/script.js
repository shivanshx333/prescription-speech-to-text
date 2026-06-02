/**
 * script.js — Prescription Speech-to-Text Frontend
 *
 * Handles microphone recording, API communication, and results rendering
 * for the CRIS Prescription Speech-to-Text System.
 */

const API_BASE = "http://localhost:5000";

// --------------------------------------------------------------------------
// State
// --------------------------------------------------------------------------
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// --------------------------------------------------------------------------
// DOM Elements
// --------------------------------------------------------------------------
const recordBtn        = document.getElementById("recordBtn");
const recordBtnText    = document.getElementById("recordBtnText");
const statusBadge      = document.getElementById("statusBadge");
const recIndicator     = document.getElementById("recIndicator");
const recDot           = recIndicator.querySelector(".rec-dot");
const statusText       = document.getElementById("statusText");
const manualText       = document.getElementById("manualText");
const processTextBtn   = document.getElementById("processTextBtn");
const messageBox       = document.getElementById("messageBox");
const transcriptionCard = document.getElementById("transcriptionCard");
const transcriptionText = document.getElementById("transcriptionText");
const transcriptionMeta = document.getElementById("transcriptionMeta");
const correctedCard    = document.getElementById("correctedCard");
const correctedText    = document.getElementById("correctedText");
const resultsCard      = document.getElementById("resultsCard");
const resultsBody      = document.getElementById("resultsBody");
const resultCount      = document.getElementById("resultCount");
const emptyState       = document.getElementById("emptyState");
const spinnerOverlay   = document.getElementById("spinnerOverlay");
const spinnerText      = document.getElementById("spinnerText");
const serverStatusEl   = document.getElementById("serverStatus");

// --------------------------------------------------------------------------
// Recording
// --------------------------------------------------------------------------

async function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                sampleRate: 16000,
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
            }
        });

        const mimeType = getSupportedMimeType();
        mediaRecorder = new MediaRecorder(stream, { mimeType });
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            stream.getTracks().forEach(t => t.stop());
            const audioBlob = new Blob(audioChunks, { type: mimeType });

            if (audioBlob.size < 1000) {
                showMessage("error", "Recording too short. Please speak for at least 2–3 seconds.");
                setStatus("ready");
                return;
            }

            processAudio(audioBlob);
        };

        mediaRecorder.start(250);
        isRecording = true;

        recordBtnText.textContent = "Stop Recording";
        recordBtn.classList.add("recording");
        setStatus("recording");
        hideMessage();

    } catch (error) {
        if (error.name === "NotAllowedError") {
            showMessage("error", "Microphone access denied. Allow microphone access in browser settings.");
        } else if (error.name === "NotFoundError") {
            showMessage("error", "No microphone found. Please connect a microphone.");
        } else {
            showMessage("error", "Could not access microphone: " + error.message);
        }
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        isRecording = false;
        recordBtnText.textContent = "Start Recording";
        recordBtn.classList.remove("recording");
        setStatus("processing");
    }
}

function getSupportedMimeType() {
    const types = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
        "audio/ogg",
        "audio/mp4",
    ];
    for (const type of types) {
        if (MediaRecorder.isTypeSupported(type)) return type;
    }
    return "audio/webm";
}

// --------------------------------------------------------------------------
// API Communication
// --------------------------------------------------------------------------

async function processAudio(audioBlob) {
    showSpinner("Processing audio...");
    try {
        const formData = new FormData();
        const ext = audioBlob.type.includes("ogg") ? "ogg" :
                    audioBlob.type.includes("mp4") ? "mp4" : "webm";
        formData.append("audio", audioBlob, "recording." + ext);

        const response = await fetch(API_BASE + "/api/process", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Server error.");

        displayResults(data);
        setStatus("ready");
        showMessage("success",
            "Extracted " + data.prescription.num_medicines + " medicine(s) from prescription.");

    } catch (error) {
        setStatus("error");
        if (error.message.includes("Failed to fetch")) {
            showMessage("error", "Cannot connect to server. Ensure the Flask backend is running on localhost:5000.");
        } else {
            showMessage("error", error.message);
        }
    } finally {
        hideSpinner();
    }
}

async function processManualText() {
    const text = manualText.value.trim();
    if (!text) {
        showMessage("error", "Please enter prescription text first.");
        return;
    }

    showSpinner("Parsing prescription text...");
    try {
        const response = await fetch(API_BASE + "/api/process-text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Server error.");

        displayResults(data);
        showMessage("success",
            "Extracted " + data.prescription.num_medicines + " medicine(s) from prescription.");

    } catch (error) {
        if (error.message.includes("Failed to fetch")) {
            showMessage("error", "Cannot connect to server. Ensure the Flask backend is running on localhost:5000.");
        } else {
            showMessage("error", error.message);
        }
    } finally {
        hideSpinner();
    }
}

// --------------------------------------------------------------------------
// Display Results
// --------------------------------------------------------------------------

function displayResults(data) {
    // Hide empty state
    emptyState.classList.add("hidden");

    // Transcription
    transcriptionText.textContent = data.transcription.text;
    let meta = "";
    if (data.transcription.processing_time > 0) {
        meta = "Processing time: " + data.transcription.processing_time + "s";
    }
    transcriptionMeta.textContent = meta;
    transcriptionCard.classList.remove("hidden");

    // Corrected text (show only if different from transcription)
    const corrected = data.prescription.corrected_text || "";
    const normalized = data.prescription.normalized_text || "";
    if (corrected && corrected !== normalized) {
        correctedText.textContent = corrected;
        correctedCard.classList.remove("hidden");
    } else {
        correctedCard.classList.add("hidden");
    }

    // Results table
    resultsBody.innerHTML = "";
    const prescriptions = data.prescription.prescriptions;

    prescriptions.forEach(function(rx, index) {
        const row = document.createElement("tr");

        // Row number
        const numCell = document.createElement("td");
        numCell.textContent = index + 1;
        row.appendChild(numCell);

        // Medicine name
        const medCell = document.createElement("td");
        const confidence = rx.confidence || 0;

        // Confidence dot
        if (confidence > 0 && confidence < 1) {
            const dot = document.createElement("span");
            dot.className = "confidence-indicator " +
                (confidence >= 0.9 ? "confidence-high" :
                 confidence >= 0.8 ? "confidence-medium" : "confidence-low");
            dot.title = "Match confidence: " + Math.round(confidence * 100) + "%";
            medCell.appendChild(dot);
        }

        const medName = document.createElement("span");
        medName.className = "medicine-name";
        medName.textContent = rx.medicine_name;
        medCell.appendChild(medName);

        if (rx.generic_name) {
            const genName = document.createElement("span");
            genName.className = "generic-name";
            genName.textContent = "Generic: " + rx.generic_name;
            medCell.appendChild(genName);
        }
        row.appendChild(medCell);

        row.appendChild(createCell(rx.dosage));
        row.appendChild(createCell(rx.frequency));
        row.appendChild(createCell(rx.duration));
        row.appendChild(createCell(rx.instructions));

        resultsBody.appendChild(row);
    });

    resultCount.textContent = prescriptions.length + " medicine(s) found";
    resultsCard.classList.remove("hidden");
}

function createCell(value) {
    const cell = document.createElement("td");
    if (value === "Not specified") {
        const span = document.createElement("span");
        span.className = "not-specified";
        span.textContent = "—";
        cell.appendChild(span);
    } else {
        cell.textContent = value;
    }
    return cell;
}

// --------------------------------------------------------------------------
// UI Helpers
// --------------------------------------------------------------------------

function setStatus(state) {
    const labels = {
        ready: "Ready",
        recording: "Recording",
        processing: "Processing",
        error: "Error",
    };
    const statusLabels = {
        ready: "Ready to record",
        recording: "Recording... speak your prescription",
        processing: "Processing audio...",
        error: "Processing failed",
    };

    statusBadge.textContent = labels[state] || state;
    statusBadge.className = "badge " + state;
    statusText.textContent = statusLabels[state] || "";
    recDot.className = "rec-dot " + state;
}

function showMessage(type, text) {
    messageBox.className = "message visible " + type;
    messageBox.textContent = text;
}

function hideMessage() {
    messageBox.className = "message";
    messageBox.textContent = "";
}

function showSpinner(text) {
    spinnerText.textContent = text || "Processing...";
    spinnerOverlay.classList.add("visible");
}

function hideSpinner() {
    spinnerOverlay.classList.remove("visible");
}

function clearAll() {
    manualText.value = "";

    transcriptionCard.classList.add("hidden");
    correctedCard.classList.add("hidden");
    resultsCard.classList.add("hidden");

    resultsBody.innerHTML = "";
    transcriptionText.textContent = "";
    transcriptionMeta.textContent = "";
    correctedText.textContent = "";
    resultCount.textContent = "";

    emptyState.classList.remove("hidden");

    setStatus("ready");
    hideMessage();
}

// --------------------------------------------------------------------------
// Server Health Check
// --------------------------------------------------------------------------

async function checkServer() {
    const dot = serverStatusEl.querySelector(".server-dot");
    const label = serverStatusEl.querySelector(".server-label");

    try {
        const response = await fetch(API_BASE + "/api/health");
        if (response.ok) {
            const data = await response.json();
            dot.className = "server-dot online";
            label.textContent = "Server online";
        } else {
            dot.className = "server-dot offline";
            label.textContent = "Server error";
        }
    } catch (e) {
        dot.className = "server-dot offline";
        label.textContent = "Server offline";
        showMessage("info",
            "Backend server not detected. Start the Flask server: cd backend && python app.py");
    }
}

checkServer();
