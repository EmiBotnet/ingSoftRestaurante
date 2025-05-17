import pyodbc

def test_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost;'
            'DATABASE=Restaurante_IS;'
            'Trusted_Connection=yes;'
        )
        print("✅ Conexión exitosa a la base de datos.")
        conn.close()
    except Exception as e:
        print("❌ Error al conectar a la base de datos:")
        print(e)

if __name__ == '__main__':
    test_connection()
