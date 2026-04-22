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

let faceInterval = null;
let interviewLaunchTimer = null;

// TIMER
let timeLeft = 60;
let timerInterval;
let totalQuestions = 10;

// Circle constants
const radius = 26;
const circumference = 2 * Math.PI * radius;

document.addEventListener('DOMContentLoaded', function() {
    initializeCamera();
    loadDomains();
    wireInterviewLaunch();

    const circle = document.querySelector(".progress-ring__circle");
    if (circle) {
        circle.style.strokeDasharray = circumference;
        circle.style.strokeDashoffset = 0;
    }

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

// CAMERA
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

// INTRO → MAIN UI
function wireInterviewLaunch() {
    const startButton = document.getElementById('startInterviewBtn');

    if (!startButton) return;

    startButton.addEventListener('click', () => {
        const popup = document.getElementById('startPopup');

        if (popup) {
            popup.classList.add('is-visible');
            popup.setAttribute('aria-hidden', 'false');
        }

        if (interviewLaunchTimer) {
            clearTimeout(interviewLaunchTimer);
        }

        interviewLaunchTimer = setTimeout(() => {
            if (popup) {
                popup.classList.remove('is-visible');
                popup.setAttribute('aria-hidden', 'true');
            }

            document.body.classList.add('interview-ready');

            const interviewApp = document.getElementById('interviewApp');
            if (interviewApp) {
                interviewApp.hidden = false;
            }
        }, 2000);
    });
}

// LOAD DOMAINS
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

// START INTERVIEW
function startInterview() {
    if (!selectedDomain) {
        alert("Please select a domain");
        return;
    }

    const loader = document.getElementById("loader");
    if (loader) {
        loader.classList.add("is-visible");
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
        totalQuestions = questions.length;

        if (loader) {
            loader.classList.remove("is-visible");
        }

        // ✅ HIDE DOMAIN SELECTION
        const domainSection = document.getElementById("domainSelectionSection");
        if (domainSection) {
            domainSection.style.display = "none";
        }

        // ✅ SHOW SELECTED DOMAIN TITLE
        const domainTitle = document.getElementById("selectedDomainTitle");
        if (domainTitle) {
            domainTitle.innerText = `${selectedDomain} Interview`;
            domainTitle.style.display = "block";
        }

        document.getElementById("interviewSection").style.display = "block";

        updateQuestionCounter();
        startTimer();
        showQuestion();
    });
}

// SHOW QUESTION
function showQuestion() {
    const question = questions[currentIndex];
    document.getElementById("questionText").innerText = question;

    speak(question);

    document.getElementById("nextBtn").innerText =
        (currentIndex === questions.length - 1) ? "Submit Interview" : "Next";
}

// SPEAK
function speak(text) {
    const speech = new SpeechSynthesisUtterance(text);

    if (recognition) recognition.stop();
    window.speechSynthesis.speak(speech);
}

// START MIC
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

        let fullAnswer = finalTranscript + interimTranscript;

        document.getElementById('answerText').innerText = fullAnswer;

        let wordCount = fullAnswer.trim().split(/\s+/).filter(word => word).length;
        let confidence = Math.min(wordCount * 2, 100);

        document.getElementById("confidenceFill").style.width = confidence + "%";
    };

    recognition.start();
}

// STOP MIC
function stopSpeechRecognition() {
    if (recognition) {
        recognition.onend = null;
        recognition.stop();
    }
}

// TIMER
function startTimer() {
    clearInterval(timerInterval);

    timeLeft = 60;

    const timerElement = document.getElementById("timer");
    const circle = document.querySelector(".progress-ring__circle");

    timerElement.innerText = `${timeLeft}s`;
    timerElement.style.color = "#22D3EE";

    if (circle) {
        circle.style.stroke = "#22D3EE";
        circle.style.strokeDashoffset = 0;
    }

    timerInterval = setInterval(() => {
        timeLeft--;

        timerElement.innerText = `${timeLeft}s`;

        if (circle) {
            const progress = timeLeft / 60;
            const offset = circumference - (progress * circumference);
            circle.style.strokeDashoffset = offset;
        }

        if (timeLeft <= 10) {
            timerElement.style.color = "red";

            if (circle) {
                circle.style.stroke = "red";
            }
        }

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            nextQuestion();
        }

    }, 1000);
}

// QUESTION COUNTER
function updateQuestionCounter() {
    document.getElementById("questionCounter").innerText =
        `Question ${currentIndex + 1} / ${totalQuestions}`;
}

// NEXT QUESTION
function nextQuestion() {
    clearInterval(timerInterval);

    let answer = document.getElementById("answerText").innerText;

    answers.push(answer);
    document.getElementById("answerText").innerText = "";

    document.getElementById("confidenceFill").style.width = "0%";

    currentIndex++;

    if (currentIndex >= questions.length) {
        submitInterview();
        return;
    }

    updateQuestionCounter();
    startTimer();
    showQuestion();
}

// CAPTURE FRAME
function captureFrame() {
    const video = document.getElementById("interview-video");

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    canvas.getContext("2d").drawImage(video, 0, 0);
    return canvas.toDataURL("image/jpeg");
}

// FACE CHECK
function checkFacePosition() {
    const image = captureFrame();

    fetch('/interview/check-face', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: image })
    })
    .then(res => res.json())
    .then(data => {
        showWarning(data.warning || "");
    })
    .catch(err => console.log("Face check error:", err));
}

// WARNING
let warningTimeout = null;
let lastMessage = "";

function showWarning(message) {
    const box = document.getElementById("warningBox");
    if (!box) return;

    if (message === lastMessage) return;

    lastMessage = message;

    if (message) {
        box.innerText = message;
        box.style.display = "block";

        clearTimeout(warningTimeout);

        warningTimeout = setTimeout(() => {
            box.style.display = "none";
            lastMessage = "";
        }, 2000);
    } else {
        box.style.display = "none";
        lastMessage = "";
    }
}

// SUBMIT
function submitInterview() {
    if (!answers.length || answers.every(a => a.trim() === "")) {
        alert("Please answer at least one question!");
        return;
    }

    if (faceInterval) {
        clearInterval(faceInterval);
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