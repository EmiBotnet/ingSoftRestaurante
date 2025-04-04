document.getElementById("file-input").addEventListener("change", function(event) 
{
    const file = event.target.files[0]; // Obtiene el archivo seleccionado
    if (file) 
    {
        const reader = new FileReader(); // Crea un lector de archivos
        reader.onload = function(e) 
        {
            document.getElementById("profile-image").src = e.target.result; // Muestra la imagen seleccionada
        };
        reader.readAsDataURL(file); // Convierte el archivo en URL base64
    }
});

//Boton regresar
document.getElementById("back-button").addEventListener("click", function() {
    const confirmBack = confirm("¿Seguro que quieres regresar?");
    if (confirmBack) {
        window.location.href = "menu.html"; // Redirige al menu
    }
});

// Captura el formulario y muestra una alerta al guardar los cambios
document.querySelector("form").addEventListener("submit", function(event) {
    event.preventDefault(); // Evita el envío del formulario (para pruebas)

    // Obtén todos los campos de entrada del formulario
    const inputs = document.querySelectorAll("form input");
    let fieldsFilled = false;

    // Verifica si al menos un campo tiene datos
    inputs.forEach(input => {
        if (input.value.trim() !== "") {
            fieldsFilled = true;
        }
    });

    if (fieldsFilled) {
        // Si hay datos, muestra la alerta de actualización
        alert("Perfil actualizado correctamente.");
    } else {
        // Si no hay datos, muestra la alerta de error
        alert("No se llenaron campos.");
    }
});


//Cerrar sesion
document.getElementById("logout-button").addEventListener("click", function() {
    const confirmLogout = confirm("¿Seguro que quieres cerrar sesión?");
    if (confirmLogout) {
        alert("Has cerrado sesión correctamente.");
        window.location.href = "login.html"; // Redirige al login
    }
});

