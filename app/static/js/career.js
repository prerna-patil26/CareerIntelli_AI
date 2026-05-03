const state = {
    step: 1,
    mode: 'idle',
    skills: [],
    ratings: {},
    pointer: { x: window.innerWidth / 2, y: window.innerHeight / 2 }
};

/**
 * Neural Background Canvas Animation
 * Creates an interactive neural network visualization with cyan/purple gradient
 */
class NeuralBackground {
    constructor() {
        this.canvas = document.getElementById('neural-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.nodes = [];
        this.typingBoost = 0;
        this.pulse = 0;
        this.resize();
        this.buildNodes();
        window.addEventListener('resize', () => this.resize());
        window.addEventListener('mousemove', event => {
            state.pointer.x = event.clientX;
            state.pointer.y = event.clientY;
        });
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    buildNodes() {
        this.nodes = Array.from({ length: 85 }, () => ({
            x: Math.random() * this.canvas.width,
            y: Math.random() * this.canvas.height,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            r: 1.2 + Math.random() * 2.2,
            originalR: 1.2 + Math.random() * 2.2
        }));
    }

    reactToInput(target) {
        const rect = target.getBoundingClientRect();
        state.pointer.x = rect.left + rect.width / 2;
        state.pointer.y = rect.top + rect.height / 2;
        this.typingBoost = 1;
    }

    triggerPulse() {
        this.pulse = 1;
    }

    animate() {
        const isThinking = state.mode === 'thinking';
        const isResult = state.mode === 'result';
        const speed = isThinking ? 1.8 : isResult ? 0.7 : 1.1;
        const connectionDistance = isThinking ? 180 : isResult ? 110 : 130;
        const baseAlpha = isThinking ? 0.4 : isResult ? 0.25 : 0.22;

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Update node positions
        for (const node of this.nodes) {
            node.x += node.vx * speed;
            node.y += node.vy * speed;
            if (node.x < -10) node.x = this.canvas.width + 10;
            if (node.x > this.canvas.width + 10) node.x = -10;
            if (node.y < -10) node.y = this.canvas.height + 10;
            if (node.y > this.canvas.height + 10) node.y = -10;
        }

        // Draw connections with gradient
        for (let i = 0; i < this.nodes.length; i += 1) {
            for (let j = i + 1; j < this.nodes.length; j += 1) {
                const a = this.nodes[i];
                const b = this.nodes[j];
                const distance = Math.hypot(a.x - b.x, a.y - b.y);
                if (distance < connectionDistance) {
                    const alpha = (1 - distance / connectionDistance) * 
                        (baseAlpha + this.typingBoost * 0.35 + this.pulse * 0.3);
                    
                    // Gradient line with cyan to purple
                    const gradient = this.ctx.createLinearGradient(a.x, a.y, b.x, b.y);
                    gradient.addColorStop(0, `rgba(34, 211, 238, ${alpha * 0.7})`);
                    gradient.addColorStop(0.5, `rgba(168, 85, 247, ${alpha})`);
                    gradient.addColorStop(1, `rgba(34, 211, 238, ${alpha * 0.7})`);
                    
                    this.ctx.strokeStyle = gradient;
                    this.ctx.lineWidth = 1.2;
                    this.ctx.beginPath();
                    this.ctx.moveTo(a.x, a.y);
                    this.ctx.lineTo(b.x, b.y);
                    this.ctx.stroke();
                }
            }
        }

        // Draw pulse ring
        if (this.pulse > 0) {
            const radius = (1 - this.pulse) * Math.max(this.canvas.width, this.canvas.height) * 0.9;
            const gradient = this.ctx.createRadialGradient(
                state.pointer.x, state.pointer.y, Math.max(0, radius - 30),
                state.pointer.x, state.pointer.y, radius
            );
            gradient.addColorStop(0, `rgba(34, 211, 238, ${this.pulse * 0.5})`);
            gradient.addColorStop(1, `rgba(168, 85, 247, 0)`);
            
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(state.pointer.x, state.pointer.y, radius, 0, Math.PI * 2);
            this.ctx.fill();
            this.pulse = Math.max(0, this.pulse - 0.015);
        }

        // Draw nodes with glow
        for (const node of this.nodes) {
            const nearPointer = Math.hypot(node.x - state.pointer.x, node.y - state.pointer.y) < 140;
            const glowAlpha = nearPointer ? 0.9 : 0.35 + this.typingBoost * 0.25;
            const nodeRadius = nearPointer ? node.r + 1.5 : node.r;
            
            // Glow effect
            this.ctx.fillStyle = `rgba(34, 211, 238, ${glowAlpha * 0.3})`;
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, nodeRadius + 2, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Node gradient
            const nodeGradient = this.ctx.createRadialGradient(
                node.x - nodeRadius/2, node.y - nodeRadius/2, 0,
                node.x, node.y, nodeRadius
            );
            nodeGradient.addColorStop(0, `rgba(34, 211, 238, ${glowAlpha})`);
            nodeGradient.addColorStop(1, `rgba(168, 85, 247, ${glowAlpha * 0.6})`);
            
            this.ctx.fillStyle = nodeGradient;
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, nodeRadius, 0, Math.PI * 2);
            this.ctx.fill();
        }

        this.typingBoost *= 0.92;
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize neural background
const neuralBackground = new NeuralBackground();

// DOM Elements
const stepNodes = [...document.querySelectorAll('.wizard-step')];
const progressSteps = [...document.querySelectorAll('.progress-step')];
const skillInput = document.getElementById('skills-input');
const skillsChips = document.getElementById('skills-chips');
const ratingList = document.getElementById('rating-list');
const thinkingScreen = document.getElementById('thinking-screen');
const thinkingMessage = document.getElementById('thinking-message');
let thinkingMessageTimer = null;

/**
 * Utility Functions
 */
function formatSkill(value) {
    return value.replace(/\b\w/g, char => char.toUpperCase());
}

function parseSkills(value) {
    return [...new Set(
        value.split(',')
            .map(skill => skill.trim().toLowerCase())
            .filter(Boolean)
    )];
}

function showStep(stepNumber) {
    state.step = stepNumber;
    stepNodes.forEach(node => 
        node.classList.toggle('is-active', Number(node.dataset.step) === stepNumber)
    );
    progressSteps.forEach(step => 
        step.classList.toggle('is-active', Number(step.dataset.step) === stepNumber)
    );
    
    // Scroll to top smoothly
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderSkillChips() {
    skillsChips.innerHTML = '';
    state.skills.forEach((skill, index) => {
        const chip = document.createElement('span');
        chip.className = 'skill-chip';
        chip.textContent = formatSkill(skill);
        chip.style.animationDelay = `${index * 0.05}s`;
        skillsChips.appendChild(chip);
    });
}

function renderRatingRows() {
    ratingList.innerHTML = '';

    state.skills.forEach((skill, index) => {
        if (!state.ratings[skill]) state.ratings[skill] = 3;

        const row = document.createElement('div');
        row.className = 'rating-row';
        row.style.animationDelay = `${index * 0.05}s`;
        const safeId = skill.replace(/[^a-z0-9]/g, '');
        row.innerHTML = `
            <label for="rating-${safeId}">${formatSkill(skill)}</label>
            <input 
                id="rating-${safeId}" 
                type="range" 
                min="1" 
                max="5" 
                value="${state.ratings[skill]}" 
                data-skill="${skill}"
                aria-label="Confidence rating for ${formatSkill(skill)}"
            >
            <span class="rating-value" data-rating-output="${skill}">${state.ratings[skill]}/5</span>
        `;
        ratingList.appendChild(row);
    });

    ratingList.querySelectorAll('input[type="range"]').forEach(slider => {
        slider.addEventListener('input', () => {
            const { skill } = slider.dataset;
            state.ratings[skill] = Number(slider.value);
            const output = ratingList.querySelector(`[data-rating-output="${skill}"]`);
            if (output) output.textContent = `${slider.value}/5`;
        });
    });
}

async function fetchCareerPrediction(skills) {
    const payload = {
        skills,
        ratings: state.ratings
    };

    const response = await fetch('/api/career/predict-career', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Prediction failed');
    }

    return data;
}

async function typeText(target, text, speed = 16) {
    target.textContent = '';
    for (let index = 0; index < text.length; index += 1) {
        target.textContent += text[index];
        // Split typing for better performance
        if (index % 10 === 0) {
            await new Promise(resolve => setTimeout(resolve, speed));
        }
    }
}

function showThinkingPhase() {
    state.mode = 'thinking';
    showStep(4);
    // thinkingScreen.classList.add('is-active');
    thinkingScreen.classList.add('active');
    document.body.style.overflow = "hidden";

    thinkingScreen.setAttribute('aria-hidden', 'false');
    document.body.classList.add('analysis-loading');
    neuralBackground.triggerPulse();

    const messages = [
        'Scanning your skill profile...',
        'Comparing with industry benchmarks...',
        'Building your career roadmap...'
    ];

    let messageIndex = 0;
    thinkingMessage.textContent = messages[messageIndex];

    if (thinkingMessageTimer) {
        clearInterval(thinkingMessageTimer);
    }

    thinkingMessageTimer = setInterval(() => {
        messageIndex = (messageIndex + 1) % messages.length;
        thinkingMessage.textContent = messages[messageIndex];
    }, 850);
}

function hideThinkingPhase() {
    if (thinkingMessageTimer) {
        clearInterval(thinkingMessageTimer);
        thinkingMessageTimer = null;
    }
    thinkingScreen.classList.remove('active');
    document.body.style.overflow = "auto";
    // thinkingScreen.classList.remove('is-active');
    thinkingScreen.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('analysis-loading');
}

function renderResultList(targetId, lines) {
    const target = document.getElementById(targetId);
    target.innerHTML = '';
    lines.forEach((line, index) => {
        const item = document.createElement('div');
        item.className = 'result-item';
        item.textContent = line;
        item.style.animationDelay = `${index * 0.05}s`;
        target.appendChild(item);
    });
}

async function updateUI(data) {
    state.mode = 'result';
    document.getElementById('result-heading').textContent = `${data.career} Guidance Results`;
    document.getElementById('current-level').textContent = `Your Current Level: ${data.current_level || 'Developing'}`;
    document.getElementById('career-readiness').textContent = `You are ${Math.round(Number(data.confidence || 0))}% ready for ${data.career}`;

    const analysis = data.skills_analysis || {};
    const analysisLines = Object.entries(analysis).map(([skill, status]) => {
        const icon = status === 'Strong' ? '✓' : status === 'Basic' ? '◆' : '→';
        return `${icon} ${formatSkill(skill)} — ${status}`;
    });
    renderResultList('skills-analysis', analysisLines);

    document.getElementById('gap-intro').textContent = `To excel as a ${data.career}, focus on:`;
    renderResultList(
        'skill-gap',
        Array.isArray(data.missing_skills) && data.missing_skills.length
            ? data.missing_skills.map(skill => formatSkill(skill))
            : ['Deepen expertise through practical projects.']
    );

    const plan = document.getElementById('action-plan');
    plan.innerHTML = '';
    (data.action_plan || []).forEach((step, index) => {
        const item = document.createElement('li');
        item.textContent = step;
        item.style.animationDelay = `${index * 0.05}s`;
        plan.appendChild(item);
    });

    const alternateCareers = (data.top_3 || []).filter(career => career !== data.career).slice(0, 2);
    document.querySelectorAll('.switch-career').forEach((button, index) => {
        const nextCareer = alternateCareers[index];
        if (nextCareer) {
            button.disabled = false;
            button.dataset.career = nextCareer;
            button.textContent = `→ Explore ${nextCareer}`;
        } else {
            button.disabled = true;
            button.textContent = 'No Alternate Match';
        }
    });

    // showStep(5);
    await typeText(document.getElementById('ai-insight'), data.insight || 'Career analysis complete', 14);
}

window.updateUI = updateUI;

/**
 * Event Listeners
 */
skillInput.addEventListener('input', () => {
    state.skills = parseSkills(skillInput.value);
    renderSkillChips();
    neuralBackground.reactToInput(skillInput);
    state.mode = 'typing';
});

document.getElementById('go-step-2').addEventListener('click', () => {
    state.skills = parseSkills(skillInput.value);
    if (!state.skills.length) {
        skillInput.focus();
        return;
    }

    renderSkillChips();
    renderRatingRows();
    state.mode = 'idle';
    showStep(2);
});

document.getElementById('back-step-1').addEventListener('click', () => showStep(1));

// document.getElementById('analyze-button').addEventListener('click', async () => {
//     showThinkingPhase();

//     try {
//         const data = await fetchCareerPrediction(state.skills);
//         await updateUI(data);
//     } catch (error) {
//         alert('Prediction failed. Please try again.');
//         console.error('Error:', error);
//     } finally {
//         window.setTimeout(() => {
//             hideThinkingPhase();
//         }, 250);
//         if (state.mode === 'thinking') {
//             state.mode = 'idle';
//         }
//     }
// });


document.getElementById('analyze-button').addEventListener('click', async () => {
    showThinkingPhase();

    try {
        // ⏳ minimum loader time (important)
        const [data] = await Promise.all([
            fetchCareerPrediction(state.skills),
            new Promise(resolve => setTimeout(resolve, 1500))
        ]);

        hideThinkingPhase();   // ✅ पहले loader हटाओ
        showStep(5);           // ✅ फिर result दिखाओ
        await updateUI(data);  // ✅ फिर data render

    } catch (error) {
        hideThinkingPhase();
        alert('Prediction failed. Please try again.');
        console.error(error);
    }
});

document.querySelectorAll('.switch-career').forEach(button => {
    button.addEventListener('click', async () => {
        try {
            const data = await fetchCareerPrediction(state.skills);
            await updateUI(data);
        } catch (error) {
            alert('Prediction failed.');
            console.error('Error:', error);
        }
    });
});

document.getElementById('restart-button').addEventListener('click', () => {
    state.skills = [];
    state.ratings = {};
    state.mode = 'idle';
    skillInput.value = '';
    skillsChips.innerHTML = '';
    document.getElementById('ai-insight').textContent = '';
    document.querySelectorAll('.switch-career').forEach(button => {
        button.disabled = true;
        button.dataset.career = '';
        button.textContent = 'No Alternate Match';
    });
    showStep(1);
    skillInput.focus();
});

// Initialize
showStep(1);
skillInput.focus();

