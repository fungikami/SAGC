from curses.ascii import isdigit
from re import L
from roles import Roles
# Verificadores de los distintos registros de la base de datos

def verificar_perfil(form, Usuario, user_to_modify=None):
    error = None
    nombre_usuario = form['nombre_usuario']
    nombre = form['nombre']
    apellido = form['apellido']
    password = form['password']
    rol = form['rol']
    cosecha = form['cosecha']

    # Verificar que los campos estén llenos
    if nombre_usuario == '' or nombre == '' or apellido == '' or password == '' or rol == '':
        error = 'Todos los campos son obligatorios.'
        return error

    # USUARIO
    # Verificar que la longitud del nombre_usuario sea menor a 20
    if len(nombre_usuario) > 20:
        error = 'El nombre de usuario no puede tener mas de 20 caracteres.'
        return error

    # Verificar que el usuario no existe
    usernamedb = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
    
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

    if len(cosecha) > 0 and cosecha.lower() != 'ninguna':
        date =  cosecha.split('-')
        if len(date) != 2:
            error = 'La fecha de cosecha debe tener el formato mm-mm aaaa'
            return error
        date += date[1].split(' ')
        date.pop(1)
        validDates = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
        if date[0].lower() not in validDates or date[1].lower() not in validDates or not date[2].isdigit():
            error = 'La fecha de cosecha no es válida.'
            return error
        
    
    # Verificar que el email no existe
    # user = Usuario.query.filter_by(email=email).first()
    # if user is not None:
    #     flash('El email ya está registrado.')
    #     return redirect(url_for('perfiles'))
    return error

# Función para verificar los tipos de productores
def verificar_tipo_productor(form, TipoProductor):
    error = None
    descripcion = form['descripcion']

    # Verificar que los campos estén llenos
    if descripcion == '':
        error = 'Todos los campos son obligatorios.'
        return error

    # Verificar que sea unico
    typedb = TipoProductor.query.filter_by(descripcion=descripcion).first()
    if typedb is not None:
        error = 'El tipo de productor ya se encuentra definido.'
        return error

    return error

# Función para verificar los productores
def verificar_productor(form, Productor, producer_to_modify=None):
    error = None
    ci = form['cedula']
    nombre = form['nombre']
    apellido = form['apellido']
    telefono = form['telefono']
    celular = form['celular']
    dir1 = form['direccion1']
    dir2 = form['direccion2']
    rol = form['rol']  

    list = [ci, nombre, apellido, telefono, celular, rol]

    # Verificar que los campos estén llenos
    if not any(list):
        error = 'Todos los campos son obligatorios.'
        return error

    # USUARIO
    # Verificar que la cédula esté en formato válido

    # Verificar que la cedula no exista
    ci_db = Productor.query.filter_by(ci=ci).first()
    if ci_db is not None and producer_to_modify!=ci_db:
        error = 'El productor con dicha cedula ya se encuentra registrado.'
        return error

    # Verificar que la longitud del username sea menor a 20
    if len(nombre) > 20 or len(apellido) > 20:
        error = 'El nombre y apellido no puede tener mas de 20 caracteres.'
        return error

    return error