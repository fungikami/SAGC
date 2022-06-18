from curses.ascii import isdigit
from re import L
from roles import Roles
# Verificadores de los distintos registros de la base de datos

def verificar_perfil(form, User, user_to_modify=None):
    error = None

    print(form)
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