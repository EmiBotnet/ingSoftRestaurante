import pyodbc

try:
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=Restaurante_IS;'
        'Trusted_Connection=yes;'
    )
    print("Conexión establecida")

    cursor = conn.cursor()
    print("Cursor creado:", cursor)
    
    # Ejecutar consulta a la tabla Platillos
    cursor.execute("SELECT Id_platillo, Nom_platillo, Precio, Descripcion, Foto_platillo, Is_Available FROM Platillos")
    
    platillos = cursor.fetchall()
    print(f"Cantidad de platillos obtenidos: {len(platillos)}")
    
    for p in platillos:
        print(p)

    conn.close()

except Exception as e:
    print("Error:", e)

