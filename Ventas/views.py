from abc import ABC, abstractmethod

from models import Cliente, Producto, Venta, Proveedor, Compra
from shared.json_manager import GestorJSON


# =====================================================================
# CLASE BASE (ABSTRACTA)
# =====================================================================
# Solo dice QUÉ métodos debe tener todo controlador.
# CÓMO se hace cada uno lo escribe cada controlador con su propio modelo.
class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =====================================================================
# CONTROLADOR DE CLIENTES
# =====================================================================
class ClienteController(CrudBase):

    def __init__(self, archivo="data/clientes.json"):
        self.nombre = "cliente"            # se usa en los títulos del menú
        self.campos = Cliente.CAMPOS       # campos que el menú le pide al usuario
        self.gestor = GestorJSON(archivo)

        # Leemos el JSON y convertimos cada diccionario en un objeto Cliente
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Cliente.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for cliente in self.lista:
            datos.append(cliente.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_cliente):
        for cliente in self.lista:
            if cliente.id == id_cliente:
                return cliente
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for cliente in self.lista:
            if (texto in cliente.nombre.lower()
                    or texto in cliente.apellido.lower()
                    or texto in cliente.email
                    or texto in cliente.telefono
                    or texto in cliente.ciudad.lower()):
                encontrados.append(cliente)
        return encontrados

    def siguiente(self):
        mayor = 0
        for cliente in self.lista:
            if cliente.id > mayor:
                mayor = cliente.id
        return mayor + 1

    def crear(self, datos):
        # No puede haber dos clientes con el mismo email
        email = str(datos.get("email", "")).strip().lower()
        for cliente in self.lista:
            if cliente.email == email:
                return False, "Ese email ya está registrado"

        # Si algún dato está mal, el modelo lanza ValueError
        try:
            cliente = Cliente(self.siguiente(),
                              datos.get("nombre", ""),
                              datos.get("apellido", ""),
                              datos.get("email", ""),
                              datos.get("telefono", ""),
                              datos.get("ciudad", ""))
        except ValueError as error:
            return False, str(error)

        self.lista.append(cliente)
        self.guardar()
        return True, f"Cliente creado: {cliente.etiqueta()}"

    def actualizar(self, id_cliente, datos):
        if not datos:
            return False, "No se indicó ningún cambio"

        cliente = self.obtener(id_cliente)
        if cliente is None:
            return False, f"No existe cliente con id {id_cliente}"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            for otro in self.lista:
                if otro.email == email and otro.id != id_cliente:
                    return False, "Ese email ya está registrado"

        # Creamos un cliente nuevo con los cambios. Si algo falla,
        # el cliente viejo queda igual.
        try:
            nuevo = Cliente(cliente.id,
                            datos.get("nombre", cliente.nombre),
                            datos.get("apellido", cliente.apellido),
                            datos.get("email", cliente.email),
                            datos.get("telefono", cliente.telefono),
                            datos.get("ciudad", cliente.ciudad))
        except ValueError as error:
            return False, str(error)

        posicion = self.lista.index(cliente)
        self.lista[posicion] = nuevo
        self.guardar()
        return True, f"Cliente {id_cliente} actualizado"

    def eliminar(self, id_cliente):
        cliente = self.obtener(id_cliente)
        if cliente is None:
            return False, f"No existe cliente con id {id_cliente}"

        self.lista.remove(cliente)
        self.guardar()
        return True, f"Cliente {id_cliente} eliminado"


