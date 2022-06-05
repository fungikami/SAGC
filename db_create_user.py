from app import db
from app import User 

# Crea la database y las tablas
db.create_all()

# Insertar data (aquí se pueden agregar los administradores)
db.session.add(User("admin", "ad@min.com", "admin"))

# Guardar cambios en la database
db.session.commit()