from flask import Flask, render_template, request, redirect, url_for, session
import json
import pyodbc  # Necesario para conectar a SQL Server

# Usar comando "python app.py" para inicializar el servidor

app = Flask(__name__)
app.secret_key = 'clave_secreta123'  # Cambia esta clave en producción

# Función para conectar a la base de datos (NO TOCAR)
def get_db_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=Restaurante_IS;'
        'Trusted_Connection=yes;'
    )


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Nombre_Usuario, Contrasena, Rol
        FROM Usuarios
        WHERE Nombre_Usuario = ? AND Contrasena = ?
    """, (usuario, password))

    user = cursor.fetchone()
    conn.close()

    if user:
        session['usuario'] = user.Nombre_Usuario
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

@app.route('/cliente')
def cliente():
    if session.get('rol') == 'cliente':
        return render_template('cliente.html')
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

@app.route('/invitado')
def invitado():
    if session.get('rol') == 'invitado':
        with open('static/json/menu.json', 'r', encoding='utf-8') as archivo:
            platillos = json.load(archivo)
        return render_template('principal.html', menu=platillos)
    return "Acceso denegado"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
