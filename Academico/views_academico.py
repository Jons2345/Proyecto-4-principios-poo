from abc import abstractmethod

from models_academico import Estudiante, Docente, Materia, Matricula
from shared.json_manager import GestorJSON
from views import CrudBase


class CrudJSON(CrudBase):
    """Escribe el CRUD UNA sola vez. Cada controlador solo pone su validar()."""

    MODELO = None
    ARCHIVO = ""
    NOMBRE = ""
    CAMPOS_BUSCABLES = ()

    def __init__(self, archivo=None):
        self.nombre = self.NOMBRE
        self.campos = self.MODELO.CAMPOS
        self.gestor = GestorJSON(archivo or self.ARCHIVO)
        self.lista = [self.MODELO.desde_diccionario(d) for d in self.gestor.leer()]

    @abstractmethod
    def validar(self, datos, id_actual=None):
        """None si todo está bien, o el texto del error."""

    def guardar(self):
        self.gestor.guardar([o.a_diccionario() for o in self.lista])

    def obtener(self, id_registro):
        for objeto in self.lista:
            if objeto.id == id_registro:
                return objeto
        return None

    def existe(self, id_registro):
        return self.obtener(id_registro) is not None

    def registros(self):
        return [o.a_diccionario() for o in self.lista]

    def listar(self):
        return list(self.lista)

    def leer(self):
        return self.listar()

    def buscar(self, texto):
        texto = str(texto).strip().lower()
        if not texto:
            return []
        return [o for o in self.lista
                if any(texto in str(getattr(o, c, "") or "").lower() for c in self.CAMPOS_BUSCABLES)]

    def siguiente(self):
        return max((o.id for o in self.lista), default=0) + 1

    def crear(self, datos):
        datos = {c: datos.get(c, "") for c in self.campos}
        error = self.validar(datos)
        if error:
            return False, error
        try:
            nuevo = self.MODELO.desde_diccionario({"id": self.siguiente(), **datos})
        except (ValueError, TypeError) as error:
            return False, str(error)
        self.lista.append(nuevo)
        self.guardar()
        return True, f"{self.NOMBRE.capitalize()} registrado: {nuevo.etiqueta()}"

    def actualizar(self, id_registro, datos):
        if not datos:
            return False, "No se indicó ningún cambio"
        actual = self.obtener(id_registro)
        if actual is None:
            return False, f"No existe {self.NOMBRE} con id {id_registro}"
        error = self.validar(datos, id_actual=id_registro)
        if error:
            return False, error
        completos = actual.a_diccionario()
        completos.update({c: v for c, v in datos.items() if c in self.campos})
        try:
            nuevo = self.MODELO.desde_diccionario(completos)
        except (ValueError, TypeError) as error:
            return False, str(error)
        self.lista[self.lista.index(actual)] = nuevo
        self.guardar()
        return True, f"{self.NOMBRE.capitalize()} {id_registro} actualizado"

    def eliminar(self, id_registro):
        objeto = self.obtener(id_registro)
        if objeto is None:
            return False, f"No existe {self.NOMBRE} con id {id_registro}"
        self.lista.remove(objeto)
        self.guardar()
        return True, f"{self.NOMBRE.capitalize()} {id_registro} eliminado"


class EstudianteController(CrudJSON):
    """LISTO como ejemplo: cópialo y guíate con él para los demás."""

    MODELO = Estudiante
    ARCHIVO = "data/estudiantes.json"
    NOMBRE = "estudiante"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = [c for c in self.MODELO.OBLIGATORIOS
                         if not str(datos.get(c, "")).strip()]
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"

        if "carnet" in datos and str(datos["carnet"]).strip():
            carnet = str(datos["carnet"]).strip().upper()
            usados = {r["carnet"].upper() for r in self.registros()
                      if r["id"] != id_actual}
            if carnet in usados:
                return f"El carnet {carnet} ya está registrado"
        return None


class DocenteController(CrudJSON):
    MODELO = Docente
    ARCHIVO = "data/docentes.json"
    NOMBRE = "docente"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "especialidad")

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = [c for c in self.MODELO.OBLIGATORIOS
                         if not str(datos.get(c, "")).strip()]
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"

        if "email" in datos and str(datos["email"]).strip():
            email = str(datos["email"]).strip().lower()
            usados = {r["email"].lower() for r in self.registros()
                      if r["id"] != id_actual}
            if email in usados:
                return f"El email {email} ya está registrado"
        return None
        
