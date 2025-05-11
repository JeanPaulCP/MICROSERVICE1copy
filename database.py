import mysql.connector

DB_HOST = "34.203.234.168"
DB_PORT = 8005
DB_USER = "root"
DB_PASSWORD = "utecmysql"
DB_NAME = "usuariosdb"

# docker run -d --rm --name mysql_c --network red_bd_mysql -e MYSQL_ROOT_PASSWORD=utecmysql -p 8005:3306 -v mysql_data:/var/lib/mysql mysql:8.0

# Función para obtener conexión
def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
