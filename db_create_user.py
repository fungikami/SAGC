from app import db
from app import User
from app import Roles

# Crea la database y las tablas
db.create_all()

# Insertar data (aquí se pueden agregar los administradores)
db.session.add(User(username="admin", name="Administrador", surname="Administrador", password="admin", rol=Roles.Administrador.value))

# Guardar cambios en la database
db.session.commit()