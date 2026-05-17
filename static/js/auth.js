function getToken() { return localStorage.getItem('aidetect_token'); }
function getUserEmail() { return localStorage.getItem('aidetect_email'); }
function setSession(token, email) {
    localStorage.setItem('aidetect_token', token);
    localStorage.setItem('aidetect_email', email);
}
function clearSession() {
    localStorage.removeItem('aidetect_token');
    localStorage.removeItem('aidetect_email');
}

async function apiPost(url, data) {
    const formBody = new URLSearchParams();
    for (const [k, v] of Object.entries(data)) formBody.append(k, v);
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formBody.toString(),
    });
    return res.json();
}

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');

    if (loginForm) {
        if (getToken()) { window.location.href = '/dashboard'; return; }
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const errEl = document.getElementById('errorMsg');
            errEl.classList.add('hidden');

            const result = await apiPost('/api/login', { email, password });
            if (result.success) {
                setSession(result.access_token, result.email);
                window.location.href = '/dashboard';
            } else {
                errEl.textContent = result.error || 'Login failed';
                errEl.classList.remove('hidden');
            }
        });
    }

    if (signupForm) {
        if (getToken()) { window.location.href = '/dashboard'; return; }
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const errEl = document.getElementById('errorMsg');
            errEl.classList.add('hidden');

            const result = await apiPost('/api/signup', { email, password });
            if (result.success) {
                alert('Account created! Check your email for confirmation, then sign in.');
                window.location.href = '/login';
            } else {
                errEl.textContent = result.error || 'Signup failed';
                errEl.classList.remove('hidden');
            }
        });
    }

    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            clearSession();
            window.location.href = '/';
        });
    }
});
