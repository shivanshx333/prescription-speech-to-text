// Records voice via the browser, sends text to the backend for parsing.

const API_BASE = window.location.origin;

// --------------------------------------------------------------------------
// State
// --------------------------------------------------------------------------
let isRecording = false;
let finalTranscript = "";

// --------------------------------------------------------------------------
// Web Speech API setup
// --------------------------------------------------------------------------
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-IN";

    recognition.onresult = function (event) {
        let interim = "";
        finalTranscript = "";
        for (let i = 0; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript + " ";
            } else {
                interim += event.results[i][0].transcript;
            }
        }
        liveText.textContent = finalTranscript + interim;
    };

    recognition.onend = function () {
        // Browser stops recognition after silence — restart if still recording
        if (isRecording) {
            try { recognition.start(); } catch (e) { /* already started */ }
        }
    };

    recognition.onerror = function (event) {
        console.error("Speech error:", event.error);
        if (event.error === "not-allowed" || event.error === "service-not-allowed") {
            showMessage("error", "Microphone access denied. Please allow microphone access in browser settings.");
            stopRecording();
        } else if (event.error === "no-speech") {
            // Ignored — will auto-restart
        } else {
            showMessage("error", "Speech recognition error: " + event.error);
        }
    };
}

// --------------------------------------------------------------------------
// DOM Elements
// --------------------------------------------------------------------------
const recordBtn         = document.getElementById("recordBtn");
const recordBtnText     = document.getElementById("recordBtnText");
const statusBadge       = document.getElementById("statusBadge");
const recIndicator      = document.getElementById("recIndicator");
const recDot            = recIndicator.querySelector(".rec-dot");
const statusText        = document.getElementById("statusText");
const liveTranscriptEl  = document.getElementById("liveTranscript");
const liveText          = document.getElementById("liveText");
const manualText        = document.getElementById("manualText");
const processTextBtn    = document.getElementById("processTextBtn");
const messageBox        = document.getElementById("messageBox");
const transcriptionCard = document.getElementById("transcriptionCard");
const transcriptionText = document.getElementById("transcriptionText");
const transcriptionMeta = document.getElementById("transcriptionMeta");
const correctedCard     = document.getElementById("correctedCard");
const correctedText     = document.getElementById("correctedText");
const resultsCard       = document.getElementById("resultsCard");
const resultsBody       = document.getElementById("resultsBody");
const resultCount       = document.getElementById("resultCount");
const emptyState        = document.getElementById("emptyState");
const spinnerOverlay    = document.getElementById("spinnerOverlay");
const spinnerText       = document.getElementById("spinnerText");
const serverStatusEl    = document.getElementById("serverStatus");

// --------------------------------------------------------------------------
// Recording (Web Speech API)
// --------------------------------------------------------------------------

function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

function startRecording() {
    if (!recognition) {
        showMessage("error",
            "Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.");
        return;
    }

    finalTranscript = "";
    liveText.textContent = "";
    liveTranscriptEl.classList.add("active");
    hideMessage();

    try {
        recognition.start();
    } catch (e) {
        // Already started
    }

    isRecording = true;
    recordBtnText.textContent = "Stop Recording";
    recordBtn.classList.add("recording");
    setStatus("recording");
}

function stopRecording() {
    isRecording = false;

    if (recognition) {
        try { recognition.stop(); } catch (e) { /* not started */ }
    }

    recordBtnText.textContent = "Start Recording";
    recordBtn.classList.remove("recording");

    const text = (liveText.textContent || "").trim();
    if (text && text.length > 2) {
        setStatus("processing");
        processVoiceText(text);
    } else {
        liveTranscriptEl.classList.remove("active");
        showMessage("error", "No speech detected. Please speak clearly and try again.");
        setStatus("ready");
    }
}

// --------------------------------------------------------------------------
// API Communication
// --------------------------------------------------------------------------

