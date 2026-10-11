from abc import ABC, abstractmethod

from models import Cliente, Producto, Venta
from shared.json_manager import GestorJSON


# =====================================================================
# LA INTERFAZ DEL CRUD: clase abstracta con la lógica común
# =====================================================================
class CrudBase(ABC):
    """Define QUÉ hace todo controlador y ya implementa el CÓMO que se repite."""

    MODELO = None            # clase del modelo (Cliente, Producto, Venta...)
    ARCHIVO = None           # ruta del JSON
    NOMBRE = "registro"      # para los mensajes
    CAMPOS_BUSCABLES = ()

    def __init__(self):
        if self.MODELO is None or self.ARCHIVO is None:
            raise ValueError("El controlador debe definir MODELO y ARCHIVO")
        self._gestor = GestorJSON(self.ARCHIVO)

    # ---------- MÉTODO ABSTRACTO: cada controlador pone SUS reglas ----------
    @abstractmethod
    def validar(self, datos, id_actual=None):
        """Devuelve un mensaje de error, o None si todo está bien."""

    # ---------- GANCHO: se puede sobrescribir, pero tiene versión por defecto ----------
    def preparar(self, datos):
        """Deja los datos listos para el constructor del Modelo."""
        return {campo: datos.get(campo, "") for campo in self.MODELO.CAMPOS}

    # ---------- LÓGICA COMÚN: se hereda sin tocar ----------
    def registros(self):
        return self._gestor.leer()

    def siguiente_id(self):
        ids = [registro["id"] for registro in self.registros()]
        return max(ids) + 1 if ids else 1

    def listar(self):
        return [self.MODELO.desde_diccionario(r) for r in self.registros()]

    def obtener(self, id_registro):
        for objeto in self.listar():
            if objeto.id == id_registro:
                return objeto
        return None

    def existe(self, id_registro):
        return any(r["id"] == id_registro for r in self.registros())

    def buscar(self, termino):
        termino = str(termino).strip().lower()
        if not termino:
            return []
        encontrados = []
        for registro in self.registros():
            for campo in self.CAMPOS_BUSCABLES:
                if termino in str(registro.get(campo, "")).lower():
                    encontrados.append(self.MODELO.desde_diccionario(registro))
                    break
        return encontrados

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error
        try:
            objeto = self.MODELO(self.siguiente_id(), **self.preparar(datos))
        except ValueError as excepcion:
            return False, str(excepcion)

        registros = self.registros()
        registros.append(objeto.a_diccionario())
        if not self._gestor.guardar(registros):
            return False, "No se pudo escribir el archivo"
        return True, f"{self.NOMBRE.capitalize()} creado: {objeto.etiqueta()}"

    def actualizar(self, id_registro, cambios):
        desconocidos = set(cambios) - set(self.MODELO.CAMPOS)
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"
        if not cambios:
            return False, "No se indicó ningún cambio"

        objeto = self.obtener(id_registro)
        if objeto is None:
            return False, f"No existe {self.NOMBRE} con id {id_registro}"

        error = self.validar(cambios, id_actual=id_registro)
        if error:
            return False, error

        try:
            for campo, valor in cambios.items():
                setattr(objeto, campo, valor)     # cada setter valida
        except ValueError as excepcion:
            return False, str(excepcion)

        registros = self.registros()
        for indice, registro in enumerate(registros):
            if registro["id"] == id_registro:
                registros[indice] = objeto.a_diccionario()
                break
        self._gestor.guardar(registros)
        return True, f"{self.NOMBRE.capitalize()} {id_registro} actualizado"

    def eliminar(self, id_registro):
        registros = self.registros()
        quedan = [r for r in registros if r["id"] != id_registro]
        if len(quedan) == len(registros):
            return False, f"No existe {self.NOMBRE} con id {id_registro}"
        self._gestor.guardar(quedan)
        return True, f"{self.NOMBRE.capitalize()} {id_registro} eliminado"


# =====================================================================
class ClienteController(CrudBase):
    MODELO = Cliente
    ARCHIVO = "data/clientes.json"
    NOMBRE = "cliente"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "telefono", "ciudad")

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = [c for c in self.MODELO.OBLIGATORIOS
                         if not str(datos.get(c, "")).strip()]
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            usados = {r["email"].lower() for r in self.registros()
                      if r["id"] != id_actual}
            if email in usados:
                return "Ese email ya está registrado"
        return None


