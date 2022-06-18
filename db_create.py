from app import db
from models import Rol, User, Productor, TypeProductor, Cosecha
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
user1 = User(username="admin", name="Administrador", surname="Administrador", password="admin", rols=admin)
user2 = User(username="user", name="Usuario", surname="Usuario", password="user", rols=analista)
db.session.add(user1)
db.session.add(user2)
user1.cosechas.append(cosecha1)
user1.cosechas.append(cosecha2)
user2.cosechas.append(cosecha2)


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

