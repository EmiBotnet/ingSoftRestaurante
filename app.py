from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'clave_secreta123'  # Puedes cambiar esta clave por algo más fuerte

# Diccionario simulado de usuarios
usuarios = {
     'cliente1': {'password': '1234', 'rol': 'cliente'},
     'admin1': {'password': 'admin', 'rol': 'admin'},
     'cocinero1': {'password': 'cocina', 'rol': 'cocinero'}
 }


@app.route('/')
def index():
    return render_template('index.html') #Cargar login

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    password = request.form['password']

    #Buscar si el usuario existe
    if usuario in usuarios and usuarios[usuario]['password'] == password:
        session['usuario'] = usuario
        session['rol'] = usuarios[usuario]['rol']

        #Redireccionar a las vistas correspondientes
        if session['rol'] == 'cliente':
            return redirect('/cliente')
        elif session['rol'] == 'admin':
            return redirect('/admin')
        elif session['rol'] == 'cocinero':
            return redirect('/cocinero')
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

@app.route('/cocinero')
def cocinero():
    if session.get('rol') == 'cocinero':
        return render_template('cocinero.html')
    return "Acceso denegado"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)