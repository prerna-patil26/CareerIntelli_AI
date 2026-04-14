// 🔥 LOAD DATA
let total = parseFloat(localStorage.getItem("total_score")) || 0;
let tech = parseFloat(localStorage.getItem("technical_score")) || 0;
let comm = parseFloat(localStorage.getItem("communication_score")) || 0;
let conf = parseFloat(localStorage.getItem("confidence_score")) || 0;

let feedback = localStorage.getItem("feedback") || "";
let suggestions = JSON.parse(localStorage.getItem("suggestions")) || [];

// 🎯 SCORE TEXT ANIMATION
let scoreEl = document.getElementById("scoreText");
let current = 0;

let scoreInterval = setInterval(() => {
    if (current >= total) {
        clearInterval(scoreInterval);
    } else {
        current++;
        scoreEl.innerText = current;
    }
}, 20);

// 🌀 SCORE RING ANIMATION
setTimeout(() => {
    document.querySelector(".score-ring").style.background =
        `conic-gradient(#22D3EE ${total}%, #1e293b ${total}%)`;
}, 300);

// 🧠 SMART LABEL
let label = "";
if (total > 80) label = "🔥 Excellent";
else if (total > 60) label = "👍 Good";
else label = "⚠️ Needs Improvement";

document.getElementById("performanceLabel").innerText = label;


// 📊 PERFORMANCE BARS + %
function setBar(id, percentId, value) {
    document.getElementById(id).style.width = value + "%";
    document.getElementById(percentId).innerText = value + "%";
}

setBar("techBar", "techPercent", tech);
setBar("commBar", "commPercent", comm);
setBar("confBar", "confPercent", conf);


// ✨ TYPING EFFECT
function typeEffect(element, text, speed = 20) {
    element.innerHTML = "";
    let i = 0;

    function typing() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(typing, speed);
        }
    }

    typing();
}


// 💬 SPLIT FEEDBACK + CLEAN LABELS (🔥 FIX)
let parts = feedback.split("\n");

// 🔥 REMOVE duplicate labels
let techText = (parts[0] || "").replace(/technical:/i, "").trim();
let commText = (parts[1] || "").replace(/communication:/i, "").trim();
let confText = (parts[2] || "").replace(/confidence:/i, "").trim();

// ✨ APPLY TYPING EFFECT
typeEffect(document.getElementById("techFeedback"), techText);

setTimeout(() => {
    typeEffect(document.getElementById("commFeedback"), commText);
}, 500);

setTimeout(() => {
    typeEffect(document.getElementById("confFeedback"), confText);
}, 1000);


// 💡 SUGGESTIONS ANIMATION
let ul = document.getElementById("suggestionsList");

suggestions.forEach((s, i) => {
    setTimeout(() => {
        let div = document.createElement("div");
        div.className = "suggestion-pill";
        div.innerText = "✔ " + s;

        ul.appendChild(div);
    }, i * 200);
});