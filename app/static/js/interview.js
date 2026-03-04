/* Interview Page JavaScript */

let mediaRecorder;
let recordedChunks = [];
let isRecording = false;
let recordingTime = 0;
let timerInterval;

document.addEventListener('DOMContentLoaded', function() {
    initializeCamera();
    loadQuestion();
});

// Initialize camera access
async function initializeCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: true, 
            audio: true 
        });
        
        const videoElement = document.getElementById('interview-video');
        videoElement.srcObject = stream;
        
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (event) => {
            recordedChunks.push(event.data);
        };
        
        mediaRecorder.onstop = () => {
            const blob = new Blob(recordedChunks, { type: 'video/webm' });
            saveRecording(blob);
            recordedChunks = [];
        };
        
        console.log('Camera initialized successfully');
    } catch (error) {
        console.error('Error accessing camera:', error);
        alert('Please allow camera access to use the interview feature');
    }
}

// Start recording
function startRecording() {
    if (!isRecording && mediaRecorder) {
        mediaRecorder.start();
        isRecording = true;
        recordingTime = 0;
        
        document.getElementById('start-recording').classList.add('hidden');
        document.getElementById('stop-recording').classList.remove('hidden');
        
        startTimer();
        console.log('Recording started');
    }
}

// Stop recording
function stopRecording() {
    if (isRecording && mediaRecorder) {
        mediaRecorder.stop();
        isRecording = false;
        
        document.getElementById('start-recording').classList.remove('hidden');
        document.getElementById('stop-recording').classList.add('hidden');
        
        clearInterval(timerInterval);
        console.log('Recording stopped');
    }
}

// Timer management
function startTimer() {
    timerInterval = setInterval(() => {
        recordingTime++;
        updateTimerDisplay();
    }, 1000);
}

function updateTimerDisplay() {
    const minutes = Math.floor(recordingTime / 60);
    const seconds = recordingTime % 60;
    const display = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    document.getElementById('timer').textContent = display;
}

// Load question
function loadQuestion() {
    // TODO: Fetch question from API and display
    const questionText = 'Tell me about your experience with software development.';
    document.getElementById('question-text').textContent = questionText;
}

// Save recording
function saveRecording(blob) {
    const formData = new FormData();
    formData.append('audio', blob);
    
    // TODO: Send to server for processing
    console.log('Recording saved');
}

// Utility functions
function nextQuestion() {
    loadQuestion();
    recordedChunks = [];
    recordingTime = 0;
}

function submitAnswer() {
    if (isRecording) {
        stopRecording();
    }
    
    // TODO: Submit answer and move to next question
    nextQuestion();
}
