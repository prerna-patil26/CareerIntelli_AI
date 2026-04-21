/* ==================== AI CAREER ROADMAP - VIDEO EDITION ==================== */

let appState = {
    allRoles: [],
    allSkills: [],
    selectedRole: '',
    selectedSkills: [],
    completedSkills: new Set(),
    roadmapData: null,
    currentPage: 1,
    pageHistory: [],
    customPlans: [],
    editingPlanId: null
};

// ============ INITIALIZATION ============
document.addEventListener('DOMContentLoaded', async () => {
    console.log('=== Initializing AI Career Roadmap ===');
    
    ensureVideoPlayback();
    await loadRolesAndSkills();
    setupEventListeners();
    initializePageTransitions();
    
    console.log('✓ App initialized');
});

function ensureVideoPlayback() {
    ['video-background', 'chatbot-video'].forEach((id) => {
        const video = document.getElementById(id);
        if (video && typeof video.play === 'function') {
            video.setAttribute('playsinline', '');
            video.setAttribute('webkit-playsinline', '');
            video.playsInline = true;
            const attempt = video.play();
            if (attempt && typeof attempt.catch === 'function') {
                attempt.catch(() => {
                    video.addEventListener('canplay', () => video.play().catch(() => {}), { once: true });
                });
            }
        }
    });
}

// ============ DATA LOADING ============
async function loadRolesAndSkills() {
    try {
        const rolesEl = document.getElementById('roles-data');
        const skillsEl = document.getElementById('skills-data');
        
        if (rolesEl && skillsEl) {
            appState.allRoles = JSON.parse(rolesEl.textContent) || [];
            appState.allSkills = JSON.parse(skillsEl.textContent) || [];
            console.log('✓ Loaded data from template');
        }
    } catch (e) {
        console.warn('Template data missing, using fallback');
        appState.allRoles = ['Software Engineer', 'Data Scientist', 'DevOps Engineer', 'Frontend Developer', 'Backend Developer', 'Product Manager', 'UX/UI Designer'];
        appState.allSkills = ['JavaScript', 'Python', 'React', 'Django', 'SQL', 'Docker', 'AWS', 'Git', 'REST API', 'MongoDB', 'Node.js', 'TypeScript', 'GraphQL', 'Kubernetes'];
    }
    
    renderRoleDropdown();
    renderSkillsDropdown();
}

// ============ DROPDOWNS ============
function renderRoleDropdown() {
    const roleList = document.getElementById('role-list');
    roleList.innerHTML = '';
    
    appState.allRoles.forEach(role => {
        const li = document.createElement('li');
        li.textContent = role;
        li.className = appState.selectedRole === role ? 'selected' : '';
        li.addEventListener('click', () => {
            appState.selectedRole = role;
            document.getElementById('role-btn').textContent = role;
            document.getElementById('role-list').classList.remove('open');
            renderRoleDropdown();
        });
        roleList.appendChild(li);
    });
}

function renderSkillsDropdown() {
    const skillsList = document.getElementById('skills-list');
    skillsList.innerHTML = '';
    
    appState.allSkills.forEach(skill => {
        const li = document.createElement('li');
        li.textContent = skill;
        li.className = appState.selectedSkills.includes(skill) ? 'selected' : '';
        li.addEventListener('click', () => {
            if (appState.selectedSkills.includes(skill)) {
                appState.selectedSkills = appState.selectedSkills.filter(s => s !== skill);
            } else {
                appState.selectedSkills.push(skill);
            }
            renderSkillTags();
            renderSkillsDropdown();
        });
        skillsList.appendChild(li);
    });
}

function renderSkillTags() {
    const container = document.getElementById('skill-tags-container');
    container.innerHTML = '';
    
    appState.selectedSkills.forEach(skill => {
        const tag = document.createElement('div');
        tag.className = 'skill-tag';
        tag.innerHTML = `${skill} <button type="button">×</button>`;
        tag.querySelector('button').addEventListener('click', (e) => {
            e.preventDefault();
            appState.selectedSkills = appState.selectedSkills.filter(s => s !== skill);
            renderSkillTags();
            renderSkillsDropdown();
        });
        container.appendChild(tag);
    });
}

