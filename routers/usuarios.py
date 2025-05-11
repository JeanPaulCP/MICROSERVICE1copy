from fastapi import APIRouter, HTTPException
from typing import List
from .. import schemas, database

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=schemas.Usuario)
def crear_usuario(usuario: schemas.UsuarioCreate):
    conn = database.get_connection()
    cursor = conn.cursor()

    # Insertar o verificar roles
    roles_ids = []
    for rol in usuario.roles:
        cursor.execute("SELECT id_rol FROM roles WHERE nombre_rol = %s", (rol.nombre_rol,))
        resultado = cursor.fetchone()
        if resultado:
            id_rol = resultado[0]
        else:
            cursor.execute("INSERT INTO roles (nombre_rol) VALUES (%s)", (rol.nombre_rol,))
            conn.commit()
            id_rol = cursor.lastrowid
        roles_ids.append({"id_rol": id_rol, "nombre_rol": rol.nombre_rol})

    # Insertar usuario
    cursor.execute(
        "INSERT INTO usuarios (nombre, apellido, correo, fecha_registro) VALUES (%s, %s, %s, %s)",
        (usuario.nombre, usuario.apellido, usuario.correo, usuario.fecha_registro)
    )
    id_usuario = cursor.lastrowid

    # Insertar en tabla intermedia
    for rol in roles_ids:
        cursor.execute("INSERT INTO usuario_rol (id_usuario, id_rol) VALUES (%s, %s)", (id_usuario, rol["id_rol"]))

    conn.commit()
    conn.close()

    return schemas.Usuario(
        id_usuario=id_usuario,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        fecha_registro=usuario.fecha_registro,
        roles=[schemas.Rol(**rol) for rol in roles_ids]
    )

@router.get("/", response_model=List[schemas.Usuario])
def listar_usuarios():
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios")
    usuarios_raw = cursor.fetchall()

    usuarios = []
    for usuario in usuarios_raw:
        # Buscar roles de ese usuario
        cursor.execute("""
            SELECT r.id_rol, r.nombre_rol
            FROM roles r
            JOIN usuario_rol ur ON r.id_rol = ur.id_rol
            WHERE ur.id_usuario = %s
        """, (usuario["id_usuario"],))
        roles = cursor.fetchall()
        usuarios.append(schemas.Usuario(**usuario, roles=roles))

    conn.close()
    return usuarios

@router.get("/{id_usuario}", response_model=schemas.Usuario)
def obtener_usuario(id_usuario: int):
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    usuario = cursor.fetchone()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cursor.execute("""
        SELECT r.id_rol, r.nombre_rol
        FROM roles r
        JOIN usuario_rol ur ON r.id_rol = ur.id_rol
        WHERE ur.id_usuario = %s
    """, (id_usuario,))
    roles = cursor.fetchall()

    conn.close()
    return schemas.Usuario(**usuario, roles=roles)

@router.put("/{id_usuario}", response_model=schemas.Usuario)
def actualizar_usuario(id_usuario: int, usuario_actualizado: schemas.UsuarioCreate):
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verificar existencia
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar campos
    cursor.execute("""
        UPDATE usuarios SET nombre = %s, apellido = %s, correo = %s, fecha_registro = %s
        WHERE id_usuario = %s
    """, (
        usuario_actualizado.nombre,
        usuario_actualizado.apellido,
        usuario_actualizado.correo,
        usuario_actualizado.fecha_registro,
        id_usuario
    ))

    # Borrar roles antiguos
    cursor.execute("DELETE FROM usuario_rol WHERE id_usuario = %s", (id_usuario,))

    # Insertar o crear nuevos roles
    roles_actualizados = []
    for rol in usuario_actualizado.roles:
        cursor.execute("SELECT id_rol FROM roles WHERE nombre_rol = %s", (rol.nombre_rol,))
        result = cursor.fetchone()
        if result:
            id_rol = result["id_rol"]
        else:
            cursor.execute("INSERT INTO roles (nombre_rol) VALUES (%s)", (rol.nombre_rol,))
            conn.commit()
            id_rol = cursor.lastrowid
        cursor.execute("INSERT INTO usuario_rol (id_usuario, id_rol) VALUES (%s, %s)", (id_usuario, id_rol))
        roles_actualizados.append({"id_rol": id_rol, "nombre_rol": rol.nombre_rol})

    conn.commit()
    conn.close()

    return schemas.Usuario(
        id_usuario=id_usuario,
        nombre=usuario_actualizado.nombre,
        apellido=usuario_actualizado.apellido,
        correo=usuario_actualizado.correo,
        fecha_registro=usuario_actualizado.fecha_registro,
        roles=[schemas.Rol(**rol) for rol in roles_actualizados]
    )

@router.delete("/{id_usuario}")
def eliminar_usuario(id_usuario: int):
    conn = database.get_connection()
    cursor = conn.cursor()

    # Verificar existencia
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Eliminar relaciones
    cursor.execute("DELETE FROM usuario_rol WHERE id_usuario = %s", (id_usuario,))
    cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))

    conn.commit()
    conn.close()

    return {"mensaje": "Usuario eliminado exitosamente"}
