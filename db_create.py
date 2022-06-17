from app import db
from models import User, Productor, TypeProductor
from app import Roles

# Crea la database y las tablas
db.create_all()

# Insertar data (aquí se pueden agregar los administradores)
db.session.add(User(username="admin", name="Administrador", surname="Administrador", password="admin", rol=Roles.Administrador.name))
db.session.add(User(username="user", name="Usuario", surname="Usuario", password="user", rol="Analista de Ventas"))

prod1=TypeProductor(description="Productor1")
db.session.add(prod1)
prod2=TypeProductor(description="Productor2")
db.session.add(prod2)

db.session.add(Productor(ci=1234567, name="Productor 1", surname="Productor 1", telephone="0212-1234567", 
                phone="0212-1234567", type_prod="Productor1", direction1="Dirección 1", direction2="Dirección 2"))
db.session.add(Productor(ci=2345678, name="Productor 2", surname="Productor 2", telephone="0212-1234567", 
                phone="0212-1234567", type_prod="Productor2", direction1="Dirección 1", direction2="Dirección 2"))

# Guardar cambios en la database
db.session.commit()