// ============ EVENT LISTENERS ============
function setupEventListeners() {
    // Dropdowns
    document.getElementById('role-btn').addEventListener('click', (e) => {
        e.preventDefault();
        const list = document.getElementById('role-list');
        list.classList.toggle('open');
    });
    
    document.getElementById('skills-btn').addEventListener('click', (e) => {
        e.preventDefault();
        const list = document.getElementById('skills-list');
        list.classList.toggle('open');
    });
    
    // Form submission
    document.getElementById('roadmap-form').addEventListener('submit', onFormSubmit);

    const timelineForm = document.getElementById('timeline-form');
    if (timelineForm) {
        timelineForm.addEventListener('submit', onTimelineSubmit);
    }

    const globalProgressBtn = document.getElementById('global-progress-btn');
    if (globalProgressBtn) {
        globalProgressBtn.addEventListener('click', () => switchToPage(3));
    }
    
    // Close dropdowns on outside click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#role-btn')) {
            document.getElementById('role-list').classList.remove('open');
        }
        if (!e.target.closest('#skills-btn')) {
            document.getElementById('skills-list').classList.remove('open');
        }
    });
    
    document.addEventListener('click', (event) => {
        const rippleTarget = event.target.closest('.top-right-button, .btn-generate, .btn-small, .timeline-add-btn, .timeline-action-btn, .btn-action');
        if (rippleTarget) {
            createRipple(rippleTarget, event);
        }
    });
}

// ============ FORM SUBMISSION ============
async function onFormSubmit(e) {
    e.preventDefault();
    
    // Validation
    if (!appState.selectedRole) {
        showError('role-error', 'Please select a role');
        return;
    }
    if (appState.selectedSkills.length === 0) {
        showError('skills-error', 'Please select at least one skill');
        return;
    }
    
    clearErrors();
    
    try {
        const params = new URLSearchParams({
            role: appState.selectedRole,
            skills: appState.selectedSkills.join(',')
        });
        
        const response = await fetch(`/api/roadmap?${params.toString()}`);
        const data = await response.json();
        
        appState.roadmapData = data;
        appState.completedSkills.clear();
        
        renderRoadmap(data);
        switchToPage(2);
    } catch (error) {
        console.error('Error generating roadmap:', error);
        showError('role-error', 'Failed to generate roadmap');
    }
}

function showError(elementId, message) {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = message;
        el.style.display = 'block';
    }
}

function clearErrors() {
    document.getElementById('role-error').style.display = 'none';
    document.getElementById('skills-error').style.display = 'none';
}