# =====================================================================
class ProductoController(CrudBase):
    MODELO = Producto
    ARCHIVO = "data/productos.json"
    NOMBRE = "producto"
    CAMPOS_BUSCABLES = ("nombre",)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = [c for c in self.MODELO.OBLIGATORIOS
                         if not str(datos.get(c, "")).strip()]
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"

        if "nombre" in datos and str(datos["nombre"]).strip():
            nombre = str(datos["nombre"]).strip().title()
            usados = {r["nombre"].title() for r in self.registros()
                      if r["id"] != id_actual}
            if nombre in usados:
                return f"Ya existe un producto llamado {nombre}"
        return None

    def preparar(self, datos):
        valores = super().preparar(datos)
        valores["stock"] = valores.get("stock") or 0
        return valores

    # --- propio de productos ---
    def descontar_stock(self, producto_id, cantidad):
        producto = self.obtener(producto_id)
        if producto is None:
            return False, f"No existe producto con id {producto_id}"
        try:
            producto.descontar_stock(cantidad)
        except ValueError as excepcion:
            return False, str(excepcion)
        return self.actualizar(producto_id, {"stock": producto.stock})

    def con_stock_bajo(self, minimo=5):
        return [p for p in self.listar() if p.stock <= minimo]


# =====================================================================
class VentaController(CrudBase):
    """Depende de los otros dos controladores: ASOCIACIÓN entre controladores."""

    MODELO = Venta
    ARCHIVO = "data/ventas.json"
    NOMBRE = "venta"
    CAMPOS_BUSCABLES = ("fecha",)

    def __init__(self, clientes=None, productos=None):
        super().__init__()
        self.clientes = clientes or ClienteController()
        self.productos = productos or ProductoController()

    def validar(self, datos, id_actual=None):
        try:
            cliente_id = int(datos.get("cliente_id", 0))
        except (TypeError, ValueError):
            return "El cliente_id debe ser un número"

        if not self.clientes.existe(cliente_id):
            return f"No existe un cliente con id {cliente_id}"

        items = datos.get("items", [])
        if not items:
            return "La venta debe tener al menos un producto"

        for item in items:
            producto = self.productos.obtener(int(item["producto_id"]))
            if producto is None:
                return f"No existe producto con id {item['producto_id']}"
            if not producto.hay_stock(int(item["cantidad"])):
                return (f"Stock insuficiente de {producto.nombre}: "
                        f"hay {producto.stock}, piden {item['cantidad']}")
        return None

    def crear(self, datos):
        """Sobrescribe al padre: una venta se arma con sus detalles y mueve stock."""
        error = self.validar(datos)
        if error:
            return False, error
        try:
            venta = Venta(self.siguiente_id(), datos["cliente_id"], datos.get("fecha", ""))
            for item in datos["items"]:
                producto = self.productos.obtener(int(item["producto_id"]))
                venta.agregar_detalle(producto, int(item["cantidad"]))
        except ValueError as excepcion:
            return False, str(excepcion)

        for detalle in venta.detalles:
            exito, mensaje = self.productos.descontar_stock(detalle.producto_id,
                                                            detalle.cantidad)
            if not exito:
                return False, mensaje

        registros = self.registros()
        registros.append(venta.a_diccionario())
        self._gestor.guardar(registros)
        return True, f"Venta {venta.id} registrada por ${venta.total:.2f}"

    def factura(self, id_venta):
        """Texto de la factura: junta venta + cliente + detalles."""
        venta = self.obtener(id_venta)
        if venta is None:
            return None
        cliente = self.clientes.obtener(venta.cliente_id)
        lineas = [
            f"FACTURA #{venta.id}   fecha: {venta.fecha}",
            f"Cliente: {cliente.nombre_completo if cliente else 'eliminado'}",
            "-" * 46,
        ]
        for detalle in venta.detalles:
            lineas.append(f"  {detalle}")
        lineas.append("-" * 46)
        lineas.append(f"  TOTAL: ${venta.total:.2f}  ({venta.cantidad_items} ítems)")
        return "\n".join(lineas)

    def ventas_de_cliente(self, cliente_id):
        return [v for v in self.listar() if v.cliente_id == cliente_id]