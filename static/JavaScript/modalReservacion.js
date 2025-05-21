document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('modal-mesa');
  const info = document.getElementById('info-mesa');
  const idMesaInput = document.getElementById('id_mesa');
  const btnCerrar = document.querySelector('.btn-cerrar');
  const btnX = document.querySelector('.cerrar');
  const form = document.querySelector('.form-reserva');
  const btnConfirmar = document.querySelector('.btn-confirmar');

  // Mostrar el modal solo si la mesa está disponible
  document.querySelectorAll('.mesa').forEach(mesa => {
    mesa.addEventListener('click', () => {
      if (mesa.classList.contains('ocupada')) {
        alert("⚠️ Esta mesa ya está reservada. Por favor, elige otra.");
        return;
      }

      const numeroMesa = mesa.dataset.mesa;
      info.textContent = `Reservar Mesa ${numeroMesa}`;
      idMesaInput.value = numeroMesa;

      modal.classList.add('activo'); // Usamos clase para mostrar
    });
  });

  // Cerrar el modal con botón X, botón "Cerrar", o clic fuera del contenido
  btnX.addEventListener('click', () => {
    modal.classList.remove('activo');
  });

  btnCerrar.addEventListener('click', () => {
    modal.classList.remove('activo');
  });

  window.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.classList.remove('activo');
    }
  });

  // Confirmar reserva (opcional: validaciones adicionales antes de enviar)
  btnConfirmar.addEventListener('click', (e) => {
    e.preventDefault();

    // Podrías validar aquí fecha/hora si quieres
    alert("✅ ¡Reservación realizada con éxito!");
    form.submit();
  });
});

