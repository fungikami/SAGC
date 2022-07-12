# Sistema Automatizado de Apoyo a la Gestión de Recolección de Cosechas de Cacao (SAGC)

## Plan de Entregas
### Iteración 0
1.Como Sistema, puedo Identificar a Usuarios para Controlar el Acceso No Autorizado al Sistema (Épica).
2.Como Analista de Compras, puedo Ingresar los datos de identificación de los Recolectores para Registrar a los recolectores de Cacao en Sistema.
(Épica).
3.Como Usuario, puedo Generar diferentes Cosechas al Sistema para Gestionar elPortafolio de Cosechas de una Empresa en Particular (Épica).
### Iteración 0
1. Como Sistema, puedo Identificar a Usuarios para Controlar el Acceso No Autorizado al Sistema (Épica).
a. Como Sistema, puedo Autenticar Usuarios para Controlar el Acceso No Autorizado al Sistema (INVEST).
b. Como Administrador, puedo Crear perfiles de Usuarios para Controlar de Acceso No Autorizado al Sistema (INVEST).
c. Como Administrador, puedo Ingresar Roles a los Usuarios para Controlar el Acceso No Autorizado al Sistema (INVEST).

Nota: 
- Autenticar Usuarios implica un algoritmo de encriptación
- Crear Perfiles implica Agregar, Buscar, Modificar, Pausar, Eliminar y Descargar datos de una Cosecha.
- Los roles son Administrador, Analista de Compras, Vendedor, etc.
### Iteración 1
2. Como Analista de Compras, puedo Ingresar los datos de identificación de los recolectores para Registrar a los recolectores de Cacao en
Sistema (Épica).
a. Como Analista de Compras, puedo Ingresar los datos personales de los recolectores para Registrar a los recolectores de Cacao en Sistema (INVEST).
b. Como Analista de Compras, puedo Ingresar los datos del Tipo de Recolector para Registrar a los recolectores de Cacao en Sistema (INVEST).

Nota: 
- Ingresar los datos personales implica Agregar, Buscar, Modificar y Eliminar.
- Los datos personales implican Cédula, Nombres, Apellidos, Teléfono Local, Teléfono Celular, localización (Dirección 1 y Dirección 2).
- Ingresar los datos del Tipo de Recolector implica Agregar, Buscar, Modificar y Eliminar.
- Los datos del Tipo de Recolector implican ID, Descripción y Precio (%), es utilizada para la clasificación de los recolectores tales como: Productor 1, Productor 2, Productor 3 así como Revendedor 1, Revendedor 2 y Revendedor 3, Mayorista 1,2 y3 (Esto es en cuanto al aporte de kilos).
### Iteración 2
3. Como Usuario, puedo Generar diferentes Cosechas al Sistema para Gestionar el Portafolio de Cosechas de una Empresa en Particular (Épica).
a. Como Administrador, puedo Ingresar los parámetros de la Cosecha al Sistema para Gestionar el Portafolio de Cosechas de una Empresa en Particular (INVEST).
b. Como Analista de Compras, puedo Generar Compras de una Cosecha especifica para Gestionar el Portafolio de Cosechas de una Empresa en Particular (INVEST).

Nota: 
- Los datos de las Cosechas son ID, Descripción, Inicio (Fecha) y Cierre (Fecha).
- Ingresar Cosecha implica Agregar, Buscar, Generar Compras, Modificar, Cerrar, Eliminar, Listar y Descargar Compras.
- Generar Compras garantiza que las compras de cacao se efectúan en el periodo de tiempo estipulado.
### Iteración 3
3. Como Usuario, puedo Generar diferentes Cosechas al Sistema para Gestionar el Portafolio de Cosechas de una Empresa en Particular (Épica).
c. Como Gerente o Analista de Compras, puedo Listar las Compras de una Cosecha especifica para Gestionar el Portafolio de Cosechas de una Empresa en Particular (INVEST).

4. Como Sistema, puedo Registrar los diferentes eventos del sistema en un Logger para Auditar el Sistema (INVEST). 
Nota: Registrar implica agregar, buscar y eliminar eventos. El Logger (bitácora) esta conformada por el Usuario que genero el evento, el evento, fecha, hora. Los eventos que se deben generar son agregar, buscar, modificar, eliminar, etc. En vista que los eventos del sistema ocurren en los diferentes módulos del sistema. El Logger (bitácora) de eventos debe agregarse en las líneas de código donde estas ocurren p. e. agregar, eliminar y modificar usuario.

## Ejecutar app
```
    pip install -r requirements.txt
    python3 db_create.py
    flask run
```

