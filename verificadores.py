from curses.ascii import isdigit
from re import L
from roles import Roles
# Verificadores de los distintos registros de la base de datos

def verificar_perfil(form, User, user_to_modify=None):
    error = None
    username = form['username']
    name = form['name']
    surname = form['surname']
    password = form['password']
    rol = form['rol']
    cosechas = form['cosechas']

    # Verificar que los campos estén llenos
    if username == '' or name == '' or surname == '' or password == '' or rol == '':
        error = 'Todos los campos son obligatorios.'
        return error

    # USUARIO
    # Verificar que la longitud del username sea menor a 20
    if len(username) > 20:
        error = 'El nombre de usuario no puede tener mas de 20 caracteres.'
        return error

    # Verificar que el usuario no existe
    usernamedb = User.query.filter_by(username=username).first()
    
    if usernamedb is not None and user_to_modify != usernamedb:
        error = 'El nombre de usuario ya se encuentra en uso.'
        return error

    # CONTRASEÑA
    # Verificar longitud de la contraseña
    if len(password) < 8:
        error = 'La contraseña debe tener al menos 8 caracteres.'
        return error

    if len(password) > 80:
        error = 'La contraseña no puede tener mas de 80 caracteres.'
        return error

    # Verificar que haya al menos una letra mayúscula
    if password.islower():
        error = 'La contraseña debe contener al menos una letra mayúscula.'
        return error

    # Verificar que haya al menos un numero
    if all(not char.isdigit() for char in password):
        error = 'La contraseña debe contener almenos un número.'
        return error

    # Verificar simbolos especiales
    # especialSymbols = ['!', '@', '#', '$', '%', '&', '*', '_', '+', '-', '=', '?'] # por si se necesitan mas
    especialSymbols = ['@','*','.','-']
    if all(not char in especialSymbols for char in password):
        error = 'La contraseña debe contener almenos uno de los siguientes símbolos especiales "@","*",".","-"'
        return error

    # Verificar que sea algún rol válido
    if rol not in ['1', '2', '3']:
       error = 'El rol debe ser Administrador, Analista de Ventas o Vendedor.'
       return error

    date =  cosechas.split('-')
    date += date[1].split(' ')
    date.pop(1)
    validDates = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    if date[0].lower() not in validDates or date[1].lower() not in validDates or not date[2].isdigit():
        error = 'La fecha de cosecha no es válida.'
        return error
        
    
    # Verificar que el email no existe
    # user = User.query.filter_by(email=email).first()
    # if user is not None:
    #     flash('El email ya está registrado.')
    #     return redirect(url_for('perfiles'))
    return error

# Función para verificar los tipos de productores
def verificar_tipo_productor(form, TypeProducer):
    error = None
    description = form['description']

    # Verificar que los campos estén llenos
    if description == '':
        error = 'Todos los campos son obligatorios.'
        return error

    # Verificar que sea unico
    typedb = TypeProducer.query.filter_by(description=description).first()
    if typedb is not None:
        error = 'El tipo de productor ya se encuentra definido.'
        return error

    return error

# Función para verificar los productores
def verificar_productor(form, Producer, producer_to_modify=None):
    error = None
    ci = form['cedula']
    name = form['name']
    surname = form['surname']
    telephone = form['telephone']
    phone = form['phone']
    dir1 = form['direction1']
    dir2 = form['direction2']
    rol = form['rol']  

    list = [ci, name, surname, telephone, phone, rol]

    # Verificar que los campos estén llenos
    if not any(list):
        error = 'Todos los campos son obligatorios.'
        return error

    # USUARIO
    # Verificar que la longitud del username sea menor a 20
    if len(name) > 20:
        error = 'El nombre no puede tener mas de 20 caracteres.'
        return error

    # Verificar que la cedula no exista
    ci_db = Producer.query.filter_by(ci=ci).first()
    if ci_db is not None and producer_to_modify!=ci_db:
        error = 'El productor con dicha cedula ya se encuentra registrado.'
        return error

    return error