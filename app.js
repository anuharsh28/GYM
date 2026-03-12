const API_BASE_URL = 'http://127.0.0.1:5001';

// Navigation Logic
document.querySelectorAll('.nav-btn').forEach(button => {
    button.addEventListener('click', (e) => {
        // Remove active class from all buttons
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        // Add active class to clicked button
        e.target.classList.add('active');

        // Hide all sections
        document.querySelectorAll('.view-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show target section
        const targetId = e.target.getAttribute('data-target');
        document.getElementById(`view-${targetId}`).classList.add('active');

        // Fetch data based on tab
        loadDataForSection(targetId);
    });
});

// Helper for programmatic tab switching
function switchTab(targetId) {
    const btn = document.querySelector(`.nav-btn[data-target="${targetId}"]`);
    if (btn) btn.click();
}

// Initial API Status Check
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            const statusEl = document.getElementById('api-status');
            statusEl.textContent = 'System Online';
            statusEl.style.color = 'var(--gold)';

            const dot = document.querySelector('.status-dot');
            dot.style.backgroundColor = 'var(--gold)';
            dot.style.boxShadow = '0 0 10px var(--gold), 0 0 20px var(--gold)';

            // Update home view msg
            document.getElementById('home-status-msg').innerHTML = `
                API connected successfully. <br><br>
                <strong>Service:</strong> ${data.service} <br>
                <strong>Last Ping:</strong> ${new Date(data.timestamp).toLocaleTimeString()}
            `;
        }
    } catch (error) {
        console.error('API connection failed:', error);
        document.getElementById('api-status').textContent = 'API Offline';
        document.querySelector('.status-dot').style.backgroundColor = 'var(--amber)';
    }
}

// Load data based on active section
async function loadDataForSection(section) {
    const loader = document.getElementById('global-loader');

    if (section === 'programs') {
        const grid = document.getElementById('programs-grid');
        grid.innerHTML = '';
        loader.style.display = 'block';

        try {
            const res = await fetch(`${API_BASE_URL}/programs`);
            const data = await res.json();

            data.programs.forEach(prog => {
                grid.innerHTML += `
                    <div class="data-card glass">
                        <h3 class="card-title">${prog.name}</h3>
                        <span class="card-meta">Factor: ${prog.calorie_factor}x</span>
                        <div class="card-body">
                            <p><strong>Goal:</strong> ${prog.description}</p>
                            <p><strong>Routine:</strong> ${prog.workout_summary}</p>
                            <p><strong>Diet:</strong> ${prog.diet_summary}</p>
                        </div>
                    </div>
                `;
            });
        } catch (e) {
            console.error(e);
        } finally {
            loader.style.display = 'none';
        }
    }

    else if (section === 'classes') {
        const grid = document.getElementById('classes-grid');
        grid.innerHTML = '';
        loader.style.display = 'block';

        try {
            const res = await fetch(`${API_BASE_URL}/classes`);
            const data = await res.json();

            data.classes.forEach(cls => {
                grid.innerHTML += `
                    <div class="data-card glass">
                        <h3 class="card-title" style="color: var(--blue)">${cls.name}</h3>
                        <span class="card-meta">${cls.time} | ${cls.days}</span>
                        <div class="card-body">
                            <p><strong>Trainer:</strong> ${cls.trainer}</p>
                            <p><strong>Capacity:</strong> ${cls.capacity} members max</p>
                        </div>
                    </div>
                `;
            });
        } catch (e) {
            console.error(e);
        } finally {
            loader.style.display = 'none';
        }
    }

    else if (section === 'members') {
        const grid = document.getElementById('members-grid');
        grid.innerHTML = '';
        loader.style.display = 'block';

        try {
            const res = await fetch(`${API_BASE_URL}/members`);
            const data = await res.json();

            if (data.members.length === 0) {
                grid.innerHTML = `<div class="data-card glass"><p>No members found in database.</p></div>`;
            } else {
                data.members.forEach(member => {
                    grid.innerHTML += `
                        <div class="data-card glass">
                            <h3 class="card-title">${member.name}</h3>
                            <span class="card-meta">${member.program}</span>
                            <div class="card-body">
                                <p><strong>Age:</strong> ${member.age} yrs</p>
                                <p><strong>Weight:</strong> ${member.weight} kg</p>
                                <p><strong>Expires:</strong> ${member.membership_expiry || 'N/A'}</p>
                            </div>
                        </div>
                    `;
                });
            }
        } catch (e) {
            console.error(e);
        } finally {
            loader.style.display = 'none';
        }
    }
}

// Calorie Calculator Form Logic
document.getElementById('calorie-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const weight = document.getElementById('weight').value;
    const program = document.getElementById('program-select').value;
    const btn = e.target.querySelector('button');
    const resultCard = document.getElementById('calorie-result');

    // Animate button state
    const originalText = btn.textContent;
    btn.textContent = 'Calculating...';
    btn.style.opacity = '0.7';

    try {
        const res = await fetch(`${API_BASE_URL}/calories?weight=${weight}&program=${encodeURIComponent(program)}`);
        const data = await res.json();

        if (data.daily_calories_kcal) {
            resultCard.style.display = 'block';

            // Number increment animation
            const target = data.daily_calories_kcal;
            const numEl = document.getElementById('result-kcal');
            let current = 0;
            const inc = target / 30; // 30 frames

            const timer = setInterval(() => {
                current += inc;
                if (current >= target) {
                    numEl.textContent = target;
                    clearInterval(timer);
                } else {
                    numEl.textContent = Math.floor(current);
                }
            }, 16);

        }
    } catch (e) {
        console.error(e);
        alert("Failed to calculate. Make sure the API is running.");
    } finally {
        btn.textContent = originalText;
        btn.style.opacity = '1';
    }
});

// Init
window.addEventListener('DOMContentLoaded', () => {
    checkApiHealth();
});
