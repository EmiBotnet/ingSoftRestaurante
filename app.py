from flask import Flask, render_template, request, redirect, url_for, session
import json
import pyodbc  # Necesario para conectar a SQL Server
import base64

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
        nombre = request.form['name']
        email = request.form['email']
        telefono = request.form['phone']
        direccion = request.form['address']
        contraseña = request.form['password']
        confContraseña = request.form['ConfirmPassword']
        #Definir rol por defecto
        

        #Validar contraseña
        if contraseña != confContraseña:
            return "Las contraseñas no coinciden"
    
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            #Query para registrar usuario
            cursor.execute("""
                INSERT INTO Usuarios (Nombre_Usuario, Correo, Telefono, Direccion, Contrasena, Rol)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nombre, email, telefono, direccion, contraseña, rol))

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
    if request.method == 'GET':
        # Mostrar formulario de login
        return render_template('login.html')

    elif request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT Nombre_Usuario, Contrasena, Rol
                FROM Usuarios
                WHERE Nombre_Usuario = ? AND Contrasena = ?
            """, (usuario, password))

            user = cursor.fetchone()

            if user:
                session['usuario'] = user.Nombre_Usuario  # Asignar correctamente
                session['rol'] = user.Rol

                if user.Rol == 'cliente':
                    return redirect('/cliente')
                elif user.Rol == 'admin':
                    return redirect('/admin')
                elif user.Rol == 'mesero':
                    return redirect('/mesero')
                elif user.Rol == 'invitado':
                    return redirect('/invitado')
            else:
                return "Credenciales incorrectas"

        except Exception as e:
            return f"Error en la consulta de usuario: {e}"

        #Cerrar la conexión con la bd
        finally:
            conn.close()

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


#Rutas de roles
@app.route('/cliente')
def cliente():
    if session.get('rol') == 'cliente':
        return render_template('principal.html')
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
