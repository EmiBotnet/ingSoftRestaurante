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
def principal():
    if 'comanda' not in session:
        session['comanda'] = []
    
    platillo_id = request.form['id_platillo']
    cantidad = int(request.form.get('cantidad', 1))

    # Revisar si ya está en la comanda
    for item in session['comanda']:
        if item['id_platillo'] == platillo_id:
            item['cantidad'] += cantidad
            break
    else:
        session['carrito'].append({'id_platillo': platillo_id, 'cantidad': cantidad})

    session.modified = True
    return redirect(url_for('historialComanda'))

@app.route('/historialPedidos')
def historialPedidos():
    carrito = session.get('carrito', [])
    if not carrito:
        return render_template('historialPedidos.html', items=[], total=0)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    items = []
    total = 0
    for item in carrito:
        cursor.execute("SELECT Nombre, Precio FROM Platillos WHERE Id_platillo = ?", (item['id_platillo'],))
        platillo = cursor.fetchone()
        subtotal = platillo[1] * item['cantidad']
        total += subtotal
        items.append({
            'id': item['id_platillo'],
            'nombre': platillo[0],
            'precio': platillo[1],
            'cantidad': item['cantidad'],
            'subtotal': subtotal
        })

    conn.close()
    return render_template('historialPedidos.html', items=items, total=total)

    

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
