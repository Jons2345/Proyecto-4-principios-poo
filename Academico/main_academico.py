from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views_academico import EstudianteController, DocenteController, MateriaController, MatriculaController


class Menu:

    def __init__(self):
        self.estudiantes = EstudianteController()
        self.docentes = DocenteController()
        self.materias = MateriaController(self.docentes)
        self.matriculas = MatriculaController(self.estudiantes, self.materias)


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


    def ejecutar(self):
        while True:
            imprimir_titulo("SISTEMA ACADEMICO")
            print("  1. Estudiantes")
            print("  2. Docentes")
            print("  3. Materias")
            print("  4. Matricula")
            print("  5. Reporte general")
            print("  0. Salir\n")
            opcion = input("Opción: ").strip()

            if opcion == "1":
                self.menu_crud(self.estudiantes)
            elif opcion == "2":
                self.menu_crud(self.docentes)
            elif opcion == "3":
                self.menu_crud(self.materias)
            elif opcion == "4":
                self.menu_crud(self.matriculas)
            elif opcion == "5":
                self.reporte_general()
            elif opcion == "0":
                imprimir_info("¡Hasta luego! 👋")
                break
            else:
                imprimir_error("Opción no válida")
                self.pausa()


    def menu_crud(self, controlador):
        titulo = controlador.nombre.upper() + "S"     

        while True:
            imprimir_titulo(titulo)
            print(f"  1. Crear {controlador.nombre}")
            print("  2. Ver todos")
            print("  3. Buscar")
            print("  4. Ver por id")
            print("  5. Actualizar")
            print("  6. Eliminar")
            if controlador == self.matriculas:
                print("  7. Agregar nota")
                print("  8. Ver boletín")
            print("  0. Volver\n")
            opcion = input("Opción: ").strip()

            if opcion == "1":
                if controlador == self.matriculas:
                    self.crear_matricula()
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
            elif opcion == "7" and controlador == self.matriculas:
                self.agregar_nota()
            elif opcion == "8" and controlador == self.matriculas:
                self.ver_boletin()
            elif opcion == "0":
                break
            else:
                imprimir_error("Opción no válida")
                self.pausa()

    def crear(self, controlador):
        imprimir_titulo(f"CREAR {controlador.nombre.upper()}")
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
        elif controlador == self.matriculas:
            print(f"  {objeto}")
            for nota in objeto.notas:
                print(f"     · {nota} (peso {nota.peso:g})")
        else:
            for clave, valor in objeto.a_diccionario().items():
                print(f"  {clave.capitalize()}: {valor}")
        self.pausa()

    def actualizar(self, controlador):
        imprimir_titulo(f"ACTUALIZAR {controlador.nombre.upper()}")
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
            actual = getattr(objeto, campo)       
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

    def crear_matricula(self):
        imprimir_titulo("REGISTRAR MATRÍCULA")
        imprimir_info("Estudiantes:")
        for estudiante in self.estudiantes.leer():
            print(f"  {estudiante}")
        imprimir_info("Materias:")
        for materia in self.materias.leer():
            print(f"  {materia}")

        estudiante_id = self.pedir_entero("\nId del estudiante: ")
        materia_id = self.pedir_entero("Id de la materia: ")
        if estudiante_id is None or materia_id is None:
            imprimir_error("Los ids deben ser números")
            self.pausa()
            return
        periodo = input("Periodo [2026-1]: ").strip()

        exito, mensaje = self.matriculas.crear({"estudiante_id": estudiante_id,
                                                "materia_id": materia_id,
                                                "periodo": periodo})
        self.mostrar_resultado(exito, mensaje)
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

        exito, mensaje = self.matriculas.agregar_nota(matricula_id, tipo, valor, peso)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def ver_boletin(self):
        imprimir_titulo("BOLETÍN")
        estudiante_id = self.pedir_entero("Id del estudiante: ")
        texto = self.matriculas.boletin(estudiante_id)
        if texto is None:
            imprimir_error("No existe ese estudiante")
        else:
            print(texto)
        self.pausa()

    def reporte_general(self):
        imprimir_titulo("REPORTE GENERAL")
        
        for controlador in (self.estudiantes, self.docentes, self.materias, self.matriculas):
            lista = controlador.leer()
            print(f"\n  --- {controlador.nombre.upper()}S ({len(lista)}) ---")
            for objeto in lista:
                print(f"    {objeto.etiqueta()}")
        self.pausa()



if __name__ == "__main__":
    try:
        Menu().ejecutar()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
