from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import ClienteController, ProductoController, VentaController


# =====================================================================
# POLIMORFISMO: un solo menú sirve para cualquier controlador
# =====================================================================
class MenuCRUD:
    """No sabe si maneja clientes o productos: solo habla con la interfaz CrudBase."""

    def __init__(self, controlador, titulo):
        self._controlador = controlador
        self._titulo = titulo
        self._activo = True
        self._opciones = {
            "1": (f"Crear {controlador.NOMBRE}", self.crear),
            "2": ("Ver todos", self.listar),
            "3": ("Buscar", self.buscar),
            "4": ("Ver por id", self.ver_por_id),
            "5": ("Actualizar", self.actualizar),
            "6": ("Eliminar", self.eliminar),
            "0": ("Volver", self.volver),
        }

    # ---------- utilidades estáticas ----------
    @staticmethod
    def pausa():
        input("\nPresione Enter para continuar...")

    @staticmethod
    def pedir_entero(etiqueta):
        try:
            return int(input(etiqueta))
        except ValueError:
            return None

    @staticmethod
    def mostrar_resultado(exito, mensaje):
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)

    # ---------- operaciones ----------
    def pedir_datos(self):
        datos = {}
        for campo in self._controlador.MODELO.CAMPOS:
            datos[campo] = input(f"{campo.replace('_', ' ').capitalize()}: ")
        return datos

    def crear(self):
        imprimir_titulo(f"CREAR {self._controlador.NOMBRE.upper()}")
        self.mostrar_resultado(*self._controlador.crear(self.pedir_datos()))
        self.pausa()

    def listar(self):
        imprimir_titulo(self._titulo.upper())
        objetos = self._controlador.listar()
        if not objetos:
            imprimir_info("No hay registros todavía.")
        else:
            for objeto in objetos:
                print(f"  {objeto}")        # usa __str__ -> etiqueta() de cada modelo
            imprimir_info(f"Total: {len(objetos)}")
        self.pausa()

    def buscar(self):
        imprimir_titulo(f"BUSCAR {self._controlador.NOMBRE.upper()}")
        termino = input("Término: ")
        encontrados = self._controlador.buscar(termino)
        if not encontrados:
            imprimir_info(f"Sin coincidencias para '{termino}'.")
        else:
            for objeto in encontrados:
                print(f"  {objeto}")
        self.pausa()

    def ver_por_id(self):
        imprimir_titulo(f"VER {self._controlador.NOMBRE.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = self._controlador.obtener(id_registro) if id_registro else None
        if objeto is None:
            imprimir_error("No encontrado")
        else:
            for clave, valor in objeto.a_diccionario().items():
                print(f"  {str(clave).capitalize():<14}: {valor}")
        self.pausa()

    def actualizar(self):
        imprimir_titulo(f"ACTUALIZAR {self._controlador.NOMBRE.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = self._controlador.obtener(id_registro) if id_registro else None
        if objeto is None:
            imprimir_error("No encontrado")
            return self.pausa()

        imprimir_info(f"Editando: {objeto.etiqueta()}")
        print("Deje en blanco lo que no quiera cambiar.\n")
        cambios = {}
        for campo in self._controlador.MODELO.CAMPOS:
            actual = getattr(objeto, campo, "")
            nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
            if nuevo:
                cambios[campo] = nuevo

        self.mostrar_resultado(*self._controlador.actualizar(id_registro, cambios))
        self.pausa()

    def eliminar(self):
        imprimir_titulo(f"ELIMINAR {self._controlador.NOMBRE.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = self._controlador.obtener(id_registro) if id_registro else None
        if objeto is None:
            imprimir_error("No encontrado")
            return self.pausa()

        imprimir_info(f"Se eliminará: {objeto.etiqueta()}")
        if confirmar("¿Confirma?"):
            self.mostrar_resultado(*self._controlador.eliminar(id_registro))
        else:
            imprimir_info("Operación cancelada")
        self.pausa()

    def volver(self):
        self._activo = False

    # ---------- bucle ----------
    def mostrar_menu(self):
        imprimir_titulo(self._titulo)
        for tecla, (texto, _metodo) in self._opciones.items():
            print(f"  {tecla}. {texto}")
        print()

    def ejecutar(self):
        self._activo = True
        while self._activo:
            self.mostrar_menu()
            tecla = input("Opción: ").strip()
            if tecla not in self._opciones:
                imprimir_error("Opción no válida")
                self.pausa()
                continue
            self._opciones[tecla][1]()


# =====================================================================
# HERENCIA + SOBRESCRITURA: el menú de ventas es un MenuCRUD con extras
# =====================================================================
class MenuVentas(MenuCRUD):

    def __init__(self, controlador):
        super().__init__(controlador, "VENTAS")
        self._opciones["1"] = ("Registrar venta", self.crear)
        self._opciones["7"] = ("Ver factura", self.ver_factura)

    def crear(self):
        """Sobrescribe: una venta necesita cliente + varios productos."""
        imprimir_titulo("REGISTRAR VENTA")
        cliente_id = self.pedir_entero("Id del cliente: ")
        if cliente_id is None:
            imprimir_error("El id debe ser un número")
            return self.pausa()

        imprimir_info("Productos disponibles:")
        for producto in self._controlador.productos.listar():
            print(f"  {producto}")

        items = []
        while True:
            producto_id = self.pedir_entero("\nId del producto (0 para terminar): ")
            if not producto_id:
                break
            cantidad = self.pedir_entero("Cantidad: ")
            if not cantidad:
                imprimir_error("Cantidad inválida")
                continue
            items.append({"producto_id": producto_id, "cantidad": cantidad})

        self.mostrar_resultado(
            *self._controlador.crear({"cliente_id": cliente_id, "items": items})
        )
        self.pausa()

    def ver_factura(self):
        imprimir_titulo("FACTURA")
        id_venta = self.pedir_entero("Id de la venta: ")
        texto = self._controlador.factura(id_venta) if id_venta else None
        if texto is None:
            imprimir_error("No existe esa venta")
        else:
            print(texto)
        self.pausa()


# =====================================================================
class MenuPrincipal:

    def __init__(self):
        clientes = ClienteController()
        productos = ProductoController()
        ventas = VentaController(clientes, productos)

        self._activo = True
        # DICCIONARIO de menús: el mismo MenuCRUD con distinto controlador
        self._menus = {
            "1": MenuCRUD(clientes, "CLIENTES"),
            "2": MenuCRUD(productos, "PRODUCTOS"),
            "3": MenuVentas(ventas),
        }

    def ejecutar(self):
        while self._activo:
            imprimir_titulo("SISTEMA DE VENTAS")
            print("  1. Clientes")
            print("  2. Productos")
            print("  3. Ventas")
            print("  0. Salir\n")
            tecla = input("Opción: ").strip()

            if tecla == "0":
                imprimir_info("¡Hasta luego! 👋")
                self._activo = False
            elif tecla in self._menus:
                self._menus[tecla].ejecutar()
            else:
                imprimir_error("Opción no válida")
                MenuCRUD.pausa()


if __name__ == "__main__":
    try:
        MenuPrincipal().ejecutar()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")