// ============ NEURAL ROADMAP RENDERING ============
function renderRoadmap(data) {
    const container = document.getElementById('roadmap-container');
    container.innerHTML = '';

    const titleEl = document.getElementById('roadmap-title');
    const subtitleEl = document.getElementById('roadmap-subtitle');
    if (titleEl) {
        titleEl.textContent = `Your ${data?.role || appState.selectedRole} Career Roadmap 🚀`;
    }
    if (subtitleEl) {
        subtitleEl.textContent = 'A complete role-based roadmap with your completed skills highlighted and the missing skills marked as next steps.';
    }

    const roadmap = buildInfographicRoadmap(data);
    const infographic = document.createElement('div');
    infographic.className = 'roadmap-infographic';

    roadmap.sections.forEach((section, sectionIndex) => {
        const sectionCard = document.createElement('section');
        sectionCard.className = `roadmap-section section-${sectionIndex % 4}`;

        sectionCard.innerHTML = `
            <header class="roadmap-section-header">
                <div>
                    <span class="roadmap-section-kicker">${section.kicker}</span>
                    <h2 class="roadmap-section-title">${section.title}</h2>
                </div>
                <div class="roadmap-section-meta">
                    <span>${section.items.length} skills</span>
                    <span>${section.completedCount} completed</span>
                </div>
            </header>
            <ul class="roadmap-skill-list">
                ${section.items.map((item) => `
                    <li class="roadmap-skill-row ${item.status}" data-skill-index="${item.globalIndex}">
                        <div class="roadmap-skill-icon">${item.status === 'completed' ? '✔' : '•'}</div>
                        <div class="roadmap-skill-content">
                            <div class="roadmap-skill-topline">
                                <h3 class="roadmap-skill-name">${item.name}</h3>
                                <span class="roadmap-skill-status ${item.status}">${item.status === 'completed' ? 'Completed ✅' : 'You need to learn this'}</span>
                            </div>
                            <p class="roadmap-skill-description">${item.description}</p>
                            <div class="roadmap-skill-bullets">
                                ${item.bullets.map((bullet) => `<span class="roadmap-skill-bullet">${bullet}</span>`).join('')}
                            </div>
                        </div>
                        <div class="roadmap-skill-actions">
                            <button class="btn-action btn-detail" data-action="details" data-skill-index="${item.globalIndex}">Details</button>
                            <button class="btn-action btn-complete" data-action="complete" data-skill-index="${item.globalIndex}">✔ Complete</button>
                        </div>
                    </li>
                `).join('')}
            </ul>
        `;

        infographic.appendChild(sectionCard);

        if (sectionIndex < roadmap.sections.length - 1) {
            const connector = document.createElement('div');
            connector.className = 'section-connector';
            connector.innerHTML = '<span class="section-connector-line"></span>';
            infographic.appendChild(connector);
        }
    });

    container.appendChild(infographic);

    container.querySelectorAll('[data-action="details"]').forEach((button) => {
        button.addEventListener('click', () => showSkillDetails(Number(button.dataset.skillIndex)));
    });

    container.querySelectorAll('[data-action="complete"]').forEach((button) => {
        button.addEventListener('click', () => markNodeComplete(Number(button.dataset.skillIndex)));
    });
}

function markNodeComplete(idx) {
    appState.completedSkills.add(idx);
    
    // Confetti!
    if (typeof confetti !== 'undefined') {
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { x: 0.5, y: 0.5 }
        });
    }
    
        if (appState.currentPage === 3) {
            renderProgressPage();
        }
    renderRoadmap(appState.roadmapData);
}

