// Espera que el DOM esté completamente cargado
window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById("signupForm");

    form.addEventListener("submit", function (event) {
        const password = document.querySelector('input[name="password"]').value;
        const confirmPassword = document.querySelector('input[name="confirmPassword"]').value;

        if (password !== confirmPassword) {
            event.preventDefault(); // Detiene el envío del formulario
            alert("Las contraseñas no coinciden.");
        }
    });
});