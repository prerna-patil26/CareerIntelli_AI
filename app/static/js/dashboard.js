/* Dashboard JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
});

// Load dashboard data
function loadDashboard() {
    loadUserProfile();
    loadRecentActivity();
}

// Load user profile
function loadUserProfile() {
    // TODO: Fetch user profile from API
    const userName = localStorage.getItem('userName') || 'User';
    document.getElementById('user-name').textContent = userName;
}

// Load recent activity
function loadRecentActivity() {
    // TODO: Fetch recent activity from API
    const activityList = document.getElementById('activity-list');
    
    const activities = [
        { date: 'Today', activity: 'Completed interview preparation' },
        { date: 'Yesterday', activity: 'Uploaded resume' },
        { date: '2 days ago', activity: 'Generated career prediction' }
    ];
    
    if (activities.length > 0) {
        activityList.innerHTML = activities.map(a => 
            `<div class="activity-item">
                <strong>${a.date}:</strong> ${a.activity}
            </div>`
        ).join('');
    }
}

// Navigation functions
function startInterview() {
    // TODO: Redirect to interview page
    location.href = '/interview';
}

function viewRoadmap() {
    // TODO: Redirect to roadmap page
    alert('Feature coming soon!');
}

function backToDashboard() {
    location.href = '/dashboard';
}

// Report functions
function downloadPDF() {
    // TODO: Implement PDF download
    alert('Downloading report as PDF...');
}

function emailReport() {
    // TODO: Implement email sending
    const email = prompt('Enter your email:');
    if (email) {
        alert(`Report will be sent to ${email}`);
    }
}

// Form submission
function handleFormSubmit(formId, apiEndpoint) {
    const form = document.getElementById(formId);
    
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch(apiEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    alert('Success!');
                    form.reset();
                } else {
                    alert('An error occurred. Please try again.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error submitting form');
            }
        });
    }
}

// Initialize forms
handleFormSubmit('profile-form', '/api/profile/update');
handleFormSubmit('resume-form', '/api/resume/upload');
handleFormSubmit('login-form', '/api/auth/login');
handleFormSubmit('register-form', '/api/auth/register');
