from app import db
from models import Rol, Usuario, Productor, TipoProductor, Cosecha
from app import Roles

# Crea la database y las tablas
db.create_all()

# Insertar roles
admin = Rol(name='Administrador')
analista = Rol(name='Analista de Ventas')
vendedor = Rol(name='Vendedor')
db.session.add(admin)
db.session.add(analista)
db.session.add(vendedor)

# Insertar cosechas
cosecha1 = Cosecha(date='Dic-Mar 2022')
cosecha2 = Cosecha(date='Jul-Ago 2022')
cosechas = [cosecha1, cosecha2]
db.session.add_all(cosechas)

# Insertar data (aquí se pueden agregar los administradores)
user1 = Usuario(nombre_usuario="admin", name="Administrador", apellido="Administrador", password="admin", rols=admin)
user2 = Usuario(nombre_usuario="user", name="Usuario", apellido="Usuario", password="user", rols=analista)
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
p1 = Productor(ci=12345678, name="Productor1", apellido="Productor1", telephone="0212-1234567", phone="0212-1234567", tipo_productor=prod1, direction1="Direccion1", direction2="Direccion2")
p2 = Productor(ci=87654321, name="Productor2", apellido="Productor2", telephone="0212-1234567", phone="0212-1234567", tipo_productor=prod2, direction1="Direccion1", direction2="Direccion2")
db.session.add_all([p1, p2])

# Guardar cambios en la database
db.session.commit()