async function processVoiceText(text) {
    showSpinner("Parsing prescription...");
    try {
        const response = await fetch(API_BASE + "/api/process-text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Server error.");

        displayResults(data);
        setStatus("ready");
        showMessage("success",
            "Extracted " + data.prescription.num_medicines + " medicine(s) from prescription.");
    } catch (error) {
        setStatus("error");
        showMessage("error", error.message.includes("Failed to fetch")
            ? "Cannot connect to server."
            : error.message);
    } finally {
        hideSpinner();
        liveTranscriptEl.classList.remove("active");
    }
}

async function processManualText() {
    const text = manualText.value.trim();
    if (!text) {
        showMessage("error", "Please enter prescription text first.");
        return;
    }
    showSpinner("Parsing prescription...");
    try {
        const response = await fetch(API_BASE + "/api/process-text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Server error.");

        displayResults(data);
        showMessage("success",
            "Extracted " + data.prescription.num_medicines + " medicine(s) from prescription.");
    } catch (error) {
        showMessage("error", error.message.includes("Failed to fetch")
            ? "Cannot connect to server."
            : error.message);
    } finally {
        hideSpinner();
    }
}

// --------------------------------------------------------------------------
// Display Results
// --------------------------------------------------------------------------

function displayResults(data) {
    emptyState.classList.add("hidden");

    // Transcription
    transcriptionText.textContent = data.transcription.text;
    let meta = "";
    if (data.transcription.processing_time > 0) {
        meta = "Processing time: " + data.transcription.processing_time + "s";
    }
    transcriptionMeta.textContent = meta;
    transcriptionCard.classList.remove("hidden");

    // Corrected text
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
    var prescriptions = data.prescription.prescriptions;

    prescriptions.forEach(function (rx, index) {
        var row = document.createElement("tr");

        var numCell = document.createElement("td");
        numCell.textContent = index + 1;
        row.appendChild(numCell);

        var medCell = document.createElement("td");
        var confidence = rx.confidence || 0;

        if (confidence > 0 && confidence < 1) {
            var dot = document.createElement("span");
            dot.className = "confidence-indicator " +
                (confidence >= 0.9 ? "confidence-high" :
                 confidence >= 0.8 ? "confidence-medium" : "confidence-low");
            dot.title = "Match confidence: " + Math.round(confidence * 100) + "%";
            medCell.appendChild(dot);
        }

        var medName = document.createElement("span");
        medName.className = "medicine-name";
        medName.textContent = rx.medicine_name;
        medCell.appendChild(medName);

        if (rx.generic_name) {
            var genName = document.createElement("span");
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
    var cell = document.createElement("td");
    if (value === "Not specified") {
        var span = document.createElement("span");
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
    var labels = { ready: "Ready", recording: "Recording", processing: "Processing", error: "Error" };
    var hints = {
        ready: "Ready to record",
        recording: "Listening... speak your prescription",
        processing: "Parsing prescription...",
        error: "Processing failed",
    };
    statusBadge.textContent = labels[state] || state;
    statusBadge.className = "badge " + state;
    statusText.textContent = hints[state] || "";
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
    liveTranscriptEl.classList.remove("active");
    resultsBody.innerHTML = "";
    transcriptionText.textContent = "";
    transcriptionMeta.textContent = "";
    correctedText.textContent = "";
    resultCount.textContent = "";
    liveText.textContent = "";
    emptyState.classList.remove("hidden");
    setStatus("ready");
    hideMessage();
}

// --------------------------------------------------------------------------
// Server Health Check
// --------------------------------------------------------------------------

async function checkServer() {
    var dot = serverStatusEl.querySelector(".server-dot");
    var label = serverStatusEl.querySelector(".server-label");
    try {
        var response = await fetch(API_BASE + "/api/health");
        if (response.ok) {
            dot.className = "server-dot online";
            label.textContent = "Server online";
        } else {
            dot.className = "server-dot offline";
            label.textContent = "Server error";
        }
    } catch (e) {
        dot.className = "server-dot offline";
        label.textContent = "Server offline";
    }
}

// Speech API support indicator
if (!SpeechRecognition) {
    document.getElementById("recIndicator").innerHTML =
        '<span class="rec-dot error"></span><span>Browser speech not supported — use text input or switch to Chrome/Edge</span>';
}

checkServer();
