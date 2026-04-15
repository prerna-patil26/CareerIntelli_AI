// 🎯 Interview Page JavaScript (FINAL FIXED)

let mediaRecorder;
let recordedChunks = [];
let isRecording = false;

let questions = [];
let currentIndex = 0;
let answers = [];
let selectedDomain = "";

let recognition;
let interviewStarted = false;

// ✅ ADDED (store interval globally)
let faceInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeCamera();
    loadDomains();

    // 🔥 FIXED FACE CHECK (store interval)
    faceInterval = setInterval(() => {
        if (!interviewStarted) return;

        const video = document.getElementById("interview-video");
        if (!video || video.videoWidth === 0) return;

        checkFacePosition();
    }, 3000);

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

// 📋 LOAD DOMAINS
function loadDomains() {
    fetch('/interview/domains')
        .then(res => {
            if (!res.ok) throw new Error("API failed");
            return res.json();
        })
        .then(data => {
            displayDomains(data.domains || []);
        })
        .catch(() => {
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

    interviewStarted = true;

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

    document.getElementById("nextBtn").innerText =
        (currentIndex === questions.length - 1) ? "Submit Interview" : "Next";
}

// 🔊 SPEAK
function speak(text) {
    const speech = new SpeechSynthesisUtterance(text);

    if (recognition) recognition.stop();
    window.speechSynthesis.speak(speech);
}

// 🎤 START MIC
function startSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Speech Recognition not supported. Use Chrome.");
        return;
    }

    if (recognition) recognition.stop();

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

        document.getElementById('answerText').innerText =
            finalTranscript + interimTranscript;
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

    canvas.getContext("2d").drawImage(video, 0, 0);
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
    .then(data => showWarning(data.warning))
    .catch(err => console.log("Face check error:", err));
}

// 🔥 WARNING
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

// 🚀 SUBMIT
function submitInterview() {

    console.log("🔥 SUBMIT STARTED");

    if (!answers.length || answers.every(a => a.trim() === "")) {
        alert("Please answer at least one question!");
        return;
    }

    // ✅ MOST IMPORTANT FIX (STOP FACE CHECK)
    if (faceInterval) {
        clearInterval(faceInterval);
        console.log("🛑 Face detection stopped");
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