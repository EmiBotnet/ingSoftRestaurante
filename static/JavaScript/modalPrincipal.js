console.log("JS cargado correctamente");

document.querySelectorAll('.btn-agregar').forEach(btn => {
    btn.addEventListener('click', () => {
        const modal = document.getElementById('modalPedido');
        document.getElementById('modal_id_platillo').value = btn.dataset.id;
        document.getElementById('modal_precio_unitario').value = btn.dataset.precio;
        document.getElementById('modal_nombre_platillo').innerText = btn.dataset.nombre;
        document.getElementById('modal_cantidad').value = 1;
        document.getElementById('modal_pago_total').innerText = `$${parseFloat(btn.dataset.precio).toFixed(2)}`;
        modal.style.display = 'flex';
    });
});

document.querySelector('.close').addEventListener('click', () => {
    document.getElementById('modalPedido').style.display = 'none';
});

document.getElementById('modal_cantidad').addEventListener('input', () => {
    const precio = parseFloat(document.getElementById('modal_precio_unitario').value);
    let cantidad = parseInt(document.getElementById('modal_cantidad').value);
    if (isNaN(cantidad) || cantidad < 1) cantidad = 1;
    const total = (precio * cantidad).toFixed(2);
    document.getElementById('modal_pago_total').innerText = `$${total}`;
});