function buildInfographicRoadmap(data) {
    const steps = Array.isArray(data?.steps) && data.steps.length > 0 ? data.steps : [];
    const normalizedSelectedSkills = appState.selectedSkills.map((skill) => normalizeSkill(skill));

    const roleSkills = steps.length > 0
        ? steps.map((step, index) => ({
            index,
            name: step.skill || step.name || `Skill ${index + 1}`,
            description: step.description || step.intro || `Master ${step.skill || step.name || `Skill ${index + 1}`}`,
            why: step.why_important || step.why || 'This skill is required for your target role.',
            level: step.level ?? 1,
            tools: Array.isArray(step.tools) ? step.tools : [],
            libraries: Array.isArray(step.libraries) ? step.libraries : [],
            concepts: Array.isArray(step.concepts) ? step.concepts : [],
            subSkills: Array.isArray(step.sub_skills) ? step.sub_skills : [],
            projects: Array.isArray(step.projects) ? step.projects : [],
            status: step.status || (normalizedSelectedSkills.includes(normalizeSkill(step.skill || step.name)) ? 'completed' : 'missing')
        }))
        : appState.selectedSkills.map((skill, index) => ({
            index,
            name: skill,
            description: `Master ${skill} to advance your career`,
            why: 'This skill supports your target role.',
            level: 1,
            tools: [],
            libraries: [],
            concepts: ['Fundamentals', 'Practice', 'Projects'],
            subSkills: ['Basics', 'Practice', 'Projects'],
            projects: [],
            status: 'completed'
        }));

    const fundamentals = [];
    const coreSkills = [];
    const advancedSkills = [];
    const toolsAndTech = [];
    const projects = [];

    roleSkills.forEach((skill, index) => {
        const completed = appState.completedSkills.has(index) || skill.status === 'completed' || normalizedSelectedSkills.includes(normalizeSkill(skill.name));
        const skillItem = {
            globalIndex: index,
            name: skill.name,
            description: skill.description,
            status: completed ? 'completed' : 'missing',
            bullets: [...skill.subSkills, ...skill.concepts].filter(Boolean).slice(0, 4)
        };

        if (skill.level <= 0 || index < Math.ceil(roleSkills.length * 0.25)) {
            fundamentals.push(skillItem);
        } else if (skill.level === 1 || index < Math.ceil(roleSkills.length * 0.6)) {
            coreSkills.push(skillItem);
        } else {
            advancedSkills.push(skillItem);
        }

        if ((skill.tools && skill.tools.length) || (skill.libraries && skill.libraries.length)) {
            toolsAndTech.push({
                globalIndex: index,
                name: skill.name,
                description: skill.description,
                status: completed ? 'completed' : 'missing',
                bullets: [...skill.tools, ...skill.libraries].filter(Boolean).slice(0, 4)
            });
        }

        if (skill.projects && skill.projects.length) {
            projects.push({
                globalIndex: index,
                name: skill.name,
                description: skill.description,
                status: completed ? 'completed' : 'missing',
                bullets: skill.projects.map((project) => typeof project === 'string' ? project : project.name).filter(Boolean).slice(0, 4)
            });
        }
    });

    const finalRoleSection = {
        globalIndex: roleSkills.length,
        name: data?.role || appState.selectedRole,
        description: 'Apply your roadmap to build a polished portfolio, prepare interviews, and start applying for roles.',
        status: roleSkills.every((skill, index) => appState.completedSkills.has(index) || skill.status === 'completed' || normalizedSelectedSkills.includes(normalizeSkill(skill.name))) ? 'completed' : 'missing',
        bullets: ['Portfolio ready', 'Interview practice', 'Apply for roles', 'Career transition']
    };

    return {
        sections: [
            { title: 'Fundamentals', kicker: 'Section 1', items: fundamentals, completedCount: fundamentals.filter((item) => item.status === 'completed').length },
            { title: 'Core Skills', kicker: 'Section 2', items: coreSkills, completedCount: coreSkills.filter((item) => item.status === 'completed').length },
            { title: 'Advanced Skills', kicker: 'Section 3', items: advancedSkills, completedCount: advancedSkills.filter((item) => item.status === 'completed').length },
            { title: 'Tools & Technologies', kicker: 'Section 4', items: toolsAndTech, completedCount: toolsAndTech.filter((item) => item.status === 'completed').length },
            { title: 'Projects', kicker: 'Section 5', items: projects, completedCount: projects.filter((item) => item.status === 'completed').length },
            { title: `Final Role: ${data?.role || appState.selectedRole}`, kicker: 'Section 6', items: [finalRoleSection], completedCount: finalRoleSection.status === 'completed' ? 1 : 0 }
        ]
    };
}

function normalizeSkill(value) {
    return String(value || '').toLowerCase().trim();
}

function renderDetailList(items, fallbackMessage) {
    const list = Array.isArray(items) ? items.filter(Boolean) : [];
    if (!list.length) {
        return `<p>${fallbackMessage}</p>`;
    }

    return `<ul>${list.map((item) => `<li>${item}</li>`).join('')}</ul>`;
}

