from app import db
from models import *

# Crea la database y las tablas
db.create_all()

# Insertar roles
admin = Rol(nombre='Administrador')
analista = Rol(nombre='Analista de Ventas')
vendedor = Rol(nombre='Vendedor')
db.session.add(admin)
db.session.add(analista)
db.session.add(vendedor)

# Insertar cosechas
cosecha1 = Cosecha(date='Dic-Mar 2022')
cosecha2 = Cosecha(date='Jul-Ago 2022')
cosechas = [cosecha1, cosecha2]
db.session.add_all(cosechas)

# Insertar data (aquí se pueden agregar los administradores)
user1 = Usuario(nombre_usuario="admin", nombre="Administrador", apellido="Administrador", password="admin", rols=admin)
user2 = Usuario(nombre_usuario="user", nombre="Usuario", apellido="Usuario", password="user", rols=analista)
db.session.add(user1)
db.session.add(user2)
user1.cosechas.append(cosecha1)
user1.cosechas.append(cosecha2)
user2.cosechas.append(cosecha2)


prod1=TipoProductor(descripcion="Productor 1")
prod2=TipoProductor(descripcion="Productor 2")
prod3=TipoProductor(descripcion="Productor 3")
rev1=TipoProductor(descripcion="Revendedor 1")
db.session.add_all([prod1, prod2, prod3, rev1])
                                                                                                        # tipo_productor debe ser un objeto de la clase TypeProductor
p1 = Productor(ci="V-12345678", nombre="Productor1", apellido="Productor1", telefono="0212-1234567", celular="0212-1234567", tipo_productor=prod1, direccion1="Direccion1", direccion2="Direccion2")
p2 = Productor(ci="E-87654321", nombre="Productor2", apellido="Productor2", telefono="0212-1234567", celular="0212-1234567", tipo_productor=prod2, direccion1="Direccion1", direccion2="Direccion2")
db.session.add_all([p1, p2])

# Guardar cambios en la database
db.session.commit()

