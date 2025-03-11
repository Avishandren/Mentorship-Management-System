document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent form from reloading the page

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    
    if (data.success) {
        alert('Login successful!');
        window.location.href = "/dashboard"; // Redirect on success
    } else {
        document.getElementById('errorMessage').textContent = data.message;
    }
});