# =====================================================================
# CONTROLADOR DE PRODUCTOS
# =====================================================================
class ProductoController(CrudBase):

    def __init__(self, archivo="data/productos.json"):
        self.nombre = "producto"
        self.campos = Producto.CAMPOS
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Producto.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for producto in self.lista:
            datos.append(producto.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_producto):
        for producto in self.lista:
            if producto.id == id_producto:
                return producto
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for producto in self.lista:
            if texto in producto.nombre.lower():
                encontrados.append(producto)
        return encontrados

    def siguiente(self):
        mayor = 0
        for producto in self.lista:
            if producto.id > mayor:
                mayor = producto.id
        return mayor + 1

    def crear(self, datos):
        # El modelo guarda los nombres con .title(), así que comparamos igual
        nombre = str(datos.get("nombre", "")).strip().title()
        for producto in self.lista:
            if producto.nombre == nombre:
                return False, f"Ya existe un producto llamado {nombre}"

        # Si no escribieron el stock, empieza en 0
        stock = datos.get("stock", "")
        if str(stock).strip() == "":
            stock = 0

        try:
            producto = Producto(self.siguiente(), nombre, datos.get("precio", ""), stock)
        except ValueError as error:
            return False, str(error)

        self.lista.append(producto)
        self.guardar()
        return True, f"Producto creado: {producto.etiqueta()}"

    def actualizar(self, id_producto, datos):
        if not datos:
            return False, "No se indicó ningún cambio"

        producto = self.obtener(id_producto)
        if producto is None:
            return False, f"No existe producto con id {id_producto}"

        if "nombre" in datos:
            nombre = str(datos["nombre"]).strip().title()
            for otro in self.lista:
                if otro.nombre == nombre and otro.id != id_producto:
                    return False, f"Ya existe un producto llamado {nombre}"

        try:
            nuevo = Producto(producto.id,
                             datos.get("nombre", producto.nombre),
                             datos.get("precio", producto.precio),
                             datos.get("stock", producto.stock))
        except ValueError as error:
            return False, str(error)

        posicion = self.lista.index(producto)
        self.lista[posicion] = nuevo
        self.guardar()
        return True, f"Producto {id_producto} actualizado"

    def eliminar(self, id_producto):
        producto = self.obtener(id_producto)
        if producto is None:
            return False, f"No existe producto con id {id_producto}"

        self.lista.remove(producto)
        self.guardar()
        return True, f"Producto {id_producto} eliminado"

    # --- métodos propios de productos ---
    def descontar_stock(self, id_producto, cantidad):
        producto = self.obtener(id_producto)
        if producto is None:
            return False, f"No existe producto con id {id_producto}"
        try:
            producto.descontar_stock(cantidad)
        except ValueError as error:
            return False, str(error)
        self.guardar()
        return True, f"Stock de {producto.nombre}: quedan {producto.stock}"

    def con_stock_bajo(self, minimo=5):
        bajos = []
        for producto in self.lista:
            if producto.stock <= minimo:
                bajos.append(producto)
        return bajos


# =====================================================================
# CONTROLADOR DE VENTAS
# =====================================================================
class VentaController(CrudBase):

    def __init__(self, clientes, productos, archivo="data/ventas.json"):
        self.nombre = "venta"
        self.campos = Venta.CAMPOS
        self.gestor = GestorJSON(archivo)

        # La venta USA los controladores de clientes y productos.
        # Hay que pasarle los MISMOS que usa el menú.
        self.clientes = clientes
        self.productos = productos

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Venta.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for venta in self.lista:
            datos.append(venta.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_venta):
        for venta in self.lista:
            if venta.id == id_venta:
                return venta
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        # Las ventas se buscan por fecha, ej: "2026-10"
        texto = texto.strip()
        encontrados = []
        if texto == "":
            return encontrados

        for venta in self.lista:
            if texto in venta.fecha:
                encontrados.append(venta)
        return encontrados

    def siguiente(self):
        mayor = 0
        for venta in self.lista:
            if venta.id > mayor:
                mayor = venta.id
        return mayor + 1

    def crear(self, datos):
        # datos = {"cliente_id": 1, "items": [{"producto_id": 2, "cantidad": 3}, ...]}
        try:
            cliente_id = int(datos.get("cliente_id", 0))
        except (TypeError, ValueError):
            return False, "El cliente_id debe ser un número"

        if self.clientes.obtener(cliente_id) is None:
            return False, f"No existe un cliente con id {cliente_id}"

        items = datos.get("items", [])
        if len(items) == 0:
            return False, "La venta debe tener al menos un producto"

        # Revisamos TODOS los productos antes de vender: si uno falla, no se vende nada
        ids_vistos = []
        for item in items:
            producto = self.productos.obtener(item["producto_id"])
            if producto is None:
                return False, f"No existe producto con id {item['producto_id']}"
            if producto.id in ids_vistos:
                return False, f"El producto {producto.nombre} está repetido en la venta"
            if not producto.hay_stock(item["cantidad"]):
                return False, (f"Stock insuficiente de {producto.nombre}: "
                               f"hay {producto.stock}, piden {item['cantidad']}")
            ids_vistos.append(producto.id)

        # Todo bien: armamos la venta y descontamos el stock
        venta = Venta(self.siguiente(), cliente_id, datos.get("fecha", ""))
        for item in items:
            producto = self.productos.obtener(item["producto_id"])
            venta.agregar_detalle(producto, item["cantidad"])
            producto.descontar_stock(item["cantidad"])
        self.productos.guardar()          # guarda el stock nuevo en productos.json

        self.lista.append(venta)
        self.guardar()                    # guarda la venta en ventas.json
        return True, f"Venta {venta.id} registrada por ${venta.total:.2f}"

    def actualizar(self, id_venta, datos):
        # Una venta ya registrada no se modifica (como una factura real)
        return False, "Las ventas registradas no se pueden modificar"

    def eliminar(self, id_venta):
        venta = self.obtener(id_venta)
        if venta is None:
            return False, f"No existe venta con id {id_venta}"

        self.lista.remove(venta)
        self.guardar()
        return True, f"Venta {id_venta} eliminada"

    # --- métodos propios de ventas ---
    def factura(self, id_venta):
        venta = self.obtener(id_venta)
        if venta is None:
            return None

        cliente = self.clientes.obtener(venta.cliente_id)
        if cliente is None:
            nombre_cliente = "eliminado"
        else:
            nombre_cliente = cliente.nombre_completo

        texto = f"FACTURA #{venta.id}   fecha: {venta.fecha}\n"
        texto += f"Cliente: {nombre_cliente}\n"
        texto += "-" * 46 + "\n"
        for detalle in venta.detalles:
            texto += f"  {detalle}\n"
        texto += "-" * 46 + "\n"
        texto += f"  TOTAL: ${venta.total:.2f}  ({venta.cantidad_items} ítems)"
        return texto

    def ventas_de_cliente(self, cliente_id):
        resultado = []
        for venta in self.lista:
            if venta.cliente_id == cliente_id:
                resultado.append(venta)
        return resultado




