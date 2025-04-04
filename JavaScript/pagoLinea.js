document.getElementById("payment-form").addEventListener("submit", function(event) {
    event.preventDefault();
    alert("Pago realizado con éxito.");
    this.reset(); // Limpia el formulario
});
