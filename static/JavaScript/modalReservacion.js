document.addEventListener('DOMContentLoaded', () => {
  // Función para mostrar el modal
  function mostrarModal(numeroMesa) {
    const modal = document.getElementById('modal-mesa');
    const info = document.getElementById('info-mesa');
    info.textContent = `Mesa ${numeroMesa}`;

    // 👇 Aquí asignamos el id de la mesa al input oculto del formulario
    document.getElementById('id_mesa').value = numeroMesa;

    modal.classList.add('activo'); // Mostrar con clase
  }

  // Evento para cerrar el modal con la X
  document.querySelector('.cerrar').addEventListener('click', () => {
    document.getElementById('modal-mesa').classList.remove('activo');
  });

  // Evento para cerrar al hacer clic fuera del contenido
  window.addEventListener('click', function (e) {
    const modal = document.getElementById('modal-mesa');
    if (e.target === modal) {
      modal.classList.remove('activo');
    }
  });

  // Escuchar clic en cada mesa
  document.querySelectorAll('.mesa').forEach(mesa => {
    mesa.addEventListener('click', function () {
      const numeroMesa = this.dataset.mesa;
      mostrarModal(numeroMesa); // Llama la función con el número de mesa
    });
  });

  // Evento para cerrar con el botón "Cerrar"
  document.querySelector('.btn-cerrar').addEventListener('click', () => {
    document.getElementById('modal-mesa').classList.remove('activo');
  });

  document.querySelector('.btn-confirmar').addEventListener('click', (e) => {
    e.preventDefault(); // Evita que se envíe de inmediato

    alert("Reservación realizada!");

    // Luego, envía el formulario manualmente si todo está bien
    document.querySelector('.form-reserva').submit();
  });

});