class ProveedorController(CrudBase):

    def __init__(self, archivo="data/proveedores.json"):
        self.nombre = "proveedor"            # se usa en los títulos del menú
        self.campos = Proveedor.CAMPOS       # campos que el menú le pide al usuario
        self.gestor = GestorJSON(archivo)

        # Leemos el JSON y convertimos cada diccionario en un objeto proveedor
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Proveedor.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for proveedor in self.lista:
            datos.append(proveedor.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_proveedor):
        for proveedor in self.lista:
            if proveedor.id == id_proveedor:
                return proveedor
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for proveedor in self.lista:
            if (texto in proveedor.nombre.lower()
                    or texto in proveedor.apellido.lower()
                    or texto in proveedor.email
                    or texto in proveedor.ruc 
                    or texto in proveedor.empresa.lower()):
                encontrados.append(proveedor)
        return encontrados

    def siguiente(self):
        mayor = 0
        for proveedor in self.lista:
            if proveedor.id > mayor:
                mayor = proveedor.id
        return mayor + 1

    def crear(self, datos):
        # No puede haber dos proveedors con el mismo email
        email = str(datos.get("email", "")).strip().lower()
        ruc = str(datos.get("ruc", "")).strip()
        for proveedor in self.lista:
            if proveedor.email == email:
                return False, "Ese email ya está registrado"
            if proveedor.ruc == ruc:
                return False, "Ese RUC ya está registrado"

        # Si algún dato está mal, el modelo lanza ValueError
        try:
            proveedor = Proveedor(self.siguiente(),
                              datos.get("nombre", ""),
                              datos.get("apellido", ""),
                              datos.get("email", ""),
                              datos.get("ruc", ""),
                              datos.get("empresa", ""))
        except ValueError as error:
            return False, str(error)

        self.lista.append(proveedor)
        self.guardar()
        return True, f"proveedor creado: {proveedor.etiqueta()}"

    def actualizar(self, id_proveedor, datos):
        if not datos:
            return False, "No se indicó ningún cambio"

        proveedor = self.obtener(id_proveedor)
        if proveedor is None:
            return False, f"No existe proveedor con id {id_proveedor}"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            for otro in self.lista:
                if otro.email == email and otro.id != id_proveedor:
                    return False, "Ese email ya está registrado"
                
        if "ruc" in datos:
            ruc = str(datos["ruc"]).strip()
            for otro in self.lista:
                if otro.ruc == ruc and otro.id != id_proveedor:
                    return False, "Ese RUC ya está registrado"

        # Creamos un proveedor nuevo con los cambios. Si algo falla,
        # el proveedor viejo queda igual.
        try:
            nuevo = Proveedor(proveedor.id,
                            datos.get("nombre", proveedor.nombre),
                            datos.get("apellido", proveedor.apellido),
                            datos.get("email", proveedor.email),
                            datos.get("ruc", proveedor.ruc),
                            datos.get("empresa", proveedor.empresa))
        except ValueError as error:
            return False, str(error)

        posicion = self.lista.index(proveedor)
        self.lista[posicion] = nuevo
        self.guardar()
        return True, f"Proveedor {id_proveedor} actualizado"

    def eliminar(self, id_proveedor):
        proveedor = self.obtener(id_proveedor)
        if proveedor is None:
            return False, f"No existe proveedor con id {id_proveedor}"

        self.lista.remove(proveedor)
        self.guardar()
        return True, f"Proveedor {id_proveedor} eliminado"

    
    
