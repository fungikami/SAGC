# Verificadores de los distintos registros de la base de datos

# Verificador del perfil de usuario
def verificar_perfil(form, Usuario, user_to_modify=None):
    error = None
    nombre_usuario = form['nombre_usuario']
    nombre = form['nombre']
    apellido = form['apellido']
    rol = form['rol']
    cosecha = form['cosecha']
    password = None
    if user_to_modify is None:
        password = form['password']

    # Verificar que los campos estén llenos
    if nombre_usuario == '' or nombre == '' or apellido == '' or password == '' or rol == '':
        return 'Todos los campos son obligatorios.'

    # USUARIO
    error = verificar_nombre_usuario(nombre_usuario, Usuario, user_to_modify)
    if error is not None:
        return error

    # CONTRASEÑA
    if user_to_modify is None:
        error = verificar_contrasena(password)
        if error is not None:
            return error

    # NOMBRE Y APELLIDO
    error = verificar_nombre_apellido(nombre, apellido)
    if error is not None:
        return error

    # ROL
    return verificar_rol(rol)     

# Función para verificar los tipos de recolectores
def verificar_tipo_recolector(form, TipoRecolector, tipo_to_modify=None):
    error = None
    descripcion = form['descripcion']

    # Verificar que los campos estén llenos
    if descripcion == '':
        return 'Todos los campos son obligatorios.'

    # Verificar que sea unico
    typedb = TipoRecolector.query.filter_by(descripcion=descripcion).first()
    if typedb is not None and tipo_to_modify != typedb:
        return 'El tipo de recolector ya se encuentra definido.'

    return error

# Función para verificar los recolectores
def verificar_recolector(form, Recolector, producer_to_modify=None):
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

    # Verificar que la cedula no exista
    ci_db = Recolector.query.filter_by(ci=ci).first()
    if ci_db is not None and producer_to_modify!=ci_db:
        error = 'El recolector con dicha cedula ya se encuentra registrado.'
        return error

    # Verifica nombre y apellido
    error = verificar_nombre_apellido(nombre, apellido)

    return error

# Verifica el username
def verificar_nombre_usuario(nombre_usuario, Usuario, user_to_modify=None):
    error = None

    # Verificar que la longitud del nombre_usuario sea menor a 20
    if len(nombre_usuario) > 20:
        return 'El nombre de usuario no puede tener mas de 20 caracteres.'

    # Verificar que el usuario no existe
    usernamedb = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
    if usernamedb is not None and user_to_modify != usernamedb:
        return 'El nombre de usuario ya se encuentra en uso.'
    
    return error

# Verificar contraseña
def verificar_contrasena(password):
    error = None

    # Verificar longitud de la contraseña
    if len(password) < 8:
        return 'La contraseña debe tener al menos 8 caracteres.'

    if len(password) > 80:
        return 'La contraseña no puede tener mas de 80 caracteres.'

    # Verificar que haya al menos una letra mayúscula
    if password.islower():
        return 'La contraseña debe contener al menos una letra mayúscula.'

    # Verificar que haya al menos un numero
    if all(not char.isdigit() for char in password):
        return 'La contraseña debe contener almenos un número.'

    # Verificar simbolos especiales
    # especialSymbols = ['!', '@', '#', '$', '%', '&', '*', '_', '+', '-', '=', '?'] # por si se necesitan mas
    especialSymbols = ['@','*','.','-']
    if all(not char in especialSymbols for char in password):
        return 'La contraseña debe contener almenos uno de los siguientes símbolos especiales "@","*",".","-"'

    return error

# Verifica que el nombre y apellido sean correctos
def verificar_nombre_apellido(nombre, apellido):
    error = None

    # Verificar longitud de los nombres y apellidos
    if len(nombre) > 20 or len(apellido) > 20:
        return 'El nombre y apellido no puede tener mas de 20 caracteres.'

    return error

# Verificar que el rol sea correcto
def verificar_rol(rol):
    error = None
    if rol not in ['1', '2', '3']:
       return 'El rol debe ser Administrador, Analista de Ventas o Vendedor.'
    return error

# Verificar que la cosecha sea correcta
def verificar_cosecha(form, Cosecha, cosecha_to_modify=None):
    error = None

    # Verificar la descripción de la cosecha no exista
    descripcion = form['descripcion']
    cosechadb = Cosecha.query.filter_by(descripcion=descripcion).first()
    if cosechadb is not None and cosecha_to_modify != cosechadb:
        return 'La cosecha que se intenta agregar ya se encuentra definida.'
    
    # Verificar que la fecha de inicio sea menor que la de cierre
    yi, mi, di = form['inicio'].split('-')
    yc, mc, dc = form['cierre'].split('-')

    if (int(yi) > int(yc) or (int(yi) == int(yc) and int(mi) > int(mc)) or 
        (int(yi) == int(yc) and int(mi) == int(mc) and int(di) > int(dc))):
        return 'La fecha de cierre debe ser posterior a la fecha de inicio.'

    return error

# Verificar que la cosecha exista en la base de datos o esté habilitada
def verificar_cosecha_exists(id, tipo, cosecha):
    error = None
    if cosecha is None or (not cosecha.estado and tipo=='compras'):
        error = "La cosecha no está habilitada"
        if cosecha is None:
            return "La cosecha no se encuentra registrada. Registre la cosecha antes de realiza la compra."
    return error

