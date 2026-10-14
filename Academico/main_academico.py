
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views_academico import (
    EstudianteController, DocenteController, MateriaController, MatriculaController
)
 
 
# =====================================================================
# MENÚ GENÉRICO: sirve para cualquier controlador
# =====================================================================
class MenuCRUD:
 
    def __init__(self, controlador):
        # El controlador se recibe por parámetro (inyección / dependencia)
        self.controlador = controlador
 
    # ---------- ayudas ----------
    def pausa(self):
        input("\nPresione Enter para continuar...")
 
    def pedir_entero(self, texto):
        try:
            return int(input(texto))
        except ValueError:
            return None
 
    def mostrar_resultado(self, exito, mensaje):
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)
 
    # ---------- gancho para los hijos ----------
    def opciones_extra(self):
        """El menú normal no tiene opciones extra.
        Un hijo devuelve {"7": ("Texto", metodo), ...}"""
        return {}
 
    # ---------- el menú ----------
    def ejecutar(self):
        titulo = self.controlador.nombre.upper() + "S"
 
        while True:
            imprimir_titulo(titulo)
            print(f"  1. Crear {self.controlador.nombre}")
            print("  2. Ver todos")
            print("  3. Buscar")
            print("  4. Ver por id")
            print("  5. Actualizar")
            print("  6. Eliminar")
            extras = self.opciones_extra()
            for clave, (texto, metodo) in extras.items():
                print(f"  {clave}. {texto}")
            print("  0. Volver\n")
            opcion = input("Opción: ").strip()
 
            if opcion == "1":
                self.crear()          # POLIMORFISMO: si es MenuMatriculas, usa SU crear()
            elif opcion == "2":
                self.ver_todos()
            elif opcion == "3":
                self.buscar()
            elif opcion == "4":
                self.ver_por_id()
            elif opcion == "5":
                self.actualizar()
            elif opcion == "6":
                self.eliminar()
            elif opcion in extras:
                texto, metodo = extras[opcion]
                metodo()
            elif opcion == "0":
                break
            else:
                imprimir_error("Opción no válida")
                self.pausa()
 
    # ---------- operaciones ----------
    def crear(self):
        imprimir_titulo(f"CREAR {self.controlador.nombre.upper()}")
        datos = {}
        for campo in self.controlador.campos:
            datos[campo] = input(f"{campo.capitalize()}: ")
 
        exito, mensaje = self.controlador.crear(datos)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()
 
    def ver_todos(self):
        imprimir_titulo(self.controlador.nombre.upper() + "S")
        lista = self.controlador.leer()
        if len(lista) == 0:
            imprimir_info("No hay registros todavía.")
        else:
            for objeto in lista:
                print(f"  {objeto}")
            imprimir_info(f"Total: {len(lista)}")
        self.pausa()
 
    def buscar(self):
        imprimir_titulo(f"BUSCAR {self.controlador.nombre.upper()}")
        texto = input("Buscar: ")
        encontrados = self.controlador.buscar(texto)
        if len(encontrados) == 0:
            imprimir_info(f"Sin coincidencias para '{texto}'.")
        else:
            for objeto in encontrados:
                print(f"  {objeto}")
        self.pausa()
 
    def ver_por_id(self):
        imprimir_titulo(f"VER {self.controlador.nombre.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = self.controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error("No encontrado")
        else:
            for clave, valor in objeto.a_diccionario().items():
                print(f"  {clave.capitalize()}: {valor}")
        self.pausa()
 
    def actualizar(self):
        imprimir_titulo(f"ACTUALIZAR {self.controlador.nombre.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = self.controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error("No encontrado")
            self.pausa()
            return
 
        imprimir_info(f"Editando: {objeto.etiqueta()}")
        print("Deje en blanco lo que no quiera cambiar.\n")
        cambios = {}
        for campo in self.controlador.campos:
            actual = getattr(objeto, campo)
            nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
            if nuevo != "":
                cambios[campo] = nuevo
 
        exito, mensaje = self.controlador.actualizar(id_registro, cambios)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()
 
    def eliminar(self):
        imprimir_titulo(f"ELIMINAR {self.controlador.nombre.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = self.controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error("No encontrado")
            self.pausa()
            return
 
        imprimir_info(f"Se eliminará: {objeto.etiqueta()}")
        if confirmar("¿Confirma?"):
            exito, mensaje = self.controlador.eliminar(id_registro)
            self.mostrar_resultado(exito, mensaje)
        else:
            imprimir_info("Operación cancelada")
        self.pausa()
 
 
# =====================================================================
# MENÚ DE MATRÍCULAS: HEREDA todo de MenuCRUD, SOBRESCRIBE crear()
# y agrega "Agregar nota" y "Ver boletín"
# =====================================================================
class MenuMatriculas(MenuCRUD):
 
    def opciones_extra(self):
        return {
            "7": ("Agregar nota", self.agregar_nota),
            "8": ("Ver boletín", self.ver_boletin),
        }
 
    def crear(self):
        # Matricular = añadir un estudiante a una materia existente.
        # Las notas NO se piden aquí: se agregan con la opción 7 (composición).
        imprimir_titulo("REGISTRAR MATRÍCULA")
        imprimir_info("Estudiantes:")
        for estudiante in self.controlador.estudiantes.leer():
            print(f"  {estudiante}")
        imprimir_info("Materias:")
        for materia in self.controlador.materias.leer():
            print(f"  {materia}")
 
        estudiante_id = self.pedir_entero("\nId del estudiante: ")
        materia_id = self.pedir_entero("Id de la materia: ")
        if estudiante_id is None or materia_id is None:
            imprimir_error("Los ids deben ser números")
            self.pausa()
            return
        periodo = input("Periodo [2026-1]: ").strip()
 
        exito, mensaje = self.controlador.crear({"estudiante_id": estudiante_id,
                                                 "materia_id": materia_id,
                                                 "periodo": periodo})
        self.mostrar_resultado(exito, mensaje)
        self.pausa()
 
    def ver_por_id(self):
        # Sobrescrito para mostrar las notas bonitas en vez del diccionario
        imprimir_titulo("VER MATRÍCULA")
        objeto = self.controlador.obtener(self.pedir_entero("Id: "))
        if objeto is None:
            imprimir_error("No encontrado")
        else:
            print(f"  {objeto}")
            for nota in objeto.notas:
                print(f"     · {nota} (peso {nota.peso:g})")
        self.pausa()
 
    def actualizar(self):
        # Una matrícula no se edita: se elimina y se crea otra
        imprimir_error("Las matrículas no se modifican; elimínela y créela de nuevo")
        self.pausa()
 
    def agregar_nota(self):
        imprimir_titulo("AGREGAR NOTA")
        matricula_id = self.pedir_entero("Id de la matrícula: ")
        if matricula_id is None:
            imprimir_error("El id debe ser un número")
            self.pausa()
            return
        tipo = input("Tipo (deber, lección, examen): ")
        valor = input("Nota (0 a 20): ")
        peso = input("Peso [1]: ").strip() or 1
 
        exito, mensaje = self.controlador.agregar_nota(matricula_id, tipo, valor, peso)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()
 
    def ver_boletin(self):
        imprimir_titulo("BOLETÍN")
        estudiante_id = self.pedir_entero("Id del estudiante: ")
        texto = self.controlador.boletin(estudiante_id)
        if texto is None:
            imprimir_error("No existe ese estudiante")
        else:
            print(texto)
        self.pausa()
 
 
# =====================================================================
# MENÚ PRINCIPAL
# =====================================================================
class MenuPrincipal:
 
    def __init__(self):
        # UN solo controlador de cada tipo, compartidos entre todos
        self.estudiantes = EstudianteController()
        self.docentes = DocenteController()
        self.materias = MateriaController(self.docentes)
        self.matriculas = MatriculaController(self.estudiantes, self.materias)
 
        # Los tres primeros usan MenuCRUD TAL CUAL; matrículas usa su hijo
        self.menus = {
            "1": ("Estudiantes", MenuCRUD(self.estudiantes)),
            "2": ("Docentes", MenuCRUD(self.docentes)),
            "3": ("Materias", MenuCRUD(self.materias)),
            "4": ("Matrículas", MenuMatriculas(self.matriculas)),
        }
 
    def ejecutar(self):
        while True:
            imprimir_titulo("SISTEMA ACADÉMICO")
            for clave, (texto, menu) in self.menus.items():
                print(f"  {clave}. {texto}")
            print("  5. Reporte: materias por docente")
            print("  6. Reporte general")
            print("  0. Salir\n")
            opcion = input("Opción: ").strip()
 
            if opcion in self.menus:
                texto, menu = self.menus[opcion]
                menu.ejecutar()       # POLIMORFISMO: MenuCRUD o MenuMatriculas, da igual
            elif opcion == "5":
                self.reporte_materias_por_docente()
            elif opcion == "6":
                self.reporte_general()
            elif opcion == "0":
                imprimir_info("¡Hasta luego! 👋")
                break
            else:
                imprimir_error("Opción no válida")
                input("\nPresione Enter para continuar...")
 
    # ---------- reportes ----------
    def reporte_materias_por_docente(self):
        imprimir_titulo("MATERIAS POR DOCENTE")
        for docente in self.docentes.leer():
            print(f"\n  {docente.etiqueta()}")          # etiqueta() de Docente
            materias = self.materias.materias_de_docente(docente.id)
            if len(materias) == 0:
                print("     (sin materias)")
            for materia in materias:
                print(f"     - {materia.etiqueta()}")  # etiqueta() de Materia
 
        sin_docente = [m for m in self.materias.leer() if m.docente_id is None]
        if sin_docente:
            print("\n  Sin docente asignado:")
            for materia in sin_docente:
                print(f"     - {materia.etiqueta()}")
        input("\nPresione Enter para continuar...")
 
    def reporte_general(self):
        # POLIMÓRFICO: el mismo bucle sirve para los 4 controladores, sin un solo if
        imprimir_titulo("REPORTE GENERAL")
        for controlador in (self.estudiantes, self.docentes, self.materias, self.matriculas):
            lista = controlador.leer()
            print(f"\n  --- {controlador.nombre.upper()}S ({len(lista)}) ---")
            for objeto in lista:
                print(f"    {objeto.etiqueta()}")
        input("\nPresione Enter para continuar...")
 
 
if __name__ == "__main__":
    try:
        MenuPrincipal().ejecutar()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")