class CompraController(CrudBase):

    def __init__(self, proveedores, productos, archivo="data/compras.json"):
        self.nombre = "compra"
        self.campos = Compra.CAMPOS
        self.gestor = GestorJSON(archivo)

        # La compra USA los controladores de clientes y productos.
        # Hay que pasarle los MISMOS que usa el menú.
        self.proveedores = proveedores
        self.productos = productos

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Compra.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for compra in self.lista:
            datos.append(compra.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_compra):
        for compra in self.lista:
            if compra.id == id_compra:
                return compra
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        # Las compras se buscan por fecha, ej: "2026-10"
        texto = texto.strip()
        encontrados = []
        if texto == "":
            return encontrados

        for compra in self.lista:
            if texto in compra.fecha:
                encontrados.append(compra)
        return encontrados

    def siguiente(self):
        mayor = 0
        for compra in self.lista:
            if compra.id > mayor:
                mayor = compra.id
        return mayor + 1

    def crear(self, datos):
        # datos = {"proveedor_id": 1, "items": [{"producto_id": 2, "cantidad": 3}, ...]}
        try:
            proveedor_id= int(datos.get("proveedor_id", 0))
        except (TypeError, ValueError):
            return False, "El proveedor_iddebe ser un número"

        if self.proveedores.obtener(proveedor_id) is None:
            return False, f"No existe un proveedor con id {proveedor_id}"

        items = datos.get("items", [])
        if len(items) == 0:
            return False, "La compra debe tener al menos un producto"

        # Revisamos TODOS los productos antes de vender: si uno falla, no se vende nada
        ids_vistos = []
        for item in items:
            producto = self.productos.obtener(item["producto_id"])
            if producto is None:
                return False, f"No existe producto con id {item['producto_id']}"
            if producto.id in ids_vistos:
                return False, f"El producto {producto.nombre} está repetido en la compra"
            
            ids_vistos.append(producto.id)

        # Todo bien: armamos la compra y descontamos el stock
        compra = Compra(self.siguiente(), proveedor_id, datos.get("fecha", ""))
        try:
            for item in items:
                producto = self.productos.obtener(item["producto_id"])
                compra.agregar_detalle(producto, item["cantidad"], item.get("costo_unitario", ""))
        except ValueError as error:
            return False, str(error)

        # Todo bien: ahora sí sumamos el stock
        for detalle in compra.detalles:
            producto = self.productos.obtener(detalle.producto_id)
            producto.aumentar_stock(detalle.cantidad)
        self.productos.guardar()
        self.lista.append(compra)
        self.guardar()                    # guarda la compra en compras.json
        return True, f"Compra {compra.id} registrada por ${compra.total:.2f}"
        
    def actualizar(self, id_compra, datos):
        # Una compra ya registrada no se modifica (como una orden_compra real)
        return False, "Las compras registradas no se pueden modificar"

    def eliminar(self, id_compra):
        compra = self.obtener(id_compra)
        if compra is None:
            return False, f"No existe compra con id {id_compra}"

        self.lista.remove(compra)
        self.guardar()
        return True, f"compra {id_compra} eliminada"

    # --- métodos propios de compras ---
    def orden_compra(self, id_compra):
        compra = self.obtener(id_compra)
        if compra is None:
            return None

        proveedor = self.proveedores.obtener(compra.proveedor_id)
        if proveedor is None:
            nombre_proveedor = "eliminado"
        else:
            nombre_proveedor = proveedor.etiqueta()

        texto = f"ORDEN DE COMPRA #{compra.id}   fecha: {compra.fecha}\n"
        texto += f"Proveedor: {nombre_proveedor}\n"
        texto += "-" * 46 + "\n"
        for detalle in compra.detalles:
            texto += f"  {detalle}\n"
        texto += "-" * 46 + "\n"
        texto += f"  TOTAL: ${compra.total:.2f}  ({compra.cantidad_items} ítems)"
        return texto

    def compras_de_proveedor(self, proveedor_id):
        resultado = []
        for compra in self.lista:
            if compra.proveedor_id== proveedor_id:
                resultado.append(compra)
        return resultado




