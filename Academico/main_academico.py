# main.py es la VISTA: lo único que habla con el usuario (input/print).
# No valida ni guarda nada: le pide todo a los controladores de views.py
# y solo muestra lo que ellos responden.
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views_academico import EstudianteController, DocenteController, MateriaController, MatriculaController


class Menu:

    def __init__(self):
        # Se crea UN solo controlador de cada tipo.
        # A ventas se le pasan los MISMOS clientes y productos.
        self.estudiantes = EstudianteController()
        self.docentes = DocenteController()
        self.materias = MateriaController()
        self.matriculas = MatriculaController(self.estudiantes, self.materias)

    # ---------- ayudas ----------
    def pausa(self):
        input("\nPresione Enter para continuar...")

    def pedir_entero(self, texto):
        # Devuelve el número, o None si el usuario no escribió un número
        try:
            return int(input(texto))
        except ValueError:
            return None

    def mostrar_resultado(self, exito, mensaje):
        # Los controladores devuelven (exito, mensaje)
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)

    # ---------- menú principal ----------
    def ejecutar(self):
        while True:
            imprimir_titulo("SISTEMA DE VENTAS")
            print("  1. Estudiantes")
            print("  2. Docentes")
            print("  3. Materias")
            print("  0. Salir\n")
            opcion = input("Opción: ").strip()

            if opcion == "1":
                self.menu_crud(self.clientes)
            elif opcion == "2":
                self.menu_crud(self.productos)
            elif opcion == "3":
                self.menu_crud(self.ventas)
            elif opcion == "0":
                imprimir_info("¡Hasta luego! 👋")
                break
            else:
                imprimir_error("Opción no válida")
                self.pausa()

    # ---------- menú de cada controlador ----------
    # El mismo menú sirve para clientes, productos y ventas,
    # porque los tres controladores tienen los mismos métodos.
    def menu_crud(self, controlador):
        titulo = controlador.nombre.upper() + "S"     # CLIENTES, PRODUCTOS, VENTAS

        while True:
            imprimir_titulo(titulo)
            print(f"  1. Crear {controlador.nombre}")
            print("  2. Ver todos")
            print("  3. Buscar")
            print("  4. Ver por id")
            print("  5. Actualizar")
            print("  6. Eliminar")
            if controlador == self.ventas:
                print("  7. Ver factura")
            print("  0. Volver\n")
            opcion = input("Opción: ").strip()

            if opcion == "1":
                if controlador == self.ventas:
                    self.crear_venta()
                else:
                    self.crear(controlador)
            elif opcion == "2":
                self.ver_todos(controlador)
            elif opcion == "3":
                self.buscar(controlador)
            elif opcion == "4":
                self.ver_por_id(controlador)
            elif opcion == "5":
                self.actualizar(controlador)
            elif opcion == "6":
                self.eliminar(controlador)
            elif opcion == "7" and controlador == self.ventas:
                self.ver_factura()
            elif opcion == "0":
                break
            else:
                imprimir_error("Opción no válida")
                self.pausa()

    # ---------- operaciones ----------
    def crear(self, controlador):
        imprimir_titulo(f"CREAR {controlador.nombre.upper()}")
        # Se pregunta un dato por cada campo del modelo
        datos = {}
        for campo in controlador.campos:
            datos[campo] = input(f"{campo.capitalize()}: ")

        exito, mensaje = controlador.crear(datos)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def ver_todos(self, controlador):
        imprimir_titulo(controlador.nombre.upper() + "S")
        lista = controlador.leer()
        if len(lista) == 0:
            imprimir_info("No hay registros todavía.")
        else:
            for objeto in lista:
                print(f"  {objeto}")
            imprimir_info(f"Total: {len(lista)}")
        self.pausa()

    def buscar(self, controlador):
        imprimir_titulo(f"BUSCAR {controlador.nombre.upper()}")
        texto = input("Buscar: ")
        encontrados = controlador.buscar(texto)
        if len(encontrados) == 0:
            imprimir_info(f"Sin coincidencias para '{texto}'.")
        else:
            for objeto in encontrados:
                print(f"  {objeto}")
        self.pausa()

    def ver_por_id(self, controlador):
        imprimir_titulo(f"VER {controlador.nombre.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error("No encontrado")
        else:
            for clave, valor in objeto.a_diccionario().items():
                print(f"  {clave.capitalize()}: {valor}")
        self.pausa()

    def actualizar(self, controlador):
        imprimir_titulo(f"ACTUALIZAR {controlador.nombre.upper()}")
        if controlador == self.ventas:
            imprimir_error("Las ventas registradas no se pueden modificar")
            self.pausa()
            return

        id_registro = self.pedir_entero("Id: ")
        objeto = controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error("No encontrado")
            self.pausa()
            return

        imprimir_info(f"Editando: {objeto.etiqueta()}")
        print("Deje en blanco lo que no quiera cambiar.\n")
        cambios = {}
        for campo in controlador.campos:
            actual = getattr(objeto, campo)       # igual que objeto.nombre, objeto.email...
            nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
            if nuevo != "":
                cambios[campo] = nuevo

        exito, mensaje = controlador.actualizar(id_registro, cambios)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def eliminar(self, controlador):
        imprimir_titulo(f"ELIMINAR {controlador.nombre.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error("No encontrado")
            self.pausa()
            return

        imprimir_info(f"Se eliminará: {objeto.etiqueta()}")
        if confirmar("¿Confirma?"):
            exito, mensaje = controlador.eliminar(id_registro)
            self.mostrar_resultado(exito, mensaje)
        else:
            imprimir_info("Operación cancelada")
        self.pausa()

    # ---------- solo para ventas ----------
    def crear_venta(self):
        imprimir_titulo("REGISTRAR VENTA")
        cliente_id = self.pedir_entero("Id del cliente: ")
        if cliente_id is None:
            imprimir_error("El id debe ser un número")
            self.pausa()
            return

        imprimir_info("Productos disponibles:")
        for producto in self.productos.leer():
            print(f"  {producto}")

        # Se piden productos hasta que el usuario escriba 0
        items = []
        while True:
            producto_id = self.pedir_entero("\nId del producto (0 para terminar): ")
            if producto_id is None or producto_id == 0:
                break
            cantidad = self.pedir_entero("Cantidad: ")
            if cantidad is None or cantidad <= 0:
                imprimir_error("Cantidad inválida")
                continue
            items.append({"producto_id": producto_id, "cantidad": cantidad})

        exito, mensaje = self.ventas.crear({"cliente_id": cliente_id, "items": items})
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def ver_factura(self):
        imprimir_titulo("FACTURA")
        id_venta = self.pedir_entero("Id de la venta: ")
        texto = self.ventas.factura(id_venta)
        if texto is None:
            imprimir_error("No existe esa venta")
        else:
            print(texto)
        self.pausa()


# Solo arranca si se ejecuta "python main.py"
if __name__ == "__main__":
    try:
        Menu().ejecutar()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")