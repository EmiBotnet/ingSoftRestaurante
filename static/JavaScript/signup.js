document.getElementById("signupForm").addEventListener("submit", function(event) {
    event.preventDefault();

    let password = document.getElementById("password").value;
    let confirmPassword = document.getElementById("confirmPassword").value;

    if (password !== confirmPassword) {
        alert("Las contraseñas no coinciden.");
    } else {
        alert("Cuenta creada con éxito.");
        this.reset(); // Limpia el formulario
    }
});