# =====================================================================
# PRUEBAS SENCILLAS: solo se ejecutan con "python views.py"
# (desde la carpeta proyecto_clientes)
# =====================================================================
if __name__ == "__main__":
    import os

    # Las pruebas usan la carpeta data_prueba/ para no tocar los datos reales.
    # Borramos los archivos de una prueba anterior para empezar desde cero.
    for ruta in ["data_prueba/clientes.json", "data_prueba/productos.json",
                 "data_prueba/ventas.json"]:
        if os.path.exists(ruta):
            os.remove(ruta)

    clientes = ClienteController("data_prueba/clientes.json")
    productos = ProductoController("data_prueba/productos.json")
    ventas = VentaController(clientes, productos, "data_prueba/ventas.json")

    # CrudBase es abstracta: no se puede crear un objeto de ella
    try:
        CrudBase()
    except TypeError as error:
        print("OK  -> CrudBase no se puede instanciar:", error)

    print()
    print("=" * 60)
    print("CLIENTES")
    print("=" * 60)
    print("Crear Juan        ->", clientes.crear({"nombre": "juan", "apellido": "perez",
                                                  "email": "juan@mail.com",
                                                  "telefono": "0991234567",
                                                  "ciudad": "milagro"}))
    print("Crear María       ->", clientes.crear({"nombre": "maria", "apellido": "lopez",
                                                  "email": "maria@mail.com"}))
    print("Email repetido    ->", clientes.crear({"nombre": "otro", "apellido": "x",
                                                  "email": "JUAN@mail.com"}))
    print("siguiente()       ->", clientes.siguiente())
    print("leer():")
    for cliente in clientes.leer():
        print("   ", cliente)
    print("buscar('LOPEZ')   ->", [str(c) for c in clientes.buscar("LOPEZ")])
    print("Actualizar ciudad ->", clientes.actualizar(2, {"ciudad": "quito"}))
    print("Email inválido    ->", clientes.actualizar(2, {"ciudad": "loja", "email": "malo"}))
    print("   ciudad sigue   :", clientes.obtener(2).ciudad)
    clientes.crear({"nombre": "borrar", "apellido": "me", "email": "borrar@mail.com"})
    print("Eliminar 3        ->", clientes.eliminar(3))

    print()
    print("=" * 60)
    print("PRODUCTOS")
    print("=" * 60)
    print("Crear laptop      ->", productos.crear({"nombre": "laptop", "precio": "800", "stock": "5"}))
    print("Crear mouse       ->", productos.crear({"nombre": "mouse", "precio": "15.75", "stock": "20"}))
    print("Crear sin stock   ->", productos.crear({"nombre": "teclado", "precio": "25"}))
    print("Actualizar precio ->", productos.actualizar(3, {"precio": "30"}))
    print("leer():")
    for producto in productos.leer():
        print("   ", producto)
    print("con_stock_bajo()  ->", [str(p) for p in productos.con_stock_bajo()])
    print("Descontar 2 mouse ->", productos.descontar_stock(2, 2))

    print()
    print("=" * 60)
    print("VENTAS")
    print("=" * 60)
    print("Venta 1           ->", ventas.crear({"cliente_id": 1,
                                                "items": [{"producto_id": 1, "cantidad": 2},
                                                          {"producto_id": 2, "cantidad": 3}]}))
    print("Stock después     -> laptop:", productos.obtener(1).stock,
          "| mouse:", productos.obtener(2).stock)
    print("Venta 2           ->", ventas.crear({"cliente_id": 2,
                                                "items": [{"producto_id": 2, "cantidad": 1}]}))
    print("Cliente no existe ->", ventas.crear({"cliente_id": 99,
                                                "items": [{"producto_id": 1, "cantidad": 1}]}))
    print("Sin productos     ->", ventas.crear({"cliente_id": 1, "items": []}))
    print("Actualizar venta  ->", ventas.actualizar(1, {"fecha": "2026-01-01"}))
    print("buscar(fecha hoy) ->", len(ventas.buscar(ventas.obtener(1).fecha)), "venta(s)")
    print()
    print(ventas.factura(1))
    print()
    print("Eliminar venta 2  ->", ventas.eliminar(2))

    print()
    print("=" * 60)
    print("¿SE GUARDÓ TODO EN LOS ARCHIVOS?")
    print("=" * 60)
    # Controladores nuevos: leen los JSON desde cero
    clientes2 = ClienteController("data_prueba/clientes.json")
    productos2 = ProductoController("data_prueba/productos.json")
    ventas2 = VentaController(clientes2, productos2, "data_prueba/ventas.json")
    print("Clientes :", [str(c) for c in clientes2.leer()])
    print("Productos:", [str(p) for p in productos2.leer()])
    print("Ventas   :", [str(v) for v in ventas2.leer()])
    
    
    
    
    
    
    