function showSkillDetails(skillIndex) {
    const steps = Array.isArray(appState.roadmapData?.steps) ? appState.roadmapData.steps : [];
    const step = steps[skillIndex];
    if (!step) {
        return;
    }

    const modalBody = document.getElementById('modal-body');
    const modal = document.getElementById('skill-details-modal');
    if (!modalBody || !modal) {
        return;
    }

    const whatToLearn = Array.isArray(step.what_to_learn?.concepts) && step.what_to_learn.concepts.length
        ? step.what_to_learn.concepts
        : Array.isArray(step.concepts) && step.concepts.length
            ? step.concepts
            : Array.isArray(step.sub_skills) ? step.sub_skills : [];
    const howToStart = Array.isArray(step.how_to_start) ? step.how_to_start : [];
    const subSkills = Array.isArray(step.sub_skills) ? step.sub_skills : [];
    const benefits = Array.isArray(step.benefits) && step.benefits.length
        ? step.benefits
        : [
            `Strengthens your readiness for ${appState.selectedRole || 'your target role'}.`,
            'Helps you build confidence in projects, interviews, and daily work.',
            'Makes it easier to progress to the next roadmap step.'
        ];
    const futureUse = Array.isArray(step.future_use) && step.future_use.length
        ? step.future_use
        : [
            'Apply it in portfolio projects that hiring managers can review.',
            'Explain it with confidence in interviews and technical discussions.',
            'Use it to connect related tools, concepts, and workflows later in the roadmap.'
        ];
    const whyNeeded = step.why_important || step.why || `This skill is important for ${step.skill || step.name || 'this role'} and helps you move from beginner understanding to practical application.`;
    const nextSteps = howToStart.length
        ? howToStart
        : [
            'Learn the fundamentals and core terminology.',
            'Practice with small examples or exercises.',
            'Apply it in a mini project or real task.'
        ];

    modalBody.innerHTML = `
        <div class="detail-card">
            <h2 id="skill-details-title">${step.skill || step.name}</h2>
            <p class="detail-summary">${step.description || step.intro || ''}</p>
        </div>
        <div class="detail-block">
            <h3>What you should study</h3>
            ${renderDetailList(whatToLearn, 'Start with the basics, then move into applied practice and projects.')}
        </div>
        <div class="detail-block">
            <h3>Why it is important</h3>
            <p>${whyNeeded}</p>
        </div>
        <div class="detail-block">
            <h3>How to begin</h3>
            ${renderDetailList(nextSteps, 'Begin with basics, then move to practice and projects.')}
        </div>
        <div class="detail-block">
            <h3>Benefits you will get</h3>
            ${renderDetailList(benefits, 'You will build stronger confidence, better job readiness, and more practical ability.')}
        </div>
        <div class="detail-block">
            <h3>How this helps in the future</h3>
            ${renderDetailList(futureUse, 'This skill will keep paying off in projects, interviews, and day-to-day job work.')}
        </div>
        <div class="detail-block">
            <h3>Related subskills</h3>
            ${renderDetailList(subSkills, 'These will appear as you explore this topic in more depth.')}
        </div>
    `;

    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
}

function hideSkillDetails() {
    const modal = document.getElementById('skill-details-modal');
    if (!modal) {
        return;
    }

    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
}

// ============ PAGE NAVIGATION ============
function initializePageTransitions() {
    // Setup initial page
    switchToPage(1, false);
    updateTopControls();
}

function switchToPage(pageNum, pushHistory = true) {
    if (pushHistory && appState.currentPage !== pageNum) {
        appState.pageHistory.push(appState.currentPage);
    }

    // Hide all pages
    document.getElementById('page1').classList.remove('active');
    document.getElementById('page2').classList.remove('active');
    document.getElementById('page3').classList.remove('active');
    
    // Show target page
    const pageId = `page${pageNum}`;
    document.getElementById(pageId).classList.add('active');
    
    appState.currentPage = pageNum;
    updateTopControls();
    
    if (pageNum === 3) {
        renderProgressPage();
    }
}

function goBackToPage1() {
    switchToPage(1);
}

function goBackToPage2() {
    switchToPage(2);
}

function switchToPage3() {
    switchToPage(3);
}

function goBackToPreviousPage() {
    const previousPage = appState.pageHistory.pop();
    if (previousPage) {
        switchToPage(previousPage, false);
        return;
    }

    if (appState.currentPage > 1) {
        switchToPage(appState.currentPage - 1, false);
    }
}

function updateTopControls() {
    const progressBtn = document.getElementById('global-progress-btn');
    if (progressBtn) {
        progressBtn.disabled = appState.currentPage === 3;
    }
}

