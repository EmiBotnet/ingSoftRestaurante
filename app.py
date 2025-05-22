from flask import Flask, render_template, request, redirect, url_for, session
import pyodbc  # Necesario para conectar a SQL Server
import base64
from werkzeug.security import generate_password_hash, check_password_hash

# Usar comando "python app.py" para inicializar el servidor

app = Flask(__name__)
app.secret_key = 'clave_secreta123'  # Cambia esta clave en producción

# Función para conectar a la base de datos (NO TOCAR)
def get_db_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost;'
            'DATABASE=Restaurante_IS;'
            'Trusted_Connection=yes;'
        )
        print("✅ Conexión exitosa a la base de datos.")
        return conn
    except Exception as e:
        print("❌ Error al conectar a la base de datos:", e)
        return None
    
   
#Rutas de páginas

#Ruta default hacia el index.html
@app.route('/')
def index():
    return render_template('index.html')

#Ruta del signup
@app.route('/signup',methods=['GET','POST'])
def signup():

    #Obtener los valores ingresados en los campos del frontend
    if request.method == 'POST':
        primerNombre = request.form['firstName']
        segundoNombre = request.form['secondName']
        primerApellido = request.form['lastName']
        segundoApellido = request.form['secondLastName']
        direccion = request.form['address']
        telefono = request.form['phone']
        email = request.form['email']
        contraseña = request.form['password']
        confContraseña = request.form['confirmPassword']
        
        #Definir rol por defecto
        rol = 'cliente'
        

        #Validar contraseña
        if contraseña != confContraseña:
            return "Las contraseñas no coinciden"
        
         # Hashear la contraseña antes de guardarla
        contraseña_hash = generate_password_hash(contraseña)
    
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            #Query para registrar usuario
            cursor.execute("""
            INSERT INTO Clientes (
                Prim_nom_cli, Seg_nom_cli, Prim_ape_cli, Seg_ape_cli,
                Dir_cliente, Num_tel_clie, Correo_electronico, Contraseña
            )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (primerNombre, segundoNombre, primerApellido, segundoApellido, direccion, telefono, email, contraseña_hash))

            conn.commit()
            conn.close() 

            return redirect(url_for('login')) #redirigir al login despues de crear la cuenta
        
        #Error en caso de no registrar al usuario
        except Exception as e:
            return f"Error en el registro de usuario: {e}", 500
    
    #Renderizar la vista signup.html en caso de ser buscada en el navegador
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Verificar si el correo pertenece a un Cliente
        cursor.execute("""
            SELECT Id_Cliente, Prim_nom_cli, Contraseña
            FROM Clientes
            WHERE Correo_electronico = ?
            """, (email,))
        cliente = cursor.fetchone()

        
        if cliente:
            id_cliente, nombre_cliente, hashed_password = cliente
            if check_password_hash(hashed_password, password):
                session['usuario_tipo'] = 'cliente'
                session['usuario_nombre'] = nombre_cliente
                session['id_cliente'] = id_cliente  # <-- Aquí guardas el id del cliente
                return redirect(url_for('cliente'))
            else:
                return "Contraseña incorrecta para cliente", 401

        # 2. Verificar si el correo pertenece a un Empleado
        cursor.execute("""
            SELECT Id_Empleado, Contraseña
            FROM Empleado
            WHERE Correo_electronico = ?
        """, (email,))
        empleado = cursor.fetchone()

        if empleado:
            id_empleado, hashed_password = empleado
            if check_password_hash(hashed_password, password):
                # Aquí puedes guardar sesión si quieres
                return redirect(url_for('empleado_dashboard'))
            else:
                return "Contraseña incorrecta para empleado", 401

        conn.close()
        return "Correo no encontrado", 404

    return render_template('login.html')

#Ruta a principal.html
@app.route('/principal')
def principal():
    rol = session.get('rol', 'invitado')
    tipo = request.args.get('tipo')  # <- obtiene lo que venga como ?tipo=...

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if tipo:
            query = """
                SELECT Id_platillo, Nom_platillo, Precio, Descripcion, Foto_platillo, Is_Available 
                FROM Platillos
                WHERE Tipo_platillo = ?
            """
            cursor.execute(query, (tipo,))
        else:
            query = """
                SELECT Id_platillo, Nom_platillo, Precio, Descripcion, Foto_platillo, Is_Available 
                FROM Platillos
            """
            cursor.execute(query)

        platillos = cursor.fetchall()

        menu = []
        for row in platillos:
            foto_base64 = base64.b64encode(row[4]).decode('utf-8')
            menu.append({
                'id': row[0],
                'nombre': row[1],
                'precio': float(row[2]),
                'descripcion': row[3],
                'foto': foto_base64,
                'disponible': bool(row[5])
            })
    except Exception as e:
        return f"Error al obtener platillos: {e}", 500
    finally:
        conn.close()

    return render_template('principal.html', menu=menu, rol=rol)

#Ruta a reservaciones
@app.route('/reservaciones')
def reservaciones():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener las mesas
        cursor.execute("SELECT Id_mesa, Is_empty FROM Mesas")
        mesas = cursor.fetchall()

        datos_mesas = []
        for mesa in mesas:
            datos_mesas.append({
                'id': mesa[0],
                'disponible': bool(mesa[1])
            })

        # Obtener las reservaciones (aquí se arregla todo)
        cursor.execute("""
            SELECT Fecha_reserva, Hora_reserva, Id_mesa
            FROM Reservacion_mesa
            WHERE Id_cliente = ?
        """, (session.get('id_cliente'),))  
        reservaciones = cursor.fetchall()

        # Convertir a lista de diccionarios si es necesario
        reservas_lista = []
        for r in reservaciones:
            reservas_lista.append({
                'Fecha_reserva': r[0],
                'Hora_reserva': r[1],
                'id_mesa': r[2]
            })

    except Exception as e:
        return f"Error al obtener datos: {e}", 500

    finally:
        conn.close()

    # Aquí SÍ se pasa 'reservas' al template
    return render_template('reservaciones.html', mesas=datos_mesas, reservas=reservas_lista)

#Ruta al modal crear_reservacion
@app.route('/crear_reservacion', methods=['POST'])
def crear_reservacion():
    if 'id_cliente' not in session:
        print("⚠️ No hay sesión activa. Redirigiendo o bloqueando.")
        return "Debe iniciar sesión para hacer una reservación", 401

    id_cliente = session['id_cliente']
    fecha = request.form['fecha_reserva']
    hora = request.form['hora_reserva']
    id_mesa = request.form['id_mesa']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insertar reservación
        cursor.execute("""
            INSERT INTO Reservacion_mesa (Fecha_reserva, Hora_reserva, Id_cliente, Id_mesa)
            VALUES (?, ?, ?, ?)
        """, (fecha, hora, id_cliente, id_mesa))

        # Actualizar mesa a ocupada
        cursor.execute("""
            UPDATE Mesas
            SET Is_empty = 0
            WHERE Id_mesa = ?
        """, (id_mesa,))

        conn.commit()
        return redirect(url_for('reservaciones'))

    except Exception as e:
        return f"Error al registrar reservación: {e}", 500

    finally:
        conn.close()

#Ruta a eliminar_reservacion
@app.route('/eliminar_reservacion', methods=['POST'])
def eliminar_reservacion():
    if 'id_cliente' not in session:
        return "No autorizado", 401
    
    id_mesa = request.form['id_mesa']
    fecha = request.form['fecha']
    hora = request.form['hora']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    
        # 1. Eliminar reservación
        cursor.execute("""
            DELETE FROM Reservacion_mesa
            WHERE Id_mesa = ? AND Fecha_reserva = ? AND Hora_reserva = ? AND Id_cliente = ?
        """, (id_mesa, fecha, hora, session['id_cliente']))

         # 2. Marcar la mesa como disponible
        cursor.execute("""
            UPDATE Mesas
            SET Is_empty = 1
            WHERE Id_mesa = ?
        """, (id_mesa,))

        conn.commit()
        return redirect(url_for('reservaciones'))

    except Exception as e:
        return f"Error al eliminar reservación: {e}", 500

    finally:
        conn.close()

@app.route('/principalPedido', methods=['POST'])
def principalPedido():
    if 'id_cliente' not in session:
        return "Cliente no identificado", 403

    id_cliente = session['id_cliente']
    platillo_id = int(request.form['id_platillo'])
    cantidad_str = request.form.get('cantidad', '1')
    cantidad = int(cantidad_str) if cantidad_str.isdigit() else 1
    is_online = 1 if request.form.get('is_delivery') == 'on' else 0

    conn = get_db_connection()
    cursor = conn.cursor()

    # Paso 1: Verificar si hay una comanda activa para el cliente
    cursor.execute("""
        SELECT Id_comanda FROM Comandas 
        WHERE Estatus_com = 'En proceso' AND Num_contac = (
            SELECT Num_tel_clie FROM Clientes WHERE Id_Cliente = ?
        )
    """, (id_cliente,))
    comanda_existente = cursor.fetchone()

    if comanda_existente:
        id_comanda = comanda_existente[0]

    else:
        # Si no existe, crear una nueva comanda
        cursor.execute("""
            SELECT Dir_cliente, Num_tel_clie FROM Clientes WHERE Id_Cliente = ?
        """, (id_cliente,))
        cliente = cursor.fetchone()

        if not cliente:
            conn.close()
            return "Cliente no encontrado", 404

        dir_envio, num_contact = cliente
        metodo_pago = 1  # Puedes hacerlo dinámico luego
        estatus_com = "En proceso"

        cursor.execute("""
        INSERT INTO Comandas (Metodo_pago, Dir_envio, Num_contac, Estatus_com, Is_online)
        VALUES (?, ?, ?, 'En Proceso', ?)
    """, (metodo_pago, dir_envio, num_contact, is_online))

        # Obtener el ID de la comanda recién insertada
        cursor.execute("SELECT SCOPE_IDENTITY()")
        id_comanda = cursor.fetchone()[0]

    # Paso 3: Obtener precio del platillo
    cursor.execute("SELECT Precio FROM Platillos WHERE Id_platillo = ?", (platillo_id,))
    precio_row = cursor.fetchone()

    if not precio_row:
        conn.close()
        return "Platillo no encontrado", 404

    precio_unitario = float(precio_row[0])
    pago_total = precio_unitario * cantidad

    # Paso 4: Insertar el producto en la tabla Detalles_Orden
    cursor.execute("""
        INSERT INTO Detalles_Orden (Id_platillo, Cant_platillos, Pago_total, Is_delivery, Id_comanda)
        VALUES (?, ?, ?, ?, ?)
    """, (platillo_id, cantidad, pago_total, is_online, id_comanda))

    print("Comanda ID:", id_comanda)
    print("Platillo agregado:", platillo_id, "Cantidad:", cantidad, "Total:", pago_total)

    conn.commit()
    conn.close()

    return redirect(url_for('principal'))

@app.route('/historialPedidos')
def historialPedidos():
    if 'id_cliente' not in session:
        return redirect(url_for('login'))  # o lo que manejes como login

    id_cliente = session['id_cliente']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener historial completo con JOINs
    cursor.execute("""
    SELECT 
        C.Id_comanda, 
        C.Estatus_com, 
        DO.Is_delivery,
        P.Nom_platillo, 
        DO.Cant_platillos, 
        P.Precio  
    FROM Comandas C
    JOIN Detalles_Orden DO ON C.Id_comanda = DO.Id_comanda
    JOIN Platillos P ON DO.Id_platillo = P.Id_platillo
    WHERE C.Num_contac = (
        SELECT Num_tel_clie FROM Clientes WHERE Id_Cliente = ?
    )
    ORDER BY C.Id_comanda DESC
""", (id_cliente,))


    registros = cursor.fetchall()

    historial = []
    for r in registros:
        historial.append({
        'id_comanda': r[0],
        'estatus': r[1],
        'is_delivery': r[2],
        'nombre': r[3],
        'cantidad': r[4],
        'precio_unitario': r[5],
        'pago_total': r[4] * r[5]
    })


    conn.close()

    return render_template('historialPedidos.html', comandas=historial)

@app.route('/cancelarPedido', methods=['POST'])
def cancelarPedido():
    id_comanda = request.form['id_comanda']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Comandas SET Estatus_com = 'Cancelada' WHERE Id_comanda = ?", (id_comanda,))
    conn.commit()
    conn.close()

    return redirect(url_for('historialPedidos'))

#Rutas de roles
@app.route('/cliente')
def cliente():
    if session.get('usuario_tipo') == 'cliente':
        return redirect(url_for('principal'))
    return "Acceso denegado"

@app.route('/admin')
def admin():
    if session.get('rol') == 'admin':
        return render_template('admin.html')
    return "Acceso denegado"

@app.route('/mesero')
def mesero():
    if session.get('rol') == 'mesero':
        return render_template('mesero.html')
    return "Acceso denegado"

@app.route('/invitado-directo')
def invitado_directo():
    return redirect(url_for('principal'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
