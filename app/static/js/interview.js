// 🎯 Interview Page JavaScript (FINAL FIXED)

let mediaRecorder;
let recordedChunks = [];
let isRecording = false;

let questions = [];
let currentIndex = 0;
let answers = [];
let selectedDomain = "";

let recognition;

document.addEventListener('DOMContentLoaded', function() {
    initializeCamera();
    loadDomains();

    // 🔥 FIXED FACE CHECK (faster + safe)
    setInterval(() => {
        const video = document.getElementById("interview-video");

        if (!video || video.videoWidth === 0) return;

        checkFacePosition();
    }, 1000);

    if (document.getElementById("finalScore")) {
        loadResultPage();
    }
});

// 🎥 CAMERA
async function initializeCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: true,
            audio: false
        });

        document.getElementById('interview-video').srcObject = stream;

        mediaRecorder = new MediaRecorder(stream);

    } catch (error) {
        alert('Please allow camera access');
    }
}

// 📋 LOAD DOMAINS (🔥 FIXED)
function loadDomains() {
    fetch('/interview/domains')
        .then(res => {
            if (!res.ok) throw new Error("API failed");
            return res.json();
        })
        .then(data => {
            console.log("✅ Domains:", data);
            displayDomains(data.domains || []);
        })
        .catch(err => {
            console.error("❌ Domain load error:", err);
            alert("Domain load failed!");
        });
}

function displayDomains(domains) {
    const ul = document.getElementById("domainList");
    ul.innerHTML = "";

    domains.forEach(domain => {
        let li = document.createElement("li");
        li.innerText = domain;

        li.onclick = (event) => {
            selectedDomain = domain;
            document.getElementById("searchBox").value = domain;

            document.querySelectorAll("li").forEach(li => li.classList.remove("selected"));
            event.target.classList.add("selected");
        };

        ul.appendChild(li);
    });
}

// 🚀 START INTERVIEW
function startInterview() {
    if (!selectedDomain) {
        alert("Please select a domain");
        return;
    }

    fetch('/interview/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ career: selectedDomain })
    })
    .then(res => res.json())
    .then(data => {
        questions = data.questions;
        currentIndex = 0;

        document.getElementById("interviewSection").style.display = "block";

        showQuestion();
    });
}

// 🧠 SHOW QUESTION
function showQuestion() {
    const question = questions[currentIndex];

    document.getElementById("questionText").innerText = question;

    speak(question);

    if (currentIndex === questions.length - 1) {
        document.getElementById("nextBtn").innerText = "Submit Interview";
    } else {
        document.getElementById("nextBtn").innerText = "Next";
    }
}

// 🔊 SPEAK
function speak(text) {
    const speech = new SpeechSynthesisUtterance(text);

    if (recognition) {
        recognition.stop();
    }

    window.speechSynthesis.speak(speech);
}

// 🎤 START MIC
function startSpeechRecognition() {

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Speech Recognition not supported. Use Google Chrome.");
        return;
    }

    if (recognition) {
        recognition.stop();
    }

    recognition = new SpeechRecognition();

    recognition.lang = "en-US";
    recognition.continuous = true;
    recognition.interimResults = true;

    let finalTranscript = "";

    recognition.onresult = function(event) {

        let interimTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {

            let text = event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                finalTranscript += text + " ";
            } else {
                interimTranscript += text;
            }
        }

        let fullText = finalTranscript + interimTranscript;

        document.getElementById('answerText').innerText = fullText;
    };

    recognition.onerror = function(e) {
        console.log("Speech Error:", e.error);
    };

    recognition.start();
}

// ⛔ STOP MIC
function stopSpeechRecognition() {
    if (recognition) {
        recognition.onend = null;
        recognition.stop();
    }
}

// ➡️ NEXT QUESTION
function nextQuestion() {
    let answer = document.getElementById("answerText").innerText;

    answers.push(answer);
    document.getElementById("answerText").innerText = "";

    currentIndex++;

    if (currentIndex >= questions.length) {
        submitInterview();
        return;
    }

    showQuestion();
}

// 📸 CAPTURE IMAGE
function captureFrame() {
    const video = document.getElementById("interview-video");

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    return canvas.toDataURL("image/jpeg");
}

// 🔥 FACE CHECK
function checkFacePosition() {

    const image = captureFrame();

    fetch('/interview/check-face', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: image })
    })
    .then(res => res.json())
    .then(data => {
        showWarning(data.warning);
    });
}

// 🔥 WARNING FUNCTION (ADDED FIX)
function showWarning(message) {
    const box = document.getElementById("warningBox");

    if (!box) return;

    if (message) {
        box.style.display = "block";
        box.innerText = message;
        box.style.color = "red";
    } else {
        box.style.display = "none";
    }
}

// 🚀 SUBMIT INTERVIEW
function submitInterview() {

    if (!answers || answers.length === 0 || answers.every(a => a.trim() === "")) {
        alert("Please answer at least one question!");
        return;
    }

    document.getElementById("loader").style.display = "flex";

    fetch('/interview/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: answers })
    })
    .then(res => res.json())
    .then(data => {

        localStorage.setItem("total_score", data.total_score);
        localStorage.setItem("technical_score", data.technical_score);
        localStorage.setItem("communication_score", data.communication_score);
        localStorage.setItem("confidence_score", data.confidence_score);
        localStorage.setItem("feedback", data.feedback);
        localStorage.setItem("suggestions", JSON.stringify(data.suggestions));

        document.getElementById("loader").style.display = "none";

        window.location.href = "/interview/result";
    })
    .catch(() => {
        document.getElementById("loader").style.display = "none";
        alert("Something went wrong!");
    });
}

// 📊 RESULT PAGE
function loadResultPage() {
    let total = localStorage.getItem("total_score");
    let tech = localStorage.getItem("technical_score");
    let comm = localStorage.getItem("communication_score");
    let conf = localStorage.getItem("confidence_score");
    let feedback = localStorage.getItem("feedback");
    let suggestions = JSON.parse(localStorage.getItem("suggestions") || "[]");

    document.getElementById("finalScore").innerText = "Score: " + total;
    document.getElementById("feedbackText").innerText = feedback;

    document.getElementById("tech").innerText = tech;
    document.getElementById("comm").innerText = comm;
    document.getElementById("conf").innerText = conf;

    let ul = document.getElementById("suggestionsList");
    ul.innerHTML = "";

    suggestions.forEach(s => {
        let li = document.createElement("li");
        li.innerText = s;
        ul.appendChild(li);
    });
}