class MateriaController(CrudJSON):
    MODELO = Materia
    ARCHIVO = "data/materias.json"
    NOMBRE = "materia"
    CAMPOS_BUSCABLES = ("nombre", "codigo")

    def __init__(self, docentes=None):
        super().__init__()
        self.docentes = docentes or DocenteController()

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = [c for c in self.MODELO.OBLIGATORIOS
                         if not str(datos.get(c, "")).strip()]
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"


        if "codigo" in datos and str(datos["codigo"]).strip():
            codigo = str(datos["codigo"]).strip().upper()
            usados = {r["codigo"].upper() for r in self.registros()
                      if r["id"] != id_actual}
            if codigo in usados:
                return f"El código {codigo} ya está registrado"


        docente_id = str(datos.get("docente_id", "")).strip()
        if docente_id not in ("", "0"):
            try:
                docente_id = int(docente_id)
            except ValueError:
                return f"docente_id inválido: '{docente_id}'"
            if not self.docentes.existe(docente_id):
                return f"No existe docente con id {docente_id}"

        return None

    def asignar_docente(self, materia_id, docente_id):
        if not self.existe(materia_id):
            return False, f"No existe materia con id {materia_id}"
        if not self.docentes.existe(docente_id):
            return False, f"No existe docente con id {docente_id}"
        return self.actualizar(materia_id, {"docente_id": docente_id})

    def materias_de_docente(self, docente_id):
        return [m for m in self.listar() if m.docente_id == docente_id]

    
class MatriculaController(CrudJSON):
    """El equivalente académico del VentaController."""

    MODELO = Matricula
    ARCHIVO = "data/matriculas.json"
    NOMBRE = "matrícula"
    CAMPOS_BUSCABLES = ("periodo",)

    def __init__(self, estudiantes=None, materias=None):
        super().__init__()
        self.estudiantes = estudiantes or EstudianteController()
        self.materias = materias or MateriaController()

    def validar(self, datos, id_actual=None):
        actual = {}
        if id_actual is not None:
            for r in self.registros():
                if r["id"] == id_actual:
                    actual = r

        try:
            estudiante_id = int(datos.get("estudiante_id", actual.get("estudiante_id")))
            materia_id = int(datos.get("materia_id", actual.get("materia_id")))
        except (TypeError, ValueError):
            return "estudiante_id y materia_id deben ser números"

        
        if not self.estudiantes.existe(estudiante_id):
            return f"No existe estudiante con id {estudiante_id}"


        if not self.materias.existe(materia_id):
            return f"No existe materia con id {materia_id}"


        periodo = str(datos.get("periodo", actual.get("periodo", ""))).strip() or "2026-1"
        for r in self.registros():
            if (r["id"] != id_actual
                    and r["estudiante_id"] == estudiante_id
                    and r["materia_id"] == materia_id
                    and r["periodo"] == periodo):
                return (f"El estudiante {estudiante_id} ya está matriculado "
                        f"en la materia {materia_id} en {periodo}")
        return None

    def agregar_nota(self, matricula_id, tipo, valor, peso=1):
        matricula = self.obtener(matricula_id)
        if matricula is None:
            return False, f"No existe matrícula con id {matricula_id}"
        try:
            nota = matricula.agregar_nota(tipo, valor, peso)
        except ValueError as error:
            return False, str(error)
        self.guardar()
        return True, f"Nota agregada ({nota}). Promedio: {matricula.promedio} · {matricula.estado}"

    def boletin(self, estudiante_id):
        estudiante = None
        for e in self.estudiantes.listar():
            if e.id == estudiante_id:
                estudiante = e
        if estudiante is None:
            return None

        matriculas = [m for m in self.listar() if m.estudiante_id == estudiante_id]
        materias = {m.id: m for m in self.materias.listar()}

        texto = f"BOLETÍN   {estudiante.nombre_completo}   carnet: {estudiante.carnet}\n"
        texto += "-" * 50 + "\n"
        promedios = []
        for matricula in matriculas:
            materia = materias.get(matricula.materia_id)
            nombre = f"{materia.codigo} {materia.nombre}" if materia else "materia eliminada"
            texto += f"  {nombre}  [{matricula.periodo}]\n"
            for nota in matricula.notas:
                texto += f"     {nota}  (peso {nota.peso})\n"
            texto += f"     Promedio: {matricula.promedio:.2f}  →  {matricula.estado}\n"
            if matricula.notas:
                promedios.append(matricula.promedio)
        texto += "-" * 50 + "\n"
        general = round(sum(promedios) / len(promedios), 2) if promedios else 0
        texto += f"  PROMEDIO GENERAL: {general:.2f}"
        return texto