// ============ PROGRESS PAGE ============
function renderProgressPage() {
    const container = document.getElementById('stats-grid');
    const timelineRows = document.getElementById('timeline-rows');
    const steps = Array.isArray(appState.roadmapData?.steps) ? appState.roadmapData.steps : [];
    const derivedRows = buildTimelineRows(steps);
    const total = derivedRows.filter((row) => row.source === 'roadmap').length;
    const completed = derivedRows.filter((row) => row.status === 'completed').length;
    const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
    const nextFocus = derivedRows.find((row) => row.source === 'roadmap' && row.status === 'pending')
        || derivedRows.find((row) => row.source === 'roadmap' && row.status === 'locked')
        || null;

    container.innerHTML = `
        <div class="stat-card completed">
            <div class="stat-value">${completed}</div>
            <div class="stat-label">Skills Completed</div>
        </div>
        <div class="stat-card remaining">
            <div class="stat-value">${Math.max(total - completed, 0)}</div>
            <div class="stat-label">Skills Remaining</div>
        </div>
        <div class="stat-card progress">
            <div class="stat-value">${percent}%</div>
            <div class="stat-label">Progress</div>
        </div>
        <div class="stat-card focus">
            <div class="stat-value">${nextFocus ? nextFocus.skill : 'Done'}</div>
            <div class="stat-label">Next Focus</div>
        </div>
    `;

    if (timelineRows) {
        timelineRows.innerHTML = derivedRows.map((row) => renderTimelineRow(row)).join('');

        timelineRows.querySelectorAll('[data-action="view"]').forEach((button) => {
            button.addEventListener('click', () => showSkillDetails(Number(button.dataset.skillIndex)));
        });

        timelineRows.querySelectorAll('[data-action="start"]').forEach((button) => {
            button.addEventListener('click', () => {
                const index = Number(button.dataset.skillIndex);
                markNodeComplete(index);
            });
        });

        timelineRows.querySelectorAll('[data-action="edit-plan"]').forEach((button) => {
            button.addEventListener('click', () => editTimelineEntry(button.dataset.planId));
        });

        timelineRows.querySelectorAll('[data-action="delete-plan"]').forEach((button) => {
            button.addEventListener('click', () => deleteTimelineEntry(button.dataset.planId));
        });
    }
}

function buildTimelineRows(steps) {
    const rows = [];
    const firstIncompleteIndex = steps.findIndex((step, index) => !appState.completedSkills.has(index) && !normalizeSkill(step.skill || step.name).includes('final role'));

    steps.forEach((step, index) => {
        const skillName = step.skill || step.name || `Skill ${index + 1}`;
        let status = 'locked';
        if (appState.completedSkills.has(index)) {
            status = 'completed';
        } else if (index === firstIncompleteIndex || firstIncompleteIndex === -1) {
            status = 'pending';
        }

        rows.push({
            id: `roadmap-${index}`,
            day: `Day ${index * 2 + 1}`,
            skill: skillName,
            status,
            duration: step.time_required || step.time_estimate || '—',
            actionLabel: status === 'completed' ? 'View' : status === 'pending' ? 'Start' : '—',
            actionType: status === 'completed' ? 'view' : status === 'pending' ? 'start' : 'locked',
            skillIndex: index,
            source: 'roadmap',
            description: step.description || step.intro || ''
        });
    });

    appState.customPlans.forEach((plan) => {
        rows.push({
            id: plan.id,
            day: plan.day,
            skill: plan.skill,
            status: plan.status || 'pending',
            duration: plan.duration,
            actionLabel: 'Edit / Delete',
            actionType: 'custom',
            source: 'custom'
        });
    });

    return rows;
}

function renderTimelineRow(row) {
    if (row.source === 'custom') {
        return `
            <div class="timeline-row ${row.status} custom-row" data-plan-id="${row.id}">
                <div class="timeline-chip ${row.status}">${row.day}</div>
                <div class="timeline-skill">${row.skill}</div>
                <div class="timeline-chip ${row.status}">${row.status === 'completed' ? 'Completed ✅' : row.status === 'locked' ? 'Locked' : 'Pending ⏳'}</div>
                <div class="timeline-chip ${row.status}">${row.duration}</div>
                <div class="timeline-actions">
                    <button type="button" class="timeline-action-btn" data-action="edit-plan" data-plan-id="${row.id}">Edit</button>
                    <button type="button" class="timeline-action-btn" data-action="delete-plan" data-plan-id="${row.id}">Delete</button>
                </div>
            </div>
        `;
    }

    const disabledAction = row.actionType === 'locked';
    return `
        <div class="timeline-row ${row.status}" data-skill-index="${row.skillIndex}">
            <div class="timeline-chip ${row.status}">${row.day}</div>
            <div class="timeline-skill">${row.skill}</div>
            <div class="timeline-chip ${row.status}">${row.status === 'completed' ? 'Completed ✅' : row.status === 'pending' ? 'Pending ⏳' : 'Locked 🔒'}</div>
            <div class="timeline-chip ${row.status}">${row.duration}</div>
            <div class="timeline-actions">
                ${disabledAction ? '<span class="timeline-chip locked">—</span>' : `<button type="button" class="timeline-action-btn" data-action="${row.actionType}" data-skill-index="${row.skillIndex}">${row.actionLabel}</button>`}
            </div>
        </div>
    `;
}

function onTimelineSubmit(event) {
    event.preventDefault();

    const dayInput = document.getElementById('timeline-day');
    const skillInput = document.getElementById('timeline-skill');
    const durationInput = document.getElementById('timeline-duration');

    const day = dayInput.value.trim();
    const skill = skillInput.value.trim();
    const duration = durationInput.value.trim();

    if (!day || !skill || !duration) {
        return;
    }

    if (appState.editingPlanId) {
        const plan = appState.customPlans.find((item) => String(item.id) === String(appState.editingPlanId));
        if (plan) {
            plan.day = day;
            plan.skill = skill;
            plan.duration = duration;
        }
    } else {
        appState.customPlans.unshift({
            id: Date.now(),
            day,
            skill,
            duration,
            status: 'pending'
        });
    }

    appState.editingPlanId = null;
    event.target.reset();
    const submitButton = event.target.querySelector('.timeline-add-btn');
    if (submitButton) {
        submitButton.textContent = '+ Add Plan';
    }

    renderProgressPage();
}

function editTimelineEntry(planId) {
    const plan = appState.customPlans.find((item) => String(item.id) === String(planId));
    if (!plan) {
        return;
    }

    document.getElementById('timeline-day').value = plan.day;
    document.getElementById('timeline-skill').value = plan.skill;
    document.getElementById('timeline-duration').value = plan.duration;
    appState.editingPlanId = plan.id;

    const submitButton = document.querySelector('#timeline-form .timeline-add-btn');
    if (submitButton) {
        submitButton.textContent = 'Update Plan';
    }
}

function deleteTimelineEntry(planId) {
    appState.customPlans = appState.customPlans.filter((item) => String(item.id) !== String(planId));
    if (String(appState.editingPlanId) === String(planId)) {
        appState.editingPlanId = null;
        const form = document.getElementById('timeline-form');
        if (form) {
            form.reset();
        }
        const submitButton = document.querySelector('#timeline-form .timeline-add-btn');
        if (submitButton) {
            submitButton.textContent = '+ Add Plan';
        }
    }
    renderProgressPage();
}

function createRipple(target, event) {
    const ripple = document.createElement('span');
    ripple.className = 'ripple-effect';
    const rect = target.getBoundingClientRect();
    ripple.style.left = `${event.clientX - rect.left}px`;
    ripple.style.top = `${event.clientY - rect.top}px`;
    target.appendChild(ripple);
    setTimeout(() => ripple.remove(), 650);
}

document.addEventListener('click', (event) => {
    if (event.target && event.target.matches('[data-close-modal]')) {
        hideSkillDetails();
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        hideSkillDetails();
    }
});

// ============ UTILITIES ============
console.log('✓ AI Career Roadmap Script Loaded');
